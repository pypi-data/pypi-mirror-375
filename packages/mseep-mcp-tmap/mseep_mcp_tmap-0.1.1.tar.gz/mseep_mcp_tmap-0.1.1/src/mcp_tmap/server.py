from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp_tmap.tmap_client import TmapClient
from typing import Dict, List, Optional

load_dotenv()

tmap_client = TmapClient()

INSTRUCTIONS = """
TMAP MCP provides tools for accessing the mobility platform provided by TMAP in South Korea.

- publicTransitRoutes: Retrieves public transit routes between two places.
  The response contains [legs], which are legs of the retrieved route.
  Use [start.name] in each leg to return a chain of legs.
  The underlying API is often rate-limited, so you have to ask a user if they really want to proceed with this tool.
- fullTextAddressGeocoding: Converts an address in full text into coordinates.
  The response contains a list of coordinates, which are ordered by the relevancy.
  If the entered address is not accurate, the response contains coordinates of a similar location.
  Use the first item in the response to return the coordinates.
  [newLat] is the latitude and [newLon] is the longitude.
""".strip()

mcp = FastMCP("mcp_tmap", instructions=INSTRUCTIONS)

@mcp.tool()
async def publicTransitRoutes(
  startLon: str,
  startLat: str,
  destLon: str,
  destLat: str,
  language: int = 0,
  searchTime: Optional[str] = None,
) -> Dict:
  """Retrieves public transportation routes from start to destination.

  Args:
    startLon (str): longitude of the starting point (WSG84).
    startLat (str): latitude of the starting point (WSG84).
    destLon (str): longitude of the destination (WSG84).
    destLat (str): latitude of the destination (WSG84).
    language (int): language of the route; 0 for Korean and 1 for English.
    searchTime (str, optional): Sets the time for the route to be searched.
      Used as information to indicate whether transportation is in operation.
      See [service] in the response for the operation status.

  Returns:
    route information
    - itineraries: route details
      - fare: total fare
      - totalTime: in seconds
      - transferCount:
      - totalWalkDistance: in meters
      - totalDistance: in meters
      - totalWalkTime: in seconds
      - legs: legs in the route
        - distance: in meters
        - sectionTime: in seconds
        - mode: transportation mode
        - route: transportation route
        - start: starting point of the leg
        - end: destination of the leg
  """
  assert (language == 0 or language == 1)
  try:
    return await tmap_client.getTransitRoutes(
      startLon, startLat,
      destLon, destLat,
      language,
      searchTime=searchTime,
    )
  except Exception as ex:
    return { "success": False, "error": str(ex) }

@mcp.tool()
async def fullTextAddressGeocoding(address: str) -> List | Dict:
  """Converts the given address to coordinates (geocoding).

  Args
    address (str): address to convert.
  
  Returns:
    a list of coordinates
    - newLat: latitude
    - newLon: longitude
    - newLatEntr: latitude of the entrance
    - newLonEntr: longitude of the entrance
  """
  assert len(address.strip()) > 0

  try:
    return await tmap_client.fullAddressGeocoding(address)
  except Exception as ex:
    return { "success": False, "error": str(ex) }
