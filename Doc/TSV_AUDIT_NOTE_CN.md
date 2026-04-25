# TSV 审计笔记

## 范围

这份笔记是针对当前代码库中 TSV 模型的第一轮逆向梳理和审计清单。

它主要回答三个问题：

1. 当前工程里的 TSV 是怎么建模的？
2. 哪些假设来自 DESTINY / CACTI-3DD 的原始语义？
3. 当前实现里哪些地方和 DESTINY 文档语义不一致，或者至少值得优先审计？

这份笔记故意偏“可执行”，目标不是立刻提出一个全新的 TSV 模型，而是为下一步对照 DESTINY 论文 / technical report 做审计打基础。

## 使用到的材料

### 本地代码和文档

- `README`
- `TSV.cpp`, `TSV.h`
- `Technology.cpp`, `Technology.h`
- `Mat.cpp`
- `BankWithHtree.cpp`
- `BankWithoutHtree.cpp`
- `Result.cpp`
- `Doc/Midterm_Progress_Report_ESE5760.tex`

### 主要参考来源

- DESTINY DATE 2015 论文  
  `https://pasalabs.org/papers/2015/2015_DATE_Destiny.pdf`
- DESTINY 扩展论文 / 更完整的建模说明  
  `https://www.mdpi.com/2079-9268/7/3/23`
- DESTINY README 中声明引用的 CACTI-3DD  
  `https://ieeexplore.ieee.org/document/6176428`

## 当前 TSV 模型：逆向梳理

当前代码中的 TSV 建模不是一个单独的模块，而是分散在三层抽象里。

### 1. Technology 层：TSV primitive 参数

`Technology.cpp` 定义了 TSV 的几何和寄生参数，包括：

- pitch
- diameter
- length
- dielectric thickness
- contact resistance
- depletion width
- liner dielectric constant

这些参数按不同 projection 选择和 TSV 类型保存在 `Technology` 中。

关键位置：

- `Technology.h:60-82`
- `Technology.cpp:1921-2015`
- `Technology.cpp:2017-2037`

重要观察：

- TSV 电阻被建模为导体电阻加接触电阻。
- TSV 电容被建模为 self-capacitance 加 lateral / diagonal coupling。
- TSV 占用面积被简化成 `pitch^2`。
- `SetLayerCount(...)` 会随着层数变化重算 TSV 长度和寄生参数。

### 2. TSV.cpp：单个 TSV primitive 的延迟 / 能耗 / 漏电

`TSV.cpp` 负责建模“一个 TSV 加上可选驱动链”的代价。·

关键位置：

- `TSV.cpp:30-80` 初始化
- `TSV.cpp:83-121` 面积
- `TSV.cpp:124-136` 读写接口
- `TSV.cpp:139-221` 延迟与动态能耗

重要观察：

- `TSV::Initialize(TSV_type, bool buffered = false)` 同时支持 buffered 和 unbuffered TSV。
- 但实际运行路径中，`Mat` 和 `Bank` 代码都只调用了 `Initialize(tsv_type)`，因此当前默认行为实际上是 `unbuffered`。
- 读和写共用同一个内部延迟/能耗计算函数，只是输入 ramp 不同。
- `reset` 和 `set` 直接沿用 write 的结果。

这一层里比较敏感的 heuristic 包括：

- `TSV.cpp:90` 里的 `buffer_area_height = 50 * tech->featureSize`
- `TSV.cpp:103-108` 中重复的 leakage 计算路径
- `TSV.cpp:115-119` 附近保留了 `TODO -- Understand this better`

### 3. 架构层：到底需要多少 TSV，以及怎么汇总进总面积/延迟/能耗

TSV 数量以及它如何计入 bank 的面积、延迟和能耗，并不是在 `TSV.cpp` 决定的，而是分散在：

- `Mat.cpp`
- `BankWithHtree.cpp`
- `BankWithoutHtree.cpp`
- `Result.cpp`

这部分才是最重要的审计对象。

## coarse-grained TSV：bank 级计数

对于 bank 级 3D stacking，H-tree 和 non-H-tree 两条路径基本使用了相同的 TSV 公式。

关键位置：

- `BankWithHtree.cpp:561-580`
- `BankWithHtree.cpp:701-735`
- `BankWithoutHtree.cpp:271-289`
- `BankWithoutHtree.cpp:504-538`

当前 coarse-grained 计数公式大致是：

- `numControlBits = stackedDieCount`
- `numAddressBits = log2(capacity / blockSize / associativity / stackedDieCount)`
- `numDataBits = blockSize * 2`

然后再计算：

- `numTotalBits = (control + address + data) * redundancy`
- `numAccessBits = (control + address + blockSize) * redundancy`
- `numReadBits = (control + address) * redundancy`
- `numDataBits = blockSize * redundancy`

延迟和能耗的汇总则默认：

- 永远按最远 die 的 worst-case 计算
- hop 数固定为 `stackedDieCount - 1`
- read latency 由 control/address 的 write 路径和 data 的 read 路径叠加
- write latency 只走 write 路径

这套逻辑在 H-tree 和 non-H-tree 两个版本里是重复出现的。

## fine-grained TSV：mat 级计数

在 fine-grained 分支中，bank 层会把 address bits 置零，而真正的地址类 TSV 由 `Mat.cpp` 中的 predecoder 输出承担。

关键位置：

- `Mat.cpp:119-163`
- `Mat.cpp:169-173`
- `Mat.cpp:203-214`
- `Mat.cpp:287-302`
- `Mat.cpp:369-377`

当前 fine-grained 的实现含义大致是：

- 所有 predecoder 输出都累加进 `totalPredecoderOutputBits`
- 在 mat 层实例化 local TSV
- `tsvArray.numTotalBits = totalPredecoderOutputBits * redundancy`
- `tsvArray.numAccessBits = numTotalBits`
- predecoder latency 会额外加上 TSV write latency
- mat power 会按 `totalPredecoderOutputBits` 计入 TSV 能耗

所以从当前代码的语义看：

- bank 级 global TSV 代表 control/data 这类共享广播流量
- mat 级 local TSV 代表 decoded predecoder-output 流量

这个方向和 DESTINY 的 fine-grained 描述是接近的，但细节上还有不少地方值得审。

## Result.cpp 又做了一层 TSV 分解

`Result.cpp` 并不是简单打印 bank 里已经聚合好的 TSV 贡献，而是又用 primitive 字段重算了几项 TSV breakdown。

关键位置：

- `Result.cpp:340-349` 面积打印
- `Result.cpp:357-364` 读延迟打印
- `Result.cpp:482-489` 读能耗打印
- `Result.cpp:646-649` 漏电打印

这说明当前代码里 TSV 账其实有两套：

1. bank / mat 聚合时的一套
2. 输出打印时重新组合的一套

这是一类典型的审计风险：最终打印出来的 TSV breakdown 可能和真实参与优化的 TSV 代价不是同一件事。

## DESTINY 文档里 TSV 语义应该是什么

根据 DESTINY README：

- coarse granularity：
  address、control、data 信号都广播到所有 stacked dies，并在目标 die 上解码
- fine granularity：
  address 信号在独立 logic layer 上 pre-decode，undecoded address signals 广播到各层
  control 和 data 依然是共享的

根据 DESTINY DATE 2015 论文：

- DESTINY 直接使用 CACTI-3DD 的 coarse/fine TSV 模型
- TSV model 可以是 buffered 或 unbuffered
- coarse-grained 模型向所有层广播 undecoded row / column select signals
- fine-grained 模型向所有层广播 decoded row / column signals
- fine-grained 假设 predecoder 在 dedicated logic layer 上
- coarse 和 fine 都假设一种比较简化的等分 folding scheme

这些描述共同构成了我们审计 TSV 的“语义基线”。

## 和 DESTINY 不一样、或者优先值得审计的地方

这一节列的是当前实现里最像“与 DESTINY 语义不完全一致”或“至少非常可疑”的地方。

### A. 代码支持 buffered / unbuffered，但实际运行路径看起来几乎只有 unbuffered

证据：

- `TSV.h:24` 默认 `buffered = false`
- `Mat.cpp:171-172`
- `BankWithHtree.cpp:461-462`
- `BankWithoutHtree.cpp:219-220`

为什么重要：

DESTINY 论文明确说 TSV model 可以是 buffered 或 unbuffered。但当前实际初始化路径全部使用默认参数，这意味着运行时几乎没有暴露 buffered 这个选择。

审计问题：

- 这是故意简化成 unbuffered-only 吗？
- 如果是，项目里有没有文档说明？
- 如果不是，buffered / unbuffered 应该从配置还是搜索空间进入？

### B. coarse-grained 的 control bit 数量是人工改写过的，而且旧公式还留在注释里

证据：

- `BankWithHtree.cpp:565-567`
- `BankWithoutHtree.cpp:274-276`

当前代码：

- 旧注释公式：`log2(stackedDieCount + 0.1)`
- 现用公式：`numControlBits = stackedDieCount`

为什么重要：

这类地方是最典型的高风险审计点。代码本身已经表明这里经历过改法变化，而 DESTINY 的公开描述里并没有直接证明这个新公式一定合理。

审计问题：

- control TSV 数量到底应该线性随层数增长，还是对数增长，还是应该按具体 control class 拆开？

### C. coarse-grained 的 address/data 计数压缩得过于粗

证据：

- `BankWithHtree.cpp:567-568`
- `BankWithoutHtree.cpp:276-277`

当前代码：

- address 用一个几何公式估算
- `numDataBits = blockSize * 2`

为什么重要：

DESTINY 论文对 coarse-grained 的描述更接近“广播 undecoded row/column select 信号”，而不是简单地压成一个 address count 加一个 `blockSize * 2`。当前实现可能是一个实用近似，但它和论文语义之间有明显抽象落差。

审计问题：

- 现在这套公式到底是对原模型的忠实近似，还是后续代码里自己做的 shortcut？
- row / column 是否应该拆开？
- control / address / data 是否应该分别建模读写路径？

### D. fine-grained 在 README 和论文里的措辞并不完全一样，而代码只部分反映了这两者

证据：

- README 说的是：undecoded address signals 广播到各层，并在 logic layer 上 pre-decode
- DATE 论文说的是：decoded row / column signals 广播到各层
- 当前代码：
  - bank 层 fine-grained 直接把 `numAddressBits = 0`
  - mat 层通过 `totalPredecoderOutputBits` 补回这部分 TSV

相关代码：

- `BankWithHtree.cpp:570-577`
- `BankWithoutHtree.cpp:279-286`
- `Mat.cpp:119-163`
- `Mat.cpp:203-214`

为什么重要：

当前实现显然是在把 bank 层的地址类 TSV 转译成 mat 层的 predecoder 输出 TSV。这个思路可能是对的，但要分清楚它到底是“对论文语义的实现翻译”，还是“公式已经和原始语义偏离了”。

审计问题：

- `totalPredecoderOutputBits` 是否真的能代表 fine-grained 的 published model？
- fine-grained 下 bank 层是不是仍然应该保留某些 undecoded address 类流量？
- row 和 column 的 decode output 是否都被正确表示了？

### E. hop 成本现在是纯 worst-case

证据：

- `BankWithHtree.cpp:721-735`
- `BankWithoutHtree.cpp:523-538`

当前代码：

- 一律使用 `(stackedDieCount - 1)` 作为 hop 数

为什么重要：

midterm 已经明确把 TSV formula audit 列成 next-phase 目标。worst-case-only 的 hop 假设会直接影响多层堆叠下 TSV latency / energy 的增长趋势，因此它至少应该在审计中被显式确认。

审计问题：

- 原始 DESTINY 是否本来就是只想做 worst-case？
- 还是说后续可以增加 average-hop / expected-hop 选项，而不是直接替换现有模型？

### F. TSV 输出分解和真实参与优化的 TSV 代价可能不一致

证据：

- bank 面积累计时使用了 `numTotalBits`
- 但 `Result.cpp` 里 coarse TSV area 打印的是 `bank->tsvArray.area`

相关代码：

- `BankWithHtree.cpp:576-580`
- `BankWithoutHtree.cpp:285-289`
- `Result.cpp:340-349`

为什么重要：

这提示了一个可能的“单位值 / 总值”混淆。即便总面积本身在优化中是对的，最终打印出来的 TSV area breakdown 也不一定是同一个量。

审计问题：

- `tsvArray.area` 表示的是单个 TSV 还是整个 TSV bundle？
- 如果它是单个 TSV，那 `Result.cpp` 打印 coarse TSV area 时是不是应该乘 `numTotalBits`？

### G. fine-grained 的读能耗输出路径明确标了未完成

证据：

- `Result.cpp:485-488`

为什么重要：

这段代码自己写了 `TODO: revisit this`。如果你后面打算把 TSV dynamic energy 拿去做图或写报告，这一段必须先和 bank/mat 的真实聚合逻辑核对。

### H. primitive TSV area 模型里还有明显 heuristic 和 TODO

证据：

- `TSV.cpp:90`
- `TSV.cpp:104-115`

为什么重要：

这些问题不如 bank 层信号计数那么紧急，但如果你后面想进一步做 primitive calibration，它们会成为第二阶段改进的入口。

## 建议的审计顺序

不要一上来就读“新 TSV 论文”并重构模型。先做一致性检查。

### 阶段 1：冻结语义基线

把三份东西并排写清楚：

- README 对 coarse/fine 的定义
- DATE 2015 对 coarse/fine 的定义
- 当前代码对 coarse/fine 的实现方式

目标：

- 区分哪些地方是“语义翻译”
- 区分哪些地方是“实现 shortcut”

### 阶段 2：优先审高风险公式

最先检查这几项：

1. `numControlBits = stackedDieCount`
2. `numAddressBits = log2(capacity / blockSize / associativity / stackedDieCount)`
3. `numDataBits = blockSize * 2`
4. fine-grained 下 `numAddressBits = 0`
5. `totalPredecoderOutputBits` 作为 fine-grained local TSV 数量
6. `(stackedDieCount - 1)` 作为固定 hop 距离

每项都记录：

- 代码位置
- 当前公式
- 想表达的信号含义
- DESTINY / CACTI-3DD 的原始语义
- 初步判断：一致 / 模糊 / 不一致

### 阶段 3：检查输出一致性

核对 `Result.cpp` 打印的 TSV breakdown 到底是：

- 真正参与优化的量
- primitive 单位量
- 还是重新组合出的近似量

这一步很重要，因为后续实验图往往会直接使用输出 breakdown。

### 阶段 4：再考虑模型升级

如果阶段 1-3 证明当前公式只是“比较粗但基本一致”，那下一步才适合做增强版模型，例如：

- signal-class-aware TSV counting
- average-hop 和 worst-hop 两种模式
- control / address / data 的明确分离
- buffered / unbuffered 作为显式可选项

## 下一轮最小交付物

下一轮最好产出这 4 个东西：

1. 一张 TSV 公式表，列出当前每个公式及其含义
2. 一张 DESTINY 语义与当前实现的对照表
3. 一个最明确不一致点的小 patch
4. 一个 2 / 4 / 8 / 16 层 sweep，对比修正前后的变化

## 当前结论

当前代码里的 TSV 模型是“能工作的”，但它不是一套单一、干净的模型，而是四层混合在一起：

- Technology 层的寄生参数
- TSV primitive 的延迟/能耗逻辑
- Mat / Bank 层的信号计数 heuristic
- Result 层的输出分解公式

这正是为什么 TSV 修正应该从“审计”开始，而不是立刻大改模型。

当前最优先的审计点是：

- 信号计数语义
- buffered / unbuffered 是否真正暴露
- worst-case hop 假设
- 输出分解和真实优化量是否一致

只要这些问题先被厘清，后面你再做 TSV 优化，就更容易把它写成“有依据的模型改进”，而不是看起来像一次随意重写。
