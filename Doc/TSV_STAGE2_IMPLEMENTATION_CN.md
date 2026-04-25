# TSV Stage 2 实施说明

## 1. 这一轮工作的目标

这一轮修改聚焦在两个问题：

- 让 TSV 的面积、延迟、动态能耗、漏电都走同一套统计口径
- 让 coarse / fine 两条 3D 建模路径更容易解释，也更容易写进课程项目的报告与展示材料

这次实现覆盖了三类内容：

- F3：把 data TSV 的读写语义显式拆开
- F6：把 stack hop 成本从固定写死，扩展成可配置模型
- 审计修正：清理 `Result.cpp` 中和真实建模口径不一致的 TSV 分项输出

## 2. 本轮改动概览

### 2.1 新增统一的全局 TSV 记账入口

文件：

- `Bank.h`
- `Bank.cpp`
- `BankWithHtree.cpp`
- `BankWithoutHtree.cpp`

新增了下面几个核心接口和字段：

- `Bank::ResetTSVAccounting()`
- `Bank::ConfigureGlobalTSVAccounting(...)`
- `Bank::GetEffectiveTSVHopCount()`
- `tsvControlBits`
- `tsvAddressBits`
- `tsvReadDataBits`
- `tsvWriteDataBits`
- 各类 `tsv*Contribution`

这一步的意义在于：

- TSV 数量的定义集中在一个地方
- TSV 贡献值在 bank 内部形成单独账本
- 后面的输出层直接读取这些贡献值，口径会稳定很多

### 2.2 F3：把读数据 TSV 和写数据 TSV 拆开

旧路径里，data TSV 的总数近似写成 `blockSize * 2`。这能表达“读通路一份、写通路一份”的资源占用直觉，但代码层面没有把它们单独记录下来。

现在改成了显式拆分：

- `numReadDataBits = blockSize`
- `numWriteDataBits = blockSize`

然后统一映射到：

- `tsvArray.numTotalBits = control + address + readData + writeData`
- `tsvArray.numAccessBits = control + address + writeData`
- `tsvArray.numReadBits = control + address`
- `tsvArray.numDataBits = readData`

这一步带来的直接收益：

- area / leakage 继续反映总 TSV 资源占用
- read dynamic energy 和 write dynamic energy 的语义分得更清楚
- 后面如果你要继续推进 signal-class-aware TSV counting，这里已经有了清晰入口

### 2.3 F6：加入可配置的 TSV hop 模型

文件：

- `typedef.h`
- `InputParameter.h`
- `InputParameter.cpp`
- `Bank.cpp`

新增配置：

```cfg
-TSVHopModel: Average
-TSVHopFactor: 0.5
```

支持三种模式：

- 默认模式：worst-case hop，等价于 `stackedDieCount - 1`
- `Average`：平均 hop，等价于 `(stackedDieCount - 1) / 2`
- `Custom`：自定义比例，等价于 `(stackedDieCount - 1) * TSVHopFactor`

当前默认行为仍然保持 worst-case，这样现有配置文件不需要改就能继续运行。

这一步的价值主要体现在实验设计上：

- 你可以单独做一组 hop 模型敏感性实验
- 你可以在 poster / presentation 里解释“模型假设如何影响 3D 趋势”
- 你可以把它写成一次建模能力增强，并突出它对实验解释力的提升

### 2.4 Fine-grained local TSV 贡献被单独记录

文件：

- `Mat.h`
- `Mat.cpp`

新增内容包括：

- `rowPredecoderOutputBits`
- `bitlineMuxPredecoderOutputBits`
- `senseAmpMuxLev1PredecoderOutputBits`
- `senseAmpMuxLev2PredecoderOutputBits`
- `tsvAreaContribution`
- `tsvReadLatencyContribution`
- `tsvWriteLatencyContribution`
- `tsvResetLatencyContribution`
- `tsvSetLatencyContribution`
- `tsvRefreshLatencyContribution`
- 各类 `tsv*DynamicEnergyContribution`
- `tsvLeakageContribution`

这样做之后，fine-grained 下的 local TSV 有了明确的归属：

- area：按每个 mat 的 local TSV footprint 统计
- latency：按 predecoder-output 跨层传输统计
- dynamic energy：按 active mats 的访问行为统计
- leakage：按所有 mat 实例累计

### 2.5 `Result.cpp` 的 TSV 分项输出改成直接读取贡献值

这是这轮修正里最关键的一步。

修改前，`Result.cpp` 会自己重新拼一套 TSV 公式。这样会带来两个风险：

- 打印出来的 TSV 分项和优化时真实参与计算的 TSV 代价不完全对齐
- fine-grained local TSV 既算在 `mat.*` 里，又在 TSV 项里单独显示，分项展示会重复计数

修改后，`Result.cpp` 统一采用：

- bank 级 `tsv*Contribution`
- mat 级 `tsv*Contribution`

并且在输出分项时做了下面这些处理：

- `Mat Area` 去掉 local TSV footprint
- `Mat Latency` 去掉 local TSV latency
- `Predecoder Latency` 去掉 local TSV latency
- `Mat Dynamic Energy` 去掉 local TSV dynamic energy
- `Predecoder Dynamic Energy` 去掉 local TSV dynamic energy
- `Mat Leakage Power` 去掉 local TSV leakage
- `TSV Area / Latency / Dynamic Energy / Leakage` 改成显示真实汇总贡献

这一步直接提升了报告可解释性，因为你后续截图或导出结果时，`TSV`、`routing`、`mat` 三部分已经共用同一套账。

## 3. 和当前 DESTINY 路径相比，现在哪些地方已经不一样

这里说的“当前 DESTINY 路径”，指的是这份代码库在你动手之前的实现方式。

### 3.1 TSV area 的输出口径变了

旧版 coarse 路径里，`Result.cpp` 直接打印 `bank->tsvArray.area`，这个值更接近单个 primitive TSV 的面积尺度。

现在输出改成：

- `bank->tsvAreaContribution`
- fine-grained 时再加上 `bank->mat.tsvAreaContribution * numMatInstances`

所以现在看到的是“总 TSV 面积贡献”，更适合直接拿去做 breakdown 图。

### 3.2 Fine-grained 的 local TSV 会从 `Mat` 分项里剥离出来

旧版 fine-grained 输出里：

- `Mat Area`
- `Mat Dynamic Energy`

都混入了 local TSV 贡献。

现在 `Mat` 分项主要代表 mat 本体，TSV 分项专门代表跨层互连成本。这样在讲架构 trade-off 时会更清楚。

### 3.3 Read / write TSV 的语义更明确

旧版用 `blockSize * 2` 做总 data-bit 近似。这个近似仍然保留了“读一份、写一份”的资源直觉，但代码里缺少显式拆分。

现在读和写分别记录：

- `tsvReadDataBits`
- `tsvWriteDataBits`

这样后续如果你想继续推进 F3，比如把某些 memory type 的 write-width、read-width 做成可变参数，改动路径会短很多。

### 3.4 Stack hop 假设从固定值扩展成可配置项

旧版所有 global TSV / local TSV 相关 hop 成本都按 `(stackedDieCount - 1)` 处理。

现在你可以：

- 保持 worst-case
- 切到 average-hop
- 给一个自定义比例

这个变化很适合在课程项目里当成“模型增强点”来讲。

## 4. 代码层面的主要修改文件

本轮涉及的核心文件如下：

- `typedef.h`
- `InputParameter.h`
- `InputParameter.cpp`
- `Bank.h`
- `Bank.cpp`
- `BankWithHtree.cpp`
- `BankWithoutHtree.cpp`
- `Mat.h`
- `Mat.cpp`
- `Result.cpp`

如果你后面要做展示，可以把它总结成三层：

- 配置层：`InputParameter.*`
- 建模层：`Bank*` 和 `Mat*`
- 输出层：`Result.cpp`

## 5. 样例验证结果

### 5.1 编译验证

本轮修改已经通过全量编译：

```powershell
g++ -Wall -O3 -mtune=native *.cpp -o destiny_tsv_stage2.exe
```

编译通过，只有原项目里已有的 `operator=` 隐藏警告，没有新的编译错误。

### 5.2 样例 1：`sample_SRAM_2layer.cfg`

运行命令：

```powershell
cd config
..\destiny_tsv_stage2.exe sample_SRAM_2layer.cfg
```

关键变化：

| 指标 | 旧值 | 新值 | 说明 |
|---|---:|---:|---|
| TSV Area | `10.240 um^2` | `5416.960 um^2` | 旧值接近 primitive 级面积，新值反映 total TSV area contribution |
| Read TSV Dynamic Energy | `3.725 pJ` | `3.739 pJ` | 读写 data-bit 拆分后数值有轻微调整 |
| Mat Dynamic Energy | `118.671 pJ / mat` | `118.671 pJ / mat` | coarse 场景下 local TSV 不在 mat 内部，这个分项基本稳定 |

这个样例说明：

- coarse-grained 的最大变化集中在 TSV area 的口径修正
- 读写 data-bit 显式拆分已经生效

### 5.3 样例 2：`sample_SRAM_4layer.cfg`

运行命令：

```powershell
cd config
..\destiny_tsv_stage2.exe sample_SRAM_4layer.cfg
```

关键变化：

| 指标 | 旧值 | 新值 | 说明 |
|---|---:|---:|---|
| Data Array TSV Area | `102425.000 um^2` | `1.549 mm^2` | 新值把 global TSV + local TSV 都纳入总贡献 |
| Read TSV Latency | `0.213 ps` | `0.320 ps` | 新值显式叠加了 global TSV 和 local TSV 的 read 路径贡献 |
| Write TSV Latency | `0.107 ps` | `0.213 ps` | 旧值遗漏了一部分 coarse/fine 汇总关系，新值与统一贡献账对齐 |
| Read TSV Dynamic Energy | `115.954 pJ` | `122.279 pJ` | 读路径 TSV 汇总口径已统一 |
| Mat Dynamic Energy | `6.897 pJ / mat` | `0.572 pJ / mat` | local TSV 从 mat 分项中拆出后，mat 本体代价更清楚 |

这个样例特别适合拿来做课程汇报里的“before / after”对照，因为变化非常直观：

- fine-grained 下 local TSV 的影响终于被单独展示出来
- mat 分项和 TSV 分项的职责分开了
- 结果图更适合讲“logic layer / local TSV / global TSV”的结构关系

## 6. 这轮修改对 writeup / poster / presentation 有什么帮助

你可以把这轮工作包装成下面三个贡献点：

### 6.1 建模一致性修正

核心表述建议：

- 统一了 bank / mat / result 三层的 TSV accounting
- 修正了 total TSV contribution 和分项输出之间的口径漂移

### 6.2 TSV 信号语义细化

核心表述建议：

- 将 data TSV 从笼统总数细化为 read-data 与 write-data 两类
- 为后续 signal-class-aware TSV 建模打下了代码基础

### 6.3 多层堆叠 hop 假设参数化

核心表述建议：

- 将固定 worst-case hop 假设扩展成可配置探索空间
- 可以分析不同 hop 假设下 3D stack depth 对 latency / energy 的影响

如果你要做 poster，可以直接做一张三栏图：

- 左栏：旧版 TSV 统计链路
- 中栏：新版统一 TSV 账本
- 右栏：`sample_SRAM_4layer` 的 before / after 数值对照

## 7. 还值得继续做的下一步

本轮已经把 TSV 修正从“发现问题”推进到“能运行、能解释、能展示”的阶段。后面如果你还想继续做出更大的工作量，推荐按下面顺序推进：

### 7.1 F1：control TSV 公式审计

当前 `numControlBits = stackedDieCount` 依然是高风险经验式。这个点很适合继续查 DESTINY 原文、technical report、或者 CACTI-3DD 代码来源。

### 7.2 buffered / unbuffered TSV 运行时开关

`TSV.cpp` 里已经有 buffered / unbuffered primitive 支持，后续可以把这个选项真正暴露到配置层。

### 7.3 finer-grained local TSV 信号分类

现在 `Mat.cpp` 已经把：

- row predecoder outputs
- bitline mux predecoder outputs
- sense-amp mux level 1 predecoder outputs
- sense-amp mux level 2 predecoder outputs

分开记录了。下一步你可以继续分析哪些信号应当通过 local TSV，哪些信号应当留在 logic layer 本地。

### 7.4 基于 hop model 的参数 sweep

建议至少做一组：

- `WorstCase`
- `Average`
- `Custom = 0.25 / 0.5 / 0.75`

然后观察：

- read latency
- write latency
- TSV dynamic energy
- total bank energy

这组图很适合放到 presentation 里。

## 8. 一句话总结

这轮 Stage 2 已经把 TSV 建模工作从“只有审计笔记”推进到了“代码层面的统一记账、显式语义拆分、可配置 hop 假设、以及可直接用于实验展示的结果输出”。
