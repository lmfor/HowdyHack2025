import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { room } from './routes/room.js'
import { members } from './routes/members.js'

const app = new Hono()

app.use('*', cors({
    // During dev: reflect whatever origin is calling you.
    // In prod: replace with a string or an array of allowed origins.
    origin: (origin) => origin || '*',
    allowMethods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowHeaders: ['Content-Type', 'Authorization'],
    exposeHeaders: [],
    maxAge: 86400,
    credentials: false // set to true only if we actually send cookies/Authorization
}))
app.get('/', (c) => c.json({ ok: true, service: 'workers-js-hono-port-js' }))

app.route('/rooms', room)
app.route('/members', members)

app.notFound((c) => c.json({ error: 'Not found' }, 404))
app.onError((err, c) => {
  console.error(err)
  return c.json({ error: 'Internal error' }, 500)
})

export default app