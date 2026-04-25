# TSV 阶段 2 - F1 审计结果

## 审计对象

F1 对应的当前公式是：

`numControlBits = stackedDieCount`

相关代码位置：

- `BankWithHtree.cpp:566`
- `BankWithHtree.cpp:706`
- `BankWithoutHtree.cpp:275`
- `BankWithoutHtree.cpp:508`

附近代码还保留了旧公式注释：

`//int numControlBits = (int)(log2((double)stackedDieCount + 0.1));`

这说明这条公式在代码历史里发生过改动，因此它本身就是高优先级审计点。

## 当前代码里它代表什么

在当前实现中，`numControlBits` 被并入 bank 级 global TSV 计数，用于后续的：

- `numTotalBits`
- `numAccessBits`
- `numReadBits`

并进一步影响：

- TSV area
- TSV latency
- TSV dynamic energy
- TSV leakage

也就是说，这不是一个局部显示用变量，它会直接影响 3D bank 的 TSV 总开销。

## DESTINY 文档 / 论文里的对应语义

### README 里的说法

本地 `README:87-107` 的相关语义是：

- coarse granularity 下，`address`、`control`、`data` 都广播到所有 stacked dies
- global TSV 用来传输 broadcast signals，例如 `data` 和 `control`

这给出了“control 需要通过 global TSV 广播”的语义，但没有给出 control TSV 数量的精确公式。

### DESTINY DATE 2015 论文里的说法

DESTINY 原论文对 coarse-grained 的表述是：

- coarse-grained 模型里，TSV 用来向所有层广播 `undecoded row and column select signals`
- 一个 logic layer 通过 shared TSV bus 为所有层提供输出

来源：

- DESTINY DATE 2015 paper  
  https://pasalabs.org/papers/2015/2015_DATE_Destiny.pdf

对应证据位置：

- `turn1view5` 中 `L219-L229`

从这段描述可以直接得到的结论有两个：

1. coarse-grained 下确实存在 broadcast 类 TSV
2. 论文强调的核心对象是 `undecoded row and column select signals`

但这段文字同样没有直接推出 `numControlBits = stackedDieCount` 这个精确公式。

### MDPI 扩展文档里的说法

扩展文档延续了同样的 coarse/fine 语义：

- coarse-grained 下广播 `undecoded row and column select signals`
- fine-grained 下广播 `decoded row and column signals`
- TSV primitive 可以是 buffered 或 unbuffered

来源：

- MDPI DESTINY extended paper  
  https://www.mdpi.com/2079-9268/7/3/23

对应证据位置：

- `turn1view1` 中 `L451-L454`

这里依然没有给出 `control bits` 必须等于 `stackedDieCount` 的直接证据。

## 初步判断

当前阶段可以得到的最稳妥结论是：

### 结论 1

`control` 类信号确实应该进入 global TSV 计数。

这一点有 README 支持，也和 DESTINY 的 3D coarse/fine 语义相容。

### 结论 2

`numControlBits = stackedDieCount` 这个具体公式，目前还没有从 DESTINY 公开文字中找到直接依据。

当前公开证据只能支持“有 control / select 类广播流量”，还不能直接支持“control TSV 数量线性等于层数”。

### 结论 3

代码里保留的旧注释公式 `log2(stackedDieCount + 0.1)` 进一步说明这里曾经有不同理解。

因此，这条公式目前最适合被标记为：

`语义上合理，但公式证据不足，需要继续核对原始实现或 technical report`

## 当前建议分类

对 F1 的状态建议标成：

- `高风险`
- `待核对原始来源`
- `暂不直接修改`

原因：

- 它会直接影响 TSV 总开销
- 当前公开文字证据不足以唯一支持现有公式
- 如果现在直接改成 `log2(...)` 或别的形式，依据仍然不够硬

## 下一步建议

### 建议 1：先查 CACTI-3DD / DESTINY technical report 的原始实现或更细描述

F1 这一项最需要的是“源码级或报告级证据”，优先级高于读更新的 TSV 封装论文。

目标是确认：

- control / select 类信号在 coarse 模型里到底如何计数
- 计数是否按 die 数线性增长
- 还是按 decode/select 结构推导

### 建议 2：如果短期内查不到更细来源，先把 control 类拆成显式类别

一个保守且容易解释的后续方案是：

- 保留现有 `control` 概念
- 在代码里把它改成更明确的名字，例如 `numBroadcastControlBits`
- 同时在注释中写清它是当前近似，不把它表述成“原论文严格公式”

这样能先降低语义歧义。

### 建议 3：在正式改公式前，先记录这条公式对结果的敏感度

建议后面做一个小敏感度实验：

- 固定其他 TSV 参数
- 分别测试 control bit 数按 `N`、`log2(N)`、常数小值时的变化
- 看 TSV area / energy / total bank metrics 对 F1 的敏感度

这会帮助你判断 F1 值不值得作为优先修正项。

## F1 当前结论

F1 这一项目前可以写成一句很稳的结论：

`当前代码把 control TSV 数量建模为 stackedDieCount，但从 DESTINY 公开语义中还找不到直接支撑这一精确公式的证据，因此这条公式应视为高优先级待核对项。`
