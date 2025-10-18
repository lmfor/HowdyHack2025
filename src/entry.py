from workers import Response, WorkerEntrypoint
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        import asgi # type: ignore

        return await asgi.fetch(app, request, self.env)
    

app = FastAPI()

@app.get("/")
async def root():
    return{"message": "root page"}

class Room(BaseModel):
    name: str

@app.post("/room")
async def create_room(room: Room, req: Request):
    env = req.scope["env"]
    from room import createRoom, joinRoom
    room_data = await createRoom(env, room.name)
    return await joinRoom(env, room_data.room_id, "Professor", admin=True)


@app.delete("/room/{room_id}")
async def delete_room(room_id: str, req: Request):
    env = req.scope["env"]
    from room import delRoom
    return await delRoom(env, room_id)

class JoinRequest(BaseModel):
    display_name: str

@app.put("/room/{room_id}")
async def join_room(payload: JoinRequest, room_id: str, req: Request):
    env = req.scope["env"]
    from room import joinRoom
    return await joinRoom(env, room_id, payload.display_name)

# ===================================== #

class MessageRequest(BaseModel):
    content: str
    member_id: str

@app.post("/room/{room_id}/messages")
async def send_message(payload: MessageRequest, room_id: str, req: Request):
    env = req.scope["env"]
    from members import sendMessage
    return await sendMessage(env, room_id, payload.member_id, payload.content)

@app.get("/room/{room_id}/messages")
async def get_messages(room_id: str, req: Request):
    env = req.scope["env"]
    from room import getMessages
    messages = await getMessages(env, room_id)
    print(messages.to_py())
    return messages.to_py()


