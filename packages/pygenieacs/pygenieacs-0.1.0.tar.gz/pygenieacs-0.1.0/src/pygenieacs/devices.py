from .client import GenieACSClient


class DevicesAPI:
    def __init__(self, client: GenieACSClient):
        self.client = client

    async def list(self, query=None):
        return await self.client.get("/devices", params=query or {})

    async def get(self, device_id: str):
        return await self.client.get(f"/devices/{device_id}")

    async def refresh_object(self, device_id: str, object_name: str):
        return await self.client.post(f"/devices/{device_id}/objects/{object_name}/refresh")

    async def delete(self, device_id: str):
        return await self.client.delete(f"/devices/{device_id}")
