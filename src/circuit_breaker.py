#!/usr/bin/env python3
"""
Circuit Breaker Pattern - Fault Tolerance for External Services
Prevents cascading failures by failing fast when services are unhealthy.

Usage:
    from circuit_breaker import CircuitBreaker
    
    breaker = CircuitBreaker("ollama", failure_threshold=3)
    
    if breaker.can_execute():
        try:
            result = call_ollama()
            breaker.record_success()
        except Exception as e:
            breaker.record_failure()
    else:
        result = fallback_response()
"""

import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Any


class CircuitState(Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing fast
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


@dataclass
class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is failing, requests are rejected
    - HALF_OPEN: Testing if service has recovered
    
    Transitions:
    - CLOSED -> OPEN: After failure_threshold consecutive failures
    - OPEN -> HALF_OPEN: After reset_timeout seconds
    - HALF_OPEN -> CLOSED: On successful request
    - HALF_OPEN -> OPEN: On failed request
    """
    
    name: str
    failure_threshold: int = 5
    reset_timeout: float = 60.0  # seconds
    
    def __post_init__(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()
    
    def can_execute(self) -> bool:
        """Check if a request can be made."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if we should transition to HALF_OPEN
            if self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)
                return True
            return False
        
        # HALF_OPEN - allow one test request
        return True
    
    def record_success(self):
        """Record a successful request."""
        self.success_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.CLOSED)
            self.failure_count = 0
            print(f"[CIRCUIT_BREAKER] {self.name}: RECOVERED ✅")
    
    def record_failure(self):
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
            print(f"[CIRCUIT_BREAKER] {self.name}: REOPENED 🔴")
        
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)
                print(f"[CIRCUIT_BREAKER] {self.name}: TRIPPED after {self.failure_count} failures 🔴")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.reset_timeout
    
    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        self.state = new_state
        self.last_state_change = time.time()
    
    def get_status(self) -> dict:
        """Get current circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time,
            "time_in_state": time.time() - self.last_state_change
        }
    
    def execute(self, func: Callable, fallback: Optional[Callable] = None, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: The function to execute
            fallback: Fallback function if circuit is open
            *args, **kwargs: Arguments to pass to func
        
        Returns:
            Result of func or fallback
        """
        if not self.can_execute():
            if fallback:
                return fallback(*args, **kwargs)
            raise CircuitOpenError(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            if fallback and self.state == CircuitState.OPEN:
                return fallback(*args, **kwargs)
            raise


class CircuitOpenError(Exception):
    """Raised when attempting to execute through an open circuit."""
    pass


# Circuit Breaker Registry
class CircuitBreakerRegistry:
    """Global registry of circuit breakers."""
    
    _breakers: dict = {}
    
    @classmethod
    def get(cls, name: str, **kwargs) -> CircuitBreaker:
        """Get or create a circuit breaker by name."""
        if name not in cls._breakers:
            cls._breakers[name] = CircuitBreaker(name=name, **kwargs)
        return cls._breakers[name]
    
    @classmethod
    def get_all_status(cls) -> list:
        """Get status of all breakers."""
        return [b.get_status() for b in cls._breakers.values()]


# Pre-configured breakers for SovereignCore
OLLAMA_BREAKER = CircuitBreakerRegistry.get("ollama", failure_threshold=3, reset_timeout=30.0)
RUST_CORE_BREAKER = CircuitBreakerRegistry.get("rust_core", failure_threshold=5, reset_timeout=10.0)
AKASHIC_BREAKER = CircuitBreakerRegistry.get("akashic", failure_threshold=5, reset_timeout=10.0)


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Circuit Breaker Test')
    parser.add_argument('--status', action='store_true', help='Show all breaker statuses')
    parser.add_argument('--test', action='store_true', help='Run test scenario')
    
    args = parser.parse_args()
    
    if args.status:
        for status in CircuitBreakerRegistry.get_all_status():
            print(f"{status['name']}: {status['state']} (failures: {status['failure_count']})")
    
    elif args.test:
        breaker = CircuitBreaker("test_service", failure_threshold=3, reset_timeout=5.0)
        
        print("Simulating failures...")
        for i in range(5):
            if breaker.can_execute():
                breaker.record_failure()
                print(f"  Failure {i+1}: State = {breaker.state.value}")
            else:
                print(f"  Request {i+1}: BLOCKED (circuit open)")
        
        print(f"\nWaiting {breaker.reset_timeout}s for reset timeout...")
        time.sleep(breaker.reset_timeout + 1)
        
        print("Attempting recovery...")
        if breaker.can_execute():
            breaker.record_success()
            print(f"  Success: State = {breaker.state.value}")
        
        print(f"\nFinal status: {breaker.get_status()}")
