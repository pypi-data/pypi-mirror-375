class ProvisionsAPI:
    def __init__(self, client):
        self.client = client

    async def list(self):
        return await self.client.get("/provisions")

    async def create(self, name, script):
        return await self.client.put(f"/provisions/{name}", json={"script": script})

    async def delete(self, name):
        return await self.client.delete(f"/provisions/{name}")
    