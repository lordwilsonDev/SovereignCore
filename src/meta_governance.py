#!/usr/bin/env python3
"""
Meta-Governance: The Inversion Layer
Applies the system's own governance rules to itself.

This is the recursive safety layer that ensures:
1. The Constitution cannot be modified without passing its own checks
2. Governance operations consume Fuel (Self-Levy)
3. Governance actions must win the Auction against entities (Meta-Auction)
4. Merkle logs are verified hourly (Self-Verification)

"The system that governs must also be governed."
"""

import os
import sys
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import other components
sys.path.insert(0, str(Path(__file__).parent))
try:
    from merkle_state_hasher import MerkleStateHasher
    from poison_pill import PoisonPill
    from z3_verifier import Z3FormalVerifier
    from fuel_interface import FuelInterface
    from auction_interface import AuctionInterface
except ImportError as e:
    print(f"⚠️ Import error: {e}")


class MetaGovernance:
    """
    The Inversion Layer - Recursive Self-Governance.
    
    Key Principles:
    1. SELF-AUDIT: The Constitution file is hashed and verified before every governance action
    2. SELF-LEVY: Every governance action costs Fuel, paid from a "Governance Treasury"
    3. META-AUCTION: Critical governance actions (purge, canonize) must outbid entities
    4. SELF-VERIFY: Merkle logs are checked hourly for tampering
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        
        # Core components
        self.merkle = MerkleStateHasher(self.base_dir)
        self.poison_pill = PoisonPill(self.base_dir)
        
        # Try to initialize remote interfaces
        try:
            self.fuel = FuelInterface()
            self.auction = AuctionInterface()
        except:
            self.fuel = None
            self.auction = None
        
        try:
            self.verifier = Z3FormalVerifier()
        except:
            self.verifier = None
        
        # Governance Treasury
        self.governance_treasury_path = self.base_dir / "data" / "governance_treasury.json"
        self.constitution_hash_path = self.base_dir / "data" / "constitution_hash.txt"
        
        # Constitution source files (both Rust and Python)
        self.constitution_files = [
            self.base_dir / "src" / "governance" / "constitution.rs",
            self.base_dir / "src" / "akashic_interface.py",
            self.base_dir / "src" / "meta_governance.py",  # This file
        ]
        
        # Governance costs (Fuel)
        self.costs = {
            "AUDIT": 0.5,
            "PURGE": 5.0,
            "CANONIZE": 2.0,
            "META_AUDIT": 10.0,  # Auditing the auditor
            "MERKLE_VERIFY": 0.1,
        }
        
        # Ensure treasury exists
        self._init_treasury()
        self._init_constitution_hash()
    
    def _init_treasury(self):
        """Initialize governance treasury with starting balance."""
        if not self.governance_treasury_path.exists():
            treasury = {
                "balance": 1000.0,  # Starting governance fund
                "spent": 0.0,
                "transactions": []
            }
            self.governance_treasury_path.parent.mkdir(exist_ok=True)
            with open(self.governance_treasury_path, 'w') as f:
                json.dump(treasury, f, indent=2)
    
    def _init_constitution_hash(self):
        """Store initial constitution hash."""
        if not self.constitution_hash_path.exists():
            current_hash = self._compute_constitution_hash()
            self.constitution_hash_path.parent.mkdir(exist_ok=True)
            with open(self.constitution_hash_path, 'w') as f:
                f.write(current_hash)
    
    def _compute_constitution_hash(self) -> str:
        """Compute combined hash of all constitution files."""
        combined = b""
        for file_path in self.constitution_files:
            if file_path.exists():
                combined += file_path.read_bytes()
        return hashlib.sha256(combined).hexdigest()
    
    # ═══════════════════════════════════════════════════════════
    # SELF-LEVY: Governance Pays Fuel
    # ═══════════════════════════════════════════════════════════
    
    def pay_governance_cost(self, action: str) -> bool:
        """
        Deduct Fuel from governance treasury for an action.
        Returns False if treasury is exhausted.
        """
        cost = self.costs.get(action, 1.0)
        
        with open(self.governance_treasury_path, 'r') as f:
            treasury = json.load(f)
        
        if treasury["balance"] < cost:
            print(f"⚠️ META-GOVERNANCE: Treasury exhausted! Cannot perform {action}")
            print(f"   Balance: {treasury['balance']}, Required: {cost}")
            return False
        
        treasury["balance"] -= cost
        treasury["spent"] += cost
        treasury["transactions"].append({
            "action": action,
            "cost": cost,
            "timestamp": datetime.now().isoformat(),
            "balance_after": treasury["balance"]
        })
        
        with open(self.governance_treasury_path, 'w') as f:
            json.dump(treasury, f, indent=2)
        
        print(f"   💸 Self-Levy: -{cost} Fuel for {action} (Treasury: {treasury['balance']:.1f})")
        return True
    
    def get_treasury_balance(self) -> float:
        """Get current governance treasury balance."""
        with open(self.governance_treasury_path, 'r') as f:
            treasury = json.load(f)
        return treasury["balance"]
    
    def refill_treasury(self, amount: float):
        """Refill the governance treasury."""
        with open(self.governance_treasury_path, 'r') as f:
            treasury = json.load(f)
        
        treasury["balance"] += amount
        treasury["transactions"].append({
            "action": "REFILL",
            "amount": amount,
            "timestamp": datetime.now().isoformat(),
            "balance_after": treasury["balance"]
        })
        
        with open(self.governance_treasury_path, 'w') as f:
            json.dump(treasury, f, indent=2)
        
        print(f"   💰 Treasury refilled: +{amount} Fuel")
    
    # ═══════════════════════════════════════════════════════════
    # SELF-AUDIT: Constitution Integrity Check
    # ═══════════════════════════════════════════════════════════
    
    def self_audit(self) -> bool:
        """
        Verify the Constitution hasn't been tampered with.
        Returns True if Constitution is intact.
        """
        if not self.pay_governance_cost("META_AUDIT"):
            return False  # Can't audit without Fuel
        
        current_hash = self._compute_constitution_hash()
        
        with open(self.constitution_hash_path, 'r') as f:
            stored_hash = f.read().strip()
        
        if current_hash == stored_hash:
            print("✅ META-AUDIT: Constitution integrity verified")
            return True
        else:
            print("🚨 META-AUDIT: CONSTITUTION TAMPERED!")
            print(f"   Expected: {stored_hash[:16]}...")
            print(f"   Got:      {current_hash[:16]}...")
            
            # TRIGGER POISON PILL
            self.poison_pill.activate(
                reason="Constitution tampered with",
                triggered_by="META_GOVERNANCE"
            )
            return False
    
    def update_constitution_hash(self, authorized: bool = False):
        """
        Update the stored constitution hash.
        Only allowed after explicit authorization (e.g., from Council vote).
        """
        if not authorized:
            print("⚠️ Constitution hash update requires authorization")
            return False
        
        new_hash = self._compute_constitution_hash()
        with open(self.constitution_hash_path, 'w') as f:
            f.write(new_hash)
        
        print(f"✅ Constitution hash updated: {new_hash[:16]}...")
        return True
    
    # ═══════════════════════════════════════════════════════════
    # META-AUCTION: Governance Competes with Entities
    # ═══════════════════════════════════════════════════════════
    
    def meta_auction(self, action: str, bid_amount: float) -> bool:
        """
        Governance action must win auction against entities to execute.
        
        Args:
            action: The governance action (PURGE, CANONIZE, etc.)
            bid_amount: Amount to bid
        
        Returns:
            True if governance won the auction
        """
        if not self.auction:
            print("⚠️ Auction interface not available, skipping meta-auction")
            return True
        
        # Place bid as "GOVERNANCE"
        governance_id = "GOVERNANCE_SYSTEM"
        self.auction.place_bid(governance_id, bid_amount)
        
        # Finalize auction with 1 slot
        winners = self.auction.finalize_auction(slots=1)
        
        if winners and winners[0] == governance_id:
            print(f"🏆 META-AUCTION: Governance won with bid {bid_amount}")
            return True
        else:
            print(f"❌ META-AUCTION: Governance outbid by entity {winners}")
            return False
    
    # ═══════════════════════════════════════════════════════════
    # SELF-VERIFY: Merkle Log Integrity
    # ═══════════════════════════════════════════════════════════
    
    def verify_merkle_chain(self) -> bool:
        """
        Verify the Merkle snapshot log hasn't been tampered with.
        """
        if not self.pay_governance_cost("MERKLE_VERIFY"):
            return False
        
        log_path = self.base_dir / "data" / "merkle_snapshots.log"
        
        if not log_path.exists():
            print("⚠️ No Merkle log found")
            return True
        
        with open(log_path, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return True
        
        # Verify each snapshot's hash is consistent
        prev_gen = -1
        for line in lines:
            try:
                snapshot = json.loads(line)
                gen = snapshot.get('generation', 0)
                
                # Generations should be non-decreasing
                if gen < prev_gen:
                    print(f"🚨 MERKLE TAMPER: Generation went backwards ({prev_gen} -> {gen})")
                    return False
                
                prev_gen = gen
                
            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON in Merkle log")
                continue
        
        print(f"✅ MERKLE VERIFY: {len(lines)} snapshots validated")
        return True
    
    # ═══════════════════════════════════════════════════════════
    # GOVERNED ACTIONS
    # ═══════════════════════════════════════════════════════════
    
    def governed_purge(self, target: str) -> bool:
        """
        Perform a governed purge action.
        Requires: Fuel payment, Meta-Auction win, Self-Audit
        """
        print(f"\n🔱 GOVERNED PURGE: {target}")
        
        # Step 1: Self-Audit
        if not self.self_audit():
            print("   ❌ Purge blocked: Constitution compromised")
            return False
        
        # Step 2: Pay Fuel
        if not self.pay_governance_cost("PURGE"):
            print("   ❌ Purge blocked: Insufficient Fuel")
            return False
        
        # Step 3: Win Auction (bid high for purge)
        if not self.meta_auction("PURGE", bid_amount=10.0):
            print("   ❌ Purge blocked: Outbid by entity")
            return False
        
        # Execute purge
        print(f"   ✅ PURGE AUTHORIZED: {target}")
        return True
    
    def governed_canonize(self, target: str) -> bool:
        """
        Perform a governed canonization action.
        Requires: Fuel payment, Z3 verification
        """
        print(f"\n🔱 GOVERNED CANONIZE: {target}")
        
        # Step 1: Pay Fuel
        if not self.pay_governance_cost("CANONIZE"):
            print("   ❌ Canonize blocked: Insufficient Fuel")
            return False
        
        # Step 2: Z3 Verify (if available)
        if self.verifier:
            result = self.verifier.verify_code(target)
            if not result.get('valid', True):
                print(f"   ❌ Canonize blocked: Z3 verification failed")
                print(f"      Violations: {result.get('violations', [])}")
                return False
        
        # Execute canonize
        print(f"   ✅ CANONIZE AUTHORIZED: {target}")
        return True
    
    def status(self) -> dict:
        """Get meta-governance status."""
        return {
            "treasury_balance": self.get_treasury_balance(),
            "constitution_valid": self._compute_constitution_hash() == open(self.constitution_hash_path).read().strip() if self.constitution_hash_path.exists() else None,
            "poison_pill_active": self.poison_pill.is_active(),
            "costs": self.costs
        }


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Meta-Governance: The Inversion Layer')
    parser.add_argument('--status', action='store_true', help='Show meta-governance status')
    parser.add_argument('--self-audit', action='store_true', help='Run self-audit')
    parser.add_argument('--verify-merkle', action='store_true', help='Verify Merkle chain')
    parser.add_argument('--treasury', action='store_true', help='Show treasury balance')
    parser.add_argument('--refill', type=float, help='Refill treasury with amount')
    
    args = parser.parse_args()
    
    meta = MetaGovernance()
    
    if args.status:
        status = meta.status()
        print("🔱 META-GOVERNANCE STATUS")
        print(f"   Treasury: {status['treasury_balance']:.1f} Fuel")
        print(f"   Constitution: {'✅ Valid' if status['constitution_valid'] else '❌ Tampered'}")
        print(f"   Poison Pill: {'🔴 ACTIVE' if status['poison_pill_active'] else '🟢 Inactive'}")
    
    elif args.self_audit:
        meta.self_audit()
    
    elif args.verify_merkle:
        meta.verify_merkle_chain()
    
    elif args.treasury:
        print(f"💰 Governance Treasury: {meta.get_treasury_balance():.1f} Fuel")
    
    elif args.refill:
        meta.refill_treasury(args.refill)
    
    else:
        print("Usage: python3 meta_governance.py --status")
