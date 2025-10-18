import random, string
from pydantic import BaseModel

SQL_CREATE_ROOM = "INSERT INTO rooms (room_id, name) VALUES (?, ?) RETURNING room_id, name;"

async def createRoom(env, name):
    '''
    try:
        length = 6
        room_id = ''.join(random.choices(string.ascii_letters.upper() + string.digits, k=length))
        # res = await env.DB.prepare(SQL_CREATE_ROOM).bind(room_id, name).all()

    except Exception as e:
        pass
    '''
    length = 6
    room_id = ''.join(random.choices(string.ascii_letters.upper() + string.digits, k=length))


    return {"room_id": room_id, 
            "name": name}