from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
import uvicorn
import json
import time
import itertools
import asyncio
import numpy as np

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global state
current_parameters = {}
input_channels = [1, 2]

import TimeTagger
tagger = TimeTagger.createTimeTagger()
for ch in input_channels:
    #Set the trigger level of an input channel in Volts.
    #The trigger level in a Time Tagger hardware refers to the voltage threshold that determines when an incoming signal 
    # is recognized as a valid event. If the signal crosses this threshold, the Time Tagger registers a timestamp for the event.
    tagger.setTriggerLevel(ch, 0.1)
    #Time tagger will mark the photon detect time at t+2ps is the delay was set to 2ps. This is done because:
    #1. Synchronizing Signals from Different Channels
    #2. Compensating for Cable Length Differences
    tagger.setInputDelay(ch, 0)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main page."""
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/set_parameters/{mode}")
async def set_parameters(mode: str, parameters: dict):
    """Set parameters for the given mode."""
    current_parameters[mode] = parameters
    print(current_parameters)
    return {"message": f"Parameters for {mode} updated.", "parameters": parameters}

@app.websocket("/ws/counter")
async def websocket_counter(websocket: WebSocket):
    """WebSocket for Counter Mode."""
    await websocket.accept()
    print("Start Counter")
    
    # Counter Mode setup
    counter_mode_parameter = current_parameters['counter']

    #Delay Adjustment
    print("Start Adjust the delay")
    for ch in input_channels:
        tagger.setInputDelay(ch, 0)
        
        
    binwidth = int(counter_mode_parameter['bin_width'])
    n_bins = int(counter_mode_parameter['n_bins'])
    
    #ensures that measurements on different channels starts and stops at the same time.
    #It returns a TimeTagger proxy object which we pass to each of our measurements so that they start & stop at same time.
    sm = TimeTagger.SynchronizedMeasurements(tagger)
    #Correlation is the measurement of the time difference between event detected on two channels.
    #It is used to analyze how the events from one channel are related to the events from another channel.
    #If you are measuring photon emissions from two different detectors, the correlation histogram could show how often the events from the two detectors happen simultaneously (or within a small time window), which is valuable for studying photon correlations in quantum optics.	
    #It gives an histogram where x-axis represent the bins and bin_width which is the time frame of the detection difference between two channels and the Y-axis is the count of events in that time-difference frame.
    corr = TimeTagger.Correlation(sm.getTagger(), input_channels[0], input_channels[1], binwidth=binwidth, n_bins=n_bins)
    
    #Starts or continues the data acquisition for given duration (in ps), after the duration time
    # the method stop() is called and isRunning() returns false.
    #Whether the accumulated data is cleared at the begining of startFor() is determined by the clear parameter which is True by default.
    sm.startFor(int(1e12), clear=True)
    sm.waitUntilFinished()

    #Delay Measurement
    hist_t = corr.getIndex() #(X-axis): A vector of size n_bins containing the time bins in ps. 
    hist_c = corr.getData()  #(Y-axis): A one-dimensional array of size n_bins containing the histogram. 
    peak_index = np.argmax(hist_c) #index of bin when the count is maximum. (The bin is a time frame [0, 10ps] or [-10,10]). So where we ge the most count and in which time frame difference
    peak_delay = hist_t[peak_index] # waht is the delay range            
    tagger.setInputDelay(input_channels[1], peak_delay)
    print(f"Delay = {peak_delay}")

    """
    The reason we set the input delay in channel 2 to the peak delay obtained from the correlation is to ensure temporal alignment of the detected photon pairs. Here's why:

    Photon Arrival Time Uncertainty: When two entangled photons are generated, they travel through different optical paths before reaching their respective detectors. Due to variations in path lengths, 
    optical components, or detector response times, the photons may not arrive at their respective detectors simultaneously.

    Time Correlation Measurement: By performing a coincidence measurement between detection events in both channels, we obtain a time correlation function, which typically shows a peak at the time delay 
    where the detection events are most strongly correlated. This peak represents the relative delay between the two detection channels caused by optical path differences.

    Correcting for the Delay: To properly measure entanglement, we need to ensure that the detection events are synchronized as if the two photons were detected simultaneously in an idealized reference frame. 
    By setting the input delay in channel 2 to match the peak delay from the correlation function, we compensate for any timing offset, allowing us to correctly measure quantum correlations (e.g., in polarization or other degrees of freedom).


    """

    #Counter Measuerment
    binwidth = int(counter_mode_parameter['counter_binwidth'])
    n_values = int(counter_mode_parameter['n_values'])
    measurement_duration = binwidth * n_values
    groups = list(itertools.combinations(input_channels, 2)) # generates all posible combinations of size 2 -> {1,2} {2,1}
    #It works by defining a time window in which events from multiple detectors are considered coincident, enabling analysis of quantum correlations.
    coincidences_vchannels = TimeTagger.Coincidences(tagger, groups, coincidenceWindow=500)
    channels = [*input_channels, *coincidences_vchannels.getChannels()]
    counter = TimeTagger.Counter(tagger, channels, binwidth=binwidth, n_values=n_values)

    try:
        start_time = time.time()
        while True:
            counter.startFor(measurement_duration)
            counter.waitUntilFinished()
            counts = counter.getData()
            elapsed_time = time.time() - start_time

            data = {
                "elapsed_time": elapsed_time,
                "ch1_counts": int(counts[0][0]),
                "ch2_counts": int(counts[1][0]),
                "coincidence_counts": int(counts[2][0]),
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket.")
    except Exception as e:
        print(f"Unexpected WebSocket error: {e}")

    counter.stop()
    print("Counter Stopped")

@app.websocket("/ws/coincidence")
async def websocket_counter(websocket: WebSocket):
    await websocket.accept()
    for ch in input_channels:
        tagger.setInputDelay(ch, 0)
    coincidence_mode_parameter = current_parameters['coincidence']
    coincidence_window = int(coincidence_mode_parameter['coincidence_window'])
    binwidth = int(coincidence_mode_parameter['coincidence_binwidth'])
    n_bins = int(coincidence_mode_parameter['coincidence_n_bins'])
    mode = coincidence_mode_parameter['mode']


    sm = TimeTagger.SynchronizedMeasurements(tagger)
    corr = TimeTagger.Correlation(sm.getTagger(), input_channels[0], input_channels[1], binwidth=binwidth, n_bins=n_bins)
    rate = TimeTagger.Countrate(sm.getTagger(), input_channels)
    if mode == 'duration':
        measurement_duration = int(coincidence_mode_parameter['measurement_duration'])
        sm.startFor(measurement_duration*int(1e12))
    elif mode == 'continuous':
        sm.start()

    try:
        start_time = time.time()
        while True:

            Ch1Rate, Ch2Rate = rate.getData()
            hist_t = corr.getIndex()
            hist_c = corr.getData()
            elapsed_time = time.time() - start_time
            if sm.isRunning() == False:
                elapsed_time = measurement_duration
            # Identify the peak delay and calculate the coincidence window around it
            peak_index = np.argmax(hist_c)
            peak_delay = hist_t[peak_index]
            hist_t_ns = hist_t * 1e-3  # Convert to ns for plotting

            # Define the coincidence window around the peak delay
            coincidence_window_start = peak_delay - int(coincidence_window / 2)  # in ps
            coincidence_window_end = peak_delay + int(coincidence_window / 2)    # in ps
            inside_window_indices = np.where((hist_t >= coincidence_window_start) & (hist_t <= coincidence_window_end))[0]
            true_coincidences = np.sum(hist_c[inside_window_indices])
            true_coincidences_rate = true_coincidences/elapsed_time

            # Define the outside window for accidental counts
            window_start = peak_delay - 1000  # -1 ns in ps
            window_end = peak_delay + 1000    # +1 ns in ps
            outside_window_indices = np.where(
                ((hist_t >= window_start) & (hist_t < coincidence_window_start)) |
                ((hist_t > coincidence_window_end) & (hist_t <= window_end))
            )[0]
            accidental_coincidences = np.sum(hist_c[outside_window_indices])
            accidental_coincidences_rate = accidental_coincidences/elapsed_time

            # Calculate CAR
            CAR = true_coincidences / accidental_coincidences if accidental_coincidences > 0 else np.inf
            
            window_indices = np.where((hist_t >= window_start) & (hist_t <= window_end))[0]
            hist_t_ns_rounded = np.around(hist_t_ns[window_indices], decimals=2).tolist()
            data = {
                "hist_t_ns": hist_t_ns_rounded,  # Convert NumPy array to list
                "hist_c": hist_c[window_indices].tolist(),
                "coincidence_window_start": float(coincidence_window_start * 1e-3),  # Convert to float
                "coincidence_window_end": float(coincidence_window_end * 1e-3),  # Convert to float
                "ch1_rate": float(Ch1Rate),  # Convert to float
                "ch2_rate": float(Ch2Rate),  # Convert to float
                "true_coincidences": int(true_coincidences),  # Convert to int
                "true_coincidences_rate": float(true_coincidences_rate),  # Convert to float
                "accidental_coincidences": int(accidental_coincidences),  # Convert to int
                "accidental_coincidences_rate": float(accidental_coincidences_rate),  # Convert to float
                "CAR": float(CAR),  # Convert to float
            }
            await websocket.send_text(json.dumps(data))
            if sm.isRunning() == False:
                break
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket.")
    except Exception as e:
        print(f"Unexpected WebSocket error: {e}")
    
    sm.stop()
    print("SM stopped")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)