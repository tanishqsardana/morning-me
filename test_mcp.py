#!/usr/bin/env python3

import subprocess
import json
import time

def test_mcp_server():
    """Test the MCP weather server with basic initialization"""
    
    # Start the server process
    process = subprocess.Popen(
        ['python', '-m', 'mcp_weather_server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send initialization message
    init_message = {
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
    
    try:
        # Send the message
        input_data = json.dumps(init_message) + '\n'
        
        # Try to read response
        stdout, stderr = process.communicate(input=input_data, timeout=5)
        
        print("STDOUT:")
        print(stdout)
        print("\nSTDERR:")
        print(stderr)
        print(f"\nReturn code: {process.returncode}")
        
    except subprocess.TimeoutExpired:
        print("Process timed out")
        process.kill()
        stdout, stderr = process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
    except Exception as e:
        print(f"Error: {e}")
        process.kill()

if __name__ == "__main__":
    test_mcp_server()