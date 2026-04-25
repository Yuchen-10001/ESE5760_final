# ESE5760 Final Project — Data Analysis Outline

**Project**: Comparative Analysis of 3D Memory Technologies Across Process Nodes Using DESTINY  
**Simulation Tool**: DESTINY (Design Space for Memory Arrays)  
**Date**: April 2026

---

## 1. Experimental Setup (Brief Recap)

### 1.1 Normalized Baseline
All configurations share a fixed baseline to enable fair cross-technology comparison:

| Parameter | Value |
|---|---|
| Capacity | 2 MB |
| Word Width | 256 bit |
| Associativity | 1-way |
| Device Roadmap | LOP |
| Temperature | 350 K |
| Optimization Target | WriteEDP |

### 1.2 Experiment 1 — Node Scaling Sweep
- **Technologies**: 2D SRAM, 3D SRAM (2-die), 2D eDRAM, 3D eDRAM (2-die)
- **Process Nodes**: 65 nm → 45 nm → 32 nm → 22 nm
- **Total runs**: 16

### 1.3 Experiment 2 — TSV Parameter Sensitivity
- **Target**: 3D SRAM at 32 nm (fixed)
- **Swept parameters** (one at a time):
  - `LocalTSVProjection`: 0, 1, 2
  - `GlobalTSVProjection`: 0, 1, 2
  - `TSVRedundancy`: 1.0, 1.2, 1.5
- **Total runs**: 6 (+ baseline reused from Exp 1)

---

## 2. Analysis Section Outline

---

### 2.1 Area Scaling Across Process Nodes

**Key data**:

| Technology | 65 nm | 45 nm | 32 nm | 22 nm | Scaling Ratio (65→22) |
|---|---|---|---|---|---|
| 2D SRAM  | 12.348 | 8.893 | 4.262 | 1.836 | **6.7×** |
| 3D SRAM  |  7.105 | 5.245 | 2.132 | 0.969 | **7.3×** |
| 2D eDRAM |  5.957 | 4.555 | 1.440 | 0.630 | **9.5×** |
| 3D eDRAM |  7.743 | 3.125 | 1.068 | 0.550 | **14.1×** |

**Points to make**:
- All four technologies show monotonic area reduction as node scales down
- eDRAM benefits more from node scaling than SRAM — eDRAM's single-transistor cell structure scales more aggressively
- 3D eDRAM achieves the highest total scaling ratio (14.1×), driven by both node scaling and 3D stacking benefit compounding at smaller nodes
- At 22 nm, 3D eDRAM reaches the smallest footprint (0.55 mm²), ~22× smaller than 2D SRAM at 65 nm

**Sub-point — 3D stacking benefit on area**:

| Node | 2D SRAM | 3D SRAM | Reduction | 2D eDRAM | 3D eDRAM | Reduction |
|---|---|---|---|---|---|---|
| 65 nm | 12.348 | 7.105 | **42%** | 5.957 | 7.743 | **−30% (overhead)** |
| 45 nm |  8.893 | 5.245 | **41%** | 4.555 | 3.125 | **31%** |
| 32 nm |  4.262 | 2.132 | **50%** | 1.440 | 1.068 | **26%** |
| 22 nm |  1.836 | 0.969 | **47%** | 0.630 | 0.550 | **13%** |

Notable: 3D eDRAM at 65 nm is **larger** than 2D eDRAM — TSV overhead dominates at larger nodes. The crossover happens between 65 nm and 45 nm. 3D SRAM consistently benefits from stacking (≈40–50% reduction) because its larger baseline cell area absorbs the TSV overhead.

---

### 2.2 Read Latency Trends

**Key data** (Cache Hit Latency, ns):

| Technology | 65 nm | 45 nm | 32 nm | 22 nm |
|---|---|---|---|---|
| 2D SRAM  | **9.942** | 0.939 | 1.061 | 1.184 |
| 3D SRAM  | **4.698** | 0.654 | 0.633 | 0.705 |
| 2D eDRAM | 2.488 | 0.663 | 0.757 | 0.790 |
| 3D eDRAM | 0.538 | 0.504 | 0.472 | **0.420** |

**Points to make**:
- 3D eDRAM achieves the lowest latency at every node and continues to improve monotonically (0.54 → 0.42 ns). Its low-capacitance cell and short interconnect paths in the 3D stack are the primary drivers.
- SRAM (both 2D and 3D) shows anomalously high latency at 65 nm, followed by a sharp drop at 45 nm. **This requires explanation** (see §2.5 Anomalies).
- 2D eDRAM and 3D SRAM converge in latency range (0.63–0.79 ns) at 32–22 nm, suggesting competitive performance for these mid-tier options.
- Post-45 nm, SRAM latency is non-monotonic (slightly increasing 45→22 nm), indicating the optimizer is trading latency for energy at smaller nodes under WriteEDP.

---

### 2.3 Write Dynamic Energy Trends

**Key data** (nJ/access):

| Technology | 65 nm | 45 nm | 32 nm | 22 nm |
|---|---|---|---|---|
| 2D SRAM  | 0.022 | 0.173 | 0.123 | 0.035 |
| 3D SRAM  | 0.037 | 0.132 | 0.089 | 0.027 |
| 2D eDRAM | 0.092 | 0.117 | 0.066 | 0.019 |
| 3D eDRAM | 0.206 | 0.102 | 0.061 | 0.021 |

**Points to make**:
- Write energy is **non-monotonic** for all technologies — it does not simply decrease with node. This is because the optimizer (WriteEDP) changes cache organization at each node, which can increase energy at intermediate nodes.
- SRAM has very low write energy at 65 nm (the optimizer selects a compact, low-energy configuration at this node) but spikes at 45 nm before recovering.
- 3D eDRAM has the highest write energy at 65 nm (0.206 nJ), likely due to TSV charging overhead at large geometries. By 22 nm it achieves near-minimum energy (0.021 nJ).
- At 22 nm, all four technologies converge to similar write energy (0.019–0.035 nJ), suggesting that energy differences shrink as the node scales.

---

### 2.4 Leakage Power Trends

**Key data** (mW):

| Technology | 65 nm | 45 nm | 32 nm | 22 nm |
|---|---|---|---|---|
| 2D SRAM  | 124.0 | 48.3 | **234.6** | 65.8 |
| 3D SRAM  | 145.8 | 51.3 | **234.6** | 70.3 |
| 2D eDRAM |  24.5 |  9.9 |  29.9 |  9.8 |
| 3D eDRAM | 107.0 | 18.4 |  50.1 | 16.2 |

**Points to make**:
- eDRAM leakage is consistently and substantially lower than SRAM at all nodes. At 45 nm, 2D eDRAM leakage (9.9 mW) is ~5× lower than 2D SRAM (48.3 mW). This reflects the single-transistor eDRAM cell's inherently lower subthreshold leakage.
- SRAM leakage at 32 nm spikes dramatically to 234.6 mW for both 2D and 3D. **This requires explanation** (see §2.5 Anomalies).
- 3D eDRAM leakage is higher than 2D eDRAM at every node — the TSV structures and additional die introduce extra leakage paths.
- For eDRAM, leakage generally tracks with area (both are lowest at 22 nm), consistent with subthreshold leakage being proportional to the total number of transistors.

---

### 2.5 Anomalies and Explanations

Two anomalies require explicit discussion in the writeup:

#### Anomaly A — SRAM latency spike at 65 nm
- 2D SRAM: 9.94 ns at 65 nm vs. 0.94 ns at 45 nm (10× difference)
- 3D SRAM: 4.70 ns at 65 nm vs. 0.65 ns at 45 nm (7× difference)
- **Cause**: DESTINY's optimizer selects the bank/mat organization that minimizes WriteEDP, not latency. At 65 nm, the large physical area forces the optimizer into a deep, hierarchical interconnect topology that incurs high H-tree latency. At 45 nm, the smaller feature size enables a more compact organization with dramatically shorter wire delays.
- **Implication**: The 65 nm latency numbers are physically meaningful but reflect an organizational choice, not a technology ceiling. They should be presented as "optimizer-selected design point" rather than absolute technology limits.

#### Anomaly B — SRAM leakage spike at 32 nm (234.6 mW)
- Identical values for 2D SRAM and 3D SRAM at 32 nm suggest the optimizer converged to the same physical configuration for both.
- The spike is non-monotonic relative to neighboring nodes (48.3 mW at 45 nm, 65.8 mW at 22 nm).
- **Likely cause**: Under WriteEDP optimization at 32 nm, the optimizer selects a configuration with high parallelism (many active subarrays) to reduce write latency, which increases total active leakage significantly.
- **Implication**: Leakage is highly sensitive to organizational choices under WriteEDP; a different optimization target (e.g., ReadLatency) would likely yield a different leakage profile.

---

### 2.6 Cross-Technology Comparison at 32 nm

Using 32 nm as the representative node (most balanced across all metrics):

| Technology | Area (mm²) | Read Lat. (ns) | Write E. (nJ) | Leakage (mW) |
|---|---|---|---|---|
| 2D SRAM  | 4.262 | 1.061 | 0.123 | 234.6 |
| 3D SRAM  | 2.132 | 0.633 | 0.089 | 234.6 |
| 2D eDRAM | 1.440 | 0.757 | 0.066 | 30.0 |
| 3D eDRAM | 1.068 | 0.472 | 0.061 | 50.1 |

**Trade-off summary**:
- **Best area density**: 3D eDRAM (1.068 mm²)
- **Best read latency**: 3D eDRAM (0.472 ns)
- **Best write energy**: 3D eDRAM (0.061 nJ)
- **Best leakage**: 2D eDRAM (30.0 mW)
- **3D SRAM** offers a middle ground: better area than 2D SRAM (−50%) with acceptable latency (0.633 ns), but carries the same leakage penalty as 2D SRAM at this node.

**Key takeaway**: At 32 nm, eDRAM-based designs dominate on all active metrics. The main cost is refresh overhead (not captured in these DESTINY metrics) and increased design complexity.

---

### 2.7 TSV Parameter Sensitivity Analysis

**Data summary** (3D SRAM @ 32 nm, baseline: L=0, G=0, R=1.0):

| Parameter | Value=0/1.0 | Value=1/1.2 | Value=2/1.5 | Max Δ Area | Max Δ Latency |
|---|---|---|---|---|---|
| LocalTSVProjection  | 2.132 mm² | 2.250 mm² | 2.139 mm² | **+5.5%** | 0% |
| GlobalTSVProjection | 2.132 mm² | 2.149 mm² | 2.133 mm² | **+0.8%** | 0% |
| TSVRedundancy       | 2.132 mm² | 2.132 mm² | 2.133 mm² | **<0.1%** | 0% |

**Points to make**:
- `LocalTSVProjection` has the largest area impact (+5.5% at level 1), but the effect is non-monotonic (level 2 is nearly the same as level 0) — indicating the optimizer compensated by restructuring the local interconnect.
- `GlobalTSVProjection` and `TSVRedundancy` have negligible impact on total area (<1%).
- **Latency is completely insensitive** to all three TSV parameters at this configuration. This means the critical path does not route through global TSV interconnect at 32 nm under this design configuration.
- **Core finding**: TSV technology assumptions (aggressive vs. conservative projection) have minimal system-level impact on a 2 MB cache at 32 nm. TSV area constitutes a small fraction of total die area at this capacity scale.
- This finding has practical significance: design teams can use conservative TSV projections without significantly penalizing the overall memory system metrics.

---

## 3. Discussion

### 3.1 Effect of 3D Integration
- 3D stacking consistently reduces SRAM area by ~40–50% with negligible latency penalty
- 3D eDRAM shows the opposite trend at 65 nm (area penalty), crossing over to area benefit at finer nodes
- The 3D benefit on latency is limited by the WriteEDP optimization target — other targets (ReadLatency) would likely show a stronger 3D latency advantage

### 3.2 eDRAM vs. SRAM Trade-off
- eDRAM dominates on area, latency, and dynamic energy at 32 nm and below
- eDRAM's leakage advantage is significant (~5–8× lower than SRAM)
- The DESTINY model does not penalize eDRAM for refresh energy — in a real system, refresh overhead should be factored in (especially at higher temperatures or longer retention times)

### 3.3 Scaling Behavior: DESTINY Model at 22 nm
- 22 nm is the smallest node natively supported by DESTINY's interpolation model
- Results at 22 nm represent the model's projection, not a fabricated data point
- All technologies show continued improvement at 22 nm, consistent with physical expectations
- Treat 22 nm results as a **model-projected extrapolation** rather than a validated data point

### 3.4 Limitations
- Single optimization target (WriteEDP) — results would differ under ReadLatency or Area optimization
- eDRAM refresh energy not modeled
- TSV sensitivity sweep performed at one node (32 nm) and one technology (3D SRAM) only
- No variability or yield analysis

---

## 4. Conclusions (Draft)

1. **Node scaling** reduces area for all technologies, with 3D eDRAM achieving the greatest scaling benefit (14.1×, 65→22 nm).
2. **3D stacking** provides consistent ~40–50% area reduction for SRAM but offers limited benefit for eDRAM at larger nodes (65 nm) due to TSV overhead dominance.
3. **3D eDRAM** achieves the best performance on all active metrics at 32 nm (smallest area, lowest latency, lowest write energy), making it attractive for latency-critical applications.
4. **Leakage power** strongly favors eDRAM at all nodes; SRAM leakage is sensitive to optimizer-selected cache organization and can spike non-monotonically.
5. **TSV parameter sensitivity** is low at the 2 MB cache scale: conservative TSV projections increase total area by at most 5.5% and have zero impact on read latency, supporting robust design under TSV technology uncertainty.

---

## 5. Figure List

| Figure | Content | Script |
|---|---|---|
| Fig. 1 | Total Area vs. Process Node (4 technologies) | `fig1_area_vs_node.m` |
| Fig. 2 | Read Latency vs. Process Node | `fig2_read_latency_vs_node.m` |
| Fig. 3 | Write Dynamic Energy vs. Process Node | `fig3_write_energy_vs_node.m` |
| Fig. 4 | Total Leakage Power vs. Process Node | `fig4_leakage_vs_node.m` |
| Fig. 5 | TSV Sensitivity — Total Area | `fig5_tsv_sensitivity_area.m` |
| Fig. 6 | TSV Sensitivity — Read Latency | `fig6_tsv_sensitivity_latency.m` |
| Fig. 7 *(optional)* | Cross-technology trade-off scatter at 32 nm | — |

---

*This outline is the basis for both the poster and the writeup. Sections 2.1–2.4 map directly to the four trend figures; §2.6 maps to the poster's summary panel; §2.7 maps to Fig. 5–6.*
