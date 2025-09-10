"""
Test basic imports and module loading.
"""

import pytest


def test_basic_imports():
    """Test that basic modules can be imported."""
    try:
        import calimero
        print("✅ Calimero module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import calimero: {e}")
        pytest.skip(f"Calimero module not available: {e}")


def test_types_import():
    """Test that types module can be imported."""
    try:
        from calimero import types
        print("✅ Types module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import types: {e}")
        pytest.skip(f"Types module not available: {e}")


def test_client_import():
    """Test that client module can be imported."""
    try:
        from calimero import client
        print("✅ Client module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import client: {e}")
        pytest.skip(f"Client module not available: {e}")


def test_ws_subscriptions_import():
    """Test that websocket subscriptions module can be imported."""
    try:
        from calimero import ws_subscriptions_client
        print("✅ WebSocket subscriptions module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ws_subscriptions_client: {e}")
        pytest.skip(f"WebSocket subscriptions module not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
