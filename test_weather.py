#!/usr/bin/env python3

import subprocess
import json
import sys

def send_mcp_request(process, request):
    """Send an MCP request and get response"""
    input_data = json.dumps(request) + '\n'
    process.stdin.write(input_data)
    process.stdin.flush()
    
    # Read response line
    response_line = process.stdout.readline()
    if response_line:
        return json.loads(response_line.strip())
    return None

def test_weather_server():
    """Test the MCP weather server functionality"""
    
    # Start the server process
    process = subprocess.Popen(
        ['python', '-m', 'mcp_weather_server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0  # Unbuffered
    )
    
    try:
        # 1. Initialize
        print("🔧 Initializing MCP connection...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = send_mcp_request(process, init_request)
        if response:
            print("✅ Server initialized successfully")
            print(f"   Server: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}")
        else:
            print("❌ Failed to initialize")
            return
        
        # 2. Get available tools
        print("\\n🛠️ Getting available tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = send_mcp_request(process, tools_request)
        if response and 'result' in response:
            tools = response['result']['tools']
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ Failed to get tools list")
            return
        
        # 3. Test weather query
        print("\\n🌤️ Testing weather query for New York...")
        weather_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_weather",
                "arguments": {
                    "city": "New York"
                }
            }
        }
        
        response = send_mcp_request(process, weather_request)
        if response and 'result' in response:
            content = response['result']['content'][0]['text']
            print("✅ Weather data received:")
            print(f"   {content[:200]}..." if len(content) > 200 else f"   {content}")
        else:
            print("❌ Failed to get weather data")
            if response:
                print(f"   Error: {response}")
        
        # 4. Test timezone query
        print("\\n🕐 Testing timezone query...")
        timezone_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_timezone_info",
                "arguments": {
                    "timezone": "America/New_York"
                }
            }
        }
        
        response = send_mcp_request(process, timezone_request)
        if response and 'result' in response:
            content = response['result']['content'][0]['text']
            print("✅ Timezone data received:")
            print(f"   {content}")
        else:
            print("❌ Failed to get timezone data")
            if response:
                print(f"   Error: {response}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        process.terminate()
        process.wait()
        print("\\n🔚 Server stopped")

if __name__ == "__main__":
    test_weather_server()