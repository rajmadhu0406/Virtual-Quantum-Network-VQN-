from queue import PriorityQueue

request_queue = PriorityQueue()

rbody1 = {'username' : 'Alice', 'channels_needed' : 3}
rbody2 = {'username' : 'Bob', 'channels_needed' : 2}

time1 = '2024-03-21T03:06:12.439Z'
time2 = '2024-03-21T03:06:22.449Z'

request_queue.put((time2, (1, rbody2, 11, "third")))
request_queue.put((time1, (2, rbody1, 55, 'second')))

while not request_queue.empty():
    t, b = request_queue.get()
    print(t,b)
    print("\n\n\n-----------------\n\n\n")
