class PresetsAPI:
    def __init__(self, client):
        self.client = client

    async def list(self):
        return await self.client.get("/presets")

    async def create(self, preset_id, config):
        return await self.client.put(f"/presets/{preset_id}", json=config)

    async def delete(self, preset_id):
        return await self.client.delete(f"/presets/{preset_id}")
    