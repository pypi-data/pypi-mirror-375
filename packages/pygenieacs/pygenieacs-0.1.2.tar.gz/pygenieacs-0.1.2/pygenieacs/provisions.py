from .clients import GenieACSClient


class ProvisionsAPI:
    def __init__(self, client: GenieACSClient):
        self.client = client

    async def list(self):
        return await self.client.get("/provisions")

    async def get(self, provision_name: str):
        return await self.client.get(f"/provisions/{provision_name}")

    async def create(self, name: str, script: str):
        """Create a provision with GenieACS script"""
        payload = {"script": script}
        return await self.client.post(f"/provisions/{name}", json=payload)

    async def delete(self, provision_name: str):
        return await self.client.delete(f"/provisions/{provision_name}")
