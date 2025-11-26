#!/usr/bin/env python3

import subprocess
import json

def test_server():
    init_msg = {
        "jsonrpc": "2.0", 
        "id": 1, 
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    input_data = json.dumps(init_msg) + '\n'
    
    try:
        result = subprocess.run(
            ['python', '-m', 'mcp_weather_server'],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=10
        )
        
        print("Return code:", result.returncode)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
    except subprocess.TimeoutExpired:
        print("Timeout - server probably waiting for more input")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_server()