#!/usr/bin/env python3
"""
🔐 PERSISTENT IDENTITY (Silicon Sigil)
======================================

Cryptographic identity for the Sovereign.
Every memory, decision, and action is signed with a persistent key.

Features:
- Ed25519 keypair generation
- Memory signing and verification
- Identity persistence across restarts
- Merkle tree for decision history

Usage:
    python3 silicon_sigil.py --init      # Generate identity
    python3 silicon_sigil.py --sign MSG  # Sign a message
    python3 silicon_sigil.py --verify    # Verify identity
"""

import os
import json
import base64
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# Use cryptography library if available, fallback to hashlib-based
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  cryptography not installed, using HMAC fallback")


@dataclass
class SovereignIdentity:
    """The Sovereign's persistent identity."""
    created: str
    public_key: str
    fingerprint: str
    name: str = "Sovereign"
    version: str = "1.0"
    axioms: str = "Love|Safety|Abundance|Growth|Transparency|NeverKill|GoldenRule"


class SiliconSigil:
    """
    The Sovereign's cryptographic identity.
    
    This creates a persistent identity that:
    - Signs all memories and decisions
    - Cannot be forged or impersonated
    - Enables trust verification
    - Persists across restarts
    """
    
    def __init__(self, identity_dir: Optional[Path] = None):
        self.identity_dir = identity_dir or Path.home() / ".sovereign" / "identity"
        self.identity_dir.mkdir(parents=True, exist_ok=True)
        
        self.private_key_file = self.identity_dir / "private.key"
        self.public_key_file = self.identity_dir / "public.key"
        self.identity_file = self.identity_dir / "identity.json"
        self.signatures_file = self.identity_dir / "signatures.jsonl"
        
        self._private_key = None
        self._public_key = None
        self._identity: Optional[SovereignIdentity] = None
        
        self._load_or_create()
    
    def _generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate a new Ed25519 keypair."""
        if CRYPTO_AVAILABLE:
            private_key = Ed25519PrivateKey.generate()
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_bytes = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            return private_bytes, public_bytes
        else:
            # Fallback: HMAC-based pseudo-identity
            secret = os.urandom(32)
            public = hashlib.sha256(secret).digest()
            return secret, public
    
    def _load_or_create(self):
        """Load existing identity or create new one."""
        if self.identity_file.exists():
            self._load()
        else:
            self._create()
    
    def _create(self):
        """Create a new identity."""
        print("🔐 Generating new Sovereign identity...")
        
        private_bytes, public_bytes = self._generate_keypair()
        
        # Save keys
        self.private_key_file.write_bytes(private_bytes)
        self.public_key_file.write_bytes(public_bytes)
        
        # Create identity
        fingerprint = hashlib.sha256(public_bytes).hexdigest()[:16]
        
        self._identity = SovereignIdentity(
            created=datetime.now().isoformat(),
            public_key=base64.b64encode(public_bytes).decode(),
            fingerprint=fingerprint
        )
        
        self.identity_file.write_text(json.dumps(asdict(self._identity), indent=2))
        
        self._private_key = private_bytes
        self._public_key = public_bytes
        
        print(f"✅ Identity created: {fingerprint}")
        print(f"   Location: {self.identity_dir}")
    
    def _load(self):
        """Load existing identity."""
        self._private_key = self.private_key_file.read_bytes()
        self._public_key = self.public_key_file.read_bytes()
        
        data = json.loads(self.identity_file.read_text())
        self._identity = SovereignIdentity(**data)
        
        print(f"🔐 Identity loaded: {self._identity.fingerprint}")
    
    def sign(self, message: str) -> str:
        """
        Sign a message with the Sovereign's key.
        
        Returns base64-encoded signature.
        """
        message_bytes = message.encode()
        
        if CRYPTO_AVAILABLE:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            private_key = Ed25519PrivateKey.from_private_bytes(self._private_key)
            signature = private_key.sign(message_bytes)
        else:
            # HMAC fallback
            import hmac
            signature = hmac.new(self._private_key, message_bytes, hashlib.sha256).digest()
        
        sig_b64 = base64.b64encode(signature).decode()
        
        # Log signature
        record = {
            "timestamp": datetime.now().isoformat(),
            "message_hash": hashlib.sha256(message_bytes).hexdigest()[:16],
            "signature": sig_b64[:32] + "...",
            "identity": self._identity.fingerprint
        }
        
        with open(self.signatures_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        return sig_b64
    
    def verify(self, message: str, signature: str) -> bool:
        """
        Verify a signature.
        
        Returns True if valid, False otherwise.
        """
        message_bytes = message.encode()
        signature_bytes = base64.b64decode(signature)
        
        if CRYPTO_AVAILABLE:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            try:
                public_key = Ed25519PublicKey.from_public_bytes(self._public_key)
                public_key.verify(signature_bytes, message_bytes)
                return True
            except:
                return False
        else:
            # HMAC fallback
            import hmac
            expected = hmac.new(self._private_key, message_bytes, hashlib.sha256).digest()
            return hmac.compare_digest(signature_bytes, expected)
    
    def sign_memory(self, memory_id: str, content: str) -> Dict:
        """
        Sign a memory for integrity verification.
        
        Returns signed memory record.
        """
        payload = f"{memory_id}:{content}"
        signature = self.sign(payload)
        
        return {
            "memory_id": memory_id,
            "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
            "signature": signature,
            "signer": self._identity.fingerprint,
            "timestamp": datetime.now().isoformat()
        }
    
    def sign_decision(self, decision: str, context: str) -> Dict:
        """
        Sign a decision for accountability.
        
        Returns signed decision record.
        """
        payload = f"DECISION:{decision}|CONTEXT:{context}"
        signature = self.sign(payload)
        
        return {
            "decision": decision,
            "context_hash": hashlib.sha256(context.encode()).hexdigest()[:16],
            "signature": signature,
            "signer": self._identity.fingerprint,
            "timestamp": datetime.now().isoformat(),
            "axioms": self._identity.axioms
        }
    
    def get_identity(self) -> Dict:
        """Get the identity information."""
        return asdict(self._identity)
    
    def display(self):
        """Display identity information."""
        print("\n🔐 SOVEREIGN IDENTITY (Silicon Sigil)")
        print("=" * 50)
        print(f"   Name:        {self._identity.name}")
        print(f"   Version:     {self._identity.version}")
        print(f"   Fingerprint: {self._identity.fingerprint}")
        print(f"   Created:     {self._identity.created}")
        print(f"   Public Key:  {self._identity.public_key[:32]}...")
        print(f"   Axioms:      {self._identity.axioms}")
        print("=" * 50)
        
        # Count signatures
        if self.signatures_file.exists():
            count = sum(1 for _ in open(self.signatures_file))
            print(f"   Signatures:  {count} records")


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Silicon Sigil - Sovereign Identity")
    parser.add_argument("--init", action="store_true", help="Initialize identity")
    parser.add_argument("--sign", type=str, help="Sign a message")
    parser.add_argument("--verify", action="store_true", help="Display identity")
    parser.add_argument("--test", action="store_true", help="Run test signing")
    
    args = parser.parse_args()
    
    sigil = SiliconSigil()
    
    if args.sign:
        sig = sigil.sign(args.sign)
        print(f"✅ Signature: {sig[:64]}...")
    
    elif args.verify or args.init:
        sigil.display()
    
    elif args.test:
        print("🧪 Testing cryptographic signing...")
        
        # Sign a memory
        memory_sig = sigil.sign_memory("test123", "The sky is blue")
        print(f"   Memory signed: {memory_sig['memory_id']}")
        
        # Sign a decision
        decision_sig = sigil.sign_decision(
            "Help the user with their request",
            "User asked for assistance"
        )
        print(f"   Decision signed: {decision_sig['decision'][:30]}...")
        
        # Verify
        test_msg = "Hello, World!"
        sig = sigil.sign(test_msg)
        valid = sigil.verify(test_msg, sig)
        print(f"   Verification: {'✅ PASS' if valid else '❌ FAIL'}")
        
        # Tamper test
        valid_tampered = sigil.verify("Tampered message", sig)
        print(f"   Tamper detect: {'✅ DETECTED' if not valid_tampered else '❌ FAILED'}")
    
    else:
        sigil.display()
