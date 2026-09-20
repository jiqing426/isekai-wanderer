#!/usr/bin/env python3
"""Test SSE streaming endpoint for character chat."""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def register_user():
    """Register a test user and return access token."""
    payload = {
        "email": "test_sse@example.com",
        "password": "***",
        "display_name": "SSE Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    if response.status_code == 201:
        data = response.json()
        return data["access_token"]
    else:
        # User might already exist, try login
        login_payload = {
            "email": "test_sse@example.com",
            "password": "***"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            raise Exception(f"Failed to get token: {response.status_code} {response.text}")

def test_sse_stream(token):
    """Test the SSE streaming endpoint."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Use a test character ID
    character_id = "00000000-0000-0000-0000-000000000001"
    
    payload = {
        "content": "你好，今天天气怎么样？"
    }
    
    print(f"Testing SSE stream for character {character_id}...")
    print(f"Sending message: {payload['content']}")
    print("-" * 60)
    
    # Make streaming request
    response = requests.post(
        f"{BASE_URL}/character-chat/{character_id}/stream",
        headers=headers,
        json=payload,
        stream=True
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print("-" * 60)
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return False
    
    # Parse SSE events
    full_reply = ""
    message_id = None
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            print(f"Received: {line_str}")
            
            # Parse SSE event
            if line_str.startswith("data: "):
                data_str = line_str[6:]  # Remove "data: " prefix
                try:
                    data = json.loads(data_str)
                    event_type = data.get("type")
                    
                    if event_type == "text":
                        content = data.get("content", "")
                        full_reply += content
                        print(f"  -> Text chunk: {content}")
                    elif event_type == "done":
                        message_id = data.get("message_id")
                        print(f"  -> Stream completed, message_id: {message_id}")
                    elif event_type == "error":
                        error_msg = data.get("message", "Unknown error")
                        print(f"  -> Error: {error_msg}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"  -> Failed to parse JSON: {e}")
    
    print("-" * 60)
    print(f"Full reply: {full_reply}")
    print(f"Message ID: {message_id}")
    print("-" * 60)
    
    # Verify message was saved
    if message_id:
        print("Verifying message was saved to database...")
        messages_response = requests.get(
            f"{BASE_URL}/character-chat/{character_id}/messages?page=1&page_size=10",
            headers=headers
        )
        if messages_response.status_code == 200:
            messages_data = messages_response.json()
            messages = messages_data.get("messages", [])
            
            # Check if our message exists
            found = False
            for msg in messages:
                if msg.get("id") == message_id:
                    found = True
                    print(f"✓ Message found in database: {msg.get('content')[:50]}...")
                    break
            
            if not found:
                print(f"✗ Message not found in database")
                return False
        else:
            print(f"✗ Failed to fetch messages: {messages_response.status_code}")
            return False
    
    print("✓ SSE stream test passed!")
    return True

def main():
    """Main test function."""
    try:
        print("=" * 60)
        print("SSE Streaming Test")
        print("=" * 60)
        
        # Register user and get token
        print("\n1. Registering user...")
        token = register_user()
        print(f"✓ Got token: {token[:20]}...")
        
        # Test SSE stream
        print("\n2. Testing SSE stream...")
        success = test_sse_stream(token)
        
        if success:
            print("\n" + "=" * 60)
            print("✓ All tests passed!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("✗ Test failed")
            print("=" * 60)
            exit(1)
            
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
