#!/usr/bin/env python3
"""Gong MCP Server implementation using FastMCP."""

import os
import sys
import hmac
import hashlib
import base64
import json
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Constants
GONG_API_URL = "https://api.gong.io/v2"
GONG_ACCESS_KEY = os.getenv("GONG_ACCESS_KEY")
GONG_ACCESS_SECRET = os.getenv("GONG_ACCESS_SECRET")

# Check for required environment variables
if not GONG_ACCESS_KEY or not GONG_ACCESS_SECRET:
    print("Error: GONG_ACCESS_KEY and GONG_ACCESS_SECRET environment variables are required", file=sys.stderr)
    sys.exit(1)


@dataclass
class GongCall:
    """Represents a Gong call."""
    id: str
    title: str
    scheduled: Optional[str] = None
    started: Optional[str] = None
    duration: Optional[int] = None
    direction: Optional[str] = None
    system: Optional[str] = None
    scope: Optional[str] = None
    media: Optional[str] = None
    language: Optional[str] = None
    url: Optional[str] = None


class GongClient:
    """Client for interacting with the Gong API."""

    def __init__(self, access_key: str, access_secret: str):
        """Initialize the Gong client with credentials."""
        self.access_key = access_key
        self.access_secret = access_secret
        self.client = httpx.Client(timeout=30.0)

    def _generate_signature(self, method: str, path: str, timestamp: str, params: Optional[dict] = None) -> str:
        """Generate HMAC-SHA256 signature for Gong API authentication."""
        # Create string to sign
        params_str = json.dumps(params) if params else ""
        string_to_sign = f"{method}\n{path}\n{timestamp}\n{params_str}"

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.access_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # Base64 encode the signature
        return base64.b64encode(signature).decode('utf-8')

    def _request(self, method: str, path: str, params: Optional[dict] = None, data: Optional[dict] = None) -> dict:
        """Make an authenticated request to the Gong API."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        url = f"{GONG_API_URL}{path}"

        # Create authentication headers
        auth_string = f"{self.access_key}:{self.access_secret}"
        basic_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {basic_auth}",
            "X-Gong-AccessKey": self.access_key,
            "X-Gong-Timestamp": timestamp,
            "X-Gong-Signature": self._generate_signature(method, path, timestamp, data or params)
        }

        # Make the request
        response = self.client.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    def list_calls(self, from_date_time: Optional[str] = None, to_date_time: Optional[str] = None) -> dict:
        """List Gong calls with optional date range filtering."""
        params = {}
        if from_date_time:
            params["fromDateTime"] = from_date_time
        if to_date_time:
            params["toDateTime"] = to_date_time

        return self._request("GET", "/calls", params=params)

    def retrieve_transcripts(self, call_ids: list[str]) -> dict:
        """Retrieve transcripts for specified call IDs."""
        data = {
            "filter": {
                "callIds": call_ids,
                "includeEntities": True,
                "includeInteractionsSummary": True,
                "includeTrackers": True
            }
        }
        return self._request("POST", "/calls/transcript", data=data)

    def close(self):
        """Close the HTTP client."""
        self.client.close()


# Initialize Gong client
gong_client = GongClient(GONG_ACCESS_KEY, GONG_ACCESS_SECRET)

# Initialize FastMCP server
mcp = FastMCP("gong-mcp", version="0.1.0")


@mcp.tool()
def list_calls(from_date_time: Optional[str] = None, to_date_time: Optional[str] = None) -> str:
    """List Gong calls with optional date range filtering.

    Args:
        from_date_time: Start date/time in ISO format (e.g. 2024-03-01T00:00:00Z)
        to_date_time: End date/time in ISO format (e.g. 2024-03-31T23:59:59Z)

    Returns:
        JSON string containing call details including ID, title, start/end times,
        participants, and duration.
    """
    try:
        response = gong_client.list_calls(from_date_time, to_date_time)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def retrieve_transcripts(call_ids: list[str]) -> str:
    """Retrieve transcripts for specified call IDs.

    Args:
        call_ids: Array of Gong call IDs to retrieve transcripts for

    Returns:
        JSON string containing detailed transcripts including speaker IDs,
        topics, and timestamped sentences.
    """
    try:
        response = gong_client.retrieve_transcripts(call_ids)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def main():
    """Main entry point for the MCP server."""
    try:
        # Run the server with STDIO transport (default)
        mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...", file=sys.stderr)
    finally:
        gong_client.close()


if __name__ == "__main__":
    main()
