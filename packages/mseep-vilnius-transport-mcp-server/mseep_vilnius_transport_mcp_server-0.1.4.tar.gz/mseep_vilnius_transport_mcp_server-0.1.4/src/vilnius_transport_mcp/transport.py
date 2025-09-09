import os
import logging
import asyncio
from typing import Any, List, Tuple
from pathlib import Path
import gtfs_kit as gk
import numpy as np
import pandas as pd
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vilnius_transport")

# Initialize MCP server
server = Server("vilnius_transport")

# Initialize GTFS feed
package_dir = Path(__file__).parent
gtfs_path = package_dir / "data" / "gtfs.zip"
feed = gk.read_feed(str(gtfs_path), dist_units='km')


def parse_coordinates(coord_str: str) -> Tuple[float, float]:
    """Parse coordinates string into latitude and longitude.

    Args:
        coord_str: String containing latitude and longitude separated by comma

    Returns:
        Tuple of (latitude, longitude) as floats

    Raises:
        ValueError: If coordinates are invalid or out of range
    """
    try:
        lat_str, lon_str = coord_str.split(',')
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())

        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("Coordinates out of valid range")

        return lat, lon
    except ValueError as e:
        raise ValueError("Invalid coordinates format. Expected 'latitude, longitude'") from e


def calculate_distances(lat: float, lon: float, stops_df: 'pd.DataFrame') -> 'pd.Series':
    """Calculate distances from given point to all stops using Haversine formula.

    Args:
        lat: Latitude of the point
        lon: Longitude of the point
        stops_df: DataFrame containing stops data

    Returns:
        Series containing distances to all stops in kilometers
    """
    R = 6371  # Earth's radius in kilometers

    # Convert degrees to radians
    lat1, lon1 = np.radians(lat), np.radians(lon)
    lat2, lon2 = np.radians(stops_df['stop_lat']), np.radians(stops_df['stop_lon'])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for interacting with Vilnius transport data."""
    return [
        Tool(
            name="find_stops",
            description="Search for public transport stops by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full or partial name of the stop to search for",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="find_closest_stop",
            description="Find the closest public transport stop to given coordinates",
            inputSchema={
                "type": "object",
                "properties": {
                    "coordinates": {
                        "type": "string",
                        "description": "Coordinates as 'latitude, longitude' (e.g., '54.687157, 25.279652')",
                    },
                },
                "required": ["coordinates"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls for transport data."""
    if name == "find_stops":
        return await handle_find_stops(arguments)
    elif name == "find_closest_stop":
        return await handle_find_closest_stop(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_find_stops(arguments: Any) -> List[TextContent]:
    """Handle the find_stops tool call."""
    if not isinstance(arguments, dict) or "name" not in arguments:
        raise ValueError("Invalid arguments: 'name' is required")

    try:
        name = arguments["name"]
        stops_df = gk.get_stops(feed)

        logger.info(f'Passing stop name: {name}')

        # Case-insensitive search
        search_term = name.lower()
        matching_stops = stops_df[
            stops_df['stop_name'].str.lower().str.contains(search_term, na=False)
        ]

        if matching_stops.empty:
            logger.error(f'No stops found for {name}')
            return [TextContent(
                type="text",
                text=f"No stops found matching '{name}'"
            )]

        # Format results
        response_parts = [
            f"Found {len(matching_stops)} stops matching '{name}':"
        ]

        logger.info(f'Found response {response_parts}')

        for _, stop in matching_stops.iterrows():
            stop_lat = float(stop['stop_lat'])
            stop_lon = float(stop['stop_lon'])
            maps_link = f"https://www.google.com/maps?q={stop_lat},{stop_lon}"

            response_parts.append(
                f"\n- {stop['stop_name']}"
                f"\n  ID: {stop['stop_id']}"
                f"\n  Location: {stop_lat:.6f}, {stop_lon:.6f}"
                f"\n  View on Maps: {maps_link}"
            )

        return [TextContent(
            type="text",
            text="\n".join(response_parts)
        )]

    except Exception as e:
        logger.error(f"Error searching for stops: {str(e)}")
        raise RuntimeError(f"Error searching for stops: {str(e)}")


async def handle_find_closest_stop(arguments: Any) -> List[TextContent]:
    """Handle the find_closest_stop tool call."""
    if not isinstance(arguments, dict) or "coordinates" not in arguments:
        raise ValueError("Invalid arguments: 'coordinates' is required")

    try:
        coord_str = arguments["coordinates"]
        logger.info(f'Processing coordinates: {coord_str}')

        # Parse coordinates
        lat, lon = parse_coordinates(coord_str)

        # Get stops data
        stops_df = gk.get_stops(feed)

        # Calculate distances to all stops
        distances = calculate_distances(lat, lon, stops_df)

        # Find the closest stop
        closest_idx = distances.idxmin()
        closest_stop = stops_df.loc[closest_idx]
        distance_km = distances[closest_idx]

        # Format response
        response_text = (
            f"Closest stop to coordinates ({lat:.6f}, {lon:.6f}):\n"
            f"- {closest_stop['stop_name']}\n"
            f"  ID: {closest_stop['stop_id']}\n"
            f"  Location: {float(closest_stop['stop_lat']):.6f}, {float(closest_stop['stop_lon']):.6f}\n"
            f"  Distance: {distance_km:.2f} km"
        )

        logger.info(f'Found closest stop: {closest_stop["stop_name"]}')

        return [TextContent(
            type="text",
            text=response_text
        )]

    except ValueError as e:
        logger.error(f"Invalid coordinates: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
    except Exception as e:
        logger.error(f"Error finding closest stop: {str(e)}")
        raise RuntimeError(f"Error finding closest stop: {str(e)}")

async def main():
    """Run the MCP server."""
    import mcp
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info('Starting vilnius transport mcp server')
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())