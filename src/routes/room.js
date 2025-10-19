// room.js
import { Hono } from 'hono'
import { z } from 'zod'
import { DatabaseQueue } from '../lib/dbQueue.js'

export const room = new Hono()

const CreateRoomSchema = z.object({
  name: z.string().min(1).max(120).optional()
})

room.get('/', async (c) => {
  const dbq = DatabaseQueue.instance()
  const data = await dbq.run(async () => {
    const { results } = await c.env.DB
      .prepare('SELECT room_id, name FROM rooms')
      .all()
    return results ?? []
  }).catch(() => [])
  return c.json(data)
})

room.post('/', async (c) => {
  const body = await c.req.json().catch(() => ({}))
  const parsed = CreateRoomSchema.safeParse(body)
  if (!parsed.success) return c.json({ error: 'Invalid payload' }, 400)

  const room_id = crypto.randomUUID().slice(0, 6).replace(/-/g, '').toUpperCase()
  const dbq = DatabaseQueue.instance()
  const id = crypto.randomUUID()

  await dbq.run(async () => {
    await c.env.DB.prepare(
      "INSERT INTO rooms (room_id, name, host_id) VALUES (?1, ?2, ?3)"
    ).bind(room_id, parsed.data.name, id).run()
  })

  await dbq.run(async () => {
    await c.env.DB.prepare(
      "INSERT INTO members (id, display_name, room_id) VALUES (?1, ?2, ?3)"
    ).bind(id, "Professor", room_id).run()
  })

  return c.json({ room_id, name: parsed.data.name, host_id: id })
})

room.get('/:id', async (c) => {
  const id = c.req.param('id')
  const dbq = DatabaseQueue.instance()
  const row = await dbq.run(async () => {
    return await c.env.DB.prepare(
      'SELECT room_id, name, host_id FROM rooms WHERE room_id = ?1'
    ).bind(id).first()
  }).catch(() => null)

  if (!row) return c.json({ error: 'Not found' }, 404)
  return c.json(row)
})

room.delete('/:id', async (c) => {
  const id = c.req.param('id')
  const dbq = DatabaseQueue.instance()
  await dbq.run(async () => {
    await c.env.DB.batch([
      c.env.DB.prepare('DELETE FROM messages WHERE room_id = ?1').bind(id),
      c.env.DB.prepare('DELETE FROM members WHERE room_id = ?1').bind(id),
      c.env.DB.prepare('DELETE FROM rooms WHERE room_id = ?1').bind(id),
    ])
  })
  return c.json({ ok: true })
})

const SendMessageSchema = z.object({
  member_id: z.string().uuid(),
  content: z.string().min(1).max(4000)
})

room.post('/:room_id/messages', async (c) => {
  try {
    const room_id = c.req.param('room_id')
    const body = await c.req.json()
    const parsed = SendMessageSchema.safeParse(body)
    if (!parsed.success) return c.json({ error: 'Invalid payload' }, 400)

    const id = crypto.randomUUID()
    const dbq = DatabaseQueue.instance()
    await dbq.run(async () => {
      await c.env.DB.prepare(
        "INSERT INTO messages (room_id, member_id, content) VALUES (?1, ?2, ?3)"
      ).bind(room_id, parsed.data.member_id, parsed.data.content).run()
    })
    return c.json({ id, room_id, ...parsed.data })
  } catch (e) {
    console.error('Error in sendMessage:', e)
    return c.json({ error: String(e) }, 500)
  }
})

// NOTE: this endpoint now returns **all** messages when the requester is the host (professor),
// otherwise it returns messages from the requester and the host (legacy behavior).
room.get('/:room_id/messages', async (c) => {
  const room_id = c.req.param('room_id')
  const memberId = String(c.req.query('member_id') || '')

  if (!memberId) {
    return c.json({ error: 'member_id required as query param' }, 400)
  }

  const dbq = DatabaseQueue.instance()

  // find host id for the room
  const row = await dbq.run(async () => {
    return await c.env.DB.prepare(
      'SELECT host_id FROM rooms WHERE room_id = ?1'
    ).bind(room_id).first()
  }).catch(() => null)

  if (!row?.host_id) {
    return c.json({ error: 'Room not found' }, 404)
  }

  const host_id = String(row.host_id)

  // host gets ALL; non-host gets self + host
  const data = await dbq.run(async () => {
    if (memberId === host_id) {
      const { results } = await c.env.DB.prepare(
        `SELECT id, room_id, member_id, content
         FROM messages
         WHERE room_id = ?1
         ORDER BY id ASC`
      ).bind(room_id).all()
      return results ?? []
    } else {
      const { results } = await c.env.DB.prepare(
        `SELECT id, room_id, member_id, content
         FROM messages
         WHERE room_id = ?1 AND member_id IN (?2, ?3)
         ORDER BY id ASC`
      ).bind(room_id, memberId, host_id).all()
      return results ?? []
    }
  }).catch(() => [])

  return c.json(data)
})

room.get('/:room_id/members', async (c) => {
  const room_id = c.req.param('room_id')
  const dbq = DatabaseQueue.instance()

  const { host_id } = await dbq.run(async () => {
    return await c.env.DB.prepare(
      'SELECT host_id FROM rooms WHERE room_id = ?1'
    ).bind(room_id).first()
  }).catch(() => ({ host_id: null }))

  const data = await dbq.run(async () => {
    const { results } =  await c.env.DB.prepare(
      'SELECT id, display_name FROM members WHERE room_id = ?1'
    ).bind(room_id).all()
    return results ?? []
  }).catch(() => [])

  return c.json({ host_id, data })
})
