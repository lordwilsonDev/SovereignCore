import sys
import pytest
from photosynthetic_governor import PhotosyntheticGovernor, CognitiveMode, GovernorState

# Fixture to provide a PhotosyntheticGovernor instance for each test
@pytest.fixture
def governor(monkeypatch):
    """
    Provides a governor instance with AppleSensors disabled to ensure
    predictable behavior without hardware dependencies.
    """
    # Prevent the 'apple_sensors' module from being imported
    monkeypatch.setitem(sys.modules, "apple_sensors", None)
    yield PhotosyntheticGovernor()

def test_initialization(governor: PhotosyntheticGovernor):
    """
    Tests that the governor initializes correctly, especially when no
    real sensors are available.
    """
    assert governor is not None
    # In a test environment, sensors should be None
    assert governor.sensors is None

def test_default_state(governor: PhotosyntheticGovernor):
    """
    Tests the default state when no sensors are present. The governor should
    return its default "healthy" state.
    """
    state = governor.get_state()
    assert state.power_watts == 15.0  # Default power
    assert state.cognitive_mode == CognitiveMode.BALANCED
    assert state.temperature == 0.5
    assert state.can_dream is False # Can't dream in balanced mode

# Parameterized test to cover all power-based cognitive modes
@pytest.mark.parametrize("power, expected_mode, expected_temp", [
    (25.0, CognitiveMode.DREAM, 0.9),
    (15.0, CognitiveMode.BALANCED, 0.5),
    (8.0, CognitiveMode.CONSERVATIVE, 0.3),
    (3.0, CognitiveMode.DETERMINISTIC, 0.0),
])
def test_power_thresholds(governor: PhotosyntheticGovernor, monkeypatch, power, expected_mode, expected_temp):
    """
    Tests that the governor correctly changes cognitive mode based on power input,
    with no other environmental pressures.
    """
    # Mock the sensor methods to return controlled values
    monkeypatch.setattr(governor, "_get_power_state", lambda: (power, 1.0, True))
    monkeypatch.setattr(governor, "_get_thermal_state", lambda: ("NOMINAL", 0.0))

    state = governor.get_state()

    assert state.cognitive_mode == expected_mode
    assert state.temperature == expected_temp
    assert state.power_watts == power

def test_thermal_throttling(governor: PhotosyntheticGovernor, monkeypatch):
    """
    Tests that high thermal pressure overrides high power and forces a
    more conservative or deterministic state.
    """
    # High power, but also high thermal pressure
    monkeypatch.setattr(governor, "_get_power_state", lambda: (25.0, 1.0, True)) # Should be DREAM mode
    monkeypatch.setattr(governor, "_get_thermal_state", lambda: ("SERIOUS", 0.8)) # But this should override it

    state = governor.get_state()
    
    # Even with high power, thermal pressure forces deterministic mode
    assert state.cognitive_mode == CognitiveMode.DETERMINISTIC
    assert state.temperature == 0.1
    assert "Thermal pressure" in state.reason

def test_critical_battery_penalty(governor: PhotosyntheticGovernor, monkeypatch):
    """
    Tests that a critical battery level (while not charging) forces deterministic mode,
    even if power and thermals are otherwise fine.
    """
    # High power, good thermals, but critical battery
    monkeypatch.setattr(governor, "_get_power_state", lambda: (25.0, 0.09, False)) # 9% battery, not charging
    monkeypatch.setattr(governor, "_get_thermal_state", lambda: ("NOMINAL", 0.1))

    state = governor.get_state()

    assert state.cognitive_mode == CognitiveMode.DETERMINISTIC
    assert state.temperature == 0.0
    assert "Critical battery" in state.reason

def test_thermal_trauma_penalty(governor: PhotosyntheticGovernor, monkeypatch):
    """
    Tests the homeostatic neuroplasticity feature. A context that previously
    caused overheating should result in a lower cognitive temperature.
    """
    # Set a healthy baseline state
    monkeypatch.setattr(governor, "_get_power_state", lambda: (15.0, 1.0, True)) # BALANCED mode, temp 0.5
    monkeypatch.setattr(governor, "_get_thermal_state", lambda: ("NOMINAL", 0.0))

    # Get the baseline temperature for a specific topic
    context = "complex physics simulation"
    baseline_state = governor.get_state(context=context)
    assert baseline_state.temperature == 0.5

    # Now, record a trauma event related to this context
    governor.record_thermal_trauma(context, severity=0.9)

    # Get the state again with the same context
    trauma_state = governor.get_state(context=context)

    # The temperature should now be lower due to the trauma penalty
    assert trauma_state.temperature < baseline_state.temperature
    assert "Trauma penalty" in trauma_state.reason
    
