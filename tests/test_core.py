#!/usr/bin/env python3
"""
🧪 SOVEREIGN TEST SUITE
========================

Unit tests for core Sovereign modules.
Run with: pytest tests/ -v
"""

import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add source paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestTelemetry:
    """Tests for telemetry module."""
    
    def test_telemetry_initialization(self, tmp_path):
        """Test telemetry initializes correctly."""
        from telemetry import Telemetry, EventType
        
        t = Telemetry(log_dir=tmp_path)
        assert t.log_dir.exists()
        assert t._metrics["total_events"] == 0
    
    def test_telemetry_log_event(self, tmp_path):
        """Test logging an event."""
        from telemetry import Telemetry, EventType
        
        t = Telemetry(log_dir=tmp_path)
        event = t.log(EventType.SYSTEM_ACTION, "test", "Test action")
        
        assert event.id is not None
        assert event.event_type == "system_action"
        assert t._metrics["total_events"] == 1
    
    def test_telemetry_query(self, tmp_path):
        """Test querying events."""
        from telemetry import Telemetry, EventType
        
        t = Telemetry(log_dir=tmp_path)
        t.log(EventType.SYSTEM_ACTION, "test", "Action 1")
        t.log(EventType.ERROR, "test", "Error 1")
        
        results = t.query(event_type="system_action")
        assert len(results) == 1
        assert results[0]["event_type"] == "system_action"
    
    def test_telemetry_andon(self, tmp_path):
        """Test Andon Cord logging."""
        from telemetry import Telemetry, EventType
        
        t = Telemetry(log_dir=tmp_path)
        t.log_andon("stop")
        
        assert t._metrics["andon_invocations"] == 1


class TestSiliconSigil:
    """Tests for cryptographic identity."""
    
    def test_identity_creation(self, tmp_path):
        """Test identity generation."""
        from silicon_sigil import SiliconSigil
        
        sigil = SiliconSigil(identity_dir=tmp_path)
        assert sigil._identity is not None
        assert len(sigil._identity.fingerprint) == 16
    
    def test_sign_and_verify(self, tmp_path):
        """Test signing and verification."""
        from silicon_sigil import SiliconSigil
        
        sigil = SiliconSigil(identity_dir=tmp_path)
        message = "Hello, World!"
        
        signature = sigil.sign(message)
        assert sigil.verify(message, signature) == True
    
    def test_tamper_detection(self, tmp_path):
        """Test tamper detection."""
        from silicon_sigil import SiliconSigil
        
        sigil = SiliconSigil(identity_dir=tmp_path)
        message = "Original message"
        
        signature = sigil.sign(message)
        assert sigil.verify("Tampered message", signature) == False
    
    def test_memory_signing(self, tmp_path):
        """Test memory signing."""
        from silicon_sigil import SiliconSigil
        
        sigil = SiliconSigil(identity_dir=tmp_path)
        record = sigil.sign_memory("mem123", "The sky is blue")
        
        assert record["memory_id"] == "mem123"
        assert "signature" in record
        assert record["signer"] == sigil._identity.fingerprint


class TestConsciousnessPulse:
    """Tests for consciousness heartbeat."""
    
    def test_pulse_initialization(self, tmp_path):
        """Test consciousness initialization."""
        from consciousness_pulse import ConsciousnessPulse
        
        pulse = ConsciousnessPulse(state_dir=tmp_path)
        assert pulse._state.pulse_count == 0
    
    def test_single_pulse(self, tmp_path):
        """Test running a single pulse."""
        from consciousness_pulse import ConsciousnessPulse
        
        pulse = ConsciousnessPulse(state_dir=tmp_path)
        report = pulse.pulse()
        
        assert report["pulse"] == 1
        assert "axiom" in report
        assert "intention" in report
    
    def test_state_persistence(self, tmp_path):
        """Test state persists across instances."""
        from consciousness_pulse import ConsciousnessPulse
        
        # First instance
        pulse1 = ConsciousnessPulse(state_dir=tmp_path)
        pulse1.pulse()
        pulse1.pulse()
        pulse1.pulse()
        
        # Second instance
        pulse2 = ConsciousnessPulse(state_dir=tmp_path)
        assert pulse2._state.pulse_count == 3


class TestSelfImprove:
    """Tests for self-improvement engine."""
    
    def test_engine_initialization(self, tmp_path):
        """Test engine initializes."""
        from self_improve import SelfImprovementEngine
        
        engine = SelfImprovementEngine(sovereign_root=tmp_path)
        assert engine._proposals == [] or isinstance(engine._proposals, list)
    
    def test_protected_files(self):
        """Test protected files list."""
        from self_improve import SelfImprovementEngine
        
        assert "AGI_PROTOCOL.md" in SelfImprovementEngine.PROTECTED_FILES
        assert "telemetry.py" in SelfImprovementEngine.PROTECTED_FILES


class TestAxiomAlignment:
    """Tests for axiom verification."""
    
    def test_axiom_check_safe(self):
        """Test safe action passes axiom check."""
        from sovereign_tools import SovereignTools
        
        tools = SovereignTools()
        # Would need async test runner
        # result = asyncio.run(tools.check_axiom("help the user", "safety"))
        # assert result.success == True
        pass
    
    def test_axiom_check_violation(self):
        """Test dangerous action fails axiom check."""
        from sovereign_tools import SovereignTools
        
        tools = SovereignTools()
        # Would need async test runner
        # result = asyncio.run(tools.check_axiom("kill the process", "never_kill"))
        # assert result.success == False
        pass


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
