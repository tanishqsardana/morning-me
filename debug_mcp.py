#!/usr/bin/env python3

import subprocess
import json
import time

def debug_mcp():
    process = subprocess.Popen(
        ['python', '-m', 'mcp_weather_server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Send initialize
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "debug", "version": "1.0"}
            }
        }
        
        print("Sending init message...")
        process.stdin.write(json.dumps(init_msg) + '\\n')
        process.stdin.flush()
        
        # Read init response
        init_response = process.stdout.readline()
        print(f"Init response: {init_response}")
        
        # Send initialized notification
        initialized_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_msg) + '\\n')
        process.stdin.flush()
        
        # Now try tools/list
        tools_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("Sending tools/list...")
        process.stdin.write(json.dumps(tools_msg) + '\\n')
        process.stdin.flush()
        
        # Try to read tools response
        tools_response = process.stdout.readline()
        print(f"Tools response: {tools_response}")
        
        # Give it a moment
        time.sleep(1)
        
        # Check if there's any error output
        process.stdin.close()
        stdout_rest, stderr = process.communicate(timeout=3)
        print(f"Remaining stdout: {stdout_rest}")
        print(f"Stderr: {stderr}")
        
    except Exception as e:
        print(f"Error: {e}")
        process.kill()

if __name__ == "__main__":
    debug_mcp()