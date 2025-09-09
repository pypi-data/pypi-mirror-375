import requests


class GenieACSClient:
	def __init__(self, base_url="http://localhost:7557", username=None, password=None):
		self.base_url = base_url.rstrip("/")
		self.session = requests.Session()
		if username and password:
			self.session.auth = (username, password)
	
	
	def _url(self, path):
		return f"{self.base_url}{path}"
	
	
	async def get(self, path, **kwargs):
		r = self.session.get(self._url(path), **kwargs)
		await r.raise_for_status()
		return r.json()
	
	
	async def post(self, path, json=None, **kwargs):
		r = self.session.post(self._url(path), json=json, **kwargs)
		await r.raise_for_status()
		return r.json()
	
	
	async def put(self, path, json=None, **kwargs):
		r = self.session.put(self._url(path), json=json, **kwargs)
		await r.raise_for_status()
		return r.json()
	
	
	async def delete(self, path, **kwargs):
		r = self.session.delete(self._url(path), **kwargs)
		await r.raise_for_status()
		return r.status_code == 204
