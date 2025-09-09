from .client import GenieACSClient


class TasksAPI:
    def __init__(self, client: GenieACSClient):
        self.client = client

    async def add(self, device_id: str, name: str, parameters=None):
        body = {"name": name}
        if parameters:
            body.update(parameters)
        return await self.client.post(f"/devices/{device_id}/tasks", json=body)

    async def get(self, device_id: str):
        return await self.client.get(f"/devices/{device_id}/tasks")