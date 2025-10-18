from workers import Response, WorkerEntrypoint
from room import createRoom

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return Response(createRoom("abcef"))
    