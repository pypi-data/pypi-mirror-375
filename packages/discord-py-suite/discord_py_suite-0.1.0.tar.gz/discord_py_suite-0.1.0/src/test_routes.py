"""Test script for route handling functionality."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from routes import route_handler, setup_default_routes


async def test_route_matching():
    """Test route pattern matching."""
    print("🧪 Testing route pattern matching...")

    # Set up default routes
    setup_default_routes()

    # Test webhook route
    match = route_handler.match_route("/webhooks/123456789/token123", "POST")
    if match:
        print(f"✅ Webhook route matched: {match.path_params}")
    else:
        print("❌ Webhook route not matched")

    # Test guild event route
    match = route_handler.match_route("/guilds/987654321/events/member_join", "POST")
    if match:
        print(f"✅ Guild event route matched: {match.path_params}")
    else:
        print("❌ Guild event route not matched")

    # Test channel message route
    match = route_handler.match_route(
        "/guilds/987654321/channels/555666777/messages", "POST"
    )
    if match:
        print(f"✅ Channel message route matched: {match.path_params}")
    else:
        print("❌ Channel message route not matched")


async def test_route_handling():
    """Test route request handling."""
    print("\n🧪 Testing route request handling...")

    # Test webhook delivery
    response = await route_handler.handle_request(
        path="/webhooks/123456789/token123",
        method="POST",
        headers={"Authorization": "Bot test_token", "Content-Type": "application/json"},
        body=b'{"type": "message", "content": "test"}',
    )

    if response["status"] == 200:
        print("✅ Webhook delivery handled successfully")
    else:
        print(f"❌ Webhook delivery failed: {response}")

    # Test invalid route
    response = await route_handler.handle_request(
        path="/invalid/route", method="GET", headers={}
    )

    if response["status"] == 404:
        print("✅ Invalid route handled correctly (404)")
    else:
        print(f"❌ Invalid route not handled correctly: {response}")


async def test_route_info():
    """Test route information retrieval."""
    print("\n🧪 Testing route information...")

    routes = route_handler.get_routes_info()
    print(f"✅ Found {len(routes)} registered routes:")

    for route in routes:
        print(f"  - {route['methods']} {route['path']}: {route['description']}")


async def main():
    """Run all route tests."""
    print("🚀 Starting Discord-Py-Suite Route Tests")
    print("=" * 50)

    try:
        await test_route_matching()
        await test_route_handling()
        await test_route_info()

        print("\n" + "=" * 50)
        print("✅ All route tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
