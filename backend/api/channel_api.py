from fastapi import APIRouter, status, Depends, HTTPException, Response, BackgroundTasks, Header, Request
import database
from models import Switch as SwitchModel
from models import Channel as ChannelModel
from models import Request as RequestModel
from models import User as UserModel
from sqlalchemy.orm import Session
import schemas
import json
import asyncio
import traceback
import logging
from queue import PriorityQueue
import httpx
import json
import requests
import redis as redis

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

REDIS_HOST = 'redis://redis'
REDIS_PORT = 6379
REDIS_HASHMAP_KEY_NAME = 'user_requests'
REDIS_URL = 'redis://redis:6379'

redisRequestClient = redis.RedisClient(REDIS_HOST, REDIS_PORT, REDIS_URL, REDIS_HASHMAP_KEY_NAME, "")

router = APIRouter(
    prefix="/api/channel",
    tags=["channel"],
    responses={404: {"description": "Not found"}},
)

@router.get("/get/all")
def get_all_channels(only_active: bool = False, db: Session = Depends(database.get_db)):
    if only_active:
        channels = db.query(ChannelModel).filter(ChannelModel.channel_active == True).all()
    else:
        channels = db.query(ChannelModel).all()
        
    return channels

@router.get("/get/{username}")
def get_channels_for_user(username: str, db: Session = Depends(database.get_db) ):
    user_channels = db.query(ChannelModel).filter(ChannelModel.channel_user == username).all()
    return user_channels

@router.delete("/delete/{id}")
def delete_channel(id: int, db: Session = Depends(database.get_db) ):
    try:
        channel_to_delete = db.query(ChannelModel).filter(ChannelModel.id == id).first()
        if not channel_to_delete:
            raise HTTPException(status_code=404, detail="Item not found") 
        else:
            # db.delete(channel_to_delete)
            # channel_to_delete = ChannelModel(channel_to_delete)
            channel_to_delete.channel_user = None;
            channel_to_delete.channel_active = False;
            db.commit()
        
        return {"message" : f"Channel deletion successful for channel with ID : {id}"}

    except Exception as e:
        db.rollback()
        traceback.print_exc()  # Print the stack trace
        logger.error(f"Error occurred during channel deletion: {e}")
        return {"error" : f"Error occurred during channel allocation: {e}"}
             

"""
    Sends a POST request to the specified URL with JSON data asynchronously and returns the response.

    Args:
        url (str): The URL to send the POST request to.
        json_data (dict): The JSON data to include in the request body.

    Returns:
        dict: A dictionary containing the response status code and response body.
"""
# async def send_post_request_async(url, json_data):
#     try:
#         async with httpx.AsyncClient() as client:
#             # requests.get(url)
#             response = client.post(url, json=json_data)
#             return {"response": response}
#     except httpx.HTTPError as e:
#         return {"error": str(e)}
    
    

"""
function that returns a list of #channels_needed number of channel_ids that are available otherwise 
an error message that requested number of channels_needed channels are not available
# """
# async def allocate_channels(request_id: str, username: str, channels_needed: int, switch_ids: list = None,  db: Session = Depends(database.get_db)):
#     try: 
        
#         # await asyncio.sleep(10)
#         if(switch_ids is not None and len(switch_ids) != 0):
#             inactive_channels = [
#                 db.query(ChannelModel)
#                 .join(SwitchModel, ChannelModel.switch_id == SwitchModel.id)
#                 .filter(SwitchModel.id.in_(switch_ids))
#                 .filter(SwitchModel.active == True)
#                 .filter(ChannelModel.channel_active == False)
#                 .limit(channels_needed)
#                 .all()
#             ]
#         else:
#             inactive_channels = [
#                 db.query(ChannelModel)
#                 .join(SwitchModel, ChannelModel.switch_id == SwitchModel.id)
#                 .filter(SwitchModel.active == True)
#                 .filter(ChannelModel.channel_active == False)
#                 .limit(channels_needed)
#                 .all()
#             ]
        
#         inactive_channels = inactive_channels[0]
        
#         if len(inactive_channels) >= channels_needed:
#             # Update channels to set active=True and channel_user=username
#             for channel in inactive_channels:
#                 channel.channel_active = True
#                 channel.channel_user = username
                
#             logger.debug(f"\n{len(inactive_channels)} channels allocated to user: {username}\n")
#             logger.debug(f"Sending request to localserver for calculation")
            
#             pydantic_list = schemas.DBChannelList(channel_list=inactive_channels) 
#             json_data = {"request_id": request_id, "channel_list": [c.dict() for c in pydantic_list.channel_list], 'time':channels_needed} 
    
            
#             db.commit()   
#             # return {"channel_list" : pydantic_list.channel_list, "message" : f"{len(inactive_channels)} channels allocated to user: {username}", "results": localserver_response_body['result']}
#             return {"channel_list" : pydantic_list.channel_list, "message" : f"{len(inactive_channels)} channels allocated to user: {username}", "json_data": json_data}

            
#         else:
#             if switch_ids is not None:
#                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Not enough inactive channels available in optical switches : {switch_ids}")
#             else:
#                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not enough inactive channels available in available active optical switches")
              
    
#     except HTTPException as he:
#         db.rollback()
#         logger.error(f"Error occurred during channel allocation (HTTPException): {he}")
#         return {"error" : f"Error occurred during channel allocation (HTTPException) : {he}"}
#     except httpx.TimeoutException as re:
#         logger.error("Request timeout!!!")
#         return {"error" : f"Error occurred during channel allocation (HTTPException) : Request Timeout!!!"}
#     except Exception as e:
#         db.rollback()
#         traceback.print_exc()  # Print the stack trace
#         logger.error(f"Error occurred during channel allocation: {e}")
#         return {"error" : f"Error occurred during channel allocation: {e}"}



request_queue = asyncio.Queue()  # Async queue for processing requests


"""
Background worker
"""
async def print_redis_request_length():
    while True:
        q_len = await redisRequestClient.get_length()
        logger.info(f"Redis Queue length : {q_len}")
        await asyncio.sleep(3) 



@router.post('/allocate')
async def allocate_resources(request: Request, channel_request: schemas.ChannelRequest, 
                             timestamp: str = Header(None, alias="X-Timestamp"), db: Session = Depends(database.get_db)):
    try:
    
        request_id  = request.state.request_id
        
        if timestamp:
            logger.debug(f"timestamp : {timestamp}")
        else:
            raise Exception("Could not retrieve Timestamp!")
        
        logger.debug(f"channel request : {channel_request}")
        
        # Serialize the request data to JSON string
        channel_request_str = json.dumps(channel_request.dict())
        
        user = db.query(UserModel).filter(UserModel.username == channel_request.username).first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found with username : {channel_request.username}")
        
        new_request = {
            "req_string": request_id,
            "user_id": user.id,
            "status": schemas.RequestStatus.processing,
            "resource_ids": []}
    
        logger.debug("\n\n-------\n\n")
        logger.debug(f"new_request : {new_request}")

        await redisRequestClient.add(request_id, channel_request_str)
        
        try:
            db_request = RequestModel(**new_request)
            db.add(db_request)
            db.commit()
            logger.debug("Request added to DB")
        except Exception as e:
            db.rollback()
            logger.error(f"Error occurred during request creation: {e}")
        finally:
            db.close()
        
        
        logger.debug(f"Request {request_id} added to Redis with data : {channel_request_str} and status : {str(new_request['status'])}")
        
        # Initialize response dictionary if it doesn't exist
        request.state.response = {}
        request.state.response[request_id] = {'data': None, 'display': ''}
        request.state.response[request_id]['display'] = "Request processing, we will notify you when resources are allocated"
            
        return request.state.response[request_id]
                
    except Exception as e:
        traceback.print_exc()  # Print the stack trace
        raise HTTPException(
            status_code=404, detail=str(e)
        )
        # return {"error" : f"error processing the request : {e}", "display" : "Could not process your request please try again"} 

 