// members.js
import { Hono } from 'hono'
import { z } from 'zod'
import { DatabaseQueue } from '../lib/dbQueue.js'

export const members = new Hono()

const AddMemberSchema = z.object({
  display_name: z.string().min(1).max(60)
})

members.get('/:room_id', async (c) => {
  const room_id = c.req.param('room_id')
  const dbq = DatabaseQueue.instance()
  const data = await dbq.run(async () => {
    const { results } = await c.env.DB.prepare(
      // FIX: removed stray comma before FROM
      'SELECT id, display_name, room_id FROM members WHERE room_id = ?1'
    ).bind(room_id).all()
    return results ?? []
  }).catch(() => [])
  return c.json(data)
})

members.post('/:room_id', async (c) => {
  const room_id = c.req.param('room_id')
  const body = await c.req.json().catch(() => ({}))
  const parsed = AddMemberSchema.safeParse(body)
  if (!parsed.success) return c.json({ error: 'Invalid payload' }, 400)

  const id = crypto.randomUUID()
  const dbq = DatabaseQueue.instance()
  await dbq.run(async () => {
    await c.env.DB.prepare(
      "INSERT INTO members (id, display_name, room_id) VALUES (?1, ?2, ?3)"
    ).bind(id, parsed.data.display_name, room_id).run()
  })
  return c.json({ id, display_name: parsed.data.display_name, room_id })
})

members.delete('/:room_id/:member_id', async (c) => {
  const room_id = c.req.param('room_id')
  const member_id = c.req.param('member_id') // FIX: param name
  const dbq = DatabaseQueue.instance()
  await dbq.run(async () => {
    await c.env.DB.prepare('DELETE FROM members WHERE id = ?1 AND room_id = ?2')
      .bind(member_id, room_id).run()
  })
  return c.json({ ok: true })
})
