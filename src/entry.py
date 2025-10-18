from workers import Response, WorkerEntrypoint
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel



class Default(WorkerEntrypoint):
    async def fetch(self, request):
        import asgi

        return await asgi.fetch(app, request, self.env)
    

app = FastAPI()

@app.get("/")
async def root():
    return{"message": "root page"}

class Room(BaseModel):
    room_id: str
    name: str
@app.post("/room")
async def create_room(room: Room, req: Request):
    env = req.scope["env"]
    from room import createRoom
    return await createRoom(env, room.name)

@app.delete("/room/{id}")
async def delete_room(room: Room, req: Request):
    env = req.scope["env"]
    if 