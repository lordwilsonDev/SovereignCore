# CRITICAL: gevent monkey-patching MUST be the ABSOLUTE FIRST executable code
# to prevent RecursionError in Python 3.12 SSL module during pytest collection.
import gevent.monkey
gevent.monkey.patch_all()

"""Load testing configuration for SovereignCore using Locust.

Usage:
    # Run with web UI
    locust -f tests/load_test.py --host=http://localhost:8528
    
    # Run headless with specific users and spawn rate
    locust -f tests/load_test.py --host=http://localhost:8528 --users 100 --spawn-rate 10 --run-time 5m --headless
    
    # Run with custom configuration
    locust -f tests/load_test.py --host=http://localhost:8528 --users 50 --spawn-rate 5
"""

import time
import uuid
import random
import json
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask, StopUser
import math


class SovereignCoreUser(HttpUser):
    """Simulated user for SovereignCore API load testing."""
    
    # Wait time between tasks (1-3 seconds)
    wait_time = between(1, 3)
    
    # User credentials for testing
    test_users = [
        {"username": "testuser", "password": "testpass123"},
        {"username": "admin", "password": "admin123"},
    ]
    
    # Thermal Simulation State
    current_temp = 45.0  # Starting temp
    mode = "RECURSIVE"   # Default mode
    
    def on_start(self):
        """Called when a simulated user starts.
        
        Authenticates the user and stores the access token.
        """
        # Select random test user
        self.credentials = random.choice(self.test_users)
        
        # Login and get token
        self.login()
    
    def login(self):
        """Authenticate and get access token."""
        response = self.client.post(
            "/api/v1/auth/token",
            data=self.credentials,
            name="/api/v1/auth/token (login)"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
        else:
            # If login fails, reschedule this user
            raise RescheduleTask()
    
    @task(10)
    def get_health(self):
        """Check health endpoint (high frequency)."""
        self.client.get(
            "/health",
            name="/health"
        )
    
    @task(5)
    def get_root(self):
        """Access root endpoint."""
        self.client.get(
            "/",
            name="/"
        )
    
    @task(3)
    def get_consciousness_state(self):
        """Get consciousness state (authenticated)."""
        self.client.get(
            "/api/v1/consciousness/state",
            headers=self.headers,
            name="/api/v1/consciousness/state"
        )
    
    @task(8)
    def process_consciousness(self):
        """Process consciousness request (main workload)."""
        # Sample prompts for testing
        prompts = [
            "What is consciousness?",
            "Explain the nature of reality.",
            "How does memory work?",
            "What is self-awareness?",
            "Can machines think?",
            "What is intelligence?",
            "Describe the concept of time.",
            "What is the meaning of existence?",
        ]
        
        payload = {
            "prompt": random.choice(prompts),
            "temperature": random.uniform(0.5, 1.0),
            "max_tokens": random.randint(100, 500)
        }
        
        self.client.post(
            "/api/v1/consciousness/process",
            headers=self.headers,
            json=payload,
            name=f"/api/v1/consciousness/process [{self.mode}]"
        )
        
        # Simulate Thermal Loading
        self.simulate_thermal_dynamics()

    def simulate_thermal_dynamics(self):
        """Simulate thermal accumulation and throttling."""
        # Simple random walk for temperature
        delta = random.uniform(-2.0, 5.0) # Tendency to heat up under load
        self.current_temp = max(40.0, min(100.0, self.current_temp + delta))
        
        # Thermal Throttling Logic
        if self.current_temp > 80.0:
            if self.mode == "RECURSIVE":
                print(f"🔥 THERMAL CRITICAL ({self.current_temp:.1f}°C). Throttling to ZERO-SHOT.")
                self.mode = "ZERO-SHOT"
        elif self.current_temp < 60.0:
            if self.mode == "ZERO-SHOT":
                print(f"❄️ COOLING ({self.current_temp:.1f}°C). Restoring RECURSIVE mode.")
                self.mode = "RECURSIVE"
    
    @task(2)
    def get_user_info(self):
        """Get current user information."""
        self.client.get(
            "/api/v1/auth/me",
            headers=self.headers,
            name="/api/v1/auth/me"
        )
    
    @task(1)
    def refresh_token(self):
        """Refresh access token (low frequency)."""
        response = self.client.post(
            "/api/v1/auth/token/refresh",
            json={"refresh_token": self.refresh_token},
            name="/api/v1/auth/token/refresh"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.access_token}"}


class AuthenticatedUser(HttpUser):
    """User that only performs authenticated operations."""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login on start."""
        response = self.client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "testpass123"}
        )
        
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
        else:
            raise RescheduleTask()
    
    @task
    def consciousness_workflow(self):
        """Complete consciousness workflow."""
        # 1. Check state
        self.client.get(
            "/api/v1/consciousness/state",
            headers=self.headers,
            name="Workflow: Get State"
        )
        
        # 2. Process query
        self.client.post(
            "/api/v1/consciousness/process",
            headers=self.headers,
            json={
                "prompt": "What is the nature of consciousness?",
                "temperature": 0.7,
                "max_tokens": 300
            },
            name="Workflow: Process Query"
        )
        
        # 3. Check state again
        self.client.get(
            "/api/v1/consciousness/state",
            headers=self.headers,
            name="Workflow: Get State (after)"
        )


class ReadOnlyUser(HttpUser):
    """User that only performs read operations (no authentication)."""
    
    wait_time = between(1, 2)
    
    @task(5)
    def get_health(self):
        """Check health."""
        self.client.get("/health")
    
    @task(3)
    def get_root(self):
        """Get root."""
        self.client.get("/")
    
    @task(1)
    def get_metrics(self):
        """Get Prometheus metrics."""
        self.client.get("/metrics")


class StressTestUser(HttpUser):
    """User for stress testing with rapid requests."""
    
    wait_time = between(0.1, 0.5)  # Very short wait time
    
    def on_start(self):
        """Login on start."""
        response = self.client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "testpass123"}
        )
        
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
        else:
            raise RescheduleTask()
    
    @task
    def rapid_fire_requests(self):
        """Make rapid requests to test rate limiting."""
        endpoints = [
            "/health",
            "/",
            "/api/v1/consciousness/state",
        ]
        
        endpoint = random.choice(endpoints)
        
        if endpoint.startswith("/api/v1"):
            self.client.get(endpoint, headers=self.headers, name="Stress: " + endpoint)
        else:
            self.client.get(endpoint, name="Stress: " + endpoint)


# ============================================================================
# Event Handlers for Custom Metrics
# ============================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts."""
    print("\n" + "="*60)
    print("SovereignCore Load Test Starting")
    print("="*60)
    print(f"Host: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops."""
    print("\n" + "="*60)
    print("SovereignCore Load Test Complete")
    print("="*60)
    
    stats = environment.stats
    
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    if stats.total.num_requests > 0:
        print(f"Min Response Time: {stats.total.min_response_time:.2f}ms")
        print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")
    else:
        print("No requests recorded.")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")
    print(f"Failure Rate: {(stats.total.num_failures / stats.total.num_requests * 100) if stats.total.num_requests > 0 else 0:.2f}%")
    
    print("\n" + "="*60 + "\n")


# ============================================================================
# Custom Load Shapes (Optional)
# ============================================================================

from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """Step load pattern: gradually increase users in steps.
    
    Increases users in steps every 60 seconds:
    - 0-60s: 10 users
    - 60-120s: 25 users
    - 120-180s: 50 users
    - 180-240s: 100 users
    - 240-300s: 150 users
    """
    
    step_time = 60  # Seconds per step
    step_load = 10  # Initial users
    spawn_rate = 5  # Users to spawn per second
    time_limit = 300  # Total test duration in seconds
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        current_step = run_time // self.step_time
        user_count = self.step_load + (current_step * 15)
        
        return (user_count, self.spawn_rate)


class SpikeLoadShape(LoadTestShape):
    """Spike load pattern: sudden increases and decreases.
    
    Simulates traffic spikes:
    - 0-30s: 10 users (baseline)
    - 30-60s: 100 users (spike)
    - 60-90s: 10 users (baseline)
    - 90-120s: 150 users (spike)
    - 120-150s: 10 users (baseline)
    """
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > 150:
            return None
        
        # Define spike pattern
        if run_time < 30:
            user_count = 10
        elif run_time < 60:
            user_count = 100
        elif run_time < 90:
            user_count = 10
        elif run_time < 120:
            user_count = 150
        else:
            user_count = 10
        
        return (user_count, 10)


# ============================================================================
# Usage Examples
# ============================================================================

"""
Basic Usage:
    locust -f tests/load_test.py --host=http://localhost:8528

Headless with specific parameters:
    locust -f tests/load_test.py --host=http://localhost:8528 \
        --users 100 --spawn-rate 10 --run-time 5m --headless

With step load shape:
    locust -f tests/load_test.py --host=http://localhost:8528 \
        --headless --users 150 --spawn-rate 5 --run-time 5m

With specific user class:
    locust -f tests/load_test.py --host=http://localhost:8528 \
        --headless --users 50 --spawn-rate 5 \
        SovereignCoreUser

Multiple user classes:
    locust -f tests/load_test.py --host=http://localhost:8528 \
        --headless --users 100 --spawn-rate 10 \
        SovereignCoreUser ReadOnlyUser

Generate HTML report:
    locust -f tests/load_test.py --host=http://localhost:8528 \
        --headless --users 100 --spawn-rate 10 --run-time 5m \
        --html report.html

With CSV output:
    locust -f tests/load_test.py --host=http://localhost:8528 \
        --headless --users 100 --spawn-rate 10 --run-time 5m \
        --csv results
"""
