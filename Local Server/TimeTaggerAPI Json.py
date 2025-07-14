from fastapi import FastAPI
from pydantic import BaseModel
from TimeTagger import createTimeTagger, Counter, Countrate
from typing import List

# Create FastAPI app
app = FastAPI()

# Initialize TimeTagger
tt = createTimeTagger()

# Dictionaries to store multiple Counters and Countrates by unique combination of channels
counters = {}
countrates = {}

# Utility function to generate UID for channel sets (unique combination of channels)
def generate_uid(channels):
    return tuple(sorted(channels))  # Sort and convert the list of channels to a tuple to use as a unique identifier

# Pydantic models for input validation
class ChannelModel(BaseModel):
    channels: List[int]

class CounterModel(BaseModel):
    channels: List[int]
    binwidth: int = 1_000_000_000  # Default 1e9 ns
    n_values: int = 1

class CountrateModel(BaseModel):
    channels: List[int]

# 1. Start Test Signal on a specific channel
@app.post("/start_test_signal/")
def start_test_signal(channel: ChannelModel):
    try:
        tt.setTestSignal(channel.channels, True)  # Enable test signal on the specified channel
        return {"status": f"Test signal started on channel {channel.channels}"}
    except Exception as e:
        return {"error": str(e)}

# 2. Create Counter for a unique set of channels
@app.post("/create_counter/")
def create_counter(counter: CounterModel):
    uid = generate_uid(counter.channels)  # Generate a unique identifier based on the channels
    if uid not in counters:
        counters[uid] = Counter(tt, counter.channels, counter.binwidth, counter.n_values)  # Create a new Counter
        return {"status": f"Counter created for channels {counter.channels}"}
    else:
        return {"error": f"A Counter already exists for channels {counter.channels}"}

# 3. Get Data from the Counter of a unique set of channels
@app.post("/get_counter_data/")
def get_counter_data(channels: ChannelModel):
    uid = generate_uid(channels.channels)  # Generate the unique identifier for this set of channels
    if uid in counters:
        data = counters[uid].getData()  # Retrieve data for the specific counter
        return {"channels": channels.channels, "data": data.tolist()}  # Convert numpy array to list if needed
    else:
        return {"error": f"Counter not found for channels {channels.channels}"}

# 4. Create Countrate for a unique set of channels
@app.post("/create_countrate/")
def create_countrate(countrate: CountrateModel):
    uid = generate_uid(countrate.channels)  # Generate a unique identifier based on the channels
    if uid not in countrates:
        countrates[uid] = Countrate(tt, countrate.channels)  # Create a new Countrate
        return {"status": f"Countrate created for channels {countrate.channels}"}
    else:
        return {"error": f"A Countrate already exists for channels {countrate.channels}"}

# 5. Get Data from the Countrate of a unique set of channels
@app.post("/get_countrate_data/")
def get_countrate_data(channels: ChannelModel):
    uid = generate_uid(channels.channels)  # Generate the unique identifier for this set of channels
    if uid in countrates:
        data = countrates[uid].getData()  # Retrieve data for the specific countrate
        return {"channels": channels.channels, "data": data.tolist()}  # Convert numpy array to list if needed
    else:
        return {"error": f"Countrate not found for channels {channels.channels}"}

# 6. List all active Counters
@app.get("/list_counters/")
def list_counters():
    # Return a list of the channel combinations for each active counter
    return {"active_counters": [list(uid) for uid in counters.keys()]}

# 7. List all active Countrates
@app.get("/list_countrates/")
def list_countrates():
    # Return a list of the channel combinations for each active countrate
    return {"active_countrates": [list(uid) for uid in countrates.keys()]}

# 8. Get TimeTagger Status
@app.get("/status/")
def get_status():
    status = {
        "model": tt.getModel()
    }
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
