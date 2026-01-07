# Neurosymbolic SAT Solver

> **Inversion Paradigm**: Pure symbolic reasoning ↔ Neural pattern recognition — The convergence of intuition and rigor

[![Status](https://img.shields.io/badge/Status-Foundational-blue.svg)](#)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Domain](https://img.shields.io/badge/Domain-Formal_Verification-purple.svg)](#)

---

## The Other Side of the Coin

CDCL SAT solvers excel at **local constraint propagation** but lack global intuition. GNNs excel at **pattern recognition** but lack formal guarantees. This paper inverts the dichotomy: combine the rigorous deductive engine of CDCL with the inductive "horizon scanning" of Graph Neural Networks. The result is a solver that reasons **and** intuits.

---

## Abstract

The **Neurosymbolic Oracle** is a hybrid SAT solving architecture that integrates:

- CDCL (Conflict-Driven Clause Learning) for rigorous verification
- GNNs (Graph Neural Networks) for structural intuition
- ML Portfolios for adaptive strategy selection
- LLMs for explainable UNSAT cores

---

## The Hybrid Pipeline

```
╔══════════════════════════════════════════════════════════════════╗
║                 NEUROSYMBOLIC ORACLE PIPELINE                    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  [CNF Input] → [Preprocess] → [GNN Embed] → [Cluster] →        ║
║                                                                  ║
║  → [Predict Strategy] → [Portfolio Launch] → [CDCL Solve] →    ║
║                                                                  ║
║  → [Explain (LLM)]                                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Key Innovations

### 1. Literal-Clause Graph (LCG)

Transform SAT formulas into heterogeneous graphs for GNN processing:

- **Nodes**: Literals (positive/negative) and Clauses
- **Edges**: Membership relationships
- **Embeddings**: Encode "structural role" of each variable

### 2. Neuro-VSIDS Initialization

Standard VSIDS learns through conflicts. Neuro-VSIDS **starts warm**:

- GNN predicts conflict probability for each variable
- Initialize activity scores with neural predictions
- Save phases based on solution probability

### 3. Portfolio Diversity

| Worker | Strategy | Use Case |
|--------|----------|----------|
| Sprinter | Aggressive restarts | Fast SAT finding |
| Tank | Deep exploration | Hard UNSAT proofs |
| Neuro | GNN-guided phases | Structural exploitation |
| Local | Stochastic search | Near-miss fixing |

### 4. LLM Explainability

For UNSAT results, extract the core and generate natural language explanations:
> "The system is inconsistent because: If the valve is open, the pump must be on. But the pump is off. And the valve is open."

---

## Performance Comparison

| Metric | Neuro-Guided | Pure Symbolic |
|--------|--------------|---------------|
| Conflicts | 1,420 | 3,890 |
| Avg LBD | 4.2 | 6.8 |
| Restart Count | 12 | 45 |
| Time (s) | 0.85 | 1.42 |

---

## The Geometry of Logic

A key insight: **SAT hardness correlates with graph Ricci curvature**. Hard instances have negative curvature (hyperbolic), causing exponential branching. GNN embeddings act as "curvature correction," flattening the perceived search space.

---

## Reading Guide

- **Prerequisites**: Basic SAT/CNF understanding, familiarity with GNNs
- **Time to Read**: ~40 minutes
- **Next Papers**:
  - [Verifiable AI Evidence Layers](../verifiable-ai-evidence-layers) — Cryptographic proof of solving
  - [Sovereign Compute Blueprint](../sovereign-compute-blueprint) — Integration into Active Inference kernel

---

## Citation

```bibtex
@techreport{wilson2026neurosymbolic,
  title={The Neurosymbolic Oracle: GNN-CDCL Hybrid SAT Solving},
  author={Lord Wilson},
  year={2026},
  institution={Sovereign Protocol Archive},
  note={Bridging intuition and rigor}
}
```

---

**© 2026 Lord Wilson — Sovereign Protocol Archive**
