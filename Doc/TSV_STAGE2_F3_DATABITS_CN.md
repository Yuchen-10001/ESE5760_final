# TSV 阶段 2 - F3 审计结果

## 审计对象

F3 对应的当前公式是：

`numDataBits = blockSize * 2`

相关代码位置：

- `BankWithHtree.cpp:568`
- `BankWithHtree.cpp:708`
- `BankWithoutHtree.cpp:277`
- `BankWithoutHtree.cpp:510`

后续与它配套使用的字段包括：

- `tsvArray.numTotalBits`
- `tsvArray.numAccessBits`
- `tsvArray.numReadBits`
- `tsvArray.numDataBits`

其中在 bank 级汇总时，代码又把：

- `numDataBits` 细化成 `blockSize * redundancy`
- `numReadBits = (control + address) * redundancy`
- `numAccessBits = (control + address + blockSize) * redundancy`

也就是说，`blockSize * 2` 主要用在“总 TSV 数量”的估算上，语义上它相当于：

- 一份 write data TSV
- 一份 read data TSV

## 当前代码里它代表什么

从当前 bank 级代码看，`numDataBits = blockSize * 2` 的直观含义是：

- 假设读数据通路需要 `blockSize` 条 TSV
- 写数据通路也需要 `blockSize` 条 TSV
- 两者直接相加形成数据类 TSV 总数

在后续的延迟和能耗处理中：

- read latency 走 control/address 写路径加 data 读路径
- write latency 走 write 路径
- read energy 中也把 control/address 和 data 分开计算

所以 `blockSize * 2` 更像是“总 TSV 占位”的粗略计数，而不是严格对应一次 read 或一次 write 的动态激活位数。

## DESTINY 文档 / 论文里的对应语义

### README 里的说法

本地 `README:87-107` 的关键信息有两条：

- coarse granularity 下，`address`、`control`、`data` 都广播到所有 stacked dies
- global TSV 用于传输 broadcast signals，例如 `data` 和 `control`

这说明 data 类 TSV 确实存在，也说明它们属于 global broadcast 类流量。

但 README 没有给出 data TSV 数量的精确公式，更没有直接写成 `blockSize * 2`。

### DESTINY DATE 2015 论文里的说法

DESTINY 原论文在 3D 模型部分强调的是：

- coarse-grained 模型中，TSV 用于向所有层广播 `undecoded row and column select signals`
- 一个 logic layer 通过 shared TSV bus 向所有层提供输出
- fine-grained 模型则广播 decoded row / column signals

来源：

- DESTINY DATE 2015 paper  
  https://pasalabs.org/papers/2015/2015_DATE_Destiny.pdf

相关证据位置：

- `turn1view3` 中 `L223-L229`

这段文字给出了两个重要信息：

1. coarse-grained 的公开描述重点放在 row / column select signal
2. 论文没有直接把 data TSV 数量写成 `2 * blockSize`

### MDPI 扩展文档里的说法

扩展文档同样写到：

- coarse-grained 下使用 TSV 广播 undecoded row / column select signals
- 一个 logic layer 通过 shared TSV bus 提供输出

来源：

- MDPI DESTINY extended paper  
  https://www.mdpi.com/2079-9268/7/3/23

相关证据位置：

- `turn1view1` 中 `L453-L454`

这段描述依然没有直接推出 `numDataBits = blockSize * 2` 这个公式。

## 初步判断

当前阶段可以得到的结论如下。

### 结论 1

data 类 TSV 在 coarse 模型里肯定应该存在。

这一点有 README 支持，因为 README 明确说 coarse granularity 下 data 是广播到所有 stacked dies 的，而且 global TSV 用来路由 broadcast signals。

### 结论 2

`numDataBits = blockSize * 2` 这条公式在公开 DESTINY 语义里找不到直接文字依据。

当前证据能支持“需要 data TSV”，还不能直接支持“总数据类 TSV 数量应写成读一份加写一份，也就是 `2 * blockSize`”。

### 结论 3

这条公式很像一种工程化近似，用来把：

- read data TSV
- write data TSV

合并成一个总量估算。

这样的写法有实现上的方便性，但语义颗粒度偏粗。

### 结论 4

如果后续要研究不同 stack depth、不同 partition granularity、或者 TSV area / energy 的占比变化，`blockSize * 2` 这种合并方式会限制解释力。

因为它默认：

- read data 与 write data 的 TSV 数量对称
- 两类数据通路的资源占位可以直接线性相加
- 不区分静态资源数量和一次访问时的实际激活模式

## 当前建议分类

对 F3 的状态建议标成：

- `高优先级`
- `公式偏粗`
- `有较大机会形成明确修正项`

和 F1 相比，F3 更接近“可以落地优化”的目标，因为：

- 它的语义更容易拆开
- 对输出解释影响更直接
- 后续修改时可以保持较小 patch 范围

## 建议修正方向

### 方向 1：先把“总量计数”和“访问激活计数”分开

当前 `blockSize * 2` 混合了“占多少 TSV 资源”和“访问时会激活哪些 TSV”这两层概念。

建议先拆成两个显式变量，例如：

- `numReadDataBits`
- `numWriteDataBits`

然后：

- `numTotalBits` 用资源占位逻辑
- read / write dynamic energy 用各自激活逻辑

这样做的好处是：

- 语义更清楚
- 后续更容易做 sensitivity study
- 也更容易和 `Result.cpp` 的 breakdown 对齐

### 方向 2：保持当前功能不变，只先做显式拆分

如果你现在想做一个最小 patch，可以先保守地写成：

- `numReadDataBits = blockSize`
- `numWriteDataBits = blockSize`
- `numDataBits = numReadDataBits + numWriteDataBits`

这样数值上和当前完全一致，代码语义会清楚很多。

这一步很适合作为“低风险第一修正”。

### 方向 3：后续再决定是否进一步细化 data TSV 模型

等你把 coarse/fine 的 signal semantics 对齐后，再看是否要进一步区分：

- broadcast data
- return data
- write input data
- 不同 access mode 下的 data-side 实际激活规模

当前阶段不建议一步走太远。

## 下一步验证建议

### 建议 1：先做一个语义重构型 patch

第一版 patch 不改变数值，只做：

- 变量重命名
- read-data / write-data 拆分
- 注释里明确说明当前仍采用对称近似

这会让后面的模型升级更安全。

### 建议 2：检查 `Result.cpp` 是否和拆分后语义一致

重点核对：

- read TSV dynamic energy
- write TSV dynamic energy
- coarse/fine breakdown

尤其是 `Result.cpp:482-489` 附近的 TSV dynamic energy 输出，后续很可能需要同步调整。

### 建议 3：做一个最小敏感度实验

建议后面做一个 sweep：

- 固定 `blockSize`
- 分别测试 read-data / write-data 对称和非对称计数
- 观察 TSV area、TSV dynamic energy、total bank energy 的变化

这样能判断 F3 对总体结果的影响强度。

## F3 当前结论

F3 这一项目前可以总结成一句话：

`当前代码把数据类 TSV 总数近似写成 blockSize * 2，这能表达“读通路和写通路各占一份数据 TSV 资源”的直觉，但 DESTINY 公开语义没有直接给出这条公式，因此它应视为高优先级、且较适合落地修正的粗粒度近似。`
