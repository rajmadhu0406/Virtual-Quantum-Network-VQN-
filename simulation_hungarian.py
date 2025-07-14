import simpy
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment

# ---------------------------
# Simulation Function
# ---------------------------
def run_simulation(NUM_USERS, NUM_RESOURCES, SIMULATION_TIME, 
                   mean_arrival_rate, mean_service_time, 
                   MIN_START_DELAY, MAX_START_DELAY, 
                   MIN_RATE, MAX_RATE, alpha):
    """
    Run the simulation for a given configuration and return:
      - logs: time series metrics (queue length, utilization, throughput, avg wait)
      - final_metrics: final QoS per user, Jain's fairness index, Gini index, avg QoS, total completions, avg wait time.
    """
    # Lists for logging time-series metrics
    queue_length_log = []
    utilization_log = []
    throughput_log = []
    wait_time_log = []
    jain_time_log = []
    gini_time_log = []
    avg_user_in_queue = dict()
    avg_user_in_system = dict()
    
    # Create the SimPy environment.
    env = simpy.Environment()
    
    # ---------------------------
    # Define ResourceManager, Resource, and User classes.
    # ---------------------------
    class ResourceManager:
        def __init__(self, env, resources):
            self.env = env
            self.resources = resources  # All resources
            self.available_resources = resources.copy()
            self.waiting_users = []  # List of tuples (user, allocation_event)
            self.completed_jobs = 0
            self.wait_times_list = []  # Store every wait time from completed requests
            # Start the allocation process.
            env.process(self.allocate_resources())
        
        def allocate_resources(self):
            def compute_proportional_ratio(user, resource):
                user_qos = user.qos()
                # A simple proportional metric; you can modify this as needed.
                new_rate = resource.data_rate if user_qos == 1 else ((1-alpha)*user_qos)*(alpha*resource.data_rate)
                proportional_ratio = np.log(1 + (new_rate / user_qos))
                return proportional_ratio
            
            while True:
                if self.available_resources and self.waiting_users:
                    
                    num_resources = len(self.available_resources)
                    num_users = len(self.waiting_users)
                    
                    # Build a cost matrix where rows correspond to resources and columns to waiting users.
                    # We use -compute_proportional_ratio because we want to maximize the ratio.
                    cost_matrix = np.zeros((num_resources, num_users))
                    for i, resource in enumerate(self.available_resources):
                        for j, (user, allocation_event) in enumerate(self.waiting_users):
                            pr = compute_proportional_ratio(user, resource)
                            cost_matrix[i, j] = -pr

                    # Solve the assignment problem using the Hungarian algorithm.
                    # This returns arrays of indices for the resources (rows) and waiting users (columns)
                    row_indices, col_indices = linear_sum_assignment(cost_matrix)
                    
                    # Allocate the matched pairs.
                    # We record the indices so that after allocation we can remove them from the lists.
                    allocated_resource_indices = set()
                    allocated_user_indices = set()
                    
                    for i, j in zip(row_indices, col_indices):
                        current_resource = self.available_resources[i]
                        user, allocation_event = self.waiting_users[j]
                        current_resource.allocate(user, allocation_event)
                        allocated_resource_indices.add(i)
                        allocated_user_indices.add(j)
                
                    # Remove allocated resources and waiting users.
                    self.available_resources = [res for idx, res in enumerate(self.available_resources)
                                                if idx not in allocated_resource_indices]
                    self.waiting_users = [wu for idx, wu in enumerate(self.waiting_users)
                                        if idx not in allocated_user_indices]

                    
                yield self.env.timeout(0.01)
        
        def record_wait_time(self, wait_time):
            self.wait_times_list.append(wait_time)
        
        def increment_completed_jobs(self):
            self.completed_jobs += 1

    class Resource:
        def __init__(self, env, resource_id, data_rate, resource_manager):
            self.env = env
            self.id = resource_id
            self.data_rate = data_rate
            self.resource_manager = resource_manager
            self.in_use = False
        
        def allocate(self, user, allocation_event):
            self.in_use = True
            allocation_event.succeed(value=self)
        
        def release(self):
            self.in_use = False
            # Update data rate randomly for next use.
            self.data_rate = random.randint(MIN_RATE, MAX_RATE)
            self.resource_manager.available_resources.append(self)
    
    class User:
        def __init__(self, env, user_id, resource_manager):
            self.env = env
            self.id = user_id
            self.resource_manager = resource_manager
            self.total_packets = 0.0
            self.total_usage_time = 0.0
            self.total_wait_time = 0.0
            self.arrival_time = None
            self.waiting = False
        
        def qos(self):
            # QoS defined as packets delivered divided by (usage time + wait time)
            current_wait = self.env.now - self.arrival_time if self.waiting and self.arrival_time is not None else 0
            effective_wait = self.total_wait_time + current_wait
            denom = self.total_usage_time + effective_wait
            if denom == 0 or self.total_packets == 0:
                return 0.0001
            return self.total_packets / denom
        
        def run(self):
            # Staggered start using a uniform random delay.
            yield self.env.timeout(random.uniform(MIN_START_DELAY, MAX_START_DELAY))
            while True:
                self.arrival_time = self.env.now
                self.waiting = True
                allocation_event = self.env.event()
                self.resource_manager.waiting_users.append((self, allocation_event))
                # Wait for resource allocation.
                yield allocation_event
                resource = allocation_event.value
                # Compute waiting time.
                wait_time = self.env.now - self.arrival_time
                self.total_wait_time += wait_time
                self.resource_manager.record_wait_time(wait_time)
                self.waiting = False
                # Service (usage) time drawn from exponential distribution.
                usage_time = np.random.exponential(1.0 / mean_service_time)
                yield self.env.timeout(usage_time)
                self.total_usage_time += usage_time
                # Packets processed (for simplicity, product of data rate and usage time).
                packets_received = resource.data_rate * usage_time
                self.total_packets += packets_received
                resource.release()
                self.resource_manager.increment_completed_jobs()
                # Next arrival time drawn from an exponential distribution.
                next_arrival = np.random.exponential(1.0 / mean_arrival_rate)
                # print(next_arrival)
                yield self.env.timeout(next_arrival)
    
    # ---------------------------
    # Set up resources, resource manager, and users.
    # ---------------------------
    resources = []
    for r in range(NUM_RESOURCES):
        resources.append(Resource(env, resource_id=r, 
                                  data_rate=random.randint(MIN_RATE, MAX_RATE), 
                                  resource_manager=None))
    
    resource_manager = ResourceManager(env, resources)
    for res in resources:
        res.resource_manager = resource_manager
    
    users = [User(env, user_id, resource_manager) for user_id in range(NUM_USERS)]
    for user in users:
        env.process(user.run())
    
    # ---------------------------
    # Monitoring process to log metrics over time.
    # ---------------------------
    def monitor(env, resource_manager):
        while True:
            current_time = env.now
            queue_len = len(resource_manager.waiting_users)
            busy = sum(1 for r in resource_manager.resources if r.in_use) #users in system using the resources
            
            #calculating the avg user in the queue
            avg_user_in_queue.setdefault(queue_len, 0)
            avg_user_in_queue[queue_len] += 1
            
            avg_user_in_system.setdefault(busy, 0)
            avg_user_in_system[busy] += 1
            
            utilization = busy / len(resource_manager.resources)
            completed = resource_manager.completed_jobs
            avg_wait = np.mean(resource_manager.wait_times_list) if resource_manager.wait_times_list else 0
            queue_length_log.append((current_time, queue_len))
            utilization_log.append((current_time, utilization))
            throughput_log.append((current_time, completed))
            wait_time_log.append((current_time, avg_wait))
            
            curr_qos = [user.qos() for user in users]
            curr_jain = (np.sum(curr_qos)**2) / (len(curr_qos) * np.sum(np.array(curr_qos)**2)) if np.sum(np.array(curr_qos)**2) != 0 else 0
            
            curr_sorted_qos = np.sort(curr_qos)
            n = len(curr_sorted_qos)
            indices = np.arange(1, n+1)
            curr_gini = (np.sum((2*indices - n - 1)*curr_sorted_qos))/(n * np.sum(curr_sorted_qos)) if np.sum(curr_sorted_qos) != 0 else 0
            
            jain_time_log.append((current_time, curr_jain))
            
            gini_time_log.append((current_time, curr_gini))
            
            yield env.timeout(1)  # Log every 10 time units.
    
    env.process(monitor(env, resource_manager))
    env.run(until=SIMULATION_TIME)
    
    # ---------------------------
    # Final performance metrics.
    # ---------------------------
    final_qos = [user.qos() for user in users]
    jain = (np.sum(final_qos)**2) / (len(final_qos) * np.sum(np.array(final_qos)**2)) if np.sum(np.array(final_qos)**2) != 0 else 0
    sorted_qos = np.sort(final_qos)
    n = len(sorted_qos)
    indices = np.arange(1, n+1)
    gini = (np.sum((2*indices - n - 1)*sorted_qos))/(n * np.sum(sorted_qos)) if np.sum(sorted_qos) != 0 else 0
    avg_qos = np.mean(final_qos)
    
    final_avg_users_in_queue = sum(key * value for key, value in avg_user_in_queue.items()) / SIMULATION_TIME
    final_avg_user_in_system = sum(key * value for key, value in avg_user_in_system.items()) / SIMULATION_TIME
    
    final_metrics = {
        "final_qos": final_qos,
        "jain": jain,
        "gini": gini,
        "avg_qos": avg_qos,
        "total_completed_jobs": resource_manager.completed_jobs,
        "avg_wait_time": np.mean(resource_manager.wait_times_list) if resource_manager.wait_times_list else 0,
        "avg_users_in_queue": final_avg_users_in_queue,
        "avg_users_in_system": final_avg_user_in_system
    }
    
    logs = {
        "queue_length": queue_length_log,
        "utilization": utilization_log,
        "throughput": throughput_log,
        "wait_time": wait_time_log,
        "jain_time": jain_time_log,
        "gini_time": gini_time_log
    }
    
    return logs, final_metrics

# ---------------------------
# Run a Representative Simulation (for time-series plots)
# ---------------------------
SIMULATION_TIME = 1000
mean_arrival_rate = 1.0 / 10       # average of 10 time units between arrivals
mean_service_time = 1.0 / 60      # average service time in minutes
MIN_START_DELAY = 0
MAX_START_DELAY = 60
MIN_RATE = 18000
MAX_RATE = 68000
alpha = 1
# random.seed(43)

# Representative configuration:
rep_config = {
    "NUM_USERS": 10,
    "NUM_RESOURCES": 6,
    "SIMULATION_TIME": SIMULATION_TIME,
    "mean_arrival_rate": mean_arrival_rate,
    "mean_service_time": mean_service_time,
    "MIN_START_DELAY": MIN_START_DELAY,
    "MAX_START_DELAY": MAX_START_DELAY,
    "MIN_RATE": MIN_RATE,
    "MAX_RATE": MAX_RATE,
    "alpha": alpha
}


logs_rep, final_metrics_rep = run_simulation(**rep_config)

print("total completed jobs : " + str(final_metrics_rep["total_completed_jobs"]) + "  when lambda = " + str(mean_arrival_rate))
print(f"avg_users_in_queue : {final_metrics_rep["avg_users_in_queue"]}")
print(f"avg_users_in_system : {final_metrics_rep["avg_users_in_system"]}")

# Unpack logged time-series data.
times_q, q_lengths = zip(*logs_rep["queue_length"])
times_u, utilizations = zip(*logs_rep["utilization"])
times_t, throughputs = zip(*logs_rep["throughput"])
times_w, avg_waits = zip(*logs_rep["wait_time"])
times_j, jain_values = zip(*logs_rep["jain_time"])
times_g, gini_values = zip(*logs_rep["gini_time"])

# Plot time-series metrics.
plt.figure(figsize=(12, 8))
plt.suptitle(f"Number of resources = 6  Number of Users = 10", fontsize=12, y=0.98)


plt.subplot(3, 2, 1) # 3 rows, 2 columns, subplot 1
plt.plot(times_q, q_lengths, '-o')
plt.xlabel('Time')
plt.ylabel('Queue Length')
plt.title('Queue Length over Time')

plt.subplot(3, 2, 2) # 3 rows, 2 columns, subplot 2
plt.plot(times_u, utilizations, '-o')
plt.xlabel('Time')
plt.ylabel('Utilization')
plt.title('Server Utilization over Time')

plt.subplot(3, 2, 3) # 3 rows, 2 columns, subplot 3
plt.plot(times_t, throughputs, '-o')
plt.xlabel('Time')
plt.ylabel('Completed Jobs')
plt.title('Cumulative Throughput over Time')

plt.subplot(3, 2, 4) # 3 rows, 2 columns, subplot 4
plt.plot(times_w, avg_waits, '-o')
plt.xlabel('Time')
plt.ylabel('Avg Wait Time')
plt.title('Average Wait Time over Time')

plt.subplot(3, 2, 5) # 3 rows, 2 columns, subplot 5
plt.plot(times_j, jain_values, '-o')
plt.xlabel('Time')
plt.ylabel('Avg Jain Fairness Index')
plt.title('Average Jain Fairness over Time')

plt.subplot(3, 2, 6) # 3 rows, 2 columns, subplot 6
plt.plot(times_g, gini_values, '-o')
plt.xlabel('Time')
plt.ylabel('Avg Gini Index')
plt.title('Average Gini Index over Time')

plt.tight_layout()
plt.show()




# ---------------------------
# Run Multiple Simulations over Varying Parameters (Summary Plots)
# ---------------------------
num_runs = 3  # Number of simulation runs per configuration

# Varying number of users (keeping resources fixed)
user_values = [5, 10, 25, 30, 40, 50]
avg_wait_times_vs_users = []
avg_qos_vs_users = []
jain_vs_users = []
gini_vs_users = []
avg_users_in_system_vs_users = []
avg_users_in_queue_vs_users = []

for num_users in user_values:
    wait_times_runs = []
    qos_runs = []
    jain_runs = []
    gini_runs = []
    avg_users_in_system_arr = []
    avg_users_in_queue_arr = []
    for _ in range(num_runs):
        _, metrics = run_simulation(
            NUM_USERS = num_users,
            NUM_RESOURCES = 25,
            SIMULATION_TIME = SIMULATION_TIME,
            mean_arrival_rate = mean_arrival_rate,
            mean_service_time = mean_service_time,
            MIN_START_DELAY = MIN_START_DELAY,
            MAX_START_DELAY = MAX_START_DELAY,
            MIN_RATE = MIN_RATE,
            MAX_RATE = MAX_RATE,
            alpha = alpha
        )
        wait_times_runs.append(metrics["avg_wait_time"])
        qos_runs.append(metrics["avg_qos"])
        jain_runs.append(metrics["jain"])
        gini_runs.append(metrics["gini"])
        avg_users_in_system_arr.append(metrics["avg_users_in_system"])
        avg_users_in_queue_arr.append(metrics["avg_users_in_queue"])
        
    avg_wait_times_vs_users.append(np.mean(wait_times_runs))
    avg_qos_vs_users.append(np.mean(qos_runs))
    jain_vs_users.append(np.mean(jain_runs))
    gini_vs_users.append(np.mean(gini_runs))
    
    avg_users_in_system_vs_users.append(np.mean(avg_users_in_system_arr))
    avg_users_in_queue_vs_users.append(np.mean(avg_users_in_queue_arr))

plt.figure(figsize=(12, 8))
plt.suptitle(f"Number of resources = 25", fontsize=12, y=0.98)

plt.subplot(3,2,1)
plt.plot(user_values, avg_wait_times_vs_users, '-o')
plt.xlabel('Number of Users')
plt.ylabel('Avg Wait Time')
plt.title('Avg Wait Time vs. Number of Users')

plt.subplot(3,2,2)
plt.plot(user_values, avg_qos_vs_users, '-o')
plt.xlabel('Number of Users')
plt.ylabel('Avg QoS')
plt.title('Avg QoS vs. Number of Users')

plt.subplot(3,2,3)
plt.plot(user_values, jain_vs_users, '-o')
plt.xlabel('Number of Users')
plt.ylabel("Jain's Fairness Index")
plt.title("Jain's Fairness vs. Number of Users")

plt.subplot(3,2,4)
plt.plot(user_values, gini_vs_users, '-o')
plt.xlabel('Number of Users')
plt.ylabel("Gini Index")
plt.title("Gini Index vs. Number of Users")
plt.tight_layout()

plt.subplot(3,2,5)
plt.plot(user_values, avg_users_in_system_vs_users, '-o')
plt.xlabel('Number of Users')
plt.ylabel("Avg Users in System")
plt.title("Avg Users in System vs. Number of Users")
plt.tight_layout()

plt.subplot(3,2,6)
plt.plot(user_values, avg_users_in_queue_vs_users, '-o')
plt.xlabel('Number of Users')
plt.ylabel("Avg Users in Queue")
plt.title("Avg Users in Queue vs. Number of Users")
plt.tight_layout()

plt.show()




# Varying number of resources (keeping users fixed)
resource_values = [5, 10, 15, 20, 25, 30]
avg_wait_times_vs_resources = []
avg_qos_vs_resources = []
jain_vs_resources = []
gini_vs_resources = []
avg_users_in_system_vs_resource = []
avg_users_in_queue_vs_resource = []

for num_resources in resource_values:
    wait_times_runs = []
    qos_runs = []
    jain_runs = []
    gini_runs = []
    avg_users_in_system_arr = []
    avg_users_in_queue_arr = []
    for _ in range(num_runs):
        _, metrics = run_simulation(
            NUM_USERS = 20,
            NUM_RESOURCES = num_resources,
            SIMULATION_TIME = SIMULATION_TIME,
            mean_arrival_rate = mean_arrival_rate,
            mean_service_time = mean_service_time,
            MIN_START_DELAY = MIN_START_DELAY,
            MAX_START_DELAY = MAX_START_DELAY,
            MIN_RATE = MIN_RATE,
            MAX_RATE = MAX_RATE,
            alpha = alpha
        )
        wait_times_runs.append(metrics["avg_wait_time"])
        qos_runs.append(metrics["avg_qos"])
        jain_runs.append(metrics["jain"])
        gini_runs.append(metrics["gini"])
        avg_users_in_system_arr.append(metrics["avg_users_in_system"])
        avg_users_in_queue_arr.append(metrics["avg_users_in_queue"])
        
    avg_wait_times_vs_resources.append(np.mean(wait_times_runs))
    avg_qos_vs_resources.append(np.mean(qos_runs))
    jain_vs_resources.append(np.mean(jain_runs))
    gini_vs_resources.append(np.mean(gini_runs))
    
    avg_users_in_system_vs_resource.append(np.mean(avg_users_in_system_arr))
    avg_users_in_queue_vs_resource.append(np.mean(avg_users_in_queue_arr))
    

plt.figure(figsize=(12, 8))
plt.suptitle(f"Number of Users = 20", fontsize=12, y=0.98)


plt.subplot(3,2,1)
plt.plot(resource_values, avg_wait_times_vs_resources, '-o')
plt.xlabel('Number of Resources')
plt.ylabel('Avg Wait Time')
plt.title('Avg Wait Time vs. Number of Resources')

plt.subplot(3,2,2)
plt.plot(resource_values, avg_qos_vs_resources, '-o')
plt.xlabel('Number of Resources')
plt.ylabel('Avg QoS')
plt.title('Avg QoS vs. Number of Resources')

plt.subplot(3,2,3)
plt.plot(resource_values, jain_vs_resources, '-o')
plt.xlabel('Number of Resources')
plt.ylabel("Jain's Fairness Index")
plt.title("Jain's Fairness vs. Number of Resources")

plt.subplot(3,2,4)
plt.plot(resource_values, gini_vs_resources, '-o')
plt.xlabel('Number of Resources')
plt.ylabel("Gini Index")
plt.title("Gini Index vs. Number of Resources")
plt.tight_layout()

plt.subplot(3,2,5)
plt.plot(resource_values, avg_users_in_system_vs_resource, '-o')
plt.xlabel('Number of Resources')
plt.ylabel("Avg Users in System")
plt.title("Avg Users in System vs. Number of Resources")
plt.tight_layout()

plt.subplot(3,2,6)
plt.plot(resource_values, avg_users_in_queue_vs_resource, '-o')
plt.xlabel('Number of Resources')
plt.ylabel("Avg Users in Queue")
plt.title("Avg Users in Queue vs. Number of Resources")
plt.tight_layout()

plt.show()

