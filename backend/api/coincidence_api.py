from fastapi import APIRouter, HTTPException, Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import httpx
import logging
from .auth_api import get_current_user
import asyncio
import random

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/coincidence",
    tags=["coincidence"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_user)]
)


@router.get("/")
async def coincidence_home():
    return {"message": "Coincidence home"}


@router.websocket("/ws/coincidence_count")
async def ws_coincidence_count(websocket: WebSocket):
    
    await websocket.accept()
    
    logger.debug("WebSocket connection established")
    
    try:
        # Wait for the client to send binwidth and n_bins
        data = await websocket.receive_json()
        
        logger.debug(f"Received data: {data}")
        
        binwidth = data.get("binwidth")  # in seconds
        n_bins = data.get("n_bins")      # integer
        
        mode = "counter"
        input_channel = [1,2]
        
        if binwidth is None or n_bins is None or not isinstance(binwidth, int) or not isinstance(n_bins, int):
            json_error = {"error": "Invalid input: 'binwidth' and 'n_bins' are required and must be integers."}
            await websocket.send_json(json_error)
            await websocket.close()
            return

        #calculate measurement duration
        measurement_duration = n_bins * binwidth
        
        # Send random data to the client for the measurement duration
        start_time = asyncio.get_event_loop().time()
        end_time = start_time + measurement_duration
        
        logger.debug(f"Request received for Measurement duration: {measurement_duration} seconds and will end at : {end_time}")
        
        while asyncio.get_event_loop().time() < end_time:
            elapsed_time = round(asyncio.get_event_loop().time() - start_time, 2)
            ch1_count = random.randint(0, 100)
            ch2_count = random.randint(0, 100)
            coincidence_count = random.randint(min(ch1_count, ch2_count), max(ch1_count, ch2_count))
            
            data = {
                "elapsed_time": elapsed_time,
                "ch1_count": ch1_count,
                "ch2_count": ch2_count,
                "coincidence_count": coincidence_count,
            }
            
            await websocket.send_json(data)
            await asyncio.sleep(0.5)  # Wait for 0.5 seconds before sending the next data point

        await websocket.send_json({"success": "Measurement completed"})
        await websocket.close()
    
    except WebSocketDisconnect:
        logger.error("WebSocket connection interupted")
        await websocket.send_json({"error": "WebSocket connection interupted"})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await websocket.send_json({"error": f"Unexpected error: {e}"})

        
        
        


