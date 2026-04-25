# TSV 阶段 2：公式审计表

## 目的

这一份文档对应 TSV 审计流程中的“阶段 2”：优先审查高风险公式。

目标不是立刻改代码，而是先把以下问题明确下来：

1. 当前公式是什么
2. 它想表达的信号含义是什么
3. DESTINY 文档 / 论文对这一类 TSV 的语义是怎么定义的
4. 当前实现是“基本一致”、“语义翻译后可接受”，还是“明显可疑 / 可能不一致”
5. 下一步应该怎么验证或修正

## 审计基线

### README 中 coarse / fine 的定义

本地 `README:87-107` 的描述可概括为：

- coarse granularity：
  address、control、data 信号都广播到所有 stacked dies，并在目标 die 上解码
- fine granularity：
  address 信号在独立 logic layer 上 pre-decode，undecoded address signals 广播到各层
  control 和 data 仍然共享
  local TSV 用来传输 pre-decoded signals
  global TSV 用来传输 broadcast signals

### DESTINY DATE 2015 论文中的定义

DATE 2015 论文 Section II.B 的关键语义可概括为：

- coarse-grained：
  TSV 用来向所有层广播 undecoded row / column select signals
  假设一个 logic layer 通过共享 TSV bus 提供输出
- fine-grained：
  向所有层广播 decoded row / column signals
  假设有 dedicated logic layer 放置 predecoder
- DESTINY 的 TSV primitive 可以是 buffered 或 unbuffered
- coarse 和 fine 都采用简化的 equal-folding 假设

注意：README 和 DATE 论文在 fine-grained 的措辞并不完全一样，所以审计时要区分“实现翻译”与“真正偏离”。

## 6 个高风险公式审计表

| ID | 当前公式 / 实现 | 代码位置 | DESTINY 语义基线 | 初步判断 | 下一步建议 |
|---|---|---|---|---|---|
| F1 | `numControlBits = stackedDieCount` | `BankWithHtree.cpp:566`, `BankWithoutHtree.cpp:275`, 同类逻辑见 `:706`, `:508` | DESTINY 公开语义里只说 coarse/fine 会广播 control 类信号，没有直接给出这个精确公式；代码里还保留了旧注释 `log2(stackedDieCount + 0.1)` | 高风险、优先审计。这里不像是从文档直接能推出的唯一公式，更像手写近似或历史改动点 | 对照 DESTINY technical report / CACTI-3DD 原始实现，确认 control TSV 数量到底应按层数线性、对数还是按具体 control class 拆分 |
| F2 | `numAddressBits = log2(capacity / blockSize / associativity / stackedDieCount)` | `BankWithHtree.cpp:567`, `BankWithoutHtree.cpp:276`, 同类逻辑见 `:707`, `:509` | README coarse 说 address 信号广播到所有层，DATE 论文 coarse 更接近“undecoded row / column select”广播 | 可疑但未必错误。当前公式把 address 压缩成了一个几何位宽，没有区分 row / column，也没有显式体现“undecoded row/column select” | 核对 technical report / CACTI-3DD 中 coarse 模型是否真的把 row / column 合成一个地址位宽；如果不是，考虑拆成 row-select / column-select 两类 |
| F3 | `numDataBits = blockSize * 2` | `BankWithHtree.cpp:568`, `BankWithoutHtree.cpp:277`, 同类逻辑见 `:708`, `:510` | DESTINY 文档只明确 data 是 shared / broadcast；没有直接说要用 `blockSize * 2` 表示读写 TSV 总量 | 高概率属于过粗近似。它把 read data 和 write data 粗暴合并，虽然方便，但语义上不够细 | 后续最小修法可以先把 read-data / write-data 两类显式拆开；如果实验时间有限，至少在文档里说明这是 current approximation |
| F4 | fine-grained 时 `numAddressBits = 0` | `BankWithHtree.cpp:571-572`, `BankWithoutHtree.cpp:280-281`, 同类逻辑见 `:711-712`, `:513-514` | README 说 fine-grained 下 address 在 logic layer 上 pre-decode，undecoded address 广播；DATE 论文说 fine-grained 广播 decoded row / column signals | 单独看这条公式会觉得“不一致”，但结合 `Mat.cpp` 后更像“地址类 TSV 从 bank 层转移到了 mat 层” | 不能孤立判断。必须和 `Mat.cpp` 中 `totalPredecoderOutputBits` 一起审；这里先标记为“语义翻译候选”，而不是直接判错 |
| F5 | `totalPredecoderOutputBits` 被当作 fine-grained local TSV 数量，面积/延迟/能耗都按它累计 | `Mat.cpp:119-163`, `Mat.cpp:204-211`, `Mat.cpp:300-301`, `Mat.cpp:370-377` | DATE 论文 fine-grained 说广播 decoded row / column signals，并假设 predecoder 在 dedicated logic layer；README 说 local TSV 用于 pre-decoded signals | 方向上和 DESTINY 语义接近，但公式代理量是否正确仍需核对。`totalPredecoderOutputBits` 是把 row decoder、bitline mux、sense-amp mux 各级 predecoder 输出都累加了 | 这是 fine-grained 审计核心。下一步要确认：DESTINY / CACTI-3DD 的 fine 模型是否真的需要把这些所有 predecoder 输出都计入 local TSV，还是只应该计入 row / column 相关的一部分 |
| F6 | hop 成本固定按 `(stackedDieCount - 1)` 汇总，即一律 worst-case 到最远 die | `BankWithHtree.cpp:721-735`, `BankWithoutHtree.cpp:523-538`, `Mat.cpp:300-301`, `Mat.cpp:370-377` | DESTINY 论文强调使用简化 folding 假设，但没有在公开摘要里明确说必须 always worst-case；当前 midterm 也把 TSV 公式列为下一阶段修正目标 | 这是典型“可能不是 bug，但会显著影响结论”的建模假设。对于层数 sweep，影响很大 | 先查 original DESTINY 是否明确使用 worst-case-only；如果没有强约束，下一步可以考虑增加 average-hop 模式，而不是直接替换 worst-case |

## 当前结论：这 6 项如何分类

### 更像“明显可疑 / 优先查原始来源”的

- F1 `numControlBits = stackedDieCount`
- F3 `numDataBits = blockSize * 2`
- F6 固定 `(stackedDieCount - 1)` worst-case hop

这三项都不是从 README / DATE 语义中一眼就能直接推出的，优先级最高。

### 更像“需要和其他代码一起联动判断”的

- F4 fine-grained 时 `numAddressBits = 0`
- F5 `totalPredecoderOutputBits`

这两项必须成对审。单看 `numAddressBits = 0` 很像不一致，但结合 `Mat.cpp` 中 local TSV 对 predecoder outputs 的建模后，它更像是“把 address 类流量迁移到另一层”的实现翻译。

### 更像“可能是粗近似，但不一定立刻错”的

- F2 `numAddressBits = log2(...)`

它的问题在于“过度压缩语义”，而不一定是立即错误。是否修，要看你对照 technical report 后能否证明 DESTINY 原始模型本来就更细。

## 与 DESTINY 不完全一致的非公式类问题

虽然阶段 2 主体是公式审计，但当前代码里还有几类“和 DESTINY 公开描述不完全一致”的非公式问题，建议一起记录。

### N1. buffered / unbuffered 选择没有真正暴露出来

证据：

- `TSV::Initialize(TSV_type, bool buffered = false)` 支持 buffered / unbuffered
- 但 `Mat.cpp:171-172`、`BankWithHtree.cpp:461-462`、`BankWithoutHtree.cpp:219-220` 都只调用了默认参数

结论：

当前运行路径看起来基本是 unbuffered-only，而 DESTINY 论文明确说 TSV model 可以是 buffered 或 unbuffered。

### N2. Result.cpp 又重新拼了一套 TSV 输出分解

证据：

- `Result.cpp:340-349`
- `Result.cpp:357-364`
- `Result.cpp:482-489`
- `Result.cpp:646-649`

结论：

优化时用的是 `Bank/Mat` 的真实聚合逻辑，而打印时 `Result.cpp` 又重新组合了一套 TSV breakdown。这会带来“实验输出的 TSV 细分”和“真实参与优化的 TSV 代价”不一致的风险。

### N3. fine-grained read TSV energy 的输出代码自己承认还没整理完

证据：

- `Result.cpp:485-488` 附近有 `TODO: revisit this`

结论：

如果后续实验图打算使用 fine-grained 的 TSV read energy，这段必须先核对，否则图表可信度会受影响。

### N4. primitive TSV area 里还有经验化常量和 TODO

证据：

- `TSV.cpp:90`
- `TSV.cpp:115-119`

结论：

这一层不是当前最优先的修正点，但它说明 primitive 模型本身也仍带有 heuristic。建议在 signal counting 语义确认之后，再决定是否对 primitive area / leakage 进一步校准。

## 建议的下一步执行顺序

### 第一步：优先查原始来源的 3 项

优先顺序建议是：

1. F1 `numControlBits = stackedDieCount`
2. F3 `numDataBits = blockSize * 2`
3. F6 worst-case hop

原因：

- 这三项最可能直接改变 2 / 4 / 8 / 16 层的趋势判断
- 也最容易写成“和原始 DESTINY/CACTI-3DD 不一致”的证据链

### 第二步：联动审 fine-grained 这 2 项

必须一起看：

- F4 bank 级 `numAddressBits = 0`
- F5 mat 级 `totalPredecoderOutputBits`

目标：

- 判断 fine-grained 是“语义翻译后仍然合理”
- 还是“把 address 类流量错位或重复计算了”

### 第三步：补一个输出一致性检查

重点核对：

- bank 层 area/latency/energy 的 TSV 总值
- `Result.cpp` 打印出的 TSV 分解值

如果两者不一致，优先修 `Result.cpp` 的 breakdown，因为这会直接影响实验结果的解读。

## 阶段 2 的最小产出建议

完成这一轮后，最好能产出这 3 个东西：

1. 一个“已核对 / 待核对”的公式清单
2. 一个最明确的不一致点的修正 patch
3. 一个小型 before/after sweep，用来证明这个修正会影响 TSV 或总体 3D 指标

## 当前阶段的工作结论

目前最稳妥的判断是：

- 当前 TSV 模型不是“完全错”，而是“混合了多层抽象、且部分公式明显偏粗”
- 真正优先要审的是 bank / mat 层的信号计数与 hop 汇总
- 在没有把 coarse/fine 语义彻底对齐之前，不建议直接跳到更现代 TSV 论文去大改 primitive 模型

换句话说，阶段 2 的核心不是“重新发明 TSV 模型”，而是：

先弄清楚当前实现到底有没有忠实实现 DESTINY 自己说的 coarse/fine 语义。
