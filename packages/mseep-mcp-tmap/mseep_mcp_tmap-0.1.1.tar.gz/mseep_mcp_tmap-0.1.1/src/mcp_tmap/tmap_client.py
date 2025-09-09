import httpx
import os

from typing import Any, Dict, List, Optional

class TmapClient:

  BASE_URL = "https://apis.openapi.sk.com"

  def __init__(self):
    self.app_key = os.getenv("SK_OPEN_API_APP_KEY")
    if not self.app_key:
      raise AuthError("Missing client id or client secret")
    
    self.headers = {
      "appKey": self.app_key,
      "accept": "application/json",
      "content-type": "application/json",
    }

  async def getTransitRoutes(
    self,
    startLon: str,
    startLat: str,
    destLon: str,
    destLat: str,
    language: int,
    count: int = 10,
    searchTime: Optional[str] = None,
  ) -> Dict:
    path = f"{self.BASE_URL}/transit/routes"
    body = {
      "startX": startLon,
      "startY": startLat,
      "endX": destLon,
      "endY": destLat,
      "lang": language,
      "count": count,
      "format": "json",
    }
    if searchTime is not None:
      body["searchDttm"] = searchTime

    return (await self._post(path, body)).get("metaData", {}).get("plan", {})
  
  async def fullAddressGeocoding(
    self,
    fullAddress: str,
    count: int = 10,
  ) -> List:
    path = f"{self.BASE_URL}/tmap/geo/fullAddrGeo"
    params = {
      "version": 1,
      "addressFlag": "F02", # accepts both street address and lot number address (지번)
      "fullAddr": fullAddress,
      "count": count,
      "format": "json",
    }

    return (await self._get(path, params)).get("coordinateInfo", {}).get("coordinate", [])

  async def _get(self, path: str, params: Dict[str, Any]) -> Any:
    async with httpx.AsyncClient(headers=self.headers, http2=True) as client:
      response = await client.get(path, params=params)

      try:
        return response.raise_for_status().json()
      except httpx.HTTPError as exc:
        self._handle_response_status(response.status_code, exc)
    
  async def _post(self, path: str, body: Dict[str, Any]) -> Any:
    async with httpx.AsyncClient(headers=self.headers, http2=True) as client:
      response = await client.post(path, json=body)

      try:
        return response.raise_for_status().json()
      except httpx.HTTPError as exc:
        self._handle_response_status(response.status_code, exc)
    
  def _handle_response_status(self, http_status_code: int, http_error: httpx.HTTPError):
    error_str = str(http_error)
    if http_status_code == 400:
      raise BadRequestError(error_str)
    if http_status_code == 401:
      raise AuthError(error_str)
    if http_status_code == 420:
      raise RateLimitError(error_str)
    if http_status_code != 200:
      raise TmapClientError(f"Unexpected error [status_code={http_status_code}, error={error_str}]")

class TmapClientError(Exception):
  def __init__(self, message: str):
    self.message = message
    super().__init__(self.message)

class BadRequestError(TmapClientError):
  def __init__(self, message):
    super().__init__(f"Bad request: {message}")

class AuthError(TmapClientError):
  def __init__(self, message):
    super().__init__(f"Auth error: {message}")

class RateLimitError(TmapClientError):
  def __init__(self, message):
    super().__init__(f"Rate limited: {message}")
