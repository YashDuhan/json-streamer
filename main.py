from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
import uvicorn
from typing import Dict, Any, List

app = FastAPI(title="JSON Streamer", 
              description="API for streaming JSON content gradually, similar to how LLMs stream their responses.")

@app.post("/stream", summary="Stream JSON content", 
          description="Takes a JSON payload and streams it back with artificial delays to simulate progressive loading.")
async def stream_json(request: Request):
    data = await request.json()
    
    async def generate():
        # For simple values
        if isinstance(data, (int, float, str, bool)) or data is None:
            yield json.dumps(data)
            return
            
        # For dictionaries
        if isinstance(data, dict):
            yield "{"
            is_first = True
            
            for key, value in data.items():
                if not is_first:
                    yield ", "
                else:
                    is_first = False
                
                # Key
                yield f'"{key}": '
                
                # String values
                if isinstance(value, str):
                    yield '"'
                    for i in range(0, len(value), 3):
                        chunk = value[i:i+3].replace('"', '\\"')
                        yield chunk
                        await asyncio.sleep(0.1)
                    yield '"'
                
                # Simple values
                elif isinstance(value, (int, float, bool)) or value is None:
                    yield json.dumps(value)
                
                # Nested dictionaries
                elif isinstance(value, dict):
                    yield "{"
                    inner_first = True
                    
                    for inner_key, inner_value in value.items():
                        if not inner_first:
                            yield ", "
                        else:
                            inner_first = False
                        
                        yield f'"{inner_key}": '
                        
                        # Inner values are dumped directly to avoid recursion
                        yield json.dumps(inner_value)
                        await asyncio.sleep(0.1)
                    
                    yield "}"
                
                # Lists/arrays
                elif isinstance(value, list):
                    yield "["
                    inner_first = True
                    
                    for item in value:
                        if not inner_first:
                            yield ", "
                        else:
                            inner_first = False
                        
                        # List items are dumped directly to avoid recursion
                        yield json.dumps(item)
                        await asyncio.sleep(0.1)
                    
                    yield "]"
                
                await asyncio.sleep(0.2)
            
            yield "}"
        
        # For lists/arrays
        elif isinstance(data, list):
            yield "["
            is_first = True
            
            for item in data:
                if not is_first:
                    yield ", "
                else:
                    is_first = False
                
                # String items
                if isinstance(item, str):
                    yield '"'
                    for i in range(0, len(item), 3):
                        chunk = item[i:i+3].replace('"', '\\"')
                        yield chunk
                        await asyncio.sleep(0.1)
                    yield '"'
                
                # Simple items
                elif isinstance(item, (int, float, bool)) or item is None:
                    yield json.dumps(item)
                
                # Dict items - simple version without deeper nesting
                elif isinstance(item, dict):
                    yield json.dumps(item)
                
                # List items - simple version without deeper nesting
                elif isinstance(item, list):
                    yield json.dumps(item)
                
                await asyncio.sleep(0.2)
            
            yield "]"
    
    return StreamingResponse(generate(), media_type="application/json")

@app.get("/")
async def root():
    return {"message": "Welcome to JSON Streamer API. Use /stream endpoint to stream JSON content or visit /docs for interactive documentation."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
