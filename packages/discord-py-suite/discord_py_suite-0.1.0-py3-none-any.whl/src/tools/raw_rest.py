"""Raw REST API tool for Discord-Py-Suite using HTTP API."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import aiohttp
from loguru import logger

from ..config import Config


def register_raw_rest_tools(app, discord_client, config: Config) -> None:
    """Register raw REST API tools with FastMCP."""

    @app.tool()
    async def raw_rest_api(
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a raw REST API call to Discord's API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: Discord API endpoint (e.g., '/guilds/123/channels')
            data: Request body data (for POST, PUT, PATCH)
            query_params: Query parameters to append to the URL
            headers: Additional headers to include

        Returns:
            Dictionary containing the API response
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            # Ensure endpoint starts with /
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint

            url = f"https://discord.com/api/v10{endpoint}"

            # Set up headers
            request_headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            if headers:
                request_headers.update(headers)

            # Prepare request data
            json_data = None
            if data and method.upper() in ["POST", "PUT", "PATCH"]:
                json_data = data

            async with aiohttp.ClientSession() as session:
                # Choose the appropriate HTTP method
                method_upper = method.upper()

                if method_upper == "GET":
                    async with session.get(
                        url, headers=request_headers, params=query_params
                    ) as response:
                        return await _handle_response(response)
                elif method_upper == "POST":
                    async with session.post(
                        url,
                        headers=request_headers,
                        json=json_data,
                        params=query_params,
                    ) as response:
                        return await _handle_response(response)
                elif method_upper == "PUT":
                    async with session.put(
                        url,
                        headers=request_headers,
                        json=json_data,
                        params=query_params,
                    ) as response:
                        return await _handle_response(response)
                elif method_upper == "PATCH":
                    async with session.patch(
                        url,
                        headers=request_headers,
                        json=json_data,
                        params=query_params,
                    ) as response:
                        return await _handle_response(response)
                elif method_upper == "DELETE":
                    async with session.delete(
                        url, headers=request_headers, params=query_params
                    ) as response:
                        return await _handle_response(response)
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported HTTP method: {method}",
                    }

        except Exception as e:
            logger.error(f"Error making raw REST API call: {e}")
            return {"success": False, "error": str(e)}


async def _handle_response(response: aiohttp.ClientResponse) -> Dict[str, Any]:
    """Handle the HTTP response from Discord API."""
    try:
        # Get response headers
        response_headers = dict(response.headers)

        # Handle different response types
        if response.status == 204:  # No Content
            return {
                "success": True,
                "status": response.status,
                "headers": response_headers,
                "data": None,
            }
        elif response.status >= 200 and response.status < 300:
            # Success responses
            try:
                data = await response.json()
                return {
                    "success": True,
                    "status": response.status,
                    "headers": response_headers,
                    "data": data,
                }
            except json.JSONDecodeError:
                # Response is not JSON
                text_data = await response.text()
                return {
                    "success": True,
                    "status": response.status,
                    "headers": response_headers,
                    "data": text_data,
                }
        else:
            # Error responses
            try:
                error_data = await response.json()
                return {
                    "success": False,
                    "status": response.status,
                    "headers": response_headers,
                    "error": error_data,
                }
            except json.JSONDecodeError:
                # Error response is not JSON
                error_text = await response.text()
                return {
                    "success": False,
                    "status": response.status,
                    "headers": response_headers,
                    "error": error_text,
                }

    except Exception as e:
        logger.error(f"Error handling API response: {e}")
        return {"success": False, "error": f"Response handling error: {str(e)}"}

    logger.info("Raw REST API tools registered with FastMCP")
