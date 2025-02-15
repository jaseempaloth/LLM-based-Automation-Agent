import asyncio
from fastapi import FastAPI, HTTPException
from typing import Optional
import os
from agent import AutomationAgent
import pandas as pd
from security import SecurityValidator

app = FastAPI()
agent = AutomationAgent()

@app.post("/run")
async def run_task(task: str):
    try:
        # Add timeout to ensure response within 20 seconds
        result = await asyncio.wait_for(
            asyncio.to_thread(agent.execute_task, task),
            timeout=19
        )
        return {"status": "success", "result": result}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
async def read_file(path: str):
    try:
        if not os.path.exists(path):
            raise HTTPException(status_code=404)
        
        with open(path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        if not os.path.exists(path):
            raise HTTPException(status_code=404)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/filter-csv")
async def filter_csv(path: str, column: str, value: str):
    try:
        SecurityValidator.validate_path(path)
        df = pd.read_csv(path)
        filtered_df = df[df[column] == value]
        return filtered_df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
