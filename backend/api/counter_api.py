from fastapi import APIRouter, HTTPException, Depends
import httpx
import logging
from models.ChannelList import ChannelListWithBins, ChannelList, ChannelDataForCounter
from .auth_api import get_current_user
import random
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

timetagger_api = os.getenv("TIMETAGGER_API")

router = APIRouter(
    prefix="/counter",
    tags=["counter"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_user)]
)

@router.get("/")
def counter():
    return {"create counter": "Hello, World!"}


# @router.post("/create_counter")
# async def create_counter(channelList: ChannelListWithBins):
#     try:
#         channels_payload = {"channels": channelList.channels, "n_values" : channelList.n_values}  # Create a dictionary with the channelList.channels
#         logger.debug(str(channels_payload))

#         async with httpx.AsyncClient() as client:
#             logger.debug(channels_payload)
#             logger.debug(timetagger_api + "/create_counter/")
#             response = await client.post(timetagger_api + "/create_counter/", json=channels_payload)
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

        
@router.post("/get_counter_data")
async def get_counter_data(channelData: ChannelDataForCounter):
    try:
        channels_payload = {"channels": channelData.numChannels, "binwidth": channelData.bin_width, "n_values": channelData.n_values }  # Create a dictionary with the channelList.channels
        logger.debug(str(channels_payload))

        async with httpx.AsyncClient() as client:
            logger.debug(channels_payload)
            logger.debug(timetagger_api + "/get_counter_data/")
            response = await client.post(timetagger_api + "/get_counter_data/", json=channels_payload)
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


@router.post("/graph")
def test_graph(form_data: ChannelDataForCounter):
    numChannels = form_data.numChannels
    bin_width = form_data.bin_width
    n_values = form_data.n_values
    
    print(form_data)
    
    graph_data = {}
    
    for channel in range(1, numChannels + 1):
        x_values = list(range(1, n_values + 1))
        y_values = [random.randint(100, 1000) for _ in range(n_values)]
        
        graph_data[channel] = {
            'x_values': x_values,
            'y_values': y_values
        }
    
    return graph_data
    
        
# @router.get("/list_counters")
# async def list_counters():
#     try:
#         async with httpx.AsyncClient() as client:
#             logger.debug(timetagger_api + "/list_counters/")
#             response = await client.get(timetagger_api + "/list_counters/")
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


