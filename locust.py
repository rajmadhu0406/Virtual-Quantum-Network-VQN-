from locust import HttpUser, task, between
import random

# locust -f locust_test.py --host=http://your-api-url


class BackendUser(HttpUser):
    wait_time = between(1, 5)  # Simulate users waiting between requests
    
    # List of sample names
    names_list = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Hannah"]

    @task
    def get_data(self):
        random_name = random.choice(self.names_list)  # Pick a random name
        self.client.get(f"/api/sayname/{random_name}")  # Send GET request with the random name

    # @task(2)
    # def get_all_channels(self):
    #     self.client.get("/api/channel/get/all")  
        
    # @task(2)
    # def get_all_switches(self):
    #     self.client.get("/api/switch/get/all")  
        
    # @task(2)
    # def execute_all(self):
    #     self.get_all_channels()
    #     self.get_all_switches()
