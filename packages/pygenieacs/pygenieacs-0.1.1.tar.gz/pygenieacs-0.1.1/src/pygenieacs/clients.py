import httpx
from urllib.parse import urljoin


class GenieACSClient:
    def __init__(self, base_url="http://localhost:7557", username=None, password=None):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password) if username and password else None
        self.client = httpx.AsyncClient(
		        auth=self.auth,
		        timeout=10.0,
		        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
    
    
    def _url(self, path):
        return urljoin(f"{self.base_url}/", path.lstrip("/"))


    async def close(self):
        await self.client.aclose()
    
    async def get(self, path, **kwargs):
        r = await self.client.get(self._url(path), **kwargs)
        r.raise_for_status()
        return r.json()
    
    
    async def post(self, path, json=None, **kwargs):
        r = await self.client.post(self._url(path), json=json, **kwargs)
        r.raise_for_status()
        return r.json()
    
    
    async def put(self, path, json=None, **kwargs):
        r = await self.client.put(self._url(path), json=json, **kwargs)
        r.raise_for_status()
        return r.json()
        
    
    async def delete(self, path, **kwargs):
        r = await self.client.delete(self._url(path), **kwargs)
        r.raise_for_status()
        return r.status_code == 204
    
    
    