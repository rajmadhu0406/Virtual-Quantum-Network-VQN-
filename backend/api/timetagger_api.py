from fastapi import APIRouter, HTTPException, Depends
from models.ChannelList import ChannelList
from config import settings
import httpx
import logging
from .auth_api import get_current_user
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

timetagger_api = os.getenv("TIMETAGGER_API")


router = APIRouter(
    prefix="/timetagger",
    tags=["timetagger"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_user)]
)

@router.get("/")
def timetagger():
    return {"timetagger": "OK"}


@router.post("/start_test_signal")
async def start_signal(channelList: ChannelList):
    try:
        channels_payload = {"channels": channelList.channels}  # Create a dictionary with the channelList.channels
        async with httpx.AsyncClient() as client:
            logger.debug(channels_payload)
            logger.debug(timetagger_api + "/start_test_signal/")
            response = await client.post(timetagger_api + "/start_test_signal/", json=channels_payload)
            response.raise_for_status()
            return response.json()
            # return {
            #     "channels": channelList.channels,
            #     "message": "Test signal started"
            #     }
    except Exception as exc:  # Catch all exceptions
        logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}")  
        raise HTTPException(
            status_code=400,
            detail=f"{type(exc).__name__}: {(exc)}"
        )
    except httpx.HTTPStatusError as http_exc:  # Catch HTTP-specific errors (4xx/5xx)
        logger.error(f"HTTP error: {http_exc.response.status_code} - {http_exc.response.text}")
        raise HTTPException(
            status_code=http_exc.response.status_code,
            detail=f"HTTP error: {http_exc.response.status_code} - {http_exc.response.text}"
        )


@router.get("/status")
async def get_status():
    try:
        async with httpx.AsyncClient() as client:
            logger.debug(timetagger_api + "/status/")
            response = await client.get(timetagger_api + "/status/")
            response.raise_for_status()
        return response.json()
    
    except httpx.HTTPStatusError as http_exc:  # Catch HTTP-specific errors (4xx/5xx)
        logger.error(f"HTTP error: {http_exc.response.status_code} - {http_exc.response.text}")
        
        if http_exc.response.status_code == 404:  
            logger.error(f"404 Not Found error: {http_exc.response.text}")
            raise HTTPException(
                status_code=404,
                detail="The requested resource was not found on the server."
            )
        else:
            raise HTTPException(
                status_code=http_exc.response.status_code,
                detail=f"HTTP error: {http_exc.response.status_code} - {http_exc.response.text}"
            )
            
    except Exception as exc:  # Catch all exceptions
        logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}")  
        raise HTTPException(
            status_code=400,
            detail=f"{type(exc).__name__}: {(exc)}"
        )

