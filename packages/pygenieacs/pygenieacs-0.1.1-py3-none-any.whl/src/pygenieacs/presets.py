from .clients import GenieACSClient


class PresetsAPI:
    def __init__(self, client: GenieACSClient):
        self.client = client

    async def list(self):
        return await self.client.get("/presets")

    async def get(self, preset_name: str):
        return await self.client.get(f"/presets/{preset_name}")

    async def create(self, name: str, data: dict):
        return await self.client.post(f"/presets/{name}", json=data)

    async def delete(self, preset_name: str):
        return await self.client.delete(f"/presets/{preset_name}")
