# DESTINY 新方向范围定义模板

这个模板对应当前第一阶段的三件事：

1. 完成技术范围、节点范围、指标范围定稿
2. 整理 baseline case 和已有数据源
3. 把“哪些参数要随节点缩放”列成表

建议先不要改 DESTINY 内核代码，先把实验定义清楚。

## 1. 项目一句话目标

请先把项目目标压缩成一句话，后面所有范围都围绕这句话服务：

> 使用 DESTINY 作为仿真引擎，比较不同 memory technology 在不同 process node 下的性能变化趋势，并基于已有 scaling trend 外推下一代节点输入，分析 latency、energy、area 等指标如何演化。

## 2. 技术范围定稿

建议第一版只选 2 到 4 个对象，优先选 DESTINY 已有示例支持、你们也容易解释的对象。

推荐第一版范围：

| 类别 | 是否纳入 | DESTINY 对应方式 | 备注 |
|---|---|---|---|
| 2D SRAM | Yes | `sample_SRAM.cell` + `StackedDieCount=1` | 作为传统基线 |
| 3D SRAM | Yes | `sample_SRAM.cell` + `StackedDieCount>1` | 用于比较 2D/3D 差异 |
| 2D eDRAM | Yes | `sample_2D_eDRAM.cell` + `StackedDieCount=1` | 有现成配置 |
| 3D eDRAM | Yes | `sample_3D_eDRAM.cell` + `StackedDieCount>1` | 有现成配置 |
| ReRAM / STT-RAM / PCRAM | Optional | 有 cell 文件，但建议第二阶段再加 | 时间紧时先不扩展 |

建议你们今天就做的决定：

- 是否只做 `SRAM + eDRAM`
- 是否同时比较 `2D vs 3D`
- 是否把 emerging NVM 暂时排除

如果只剩一周，最稳妥的正式范围是：

`SRAM, 3D SRAM, eDRAM, 3D eDRAM`

## 3. 工艺节点范围定稿

原始 DESTINY 文档写的是支持 `22nm` 到 `180nm`，而且主程序里对 node 的内插也只写到了 `22nm`。因此第一版最好不要把“预测节点”设到 `16nm/14nm/7nm`，除非后面单独扩展模型。

推荐节点链：

| 节点角色 | 推荐节点 | 用途 |
|---|---|---|
| 较老已知节点 | 65nm | 可作为起点之一 |
| 中间节点 | 45nm | 做趋势过渡 |
| 较先进已知节点 | 32nm | 做趋势观察 |
| 可作为“下一代预测”的节点 | 22nm | 在不改代码前提下最稳妥 |

建议你们选择以下两种策略之一：

策略 A，最稳妥：

- 研究范围定为 `65nm -> 45nm -> 32nm -> 22nm`
- 把 `22nm` 当作“由前几个节点 trend 外推得到的下一代节点”

策略 B，风险更高：

- 仍然整理 `16nm/14nm` 或更小节点的理论趋势
- 但在报告里说明 DESTINY 原始模型未原生支持 `22nm` 以下，因此只做趋势讨论，不做完整仿真

如果目标是这周把作业交稳，建议选策略 A。

## 4. 指标范围定稿

不要一开始铺太多指标。建议固定 3 个主指标 + 1 到 2 个辅指标。

推荐主指标：

| 指标 | 是否主指标 | DESTINY 可直接取值 | 作用 |
|---|---|---|---|
| Read Latency | Yes | Yes | 比较速度 |
| Write Dynamic Energy | Yes | Yes | 比较每次访问代价 |
| Area | Yes | Yes | 比较密度和成本 |

推荐辅指标：

| 指标 | 是否纳入 | 备注 |
|---|---|---|
| Leakage Power | Yes | 可以辅助解释静态代价 |
| Refresh-related metrics | eDRAM only | 仅用于 eDRAM 分析 |
| Area Efficiency | Optional | 适合做归一化比较 |

建议 poster 和 final report 的核心图只围绕：

- latency trend
- energy trend
- area trend
- 选做：leakage 或 refresh overhead

此外（对应 OH 建议的“修改 TSV 参数做比较”），建议再加 1 张**TSV 敏感性**图：

- 固定一个 3D case（例如 SRAM 3D fine / 4-layer / 65nm）
- 扫 `LocalTSVProjection / GlobalTSVProjection / TSVRedundancy`，以及（如果使用 stage2 可选项）`TSVHopModel`
- 展示 TSV 假设对 TSV breakdown（TSV area / TSV dynamic energy / TSV latency）的影响

## 5. baseline case 表

baseline 的定义要非常明确：哪一种技术、哪一个节点、哪一个配置文件、哪些输入固定不变。

建议先建立一个 baseline 总表：

| Case ID | Technology | 2D/3D | Node | Cell File | Config Base | Capacity | Word Width | Assoc | StackedDieCount | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| B1 | SRAM | 2D | 65nm | `sample_SRAM.cell` | `sample_SRAM_2layer.cfg` | 待定 | 待定 | 待定 | 1 | 传统基线 |
| B2 | SRAM | 3D | 65nm | `sample_SRAM.cell` | `sample_SRAM_2layer.cfg` or 4layer | 待定 | 待定 | 待定 | 2 or 4 | 3D SRAM |
| B3 | eDRAM | 2D | 45nm | `sample_2D_eDRAM.cell` | `sample_2D_eDRAM.cfg` | 待定 | 待定 | 待定 | 1 | 2D eDRAM |
| B4 | eDRAM | 3D | 32nm or 45nm | `sample_3D_eDRAM.cell` | `sample_3D_eDRAM.cfg` | 待定 | 待定 | 待定 | 2 | 3D eDRAM |

建议先统一两件事，避免后面结果不可比：

- 容量尽量统一
- word width 和 associativity 尽量统一

如果文献里有某个技术的固定 benchmark case，就在 `Notes` 列写明“文献基线，不强行统一”。

## 6. 已有数据源表

你们后面会同时用到三类数据：文献数据、DESTINY 配置输入、DESTINY 仿真输出。

先建一张数据源追踪表：

| Source ID | 类型 | 文件/论文 | 用来提供什么 | 是否已拿到 | 可信度备注 |
|---|---|---|---|---|---|
| S1 | DESTINY sample config | `config/sample_SRAM_2layer.cfg` | SRAM baseline 输入 | Yes | 可直接运行 |
| S2 | DESTINY sample config | `config/sample_2D_eDRAM.cfg` | 2D eDRAM baseline 输入 | Yes | 可直接运行 |
| S3 | DESTINY sample config | `config/sample_3D_eDRAM.cfg` | 3D eDRAM baseline 输入 | Yes | 可直接运行 |
| S4 | Paper | 待填 | 提供 scaling trend | 待填 | 写清 node 和 technology |
| S5 | Validation config | `config/validation_SRAM_2MB_4layer_Puttaswamy.cfg` | 3D SRAM 参考案例 | Yes | 适合作为补充参考 |

## 7. scaling 参数表

这是你们这次方法部分最重要的一张表。每个参数都要标明：

- 它是不是 DESTINY 的直接输入
- 它会不会随 process node 变化
- 变化依据是什么
- 变化规则是什么

先用下面这张表开始填：

| 参数 | DESTINY 输入位置 | 是否随节点缩放 | 建议处理 | 数据来源/规则 |
|---|---|---|---|---|
| `ProcessNode` | cfg | Yes | 核心自变量 | 固定为 65/45/32/22 |
| `Capacity` | cfg | Usually No | 先固定，保证可比性 | 除非你们研究容量扩展 |
| `WordWidth` | cfg | Usually No | 先固定 | 保证比较公平 |
| `Associativity` | cfg | Usually No | 先固定 | 保证比较公平 |
| `DeviceRoadmap` | cfg | Maybe | 先固定为 `HP` 或 `LOP` | 避免混入额外变量 |
| `StackedDieCount` | cfg | No | 由 2D/3D 方案决定 | 1 表示 2D，2/4 表示 3D |
| `PartitionGranularity` | cfg | No | 先固定 | 降低变量数量 |
| `LocalTSVProjection` | cfg | Optional | 可做 sensitivity，不一定纳入主实验 | 如果时间够再做 |
| `GlobalTSVProjection` | cfg | Optional | 同上 | 同上 |
| `TSVRedundancy` | cfg | Optional | 先固定为 1.0 | 避免复杂化 |
| `Temperature` | cfg | Usually No | 先固定 | 否则会混入温度影响 |
| `RetentionTime` | cfg, eDRAM only | Maybe | 先固定 | 仅 eDRAM 需要 |
| `ReadVoltage` | `.cell` | Yes if data supports it | 第二阶段再引入 | 需要可靠趋势来源 |
| Cell area related params | `.cell` | Yes if data supports it | 第二阶段再引入 | 需要文献支持 |
| eDRAM cell capacitance | `.cell` | Yes if data supports it | 第二阶段再引入 | 需要文献支持 |

建议第一轮实验时：

- 只缩放 `ProcessNode`
- 固定 `Capacity / WordWidth / Associativity / Temperature / TSVRedundancy`
- 用 `StackedDieCount` 区分 2D 和 3D

等第一轮结果出来以后，再决定是否加入更细的 cell-level scaling。

## 8. 今天就可以完成的定稿版本

如果你们今天想先定一个能执行的版本，建议直接填成下面这样：

### 技术范围

- `SRAM`
- `3D SRAM`
- `eDRAM`
- `3D eDRAM`

### 节点范围

- `65nm`
- `45nm`
- `32nm`
- `22nm`

### 主指标

- `Read Latency`
- `Write Dynamic Energy`
- `Area`

### 辅指标

- `Leakage Power`
- `Refresh Energy / Refresh Power` for eDRAM

### baseline 原则

- 固定容量
- 固定 word width
- 固定 associativity
- 固定 temperature
- 2D 用 `StackedDieCount=1`
- 3D 用 `StackedDieCount=2` 或 `4`

## 9. 交付物清单

你们完成这一阶段后，应该至少产出以下 5 个东西：

1. 一段 3 到 5 句的项目范围说明
2. 一张技术范围表
3. 一张节点范围表
4. 一张 baseline case 表
5. 一张 scaling 参数表

在 final 阶段，为了让 poster/readout 更“像一篇小研究”，建议补齐下面 3 个工程化交付物：

6. 一套可复现的批量运行脚本（cfg 生成 → 运行 → 解析 CSV）
7. 一套自动出图脚本（CSV → SVG 图）
8. 一份 poster 骨架（把图和结论组织进三栏结构）

只要这 5 个东西齐了，你们就能自然进入下一步：

- 批量生成 cfg
- 运行 DESTINY
- 提取结果到 CSV
- 画趋势图
