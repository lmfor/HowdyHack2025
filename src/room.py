import random, string
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

SQL_CREATE_ROOM = "INSERT INTO rooms (room_id, name) VALUES (?, ?) RETURNING room_id, name;"
SQL_JOIN_ROOM = "INSERT INTO members (id, room_id, display_name) VALUES (?, ?, COALESCE(NULLIF(?, ''), 'Anonymous')) RETURNING id, room_id, display_name;"
SQL_JOIN_ROOM_ADMIN = "UPDATE rooms SET host_id = ? WHERE room_id = ?;"
SQL_DEL_ROOM = "DELETE FROM rooms WHERE room_id = ?"
SQL_GET_MESSAGES = "SELECT * FROM messages WHERE room_id = ?"
SQL_GET_RELEVANT_MESSAGES = "SELECT * FROM messages WHERE room_id = ? AND member_id IN (?, ?);"
SQL_GET_ADMIN = "SELECT host_id FROM rooms WHERE room_id = ?"

async def isAdmin(env, room_id : str, member_id:str) -> bool:
    res = await env.DB.prepare(SQL_GET_ADMIN).bind(room_id).all()
    # print(res.results.to_py()) --> [{'host_id': '69d5bf78-d251-4eeb-a432-3177b18dd5bb'}]
    if res.results.to_py()[0]['host_id'] == member_id:
        return True
    return False

async def getRelevantMessages(env, room_id:str, member_id:str):
    admin_res = await env.DB.prepare(SQL_GET_ADMIN).bind(room_id).all()
    admin_id = admin_res.results.to_py()[0]['host_id']
    # print(admin_id)

    self_res = await env.DB.prepare(SQL_GET_RELEVANT_MESSAGES).bind(room_id, member_id, admin_id).all()
    return self_res



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

async def delRoom(env, room_id:str, member_id:str):
    try:
        # print("Hello world.", room_id)
        if (await isAdmin(env, room_id, member_id)):
            res = await env.DB.prepare(SQL_DEL_ROOM).bind(room_id).all()
            return {"message": f"Room {room_id} deleted."}
        
    except Exception as e:
        return {"message": f"Room {room_id} NOT FOUND"}
    
async def joinRoom(env, room_id, display_name, admin=False):
    try:
        import uuid
        member_id = str(uuid.uuid4())
        if admin:
            await env.DB.prepare(SQL_JOIN_ROOM_ADMIN).bind(member_id, room_id).all()
        
        result = await env.DB.prepare(SQL_JOIN_ROOM).bind(member_id, room_id, display_name).all()

        return {"join_message": f"{display_name} has joined room {room_id}",
                "member_id": f"{member_id}"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
    
# comment 
async def getMessages(env, room_id: str, member_id : str):
    try:
        if (await isAdmin(env, room_id, member_id)):
            res = await env.DB.prepare(SQL_GET_MESSAGES).bind(room_id).all()
            return res.results
        # comment in the functions
        
        # print(res.results)
        relevant_results = await getRelevantMessages(env,room_id, member_id)
        return relevant_results.results
                                                     
        
    except Exception as e:
        # print(e)
        return {"Error": str(e)}
    


