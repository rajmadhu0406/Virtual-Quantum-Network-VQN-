import json
import asyncio
from fastapi import Depends
from models import Channel as ChannelModel
from models import User as UserModel
from models import Request as RequestModel
import redis as redis
import schemas
import logging
import database
import aioboto3


# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# AWS credentials and region
AWS_REGION = "us-east-1"  # Change to your SES region
SENDER_EMAIL = "raj.madhu0406@gmail.com"  # Must be verified in SES

EMAIL_SUBJECT = "VQN: Your Request Has Been Processed!"

#account info is fetched from aws cli configure
ses_session = aioboto3.Session()

async def send_email(to_email, subject, body_text, body_html=None):
    """
    Sends an email via AWS SES.
    
    :param to_email: Recipient email address
    :param subject: Email subject
    :param body_text: Plain text email body
    :param body_html: Optional HTML email body
    """
    try:
        
        async with ses_session.client("ses", region_name=AWS_REGION) as ses_client:
            
            # Email format
            message = {
                "Subject": {"Data": subject},
                "Body": {
                    "Text": {"Data": body_text},
                },
            }

            # Include HTML body if provided
            if body_html:
                message["Body"]["Html"] = {"Data": body_html}

            # Send the email
            response = await ses_client.send_email(
                Source=SENDER_EMAIL,
                Destination={"ToAddresses": [to_email]},
                Message=message,
            )
            
            logger.debug(f"Email sent! Message ID: {response['MessageId']}")
    
    except Exception as e:
        logger.error(f"Error sending email: {e}")

    

#worker that subcribes to redis response pubsub
async def process_responses():
    
    redisResponseClient = redis.RedisClient('redis://redis', 6379, 'redis://redis:6379', '', "user_responses_topic")
    
    pubsub = await redisResponseClient.get_redis()
    pubsub = pubsub.pubsub()
    
    
    try:
        await pubsub.subscribe(redisResponseClient.REDIS_TOPIC)
    
        logger.info(f"Subscribed to redis topic {redisResponseClient.REDIS_TOPIC}")
    
        ## Listen for messages (this blocks until a message is received)
        async for message in pubsub.listen():
            # Filter out subscribe/unsubscribe messages
            if message["type"] == "message":
                
                logger.info(f"Received published message: {message['data']}")
                
                data = json.loads(message['data'])
                
                #response = {"request_id": request_id, "channel_ids": allocated_channels_ids, "username": request_data['username']}

                db = next(database.get_db())
                to_email = None
                
                user = db.query(UserModel).filter(UserModel.id == data['user_id']).first()
                if user:
                    to_email = user.email
                else:
                    logger.error("user not found in database")
                    raise Exception("user is not found in database")
                
                EMAIL_BODY = f"""Hello,
                
                This is to notify you that the resources you request have been allocated.

                Request ID: {data['req_string']}
                User ID: {data['user_id']}
                Status: Completed
                Resources: {data['resource_ids']}   

                Best regards,
                VQN Team"""
                
                
                await send_email(to_email=to_email, subject=EMAIL_SUBJECT, body_text=EMAIL_BODY)
                
                logger.debug(f"Sent notification for request id: {data['req_string']} ,  user_id: {data['user_id']} with resources : {data['resource_ids']}")
                
                # update status to completed
                request_to_update = db.query(RequestModel).filter(RequestModel.req_string == data['req_string']).first()
                if request_to_update:
                    request_to_update.status = schemas.RequestStatus.completed
                    db.commit()
                    logger.info("request status updated in database to completed")
                else:
                    logger.info("request is not found in database")
                    
                    
    except asyncio.CancelledError:
        logger.info("Subscriber task cancelled cleanly")
        raise
    except Exception as e:
        logger.error(f"Error occurred during Notification task: {e}")
        raise
    finally:
        await pubsub.close()
        if redisResponseClient.redis:
            await redisResponseClient.redis.close()