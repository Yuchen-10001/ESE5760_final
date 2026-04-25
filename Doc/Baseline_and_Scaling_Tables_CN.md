# Baseline 表与 Scaling 参数表

这个文档给出当前项目第一轮实验的正式表格版本，适用于：

- proposal/update 的方法说明
- poster 的实验设定页
- final report 的 methodology 初稿

当前版本采用的统一实验范围如下：

- 技术范围：`SRAM`、`3D SRAM`、`eDRAM`、`3D eDRAM`
- 节点范围：`65nm`、`45nm`、`32nm`、`22nm`
- 主指标：`Read Latency`、`Write Dynamic Energy`、`Area`
- 辅指标：`Leakage Power`，以及 `eDRAM` 的 `Refresh` 相关指标

## 1. Baseline Case Table (已修正为“真实统一 baseline”)

第一轮实验使用统一后的 baseline 假设，目的是让不同技术在同一组控制条件下可比较。

| Case ID | Technology | Dimensionality | Base Config Template | Cell File | Process Nodes | Capacity | Word Width | Associativity | DeviceRoadmap | Temperature | RetentionTime | StackedDieCount | PartitionGranularity | LocalTSVProjection | GlobalTSVProjection | TSVRedundancy | OptimizationTarget | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | SRAM | 2D | `config/final/templates/B1_SRAM_2D_base.cfg` | `config/sample_SRAM.cell` | `65, 45, 32, 22 nm` | `2 MB` | `256 bit` | `1` | `LOP` | `350 K` | `N/A` | `1` | `0` | `0` | `0` | `1.0` | `WriteEDP` | 2D SRAM baseline (normalized) |
| B2 | SRAM | 3D | `config/final/templates/B2_SRAM_3D_coarse_base.cfg` | `config/sample_SRAM.cell` | `65, 45, 32, 22 nm` | `2 MB` | `256 bit` | `1` | `LOP` | `350 K` | `N/A` | `4` | `0` | `0` | `0` | `1.0` | `WriteEDP` | 3D SRAM baseline (4-layer, coarse) |
| B3 | eDRAM | 2D | `config/final/templates/B3_eDRAM_2D_base.cfg` | `config/sample_2D_eDRAM.cell` | `65, 45, 32, 22 nm` | `2 MB` | `256 bit` | `1` | `LOP` | `350 K` | `40 us` | `1` | `0` | `0` | `0` | `1.0` | `WriteEDP` | 2D eDRAM baseline (normalized) |
| B4 | eDRAM | 3D | `config/final/templates/B4_eDRAM_3D_coarse_base.cfg` | `config/sample_3D_eDRAM.cell` | `65, 45, 32, 22 nm` | `2 MB` | `256 bit` | `1` | `LOP` | `350 K` | `40 us` | `4` | `0` | `0` | `0` | `1.0` | `WriteEDP` | 3D eDRAM baseline (4-layer, coarse) |

## 2. Baseline 设定说明

上表采用以下统一规则：

| 项目 | 设定 |
|---|---|
| 容量 | 所有 case 统一为 `2 MB` |
| 字宽 | 所有 case 统一为 `256 bit` |
| 相联度 | 所有 case 统一为 `1` |
| 工艺路线 | 所有 case 统一为 `LOP` |
| 温度 | 所有 case 统一为 `350 K` |
| 2D/3D 区分 | 用 `StackedDieCount` 区分，`1` 表示 2D，`2` 表示 3D |
| TSV 设定 | 第一轮统一固定 `LocalTSVProjection=0`、`GlobalTSVProjection=0`、`TSVRedundancy=1.0`（3D case 才会实际生效） |
| 分区粒度 | 第一轮统一固定 `PartitionGranularity=0` |
| 优化目标 | 第一轮统一固定 `WriteEDP` |

## 3. Scaling Parameter Table

第一轮实验只让最关键的工艺节点参数变化，其他参数保持固定，用来确保趋势分析更清晰。

| Parameter | File Location | Round-1 Setting | Used for 22nm Projection | Fixed or Scaled | Rationale |
|---|---|---|---|---|---|
| `ProcessNode` | `.cfg` | `65, 45, 32, 22` | Yes | `Scaled` | 工艺节点是第一轮实验的核心自变量 |
| `StackedDieCount` | `.cfg` | `1` for 2D, `2` for 3D | No | `Fixed per case` | 用来区分 2D 和 3D 技术 |
| `MemoryCellInputFile` | `.cfg` | 根据技术选择 SRAM 或 eDRAM cell file | No | `Fixed per case` | 用来区分器件技术类型 |
| `Capacity` | `.cfg` | `2 MB` | No | `Fixed` | 保证不同技术之间可比 |
| `WordWidth` | `.cfg` | `256 bit` | No | `Fixed` | 保证带宽接口设定一致 |
| `Associativity` | `.cfg` | `1` | No | `Fixed` | 降低结构差异对比较结果的影响 |
| `DeviceRoadmap` | `.cfg` | `LOP` | No | `Fixed` | 避免不同路线引入额外变量 |
| `Temperature` | `.cfg` | `350 K` | No | `Fixed` | 避免温度影响趋势解释 |
| `RetentionTime` | `.cfg`, eDRAM only | `40 us` | No | `Fixed` | 第一轮先不研究 retention scaling |
| `PartitionGranularity` | `.cfg` | `0` | No | `Fixed` | 降低 3D 组织方式带来的额外复杂性 |
| `LocalTSVProjection` | `.cfg` | `0` | No | `Fixed` | 第一轮先不做 TSV sensitivity |
| `GlobalTSVProjection` | `.cfg` | `0` | No | `Fixed` | 第一轮先不做 TSV sensitivity |
| `TSVRedundancy` | `.cfg` | `1.0` | No | `Fixed` | 避免 yield/redundancy 影响主结论 |
| `ReadVoltage` | `.cell` | 保持原 cell 文件设定 | Optional later | `Fixed in Round 1` | 后续可在第二轮加入 cell-level scaling |
| `CellArea` related parameters | `.cell` | 保持原 cell 文件设定 | Optional later | `Fixed in Round 1` | 第一轮先观察 process node 趋势 |
| `SRAM transistor width` related parameters | `.cell` | 保持原 cell 文件设定 | Optional later | `Fixed in Round 1` | 第一轮先不改晶体管尺寸 |
| `eDRAM cell capacitance` | `.cell` | 保持原 cell 文件设定 | Optional later | `Fixed in Round 1` | 第一轮先不引入更细粒度器件缩放 |

## 4. 报告中可直接使用的文字

下面这段可以直接放到 proposal、check-in 或 final report 的 methods 部分：

> In the first round of experiments, we normalize the baseline assumptions across all technologies by fixing capacity, word width, associativity, roadmap, temperature, and TSV-related settings. Process node is treated as the primary scaling variable, while the 2D/3D distinction is modeled through stacked die count and the technology distinction is modeled through the selected memory cell input file. We evaluate SRAM, 3D SRAM, eDRAM, and 3D eDRAM across 65nm, 45nm, 32nm, and 22nm, and treat 22nm as the projected next-node evaluation point supported by the original DESTINY implementation.

## 5. 已有配置来源

下面这些文件是当前表格的直接来源：

- `config/final/templates/B1_SRAM_2D_base.cfg`
- `config/final/templates/B2_SRAM_3D_coarse_base.cfg`
- `config/final/templates/B3_eDRAM_2D_base.cfg`
- `config/final/templates/B4_eDRAM_3D_coarse_base.cfg`
- `config/final/templates/TSV_SRAM_3D_fine_sweep_base.cfg`
- `config/sample_SRAM.cell`
- `config/sample_2D_eDRAM.cell`
- `config/sample_3D_eDRAM.cell`

## 6. 下一步建议

表格确定后，下一步可以直接进入：

1. 生成项目专用 cfg 模板（已完成：见 `config/final/templates`）
2. 自动生成 `65/45/32/22nm` 节点 cfg（脚本：`scripts/final_generate_configs.ps1`）
3. 批量运行 DESTINY 并保存 raw log（脚本：`scripts/final_run.ps1`）
4. 解析并汇总核心指标到 CSV（脚本：`scripts/final_parse.ps1`）
5. 从 CSV 生成 poster 级 SVG 图（脚本：`scripts/final_make_figures.ps1`）
