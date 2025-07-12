from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.switch_api import router as switch_routers
from api.channel_api import router as channel_routers
from api.auth_api import router as auth_routers
from api.channel_api import print_redis_request_length
from api.counter_api import router as counter_api
from api.countrate_api import router as countrate_api
from api.timetagger_api import router as timetagger_api
from api.coincidence_api import router as coincidence_api
from allocation import process_request
from api.user_api import router as user_routers
import api.auth_api as authService
import asyncio
import logging
import uuid
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import schemas
from typing_extensions import Annotated, Union
from notification import process_responses
import os
from test.seed import seed_database
from config import TEST_MODE

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

subscriber_task = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(switch_routers)
app.include_router(channel_routers)
app.include_router(auth_routers)
app.include_router(user_routers)
app.include_router(counter_api.router)
app.include_router(countrate_api.router)
app.include_router(timetagger_api.router)
app.include_router(coincidence_api.router)


@app.get("/api")
def home(current_user: Annotated[schemas.DBUser, Depends(authService.get_current_user)]):
    return {"Hello" : "Weorld"}

@app.get("/api/sayname/{name}")
def say(name: str):
    return {"Hello" : name}


# # Start processing the queue automatically when the server starts
@app.on_event("startup")
async def startup_event():
    #makes sure once executed once and again even on reload on changes
    if TEST_MODE and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        seed_database()

    asyncio.create_task(process_request())

@app.on_event("startup")
async def startup_event2():
    asyncio.create_task(print_redis_request_length())
    
    
@app.on_event("startup")
async def startup_event3():
    app.state.pubsub_task = asyncio.create_task(process_responses())

@app.on_event("shutdown")
async def shutdown_event():
    pubsub_task = getattr(app.state, "pubsub_task", None)
    if pubsub_task:
        pubsub_task.cancel()
        try:
            await pubsub_task
        except asyncio.CancelledError:
            logger.info("PubSub task cancelled on shutdown")
    
# Define a middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # Generate a unique ID for the request
    request.state.request_id = str(uuid.uuid4())
    # Continue processing the request
    response = await call_next(request)
    return response

# Define a middleware
# @app.middleware("https")
# async def add_request_id(request: Request, call_next):
#     # Generate a unique ID for the request
#     request.state.request_id = str(uuid.uuid4())
#     # Continue processing the request
#     response = await call_next(request)
#     return response



# request_queue = PriorityQueue()
# global count
# count = 0

# async def process_request():
#     while True:
#         logger.info(f"Queue length : {(request_queue.qsize())}")
#         if not request_queue.empty():
            
#             c, request_info = request_queue.get()
#             request, allocation_event = request_info
            
#             # Simulated resource allocation process
#             await asyncio.sleep(4)  # Simulated delay
            
            
#             allocated = True  # Simulated result, can be True or False
#             message = f"Resource allocated successfully custom  msg {c}" if allocated else "Resource not available"
#             response = Response(content=(message))
            
#             # Store the response in the request's state
#             # request.state.response = response
#             # Store the response in the request's state along with request ID
#             request.state.response = {c : response.body}
#             # Signal that allocation is complete
#             allocation_event.set()

#         else:
#             await asyncio.sleep(1)  # Wait for 1 second before checking the queue again


        

# @app.post("/allocate-resource/")
# async def allocate_resource(request: Request, background_tasks: BackgroundTasks):
#     # Record the time when the request is received
#     # request_time = datetime.now()

#     # Add request to the queue
#     global count
#     count = count + 1 #request id
#     id  = count
#     allocation_event = asyncio.Event()  
#     request_queue.put((count, (request, allocation_event)))

#     await allocation_event.wait()
#     allocation_event.clear()  # Reset event for the next allocation
    
#     # Send JSON response to the user
#     return {"message": request.state.response[id]}