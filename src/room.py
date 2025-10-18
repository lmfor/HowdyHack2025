import random, string
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

SQL_CREATE_ROOM = "INSERT INTO rooms (room_id, name) VALUES (?, ?) RETURNING room_id, name;"
SQL_JOIN_ROOM = "INSERT INTO members (id, room_id, display_name) VALUES (?, ?, COALESCE(NULLIF(?, ''), 'Anonymous')) RETURNING id, room_id, display_name;"
SQL_DEL_ROOM = "DELETE FROM rooms WHERE room_id = ?"
async def createRoom(env, name):
    
    try:
        length = 6
        room_id = ''.join(random.choices(string.ascii_letters.upper() + string.digits, k=length))
        res = await env.DB.prepare(SQL_CREATE_ROOM).bind(room_id, name).all()
        print(res)

    except Exception as e:
        print(str(e))
    
    # length = 6
    # room_id = ''.join(random.choices(string.ascii_letters.upper() + string.digits, k=length))


    return {"room_id": room_id, 
            "name": name}

async def delRoom(env, room_id):
    try:
        # print("Hello world.", room_id)
        res = await env.DB.prepare(SQL_DEL_ROOM).bind(room_id).all()
        return {"message": f"Room {room_id} deleted."}
    except Exception as e:
        return {"message": f"Room {room_id} NOT FOUND"}
    
async def joinRoom(env, room_id, display_name):
    try:
        import uuid
        member_id = str(uuid.uuid4())
        result = await env.DB.prepare(SQL_JOIN_ROOM).bind(member_id, room_id, display_name).all()
        return {"join_message": f"{display_name} has joined room {room_id}",
                "member_id": f"{member_id}"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}


