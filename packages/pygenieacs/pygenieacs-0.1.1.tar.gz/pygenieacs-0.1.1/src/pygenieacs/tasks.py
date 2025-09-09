from .clients import GenieACSClient


class TasksAPI:
    def __init__(self, client: GenieACSClient):
        self.client = client

    async def list(self, query=None):
        return await self.client.get("/tasks", params=query or {})

    async def add(self, device_id: str, command: str, params=None):
        """Add a task to a device"""
        payload = {"command": command, "params": params or {}}
        return await self.client.post(f"/devices/{device_id}/tasks", json=payload)

    async def get(self, task_id: str):
        return await self.client.get(f"/tasks/{task_id}")

    async def delete(self, task_id: str):
        return await self.client.delete(f"/tasks/{task_id}")
