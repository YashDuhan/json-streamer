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
        if isinstance(data, dict):
            yield "{"
            first_item = True
            for key, value in data.items():
                if not first_item:
                    yield ", "
                else:
                    first_item = False
                
                yield f'"{key}": '
                
                if isinstance(value, str):
                    yield from stream_string(value)
                elif isinstance(value, (int, float, bool)) or value is None:
                    yield json.dumps(value)
                elif isinstance(value, dict):
                    yield from stream_dict(value)
                elif isinstance(value, list):
                    yield from stream_list(value)
                
                await asyncio.sleep(0.5)
            yield "}"
        
        elif isinstance(data, list):
            yield from stream_list(data)
        else:
            yield json.dumps(data)
    
    async def stream_string(value: str):
        yield '"'
        for i in range(0, len(value), 3):
            chunk = value[i:i+3]
            yield chunk.replace('"', '\\"')
            await asyncio.sleep(0.1)
        yield '"'
    
    async def stream_dict(d: Dict[str, Any]):
        yield "{"
        first_item = True
        for key, value in d.items():
            if not first_item:
                yield ", "
            else:
                first_item = False
            
            yield f'"{key}": '
            
            if isinstance(value, str):
                yield from stream_string(value)
            elif isinstance(value, (int, float, bool)) or value is None:
                yield json.dumps(value)
            elif isinstance(value, dict):
                yield from stream_dict(value)
            elif isinstance(value, list):
                yield from stream_list(value)
            
            await asyncio.sleep(0.2)
        yield "}"
    
    async def stream_list(l: List[Any]):
        yield "["
        first_item = True
        for item in l:
            if not first_item:
                yield ", "
            else:
                first_item = False
            
            if isinstance(item, str):
                yield from stream_string(item)
            elif isinstance(item, (int, float, bool)) or item is None:
                yield json.dumps(item)
            elif isinstance(item, dict):
                yield from stream_dict(item)
            elif isinstance(item, list):
                yield from stream_list(item)
            
            await asyncio.sleep(0.2)
        yield "]"
    
    return StreamingResponse(generate(), media_type="application/json")

@app.get("/")
async def root():
    return {"message": "Welcome to JSON Streamer API. Use /stream endpoint to stream JSON content or visit /docs for interactive documentation."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 