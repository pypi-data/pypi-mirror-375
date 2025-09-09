import httpx
from typing import Any, Dict


class OpenEarth:
	def __init__(self, base_url: str, timeout: float = 15.0):
		self.base_url = base_url.rstrip("/")
		self._client = httpx.Client(timeout=timeout)

	def health(self) -> Dict[str, Any]:
		r = self._client.get(f"{self.base_url}/health"); r.raise_for_status(); return r.json()

	def rain(self, query: str) -> Dict[str, Any]:
		r = self._client.post(f"{self.base_url}/rain", json={"query": query}); r.raise_for_status(); return r.json()

	def wildfire(self, query: str) -> Dict[str, Any]:
		r = self._client.post(f"{self.base_url}/wildfire", json={"query": query}); r.raise_for_status(); return r.json()

	def close(self) -> None:
		self._client.close()
