import json
import asyncio
from fastapi import Depends, HTTPException
from models import Channel as ChannelModel
from models import Request as RequestModel
from models import User as UserModel
import redis as redis
import schemas
import logging
import database


# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

redisRequestClient = redis.RedisClient('redis://redis', 6379, 'redis://redis:6379', 'user_requests', '')

redisResponsePublishClient = redis.RedisClient('redis://redis', 6379, 'redis://redis:6379', '', "user_responses_topic")



def get_available_channels_sync():
    # Create a new session manually.
    db = next(database.get_db())
    try:
        inactive_channels = db.query(ChannelModel).filter(ChannelModel.channel_active == False).all()
        return inactive_channels 
    except Exception as e:
        logger.error(f"Error occurred during get_available_channels_sync: {e}")
    finally:
        db.close()

    
# worker to process redis queue
async def process_request():
    while True:
        await asyncio.sleep(5) 
        
        inactive_channels = get_available_channels_sync() # list of channels
        user_requests = await redisRequestClient.get_all() # dict of requests
        user_requests = list(user_requests.items())
        
        if len(inactive_channels) > 0 and len(user_requests) > 0:
            logger.info(f"Available channels : {len(inactive_channels)}")
            logger.info(f"first request : {user_requests[0]}")
            
            # '{"username": "raj", "channels_needed": 2, "switch_ids": null, "request_id": "6be71348-0366-4e96-984d-8c87c338de20"}')
            
            request_id = user_requests[0][0]
            request_data = json.loads(user_requests[0][1])
            
            if len(inactive_channels) >= request_data['channels_needed']:
                logger.info(f"Allocating {request_data['channels_needed']} channels for {request_data['username']} for request id : {request_id}")
                
                
                db = next(database.get_db())
                allocated_channels_ids = []
                try:
                    #allocate channels to the user
                    for channel in inactive_channels[:request_data['channels_needed']]:
                        attached_channel = db.merge(channel)
                        attached_channel.channel_active = True
                        attached_channel.channel_user = request_data['username']
                        allocated_channels_ids.append(attached_channel.id)
                    db.commit() 
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error occurred during channel allocation: {e}")
                finally:
                    db.close()
 
                #update the status of the request in Database
                request_to_update = db.query(RequestModel).filter(RequestModel.req_string == request_id).first()
                if request_to_update:
                    request_to_update.resource_ids = allocated_channels_ids
                    request_to_update.status = schemas.RequestStatus.processed
                    db.commit()
                    logger.info("request status updated in database to processed")
                else:
                    logger.error("request id not found in database")


                request_schema = schemas.DBRequest.from_orm(request_to_update)

                #delete user from the queue
                await redisRequestClient.delete(request_id)
                logger.info("request deleted from queue")
                
                #add response to the response queue for notification
                await redisResponsePublishClient.publish(json.dumps(request_schema.dict()))
                logger.info("response published to response topic")
             
        else:
            logger.info(f"No Available channels or requests")
            
