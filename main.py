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
                    for chunk in await stream_string(value):
                        yield chunk
                elif isinstance(value, (int, float, bool)) or value is None:
                    yield json.dumps(value)
                elif isinstance(value, dict):
                    for chunk in await stream_dict(value):
                        yield chunk
                elif isinstance(value, list):
                    for chunk in await stream_list(value):
                        yield chunk
                
                await asyncio.sleep(0.5)
            yield "}"
        
        elif isinstance(data, list):
            async for chunk in stream_list(data):
                yield chunk
        else:
            yield json.dumps(data)
    
    async def stream_string(value: str):
        chunks = ['"']
        for i in range(0, len(value), 3):
            chunk = value[i:i+3]
            chunks.append(chunk.replace('"', '\\"'))
            await asyncio.sleep(0.1)
        chunks.append('"')
        return chunks
    
    async def stream_dict(d: Dict[str, Any]):
        chunks = ["{"]
        first_item = True
        for key, value in d.items():
            if not first_item:
                chunks.append(", ")
            else:
                first_item = False
            
            chunks.append(f'"{key}": ')
            
            if isinstance(value, str):
                for chunk in await stream_string(value):
                    chunks.append(chunk)
            elif isinstance(value, (int, float, bool)) or value is None:
                chunks.append(json.dumps(value))
            elif isinstance(value, dict):
                for chunk in await stream_dict(value):
                    chunks.append(chunk)
            elif isinstance(value, list):
                for chunk in await stream_list(value):
                    chunks.append(chunk)
            
            await asyncio.sleep(0.2)
        chunks.append("}")
        return chunks
    
    async def stream_list(l: List[Any]):
        chunks = ["["]
        first_item = True
        for item in l:
            if not first_item:
                chunks.append(", ")
            else:
                first_item = False
            
            if isinstance(item, str):
                for chunk in await stream_string(item):
                    chunks.append(chunk)
            elif isinstance(item, (int, float, bool)) or item is None:
                chunks.append(json.dumps(item))
            elif isinstance(item, dict):
                for chunk in await stream_dict(item):
                    chunks.append(chunk)
            elif isinstance(item, list):
                for chunk in await stream_list(item):
                    chunks.append(chunk)
            
            await asyncio.sleep(0.2)
        chunks.append("]")
        return chunks
    
    return StreamingResponse(generate(), media_type="application/json")

@app.get("/")
async def root():
    return {"message": "Welcome to JSON Streamer API. Use /stream endpoint to stream JSON content or visit /docs for interactive documentation."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
