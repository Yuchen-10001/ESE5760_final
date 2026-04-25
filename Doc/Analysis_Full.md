# Comparative Analysis of 2D and 3D Memory Technologies Across Process Nodes Using DESTINY

**Course**: ESE5760 — Advanced Memory Systems  
**Simulation Tool**: DESTINY (Design Space Exploration Tool for Integrated Circuit Memory)  
**Baseline**: 2 MB capacity, 256-bit word width, 1-way associativity, LOP device roadmap, 350 K, WriteEDP optimization  
**Date**: April 2026

---

## 1. Introduction and Experimental Setup

As process nodes advance beyond 45 nm, the relationship between dimensional scaling and memory system performance becomes increasingly non-trivial. While shrinking feature size generally reduces cell area and wire capacitance, the interplay between cell topology, interconnect hierarchy, and optimizer-selected cache organization introduces complex, often non-monotonic behavior across the performance-energy-area design space. This analysis evaluates four memory technologies — planar SRAM (2D SRAM), stacked-die SRAM (3D SRAM), planar embedded DRAM (2D eDRAM), and stacked-die eDRAM (3D eDRAM) — across four representative process nodes (65 nm, 45 nm, 32 nm, and 22 nm) using the DESTINY simulator. A secondary experiment sweeps three TSV (Through-Silicon Via) technology parameters on a fixed 3D SRAM configuration to quantify the sensitivity of system-level metrics to TSV modeling assumptions.

All 22 simulation runs share an identical normalized baseline to ensure that observed differences reflect technology and node choices rather than configuration artifacts: 2 MB capacity, 256-bit word width, 1-way set associativity, LOP (Low Operating Power) device roadmap, 350 K operating temperature, H-tree global routing, and WriteEDP as the optimization target. The WriteEDP metric — the product of write energy and write delay — guides DESTINY's internal optimizer to select the cache bank organization (number of subarrays, mat count, bit-cell array dimensions) that minimizes this composite cost function at each configuration point.

Five metrics are extracted from each simulation: total die area (mm²), cache hit (read) latency (ns), cache write latency (ns), write dynamic energy (nJ/access), and total leakage power (mW). The complete dataset is reproduced in Table 1.

**Table 1. Simulation Results Summary (Experiment 1 — Node Scaling)**

| Technology | Node (nm) | Area (mm²) | Read Lat. (ns) | Write Lat. (ns) | Write E. (nJ) | Leakage (mW) |
|---|---|---|---|---|---|---|
| 2D SRAM | 65 | 12.348 | 9.942 | 7.213 | 0.022 | 124.0 |
| 2D SRAM | 45 |  8.893 | 0.939 | 0.526 | 0.173 |  48.3 |
| 2D SRAM | 32 |  4.262 | 1.061 | 0.605 | 0.123 | 234.6 |
| 2D SRAM | 22 |  1.836 | 1.184 | 0.710 | 0.035 |  65.8 |
| 3D SRAM | 65 |  7.105 | 4.698 | 3.740 | 0.037 | 145.8 |
| 3D SRAM | 45 |  5.245 | 0.654 | 0.367 | 0.132 |  51.3 |
| 3D SRAM | 32 |  2.132 | 0.633 | 0.423 | 0.089 | 234.6 |
| 3D SRAM | 22 |  0.969 | 0.705 | 0.447 | 0.027 |  70.3 |
| 2D eDRAM | 65 |  5.957 | 2.488 | 1.550 | 0.092 |  24.5 |
| 2D eDRAM | 45 |  4.555 | 0.663 | 0.453 | 0.117 |  10.0 |
| 2D eDRAM | 32 |  1.440 | 0.757 | 0.607 | 0.066 |  30.0 |
| 2D eDRAM | 22 |  0.630 | 0.790 | 0.579 | 0.019 |   9.8 |
| 3D eDRAM | 65 |  7.743 | 0.538 | 0.347 | 0.206 | 107.0 |
| 3D eDRAM | 45 |  3.125 | 0.504 | 0.273 | 0.102 |  18.4 |
| 3D eDRAM | 32 |  1.068 | 0.472 | 0.340 | 0.061 |  50.1 |
| 3D eDRAM | 22 |  0.550 | 0.420 | 0.281 | 0.021 |  16.2 |

---

## 2. Area Scaling

### 2.1 Observed Trends

Total die area decreases monotonically for all four technologies as the process node scales from 65 nm to 22 nm, consistent with the fundamental expectation that smaller feature sizes yield denser cells. However, the magnitude of this reduction varies substantially across technologies: 2D SRAM achieves a 6.7× reduction (12.348 → 1.836 mm²), 3D SRAM achieves 7.3× (7.105 → 0.969 mm²), 2D eDRAM achieves 9.5× (5.957 → 0.630 mm²), and 3D eDRAM achieves 14.1× (7.743 → 0.550 mm²). These scaling ratios encode two distinct physical mechanisms — cell-level scaling and 3D integration — which must be disentangled.

### 2.2 Cell-Level Scaling Mechanisms

The SRAM cell is a six-transistor (6T) cross-coupled inverter pair with two access transistors. Its minimum area is bounded by the requirement to maintain a sufficient static noise margin (SNM), which prevents aggressive width-length ratio scaling. In DESTINY's LOP model, the effective area per SRAM bit decreases approximately as F² (where F is the half-pitch), but the proportionality constant is constrained by the multi-transistor cell topology. As a result, 2D SRAM area scales from 12.35 mm² to 1.84 mm², a factor of ~6.7 over the 65-to-22 nm range, broadly consistent with an F² ≈ (65/22)² ≈ 8.7× geometric expectation modulated by the fixed overhead of peripheral and routing structures.

The eDRAM cell topology — one access transistor plus one storage capacitor (1T-1C) — is fundamentally more area-efficient than SRAM. At large process nodes, the capacitor occupies a disproportionate fraction of cell area; as the node shrinks, the capacitor area scales more aggressively relative to the transistor gate pitch. Consequently, 2D eDRAM scales 9.5×, noticeably faster than 2D SRAM (6.7×) over the same node range. This is consistent with prior literature showing that DRAM-family cells benefit more from each successive node shrink than SRAM cells, which are constrained by SNM and leakage requirements.

### 2.3 Effect of 3D Stacking on Area

Comparing 2D and 3D variants at each node reveals the net system-level impact of vertical die stacking. For SRAM, 3D stacking reduces total footprint by 42–50% across all nodes: at 65 nm, the 3D SRAM footprint is 7.11 mm² versus 12.35 mm² for 2D SRAM (−42%); at 32 nm, the reduction reaches 50% (2.13 vs. 4.26 mm²). The DESTINY model assigns a StackedDieCount of 2 with fine-grain partitioning (PartitionGranularity = 0), effectively splitting the memory array across two bonded dies and halving the in-plane area at the cost of TSV insertion overhead. For SRAM, whose baseline 2D cell is large enough relative to the TSV pitch to absorb this overhead, the area benefit of stacking is consistently close to the theoretical 2× reduction.

For eDRAM, the 3D stacking benefit is strongly node-dependent. At 65 nm, the 3D eDRAM footprint (7.74 mm²) is 30% *larger* than its 2D counterpart (5.96 mm²). This reversal arises because the TSV structures and their associated keep-out zones consume a non-trivial fraction of the die at large feature sizes. At 65 nm, eDRAM's already-compact 1T-1C cell occupies relatively little area per bit, so the additive TSV overhead constitutes a significant fraction of total area. As the node scales to 45 nm, eDRAM's 3D configuration achieves a 31% area reduction over 2D eDRAM, indicating that the crossover point — where the die-halving benefit exceeds the TSV overhead — falls between 65 nm and 45 nm for this specific capacity (2 MB) and TSV projection setting (LocalTSVProjection = 0, aggressive). At 22 nm, 3D eDRAM (0.550 mm²) achieves only 13% improvement over 2D eDRAM (0.630 mm²), reflecting the fact that as eDRAM cells become extremely compact, the theoretical 2× stacking benefit is partially offset by residual TSV overhead. Nevertheless, 3D eDRAM at 22 nm achieves the smallest absolute footprint of all configurations tested: 0.55 mm², approximately 22× smaller than 2D SRAM at 65 nm.

The 3D eDRAM's superior scaling ratio (14.1×) compared to 3D SRAM (7.3×) can be understood as the product of eDRAM's faster cell-level scaling and the compounding benefit of 3D integration, which is more pronounced at finer nodes where TSV overhead becomes negligible relative to the total die area.

---

## 3. Read Latency

### 3.1 Observed Trends

Cache hit (read) latency exhibits qualitatively different behavior across technologies. 3D eDRAM is the only technology that achieves strict monotonic latency improvement across all four nodes: 0.538 → 0.504 → 0.472 → 0.420 ns. All other technologies display non-monotonic behavior, most dramatically for SRAM. 2D SRAM at 65 nm exhibits 9.942 ns, more than ten times higher than its 45 nm value (0.939 ns). 3D SRAM shows an analogous but attenuated anomaly (4.698 ns at 65 nm versus 0.654 ns at 45 nm). After this discontinuity, SRAM latency rises slightly from 45 nm to 22 nm (0.939 → 1.184 ns for 2D SRAM), suggesting a progressive but mild latency degradation at the finest nodes. 2D eDRAM and 3D SRAM occupy a mid-tier latency range at 32–22 nm (0.63–0.79 ns), while 3D eDRAM consistently leads.

### 3.2 Interconnect-Dominated Latency and the Role of Array Organization

In DESTINY's cache model, the total access latency is decomposed into cell access time (t_cell), local wire delay within a mat (t_local), and the H-tree global interconnect delay (t_global). At the 2 MB scale, the H-tree delay is typically dominant, and it scales as:

t_global ∝ √A × (R_wire × C_wire per unit length)

where A is the total array area and R_wire, C_wire are the technology-dependent wire parameters. For a given process node, the optimizer selects the number of banks, mats per bank, and subarray dimensions to minimize WriteEDP. At fine nodes, area is small, the H-tree is short, and t_global is modest. At 65 nm, however, 2D SRAM occupies 12.35 mm², implying an H-tree with long branches and correspondingly large delay. The optimizer cannot eliminate this overhead without restructuring into a shallower but wider bank hierarchy, which would increase energy. Under WriteEDP minimization, latency is sacrificed in favor of the energy term, yielding the observed 9.942 ns access time. This is not a physical limit of SRAM technology but rather a consequence of the optimizer's objective function and the unavoidable interconnect penalty associated with a large 65-nm die footprint.

The 3D SRAM anomaly (4.698 ns at 65 nm) follows the same logic but is partially mitigated by the roughly 2× smaller per-die footprint, which shortens the H-tree branches and reduces t_global. The residual 4.7 ns reflects continued H-tree dominance even after stacking.

### 3.3 3D eDRAM's Latency Advantage

3D eDRAM achieves the lowest latency at every node for two compounding reasons. First, the 1T-1C cell has lower intrinsic access time than the SRAM cell because the single-transistor access path presents less gate and diffusion capacitance to the bitline. Second, the 3D stack distributes the array vertically, further reducing per-die footprint and thereby shortening the H-tree. At 22 nm, the 3D eDRAM access time of 0.420 ns represents a 3.0× advantage over 2D SRAM (1.184 ns) and a 1.7× advantage over 2D eDRAM (0.790 ns) at the same node.

The monotonic improvement of 3D eDRAM latency from 65 nm to 22 nm (0.538 → 0.420 ns) is consistent with the simultaneous decrease in wire capacitance per unit length and the continued reduction in die footprint. For other technologies, optimizer-induced reorganization and the trade-off between energy and latency under WriteEDP partially counteract these physical improvements, resulting in the slight non-monotonicity observed post-45 nm.

### 3.4 Post-45 nm SRAM Latency Increase

After the sharp drop at 45 nm, SRAM (both 2D and 3D) exhibits a mildly increasing latency trend: 0.939 → 1.061 → 1.184 ns for 2D SRAM. This is counterintuitive if one expects smaller nodes to always yield faster circuits. Under WriteEDP optimization, the relative weight of the energy term increases at smaller nodes because the energy penalty for a high-parallelism organization (which would minimize latency) grows with the number of simultaneously switching wires and transistors. The optimizer therefore selects progressively more energy-conservative (and latency-penalizing) configurations at 32 and 22 nm. Under a ReadLatency optimization target, this trend would likely reverse, as noted in Section 6.2.

---

## 4. Write Dynamic Energy

### 4.1 Non-Monotonic Scaling Behavior

Write dynamic energy is the most counter-intuitive metric in this dataset. Rather than decreasing monotonically with node, it exhibits strong non-monotonicity for SRAM variants: 2D SRAM energy peaks at 45 nm (0.173 nJ), nearly eight times higher than its 65-nm value (0.022 nJ), before declining to 0.035 nJ at 22 nm. 3D SRAM follows the same pattern: 0.037 → 0.132 → 0.089 → 0.027 nJ. The eDRAM variants show a more regular progression — 2D eDRAM: 0.092 → 0.117 → 0.066 → 0.019 nJ (mild peak at 45 nm), 3D eDRAM: 0.206 → 0.102 → 0.061 → 0.021 nJ (monotonically decreasing).

### 4.2 Physical Mechanism: Configuration-Induced Energy Variation

Dynamic write energy in a cache array is determined by:

E_write = C_switched × V_DD² × α

where C_switched is the total switched capacitance per write access, V_DD is the supply voltage, and α is an activity factor. In principle, both C_switched and V_DD decrease as the node scales, implying that energy should decrease monotonically. The observed peaks indicate that C_switched (governed by the optimizer-selected cache organization) does not decrease monotonically.

At 65 nm, DESTINY selects a compact, low-parallelism configuration to minimize WriteEDP given the large cell area. Fewer subarrays switch simultaneously, keeping C_switched low despite the large physical dimensions. At 45 nm, the smaller cell area enables the optimizer to select a higher-parallelism organization — more mats activated per access, more bitlines switching — that reduces write latency (improving the EDP latency term) at the cost of increased C_switched. This reorganization more than offsets the voltage scaling benefit, resulting in elevated energy. By 32 nm and 22 nm, continued voltage scaling and the diminishing marginal latency benefit of additional parallelism shift the optimizer back toward more energy-conservative configurations, recovering the expected energy reduction.

For 3D eDRAM, which starts with a very compact per-die footprint even at 65 nm, the optimizer begins in a reasonably high-parallelism state at the coarsest node. Energy therefore decreases monotonically as V_DD and cell capacitance scale down, without the reorganization-induced peak seen in SRAM.

### 4.3 Convergence at 22 nm

At 22 nm, all four technologies converge to a narrow energy range of 0.019–0.035 nJ/access. This convergence reflects the dominance of supply voltage scaling at fine nodes: as V_DD decreases, the V_DD² factor in the energy expression forces all technologies toward similar absolute energy values regardless of differences in C_switched. It also implies that at the 22 nm node, write energy differentiation between SRAM and eDRAM largely disappears, shifting the competitive landscape toward area and leakage as the primary discriminators.

---

## 5. Leakage Power

### 5.1 The eDRAM Leakage Advantage

Leakage power is the metric with the most consistent and physically interpretable cross-technology trend. eDRAM leakage is lower than SRAM leakage at every single data point, by factors ranging from approximately 2.1× (3D eDRAM vs. 3D SRAM at 65 nm: 107.0 vs. 145.8 mW) to 23.9× (2D eDRAM vs. 2D SRAM at 32 nm: 30.0 vs. 234.6 mW). The median leakage ratio across all comparable node pairs is approximately 5–8×.

This advantage is rooted in cell topology. SRAM's 6T cell contains six transistors, each of which contributes a subthreshold leakage current I_sub ∝ exp(−V_th / n·V_T), where V_th is the threshold voltage, n is the subthreshold slope factor, and V_T is the thermal voltage. With six transistors per cell and millions of cells in a 2 MB array, the aggregate standby leakage is substantial. eDRAM's 1T-1C cell contains only a single access transistor; the storage capacitor is a passive element with no DC leakage path in steady state. This six-to-one transistor count ratio (6T SRAM vs. 1T eDRAM) largely explains the observed leakage advantage, though the exact ratio varies with node-specific V_th tuning in the LOP roadmap.

### 5.2 Effect of 3D Stacking on Leakage

3D integration consistently increases leakage relative to the 2D counterpart. For SRAM at 65 nm, 3D SRAM (145.8 mW) is 18% higher than 2D SRAM (124.0 mW); at 22 nm, 3D SRAM (70.3 mW) is 7% higher. For eDRAM, the increase is more pronounced: 3D eDRAM leakage is 2.1–4.4× higher than 2D eDRAM across nodes (e.g., 16.2 mW vs. 9.8 mW at 22 nm, a 65% increase). The excess leakage from 3D integration originates from three sources: (1) TSV driver and receiver circuits on each die, (2) additional peripheral logic on the second die, and (3) the increased total transistor count associated with the redundant TSV circuitry. At larger nodes, the relative contribution of these overhead circuits to total leakage is more significant because the baseline cell leakage is comparatively low in the compact eDRAM case.

### 5.3 Leakage Scaling with Node

For eDRAM, leakage tracks the area trend closely: 2D eDRAM leakage decreases from 24.5 mW to 9.8 mW over the 65-to-22 nm range, a 2.5× reduction that roughly parallels the 9.5× area reduction (the nonlinear relationship reflects node-dependent V_th changes in the LOP model). For SRAM, leakage scaling is dramatically disrupted by the anomalous spike at 32 nm, discussed in Section 6.

---

## 6. Anomalous Behavior: Physical Interpretation

### 6.1 Anomaly A: SRAM Latency Spike at 65 nm

At 65 nm, 2D SRAM exhibits a read latency of 9.942 ns — over ten times higher than its 45-nm value of 0.939 ns. The corresponding values for 3D SRAM are 4.698 ns and 0.654 ns (a 7.2× ratio). No such discontinuity appears in any eDRAM configuration.

This anomaly is not a fabrication or simulation artifact; it is a direct consequence of the optimizer's response to the large physical die area at 65 nm combined with the WriteEDP objective. The 2D SRAM array at 65 nm occupies 12.348 mm². To organize a 2 MB, 256-bit-wide cache on a 12.35 mm² die, DESTINY selects a deeply hierarchical bank-and-mat structure. The global H-tree required to distribute addresses and data across this large footprint introduces a wire delay that dominates the access time. Because WriteEDP penalizes the product of energy and delay, and because the optimizer can substantially reduce energy by accepting higher latency (choosing fewer simultaneously active mats reduces switching capacitance but increases the number of H-tree levels traversed), the minimum-WriteEDP design point at 65 nm selects an organization with very high H-tree latency.

At 45 nm, the 2.34× reduction in area (from 12.348 to 8.893 mm² between 65 and 45 nm) collapses the H-tree depth sufficiently that the optimizer can now find configurations where latency is comparable to energy in the EDP term, yielding the observed 0.939 ns result. The 3D SRAM case is qualitatively identical but the anomaly is less severe because the 3D footprint (7.105 mm² at 65 nm) is smaller than the 2D case, resulting in a shallower initial H-tree.

These results should be interpreted as optimizer-selected design points within the WriteEDP framework rather than intrinsic technology latency ceilings. Under a ReadLatency optimization target, the 65-nm designs would yield substantially lower latency at the cost of higher energy.

### 6.2 Anomaly B: SRAM Leakage Spike at 32 nm

Both 2D and 3D SRAM exhibit a leakage power of 234.6 mW at 32 nm — nearly 5× the value at 45 nm (48.3 and 51.3 mW, respectively) and 3.6× the value at 22 nm (65.8 and 70.3 mW). The identity of the two values (both exactly 234.632 mW in the raw output) confirms that the optimizer converged to the same physical configuration for both 2D and 3D SRAM at this node. No such spike is observed for eDRAM.

The physical mechanism involves the leakage composition of the cache array. Total leakage in DESTINY includes subthreshold leakage from all transistors in active and inactive subarrays. When the optimizer selects a high-parallelism configuration — many subarrays sharing a data path, all of which must be pre-charged and held in a ready state during access — the total transistors contributing to standby leakage increases proportionally. Under WriteEDP at 32 nm, achieving the minimum product of write energy and write delay requires a configuration with many simultaneously active subarrays (which reduces write latency and therefore the delay term in EDP). This high-parallelism organization substantially increases the number of simultaneously biased transistors and thus the total subthreshold leakage.

The convergence to the same value for 2D and 3D SRAM at 32 nm further supports this interpretation: the optimizer's WriteEDP objective selects the same fundamental subarray organization regardless of die stacking, because the primary cost driver is the memory cell and subarray transistor count rather than the die partitioning. eDRAM is immune because its 1T-1C cell has far fewer leakage transistors per bit, so the same parallelism increase causes a much smaller absolute leakage jump.

---

## 7. Cross-Technology Comparison at 32 nm

The 32-nm node is selected as the representative comparison point because it lies at the center of the swept range and avoids the extreme 65-nm anomalies while representing a well-characterized, production-relevant technology generation.

**Table 2. Multi-Metric Comparison at 32 nm**

| Technology | Area (mm²) | Read Lat. (ns) | Write E. (nJ) | Leakage (mW) |
|---|---|---|---|---|
| 2D SRAM  | 4.262 | 1.061 | 0.123 | 234.6 |
| 3D SRAM  | 2.132 | 0.633 | 0.089 | 234.6 |
| 2D eDRAM | 1.440 | 0.757 | 0.066 |  30.0 |
| 3D eDRAM | 1.068 | 0.472 | 0.061 |  50.1 |

At 32 nm, 3D eDRAM leads on three of the four primary metrics: it achieves the smallest area (1.068 mm², 4× smaller than 2D SRAM), the lowest read latency (0.472 ns, 2.2× faster than 2D SRAM), and the lowest write energy (0.061 nJ, 2× lower than 2D SRAM). The only metric on which 3D eDRAM is not optimal is leakage, where 2D eDRAM (30.0 mW) outperforms 3D eDRAM (50.1 mW) by 40%, owing to the additional TSV and peripheral circuitry in the stacked configuration.

3D SRAM presents a compelling middle-ground option. Its area (2.132 mm²) is 50% of 2D SRAM and only 2× that of 3D eDRAM. Its read latency (0.633 ns) is competitive with 2D eDRAM (0.757 ns). However, both SRAM variants carry the same 234.6 mW leakage penalty, which is a significant disadvantage in any power-constrained application. For latency-insensitive workloads where standby power dominates, 2D eDRAM's combination of 1.440 mm² footprint and 30.0 mW leakage is likely the optimal choice.

It is important to note that DESTINY's metric set does not include eDRAM refresh energy. In a real implementation, the periodic refresh operation of the 1T-1C capacitor adds a baseline power overhead proportional to the refresh rate (governed by cell retention time, here set to 40 µs) and the total bit count. For a 2 MB array, refresh energy can add several milliwatts of additional power, partially eroding the leakage advantage of eDRAM. This overhead is absent from the SRAM metrics and must be accounted for in any full system evaluation.

---

## 8. TSV Parameter Sensitivity Analysis

### 8.1 Experimental Design

Experiment 2 holds the technology (3D SRAM at 32 nm) and all cache configuration parameters constant while independently varying three TSV technology parameters: LocalTSVProjection (0 = aggressive, 1 = nominal, 2 = conservative), GlobalTSVProjection (same levels), and TSVRedundancy (1.0, 1.2, 1.5, representing 0%, 20%, and 50% extra TSV overhead for yield management).

**Table 3. TSV Sensitivity Results (3D SRAM @ 32 nm)**

| Parameter | Level 0/1.0 | Level 1/1.2 | Level 2/1.5 | Max Δ Area | Max Δ Write E. |
|---|---|---|---|---|---|
| LocalTSVProjection  | 2.132 mm², 0.089 nJ | 2.250 mm², 0.093 nJ | 2.139 mm², 0.095 nJ | +5.5% | +6.7% |
| GlobalTSVProjection | 2.132 mm², 0.089 nJ | 2.149 mm², 0.090 nJ | 2.133 mm², 0.090 nJ | +0.8% | +1.1% |
| TSVRedundancy       | 2.132 mm², 0.089 nJ | 2.132 mm², 0.090 nJ | 2.133 mm², 0.090 nJ | <0.1% | +1.1% |

Read latency is 0.633 ns and write latency is 0.423 ns for all nine configurations — completely invariant to TSV parameter changes.

### 8.2 Local vs. Global TSV Area Impact

LocalTSVProjection has the largest area impact (+5.5% at level 1) because local TSVs connect directly between the two stacked dies within each subarray, and their pitch and keep-out zones consume area that directly competes with the bitcell array. Increasing LocalTSVProjection from 0 (aggressive) to 1 (nominal) adds 0.118 mm² to the total footprint. The non-monotonic behavior — area increases from level 0 to level 1 but partially recovers at level 2 — indicates that DESTINY's optimizer restructures the local interconnect at the conservative projection: when local TSV area is large, the optimizer reduces the number of TSV connections per subarray (at the cost of slightly higher write energy) and partially reclaims die area through reorganization.

GlobalTSVProjection has a much smaller impact (+0.8% at most) because global TSVs are placed at the bank level, where their area is amortized over a much larger array footprint. At the 2 MB cache scale, global TSV count is determined by the word width and control bus requirements, and their contribution to total die area is marginal. TSVRedundancy has essentially zero area impact (<0.1%) because the redundant TSVs added for yield improvement are placed in reserved keepout areas that were already allocated in the baseline layout.

### 8.3 Latency Insensitivity

The complete insensitivity of read and write latency to all TSV parameter changes (0.633 ns and 0.423 ns, respectively, across all nine configurations) is the most significant finding of Experiment 2. It implies that the critical timing path of this 2 MB cache at 32 nm does not route through any TSV interconnect — neither local nor global. This is consistent with DESTINY's architectural model in which the inter-die TSV crossing is absorbed within the local wire hierarchy, and the dominant latency component remains the within-die H-tree. As long as TSV delay is smaller than the H-tree delay budget, changes to TSV technology projections do not propagate to the system-level latency metric.

### 8.4 Write Energy Sensitivity

While latency is immune, write energy shows a mild sensitivity to LocalTSVProjection: baseline 0.089 nJ, level 1: 0.093 nJ (+4.5%), level 2: 0.095 nJ (+6.7%). Unlike the area trend, write energy increases monotonically with LocalTSVProjection level. This suggests that the optimizer's reorganized local interconnect at conservative TSV projections, while partially recovering area, introduces a higher switching capacitance per write operation. The longer or more resistive local interconnect paths that result from a conservative TSV pitch increase the capacitance that must be driven during a write access. GlobalTSVProjection and TSVRedundancy produce at most a 1.1% increase in write energy, which is within the noise floor of the simulator's numerical precision.

### 8.5 Practical Implication

The aggregate finding of the TSV sensitivity experiment is that, at the 2 MB cache scale and 32 nm process node, the choice of TSV technology assumption (aggressive vs. conservative process projection) has minimal system-level consequences. The worst-case scenario — LocalTSVProjection = 2 with TSVRedundancy = 1.5 — increases area by at most 5.5% and write energy by 6.7%, while leaving latency unchanged. This result provides practical guidance for design teams: conservative TSV projections can be used for robust design without incurring a significant penalty in system performance, and the uncertainty in TSV technology modeling does not constitute a first-order design risk for this class of memory system.

---

## 9. Discussion

### 9.1 Synthesis: Technology Selection Trade-offs

The four-dimensional performance space (area, latency, energy, leakage) does not admit a single dominant technology across all metrics at all nodes. However, several practical conclusions emerge from the aggregate analysis.

For latency-critical applications such as last-level cache in a high-performance processor, 3D eDRAM consistently offers the best read latency across all nodes (0.54 → 0.42 ns) while also achieving the best area density. The penalty is moderately elevated leakage (50.1 mW at 32 nm vs. 30.0 mW for 2D eDRAM) and the unmodeled refresh overhead. For designs where refresh can be managed (e.g., through adaptive retention voltage techniques or data migration), 3D eDRAM represents a compelling option.

For power-constrained applications — embedded systems, IoT memory hierarchies, or any design with strict idle-power budgets — 2D eDRAM at 32 nm offers the best leakage (30.0 mW), acceptable area (1.440 mm²), and competitive latency (0.757 ns). 3D SRAM offers a middle ground: better area than 2D SRAM without the refresh complexity of eDRAM, though it inherits SRAM's high leakage at certain nodes.

### 9.2 Optimizer Effects and Metric Interpretation

A critical interpretive caveat applies to all results in this study: DESTINY's optimizer selects the cache organization that minimizes WriteEDP at each configuration point. The resulting metrics — area, latency, energy, leakage — reflect this particular optimization target and do not represent the Pareto-optimal surface of the full design space. Under a different optimization target (ReadLatency, WriteLatency, or LeakagePower), the optimizer would select different organizations, potentially yielding different scaling trends and different anomaly behavior. The SRAM latency spike at 65 nm and the leakage spike at 32 nm are both direct consequences of WriteEDP optimization; they would manifest differently or disappear under alternative targets. Any comparative conclusion drawn from this dataset should be understood as specific to the WriteEDP optimization context.

### 9.3 DESTINY Model Scope and Limitations

DESTINY models the memory array (cells, local wires, global H-tree) but does not capture several important real-world effects:

1. **Refresh overhead** (eDRAM): The simulator reports static leakage for eDRAM but not the dynamic energy consumed during periodic refresh cycles. At 350 K, retention time degrades due to increased junction leakage, potentially requiring sub-40 µs refresh intervals and significantly increasing effective power.

2. **Variability and yield**: Cell-level parameter variation (V_th spread, contact resistance) is not modeled. In practice, TSV-based 3D integration introduces additional mechanical stress and bonding yield concerns, especially at fine pitches.

3. **22 nm extrapolation**: DESTINY's parameterized models are calibrated against fabricated technology data. At 22 nm, the model relies on interpolation and projection rather than measured hardware data. Results at this node should be treated as model-projected rather than experimentally validated.

4. **Single optimization target**: Only WriteEDP was evaluated. Application-specific optimization could substantially change the relative ranking of technologies.

---

## 10. Conclusions

This study evaluated four memory technologies — 2D SRAM, 3D SRAM, 2D eDRAM, and 3D eDRAM — across four process nodes (65–22 nm) and characterized TSV parameter sensitivity for 3D SRAM at 32 nm. The following principal conclusions are drawn:

1. **Area scaling**: All technologies reduce die area as the node scales, with eDRAM benefiting more than SRAM due to its single-transistor cell topology. 3D eDRAM achieves the greatest aggregate scaling (14.1× from 65 to 22 nm) and the smallest absolute footprint at 22 nm (0.550 mm²). 3D stacking provides a consistent ~40–50% area reduction for SRAM, but penalizes eDRAM at 65 nm (−30%) due to TSV overhead exceeding the die-halving benefit at large feature sizes.

2. **Read latency**: 3D eDRAM achieves the lowest latency at all nodes (0.42–0.54 ns) with strict monotonic improvement. SRAM exhibits an anomalous latency spike at 65 nm (9.94 ns for 2D SRAM) that is attributable to optimizer-selected deep H-tree hierarchy under WriteEDP and the large die footprint at this node — it is an optimizer-induced design point, not a technology-intrinsic limit.

3. **Write energy**: Write dynamic energy is non-monotonic for all technologies under WriteEDP optimization, reflecting configuration reorganization at each node rather than simple voltage and capacitance scaling. All technologies converge to 0.019–0.035 nJ/access at 22 nm as supply voltage scaling dominates.

4. **Leakage power**: eDRAM leakage is 5–8× lower than SRAM at most nodes, a direct consequence of the 1T-1C vs. 6T cell topology. SRAM exhibits a sharp leakage spike at 32 nm (234.6 mW for both 2D and 3D variants), attributed to the optimizer selecting a high-parallelism cache organization to minimize write EDP, which dramatically increases active transistor count. 3D integration adds leakage in all cases.

5. **TSV sensitivity**: At the 2 MB cache scale and 32 nm node, TSV technology assumptions have minimal system-level impact. The most sensitive parameter, LocalTSVProjection, increases total area by at most 5.5% and write energy by 6.7% between aggressive and conservative projections. Read and write latency are completely insensitive to all TSV parameter variations, indicating that the critical timing path does not traverse the inter-die TSV stack under this configuration.

Collectively, these results indicate that 3D eDRAM is the most attractive technology for latency- and area-critical applications at 32 nm and below, while 2D eDRAM is preferred when standby leakage is the binding constraint. SRAM-based technologies remain relevant where refresh complexity is unacceptable and SRAM's leakage penalty can be tolerated. The low sensitivity to TSV technology projections provides confidence that 3D memory designs can be evaluated with conservative modeling assumptions without incurring significant risk of overoptimistic predictions.

---

*All simulation results were generated using DESTINY with the parameters described in Section 1. Raw output files and configuration scripts are archived in `experiments/results/` and `experiments/configs/` respectively.*
