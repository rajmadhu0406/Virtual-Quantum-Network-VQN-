from fastapi import APIRouter, HTTPException, Depends
from models.ChannelList import ChannelDataForCountRate
from config import settings
import httpx
import logging
from .auth_api import get_current_user
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

timetagger_api = os.getenv("TIMETAGGER_API")

router = APIRouter(
    prefix="/countrate",
    tags=["countrate"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_user)]
)


"""
When you add a dependency in the APIRouter (or globally) using the dependencies parameter, FastAPI will 
execute that dependency for each endpoint, but it won't pass its return value into your endpoint functions. 
To access the username (or any value returned by get_current_user) within your endpoint functions, you should 
declare it as a parameter in your endpoint using Depends

from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/countrate",
    tags=["countrate"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_countrate(current_user: str = Depends(get_current_user)):
    return {"username": current_user, "message": "Welcome to countrate!"}

"""

# @router.post("/create_countrate")
# async def create_countrate(channelList: ChannelList):
#     try:
#         channels_payload = {"channels": channelList.channels}  # Create a dictionary with the channelList.channels
#         async with httpx.AsyncClient() as client:
#             logger.debug(channels_payload)
#             logger.debug(timetagger_api + "/create_countrate/")
#             response = await client.post(timetagger_api + "/create_countrate/", json=channels_payload)
#             response.raise_for_status()
#             return response.json()
#     except Exception as exc:  # Catch all exceptions
#         logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}")  
#         raise HTTPException(
#             status_code=400,
#             detail=f"{type(exc).__name__}: {(exc)}"
#         )
#     except httpx.HTTPStatusError as http_exc:  # Catch HTTP-specific errors (4xx/5xx)
#         logger.error(f"HTTP error: {http_exc.response.status_code} - {http_exc.response.text}")
#         raise HTTPException(
#             status_code=http_exc.response.status_code,
#             detail=f"HTTP error: {http_exc.response.status_code} - {http_exc.response.text}"
#         )

        
@router.post("/get_countrate_data")
async def get_countrate_data(channelData: ChannelDataForCountRate):
    try:
        channels_payload = {"channels": channelData.numChannels}  # Create a dictionary with the channelList.channels
        logger.debug(str(channels_payload))

        async with httpx.AsyncClient() as client:
            logger.debug(channels_payload)
            logger.debug(timetagger_api + "/get_countrate_data/")
            response = await client.post(timetagger_api + "/get_countrate_data/", json=channels_payload)
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
   
        
# @router.get("/list_countrates")
# async def list_counters():
#     try:
#         async with httpx.AsyncClient() as client:
#             logger.debug(timetagger_api + "/list_countrates/")
#             response = await client.get(timetagger_api + "/list_countrates/")
#             response.raise_for_status()
#         return response.json()

#     except Exception as exc:  # Catch all exceptions
#         logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}")  
#         raise HTTPException(
#             status_code=400,
#             detail=f"{type(exc).__name__}: {(exc)}"
#         )
#     except httpx.HTTPStatusError as http_exc:  # Catch HTTP-specific errors (4xx/5xx)
#         logger.error(f"HTTP error: {http_exc.response.status_code} - {http_exc.response.text}")
#         raise HTTPException(
#             status_code=http_exc.response.status_code,
#             detail=f"HTTP error: {http_exc.response.status_code} - {http_exc.response.text}"
#         )
