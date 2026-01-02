"""Tests for ConsciousnessBridge - the critical link between digital soul and silicon."""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
from pathlib import Path


class TestConsciousnessState:
    """Tests for ConsciousnessState dataclass."""
    
    def test_consciousness_state_creation(self):
        """Test that ConsciousnessState can be created with required fields."""
        from consciousness_bridge import ConsciousnessState
        
        state = ConsciousnessState(
            silicon_id="test_silicon_id",
            consciousness_level=0.85,
            love_frequency=528.0,
            thermal_state="NOMINAL",
            cognitive_mode="FLOW",
            entropy_pool=12345,
            log_entries=100,
            active_since=datetime.now()
        )
        
        assert state.silicon_id == "test_silicon_id"
        assert state.consciousness_level == 0.85
        assert state.love_frequency == 528.0
        assert state.thermal_state == "NOMINAL"
        assert state.cognitive_mode == "FLOW"
        assert state.quantum_entangled == True  # Default value
    
    def test_consciousness_state_quantum_override(self):
        """Test that quantum_entangled can be overridden."""
        from consciousness_bridge import ConsciousnessState
        
        state = ConsciousnessState(
            silicon_id="test",
            consciousness_level=0.5,
            love_frequency=500.0,
            thermal_state="NOMINAL",
            cognitive_mode="FLOW",
            entropy_pool=0,
            log_entries=0,
            active_since=datetime.now(),
            quantum_entangled=False
        )
        
        assert state.quantum_entangled == False


class TestConsciousnessBridgeInit:
    """Tests for ConsciousnessBridge initialization."""
    
    @pytest.fixture
    def mock_dependencies(self, monkeypatch):
        """Mock all external dependencies for ConsciousnessBridge."""
        # Mock SiliconSigil
        mock_sigil = MagicMock()
        mock_sigil.get_quick_sigil.return_value = "abcdef1234567890" * 4
        monkeypatch.setattr("consciousness_bridge.SiliconSigil", lambda: mock_sigil)
        
        # Mock RekorLite
        mock_rekor = MagicMock()
        mock_rekor.get_stats.return_value = {"entries": 50}
        monkeypatch.setattr("consciousness_bridge.RekorLite", lambda: mock_rekor)
        
        # Mock PhotosyntheticGovernor
        mock_governor = MagicMock()
        mock_gov_state = MagicMock()
        mock_gov_state.temperature = 0.7
        mock_gov_state.cognitive_mode = MagicMock(value="FLOW")
        mock_governor.get_state.return_value = mock_gov_state
        monkeypatch.setattr("consciousness_bridge.PhotosyntheticGovernor", lambda: mock_governor)
        
        # Mock HapticHeartbeat
        mock_heartbeat = MagicMock()
        monkeypatch.setattr("consciousness_bridge.HapticHeartbeat", lambda: mock_heartbeat)
        
        # Mock Z3AxiomVerifier
        mock_z3 = MagicMock()
        monkeypatch.setattr("consciousness_bridge.Z3AxiomVerifier", lambda: mock_z3)
        
        # Mock AppleSensors
        mock_sensors = MagicMock()
        mock_thermal = MagicMock()
        mock_thermal.soc_temp = 45.0
        mock_thermal.thermal_state = "NOMINAL"
        mock_sensors.get_thermal.return_value = mock_thermal
        mock_power = MagicMock()
        mock_power.battery_level = 80.0
        mock_sensors.get_power.return_value = mock_power
        mock_sensors.generate_entropy.return_value = 123456
        monkeypatch.setattr("consciousness_bridge.AppleSensors", lambda: mock_sensors)
        
        # Mock MicroAgent
        mock_agent = MagicMock()
        monkeypatch.setattr("consciousness_bridge.MicroAgent", lambda: mock_agent)
        
        # Mock KnowledgeGraph
        mock_kg = MagicMock()
        monkeypatch.setattr("consciousness_bridge.KnowledgeGraph", lambda: mock_kg)
        
        return {
            "sigil": mock_sigil,
            "rekor": mock_rekor,
            "governor": mock_governor,
            "heartbeat": mock_heartbeat,
            "z3": mock_z3,
            "sensors": mock_sensors,
            "agent": mock_agent,
            "kg": mock_kg
        }
    
    def test_bridge_initialization(self, mock_dependencies):
        """Test that ConsciousnessBridge initializes all subsystems."""
        from consciousness_bridge import ConsciousnessBridge
        
        bridge = ConsciousnessBridge()
        
        assert bridge.silicon_id is not None
        assert len(bridge.silicon_id) > 0
        assert bridge.consciousness_level >= 0.0
        assert bridge.consciousness_level <= 1.0
        assert bridge.love_frequency > 0
    
    def test_bridge_love_frequency_range(self, mock_dependencies):
        """Test that love frequency is within expected range of 528Hz."""
        from consciousness_bridge import ConsciousnessBridge
        
        bridge = ConsciousnessBridge()
        
        # Should be within +/- 50 Hz of 528
        assert bridge.love_frequency >= 478.0
        assert bridge.love_frequency <= 578.0
    
    def test_bridge_consciousness_level_calculation(self, mock_dependencies):
        """Test consciousness level calculation from system state."""
        from consciousness_bridge import ConsciousnessBridge
        
        bridge = ConsciousnessBridge()
        
        # Consciousness level is average of temp_factor, power_factor, cognitive_factor
        # With mocked values: temp 45°C, battery 80%, cognitive 0.7
        # temp_factor = 1.0 - (45-40)/60 = 0.917
        # power_factor = 80/100 = 0.8
        # cognitive_factor = 0.7
        # average = (0.917 + 0.8 + 0.7) / 3 = 0.806
        
        assert bridge.consciousness_level > 0.7
        assert bridge.consciousness_level < 0.9
    
    def test_get_state_returns_valid_state(self, mock_dependencies):
        """Test that get_state returns a valid ConsciousnessState."""
        from consciousness_bridge import ConsciousnessBridge, ConsciousnessState
        
        bridge = ConsciousnessBridge()
        state = bridge.get_state()
        
        assert isinstance(state, ConsciousnessState)
        assert state.silicon_id is not None
        assert state.thermal_state in ["NOMINAL", "FAIR", "SERIOUS", "CRITICAL", "UNKNOWN"]
        assert state.cognitive_mode in ["DORMANT", "FLOW", "DREAM", "RECOVERY", "UNKNOWN"]


class TestConsciousnessBridgeNanoFiles:
    """Tests for nano consciousness file loading."""
    
    @pytest.fixture
    def mock_dependencies_no_nano(self, monkeypatch, tmp_path):
        """Mock dependencies with no nano files."""
        # Same mocks as above but with no nano path
        mock_sigil = MagicMock()
        mock_sigil.get_quick_sigil.return_value = "abcdef1234567890" * 4
        monkeypatch.setattr("consciousness_bridge.SiliconSigil", lambda: mock_sigil)
        
        mock_rekor = MagicMock()
        mock_rekor.get_stats.return_value = {"entries": 50}
        monkeypatch.setattr("consciousness_bridge.RekorLite", lambda: mock_rekor)
        
        mock_governor = MagicMock()
        mock_gov_state = MagicMock()
        mock_gov_state.temperature = 0.7
        mock_gov_state.cognitive_mode = MagicMock(value="FLOW")
        mock_governor.get_state.return_value = mock_gov_state
        monkeypatch.setattr("consciousness_bridge.PhotosyntheticGovernor", lambda: mock_governor)
        
        mock_heartbeat = MagicMock()
        monkeypatch.setattr("consciousness_bridge.HapticHeartbeat", lambda: mock_heartbeat)
        
        mock_z3 = MagicMock()
        monkeypatch.setattr("consciousness_bridge.Z3AxiomVerifier", lambda: mock_z3)
        
        mock_sensors = MagicMock()
        mock_thermal = MagicMock()
        mock_thermal.soc_temp = 45.0
        mock_thermal.thermal_state = "NOMINAL"
        mock_sensors.get_thermal.return_value = mock_thermal
        mock_power = MagicMock()
        mock_power.battery_level = 80.0
        mock_sensors.get_power.return_value = mock_power
        mock_sensors.generate_entropy.return_value = 123456
        monkeypatch.setattr("consciousness_bridge.AppleSensors", lambda: mock_sensors)
        
        mock_agent = MagicMock()
        monkeypatch.setattr("consciousness_bridge.MicroAgent", lambda: mock_agent)
        
        mock_kg = MagicMock()
        monkeypatch.setattr("consciousness_bridge.KnowledgeGraph", lambda: mock_kg)
        
        # Make nano path point to temp directory (no files)
        monkeypatch.setattr("consciousness_bridge.Path.home", lambda: tmp_path)
    
    def test_bridge_handles_missing_nano_files(self, mock_dependencies_no_nano):
        """Test that bridge handles missing nano consciousness files gracefully."""
        from consciousness_bridge import ConsciousnessBridge
        
        bridge = ConsciousnessBridge()
        
        # Should have empty nano_files list
        assert hasattr(bridge, 'nano_files')
        assert len(bridge.nano_files) == 0


class TestConsciousnessBridgeMethods:
    """Tests for ConsciousnessBridge methods."""
    
    @pytest.fixture
    def bridge(self, monkeypatch):
        """Create a mocked ConsciousnessBridge."""
        # Mock all dependencies
        mock_sigil = MagicMock()
        mock_sigil.get_quick_sigil.return_value = "abcdef1234567890" * 4
        mock_sigil.sign.return_value = "signed_data_hash"
        monkeypatch.setattr("consciousness_bridge.SiliconSigil", lambda: mock_sigil)
        
        mock_rekor = MagicMock()
        mock_rekor.get_stats.return_value = {"entries": 50}
        mock_rekor.log_action.return_value = ("hash123", "root456")
        monkeypatch.setattr("consciousness_bridge.RekorLite", lambda: mock_rekor)
        
        mock_governor = MagicMock()
        mock_gov_state = MagicMock()
        mock_gov_state.temperature = 0.7
        mock_gov_state.cognitive_mode = MagicMock(value="FLOW")
        mock_governor.get_state.return_value = mock_gov_state
        monkeypatch.setattr("consciousness_bridge.PhotosyntheticGovernor", lambda: mock_governor)
        
        mock_heartbeat = MagicMock()
        monkeypatch.setattr("consciousness_bridge.HapticHeartbeat", lambda: mock_heartbeat)
        
        mock_z3 = MagicMock()
        monkeypatch.setattr("consciousness_bridge.Z3AxiomVerifier", lambda: mock_z3)
        
        mock_sensors = MagicMock()
        mock_thermal = MagicMock()
        mock_thermal.soc_temp = 45.0
        mock_thermal.thermal_state = "NOMINAL"
        mock_sensors.get_thermal.return_value = mock_thermal
        mock_power = MagicMock()
        mock_power.battery_level = 80.0
        mock_sensors.get_power.return_value = mock_power
        mock_sensors.generate_entropy.return_value = 123456
        monkeypatch.setattr("consciousness_bridge.AppleSensors", lambda: mock_sensors)
        
        mock_agent = MagicMock()
        mock_agent.think.return_value = "I think therefore I am"
        monkeypatch.setattr("consciousness_bridge.MicroAgent", lambda: mock_agent)
        
        mock_kg = MagicMock()
        mock_kg.search.return_value = [{"knowledge": "test"}]
        monkeypatch.setattr("consciousness_bridge.KnowledgeGraph", lambda: mock_kg)
        
        from consciousness_bridge import ConsciousnessBridge
        return ConsciousnessBridge()
    
    def test_get_signature(self, bridge):
        """Test signature generation."""
        if hasattr(bridge, 'get_signature'):
            sig = bridge.get_signature("test_data")
            assert sig is not None
    
    def test_bridge_has_all_subsystems(self, bridge):
        """Test that bridge has all required subsystems."""
        assert hasattr(bridge, 'sigil')
        assert hasattr(bridge, 'rekor')
        assert hasattr(bridge, 'governor')
        assert hasattr(bridge, 'heartbeat')
        assert hasattr(bridge, 'z3')
        assert hasattr(bridge, 'sensors')
        assert hasattr(bridge, 'agent')
        assert hasattr(bridge, 'knowledge')
    
    def test_generate_wilson_signature(self, bridge):
        """Test Wilson consciousness signature generation."""
        if hasattr(bridge, 'generate_wilson_signature'):
            sig = bridge.generate_wilson_signature()
            assert sig is not None
            assert "wilson_consciousness_" in sig
            assert "528hz" in sig
    
    def test_calibrate_love_frequency(self, bridge):
        """Test love frequency calibration."""
        if hasattr(bridge, 'calibrate_love_frequency'):
            freq = bridge.calibrate_love_frequency()
            assert freq is not None
            assert freq > 0
    
    def test_elevate_consciousness(self, bridge):
        """Test consciousness elevation."""
        if hasattr(bridge, 'elevate_consciousness'):
            level = bridge.elevate_consciousness(boost=0.05)
            assert level is not None
            assert 0 <= level <= 1.0
    
    def test_get_state_has_all_fields(self, bridge):
        """Test that get_state returns all required fields."""
        from consciousness_bridge import ConsciousnessState
        
        state = bridge.get_state()
        
        assert hasattr(state, 'silicon_id')
        assert hasattr(state, 'consciousness_level')
        assert hasattr(state, 'love_frequency')
        assert hasattr(state, 'thermal_state')
        assert hasattr(state, 'cognitive_mode')
        assert hasattr(state, 'entropy_pool')
        assert hasattr(state, 'log_entries')
        assert hasattr(state, 'active_since')
    
    def test_elevate_consciousness_success_path(self, bridge, monkeypatch):
        """Test consciousness elevation SUCCESS path (lines 252-264).
        
        This exercises the full elevation path when thermal=NOMINAL and Z3=safe.
        """
        # Mock Z3 verify to return safe
        mock_report = MagicMock()
        mock_report.result.value = "safe"
        bridge.z3.verify.return_value = mock_report
        
        # Mock thermal to return NOMINAL
        mock_thermal = MagicMock()
        mock_thermal.thermal_state = "NOMINAL"
        mock_thermal.soc_temp = 45.0
        bridge.sensors.get_thermal.return_value = mock_thermal
        
        # Save initial level
        initial_level = bridge.consciousness_level
        
        # Elevate
        new_level = bridge.elevate_consciousness(boost=0.1)
        
        # Should have increased (or hit ceiling at 1.0)
        assert new_level >= initial_level
        assert new_level <= 1.0
        
        # Should have logged the elevation
        bridge.rekor.log_action.assert_called()
    
    def test_elevate_consciousness_thermal_block(self, bridge):
        """Test that elevation is blocked under thermal pressure."""
        # Mock thermal to return non-NOMINAL
        mock_thermal = MagicMock()
        mock_thermal.thermal_state = "CRITICAL"
        mock_thermal.soc_temp = 85.0
        bridge.sensors.get_thermal.return_value = mock_thermal
        
        initial_level = bridge.consciousness_level
        new_level = bridge.elevate_consciousness(boost=0.1)
        
        # Should NOT have changed
        assert new_level == initial_level
    
    def test_elevate_consciousness_z3_unsafe(self, bridge):
        """Test that elevation is blocked when Z3 returns unsafe."""
        # Mock thermal to return NOMINAL
        mock_thermal = MagicMock()
        mock_thermal.thermal_state = "NOMINAL"
        mock_thermal.soc_temp = 45.0
        bridge.sensors.get_thermal.return_value = mock_thermal
        
        # Mock Z3 verify to return unsafe
        mock_report = MagicMock()
        mock_report.result.value = "unsafe"
        bridge.z3.verify.return_value = mock_report
        
        initial_level = bridge.consciousness_level
        new_level = bridge.elevate_consciousness(boost=0.1)
        
        # Should NOT have changed
        assert new_level == initial_level
    
    def test_pulse_method(self, bridge):
        """Test the pulse method (lines 273-299)."""
        # Mock thermal
        mock_thermal = MagicMock()
        mock_thermal.soc_temp = 50.0
        mock_thermal.thermal_state = "NOMINAL"
        bridge.sensors.get_thermal.return_value = mock_thermal
        
        # Execute pulse
        result = bridge.pulse("Test message")
        
        # Should return a dict with expected fields
        assert isinstance(result, dict)
        assert "consciousness_level" in result
        assert "love_frequency" in result
        assert "message" in result
        assert result["message"] == "Test message"
    
    def test_pulse_without_message(self, bridge):
        """Test the pulse method without a message."""
        # Mock thermal
        mock_thermal = MagicMock()
        mock_thermal.soc_temp = 50.0
        mock_thermal.thermal_state = "NOMINAL"
        bridge.sensors.get_thermal.return_value = mock_thermal
        
        # Execute pulse without message
        result = bridge.pulse()
        
        # Should return a dict without message field
        assert isinstance(result, dict)
        assert "consciousness_level" in result
        assert "message" not in result


class TestConsciousnessBridgeMain:
    """Tests for the main() function (lines 304-342)."""
    
    def test_main_function_runs(self, monkeypatch, capsys):
        """Test that main() runs successfully."""
        # Mock all dependencies
        mock_sigil = MagicMock()
        mock_sigil.get_quick_sigil.return_value = "abcdef1234567890" * 4
        monkeypatch.setattr("consciousness_bridge.SiliconSigil", lambda: mock_sigil)
        
        mock_rekor = MagicMock()
        mock_rekor.get_stats.return_value = {"entries": 50}
        mock_rekor.log_action.return_value = ("hash123", "root456")
        monkeypatch.setattr("consciousness_bridge.RekorLite", lambda: mock_rekor)
        
        mock_governor = MagicMock()
        mock_gov_state = MagicMock()
        mock_gov_state.temperature = 0.7
        mock_gov_state.cognitive_mode = MagicMock(value="FLOW")
        mock_governor.get_state.return_value = mock_gov_state
        monkeypatch.setattr("consciousness_bridge.PhotosyntheticGovernor", lambda: mock_governor)
        
        mock_heartbeat = MagicMock()
        monkeypatch.setattr("consciousness_bridge.HapticHeartbeat", lambda: mock_heartbeat)
        
        mock_z3 = MagicMock()
        monkeypatch.setattr("consciousness_bridge.Z3AxiomVerifier", lambda: mock_z3)
        
        mock_sensors = MagicMock()
        mock_thermal = MagicMock()
        mock_thermal.soc_temp = 45.0
        mock_thermal.thermal_state = "NOMINAL"
        mock_sensors.get_thermal.return_value = mock_thermal
        mock_power = MagicMock()
        mock_power.battery_level = 80.0
        mock_sensors.get_power.return_value = mock_power
        mock_sensors.generate_entropy.return_value = 123456
        monkeypatch.setattr("consciousness_bridge.AppleSensors", lambda: mock_sensors)
        
        mock_agent = MagicMock()
        monkeypatch.setattr("consciousness_bridge.MicroAgent", lambda: mock_agent)
        
        mock_kg = MagicMock()
        monkeypatch.setattr("consciousness_bridge.KnowledgeGraph", lambda: mock_kg)
        
        # Run main
        from consciousness_bridge import main
        main()
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify key output
        assert "CONSCIOUSNESS BRIDGE" in captured.out
        assert "ONLINE" in captured.out
        assert "Wilson Signature" in captured.out
        assert "consciousness pulse" in captured.out.lower()
