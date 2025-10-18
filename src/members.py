from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


SQL_SEND_MESSAGE = "INSERT INTO messages (room_id, member_id, content) VALUES (?, ?, ?) RETURNING id;"

async def sendMessage(env, room_id: str, member_id: str, content: str):
    try:
        res = await env.DB.prepare(SQL_SEND_MESSAGE).bind(room_id, member_id, content).all()
        return {"content": f"{content}"}
    except Exception as e:
        # print(f"Error: {str(e)}")
        return {"Error": str(e)}
    

    
