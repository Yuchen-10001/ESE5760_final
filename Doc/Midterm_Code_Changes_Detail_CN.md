# Midterm 代码改动详细说明（中文版）

这份说明整理了 midterm report 中提到的各项代码修改，并尽量做到和报告中的 defect / repair 一一对应。

需要先说明一点：

- 当前仓库快照里，**并不是** midterm report 中提到的所有修复都还完整保留在源码里。
- 因此，下面每一节都按照以下结构组织：
  - **原始代码位置**：当前基线中对应的问题代码；
  - **midterm 修复版本**：midterm 阶段应当采用的修复写法；
  - **修改原因**：说明为什么这个改动是必要的。

这份文档的目标，是为 midterm report 提供“代码层面的证据”，而不是声称当前 working tree 已经包含了所有这些修复。

## 1. 增加严格的 Process Node 合法性检查

### 原始代码位置

文件：`main.cpp`

当前基线中的逻辑如下：

```cpp
Technology techHigh;
double alpha = 0;
if (inputParameter->processNode > 200){
    // TO-DO: technology node > 200 nm
} else if (inputParameter->processNode > 120) { // 120 nm < technology node <= 200 nm
    techHigh.Initialize(200, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 120.0) / 60;
} else if (inputParameter->processNode > 90) { // 90 nm < technology node <= 120 nm
    techHigh.Initialize(120, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 90.0) / 30;
} else if (inputParameter->processNode > 65) { // 65 nm < technology node <= 90 nm
    techHigh.Initialize(90, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 65.0) / 25;
} else if (inputParameter->processNode > 45) { // 45 nm < technology node <= 65 nm
    techHigh.Initialize(65, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 45.0) / 20;
} else if (inputParameter->processNode >= 32) { // 32 nm < technology node <= 45 nm
    techHigh.Initialize(45, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 32.0) / 13;
} else if (inputParameter->processNode >= 22) { // 22 nm < technology node <= 32 nm
    techHigh.Initialize(32, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 22.0) / 10;
} else {
    //TO-DO: technology node < 22 nm
}
```

### Midterm 修复版本

```cpp
Technology techHigh;
double alpha = 0;

if (inputParameter->processNode < 22 || inputParameter->processNode > 200) {
    cout << "[ERROR] Process node " << inputParameter->processNode
         << "nm is outside the supported DESTINY range of 22nm to 200nm." << endl;
    exit(-1);
}

if (inputParameter->processNode > 120) {
    techHigh.Initialize(200, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 120.0) / 60;
} else if (inputParameter->processNode > 90) {
    techHigh.Initialize(120, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 90.0) / 30;
} else if (inputParameter->processNode > 65) {
    techHigh.Initialize(90, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 65.0) / 25;
} else if (inputParameter->processNode > 45) {
    techHigh.Initialize(65, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 45.0) / 20;
} else if (inputParameter->processNode >= 32) {
    techHigh.Initialize(45, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 32.0) / 13;
} else {
    techHigh.Initialize(32, inputParameter->deviceRoadmap, inputParameter);
    alpha = (inputParameter->processNode - 22.0) / 10;
}
```

### 修改原因

原始代码在 `processNode < 22nm` 或 `processNode > 200nm` 时并不会真正阻止程序继续运行，而是落入未完成的 `TODO` 分支。这会导致后续插值过程使用不完整或未定义状态。midterm 修复把它改成显式报错并终止运行。

## 2. 对非 2 次幂 associativity 恢复 fail-fast

### 原始代码位置

文件：`main.cpp`

```cpp
if (!isPow2(inputParameter->associativity)) {
    cout << "[ERROR] The associativity value has to be a power of 2 in this version" << endl;
    //exit(-1);
}
```

### Midterm 修复版本

```cpp
if (!isPow2(inputParameter->associativity)) {
    cout << "[ERROR] The associativity value has to be a power of 2 in this version" << endl;
    exit(-1);
}
```

### 修改原因

原始代码虽然打印了错误信息，但并没有真正终止执行。这样程序会在非法 cache geometry 下继续搜索设计空间，输出结果就会带有误导性。midterm 修复恢复了 `exit(-1)`，保证非法输入立即失败。

## 3. 重新启用 eDRAM 专用 technology path

### 原始代码位置

文件：`main.cpp`

```cpp
devtech = tech;

if (cell->memCellType == eDRAM && false) {
    devtech = new Technology();
    devtech->Initialize(inputParameter->processNode, EDRAM, inputParameter);
}

...

if (cell->memCellType == eDRAM && false) {
    delete devtech;
}
```

### Midterm 修复版本

```cpp
devtech = tech;

if (cell->memCellType == eDRAM) {
    devtech = new Technology();
    devtech->Initialize(inputParameter->processNode, EDRAM, inputParameter);
}

...

if (cell->memCellType == eDRAM) {
    delete devtech;
}
```

### 修改原因

原始代码里的 `&& false` 会让 eDRAM 专用初始化路径永久失效，导致 eDRAM 实际上走的是通用 peripheral technology flow，而不是原本 intended 的专用路径。

## 4. 增加显式 `ReadEnergy` 支持

### 原始代码位置

文件：`MemCell.h`

```cpp
double readVoltage;     /* Read voltage */
double readCurrent;     /* Read current */
double minSenseVoltage; /* Minimum sense voltage */
double wordlineBoostRatio;
double readPower;       /* Read power per bitline (uW)*/
```

文件：`MemCell.cpp`

```cpp
if (!strncmp("-ReadPower", line, strlen("-ReadPower"))) {
    sscanf(line, "-ReadPower (uW): %lf", &readPower);
    readPower /= 1e6;
    continue;
}
```

也就是说，原始解析器根本没有处理：

```text
-ReadEnergy (pJ): ...
```

### Midterm 修复版本

文件：`MemCell.h`

```cpp
double readVoltage;     /* Read voltage */
double readCurrent;     /* Read current */
double minSenseVoltage; /* Minimum sense voltage */
double wordlineBoostRatio;
double readPower;       /* Read power per bitline (W) */
double readEnergy;      /* Explicit read energy per cell (J) */
```

文件：`MemCell.cpp`

```cpp
readPower = 0;
readEnergy = 0;
```

```cpp
if (!strncmp("-ReadPower", line, strlen("-ReadPower"))) {
    sscanf(line, "-ReadPower (uW): %lf", &readPower);
    readPower /= 1e6;
    continue;
}

if (!strncmp("-ReadEnergy", line, strlen("-ReadEnergy"))) {
    sscanf(line, "-ReadEnergy (pJ): %lf", &readEnergy);
    readEnergy /= 1e12;
    continue;
}
```

### 修改原因

`sample_RRAM.cell` 里明确提供了 `-ReadEnergy (pJ): 0.1`，但原始代码完全忽略这个输入。midterm 修复的目的，是让用户明确提供的能耗参数真正进入模型。

## 5. 修正 subarray 路径中的 read-energy 选择逻辑

### 原始代码位置

文件：`SubArray.cpp`

```cpp
if (cell->readPower == 0) 
    cellReadEnergy = 2 * cell->CalculateReadPower() * senseAmp.readLatency; /* x2 is because of the reference cell */
else
    cellReadEnergy = 2 * cell->readPower * senseAmp.readLatency;
cellReadEnergy *= numColumn / muxSenseAmp / muxOutputLev1 / muxOutputLev2;
```

### Midterm 修复版本

```cpp
if (cell->readEnergy > 0) {
    cellReadEnergy = 2 * cell->readEnergy;
} else if (cell->readPower > 0) {
    cellReadEnergy = 2 * cell->readPower * senseAmp.readLatency;
} else {
    cellReadEnergy = 2 * cell->CalculateReadPower() * senseAmp.readLatency;
}

cellReadEnergy *= numColumn / muxSenseAmp / muxOutputLev1 / muxOutputLev2;
```

### 修改原因

原始逻辑只会在 `explicit readPower` 和 `derived read power` 之间二选一，完全没有 `readEnergy` 的入口。因此即便 cell file 已经给了明确的 `ReadEnergy`，程序仍然会走 fallback 推导路径。

## 6. 防止导出的 Read Power 变成负值

### 原始代码位置

文件：`MemCell.cpp`

```cpp
double MemCell::CalculateReadPower() { /* TO-DO consider charge pumped read voltage */
    if (readPower == 0) {
        if (cell->readMode) {   /* voltage-sensing */
            if (readVoltage == 0) { /* Current-in voltage sensing */
                return tech->vdd * readCurrent;
            }
            if (readCurrent == 0) { /*Voltage-divider sensing */
                double resInSerialForSenseAmp, maxBitlineCurrent;
                resInSerialForSenseAmp = sqrt(resistanceOn * resistanceOff);
                maxBitlineCurrent = (readVoltage - voltageDropAccessDevice) / (resistanceOn + resInSerialForSenseAmp);
                return tech->vdd * maxBitlineCurrent;
            }
        } else { /* current-sensing */
            double maxBitlineCurrent = (readVoltage - voltageDropAccessDevice) / resistanceOn;
            return tech->vdd * maxBitlineCurrent;
        }
    } else {
        return -1.0; /* should not call the function if read energy exists */
    }
    return -1.0;
}
```

### Midterm 修复版本

```cpp
double MemCell::CalculateReadPower() {
    if (readPower > 0) {
        return readPower;
    }

    if (readMode) { /* voltage-sensing */
        if (readVoltage == 0) {
            return tech->vdd * readCurrent;
        }

        if (readCurrent == 0) {
            double resInSerialForSenseAmp = sqrt(resistanceOn * resistanceOff);
            double effectiveReadVoltage = readVoltage - voltageDropAccessDevice;
            if (effectiveReadVoltage < 0) {
                effectiveReadVoltage = 0;
            }
            double maxBitlineCurrent = effectiveReadVoltage / (resistanceOn + resInSerialForSenseAmp);
            return tech->vdd * maxBitlineCurrent;
        }
    } else { /* current-sensing */
        double effectiveReadVoltage = readVoltage - voltageDropAccessDevice;
        if (effectiveReadVoltage < 0) {
            effectiveReadVoltage = 0;
        }
        double maxBitlineCurrent = effectiveReadVoltage / resistanceOn;
        return tech->vdd * maxBitlineCurrent;
    }

    return 0;
}
```

### 修改原因

对于 `sample_RRAM.cell` 来说，原始代码在 current-sensing 路径上会直接计算：

```text
(0.3 - 1.8) / resistanceOn
```

也就是负电压差，结果得到负电流，再乘上 `Vdd` 变成负功率，最后在 `SubArray.cpp` 里又被乘以正的 latency 变成负能耗。midterm 修复通过对 `effectiveReadVoltage` 做下界钳位，消除了这个非物理现象。

另外，这个修复也顺便把 `cell->readMode` 改成直接使用对象自己的 `readMode` 字段，避免依赖全局指针。

## 7. 修复 `SetVoltage` parser 的 copy/paste bug

### 原始代码位置

文件：`MemCell.cpp`

```cpp
if (!strncmp("-SetVoltage", line, strlen("-SetVoltage"))) {
    sscanf(line, "-ResetVoltage (V): %s", tmp);
    if (!strcmp(tmp, "vdd"))
        resetVoltage = tech->vdd;
    else
        sscanf(line, "-SetVoltage (V): %lf", &setVoltage);
    continue;
}
```

### Midterm 修复版本

```cpp
if (!strncmp("-SetVoltage", line, strlen("-SetVoltage"))) {
    sscanf(line, "-SetVoltage (V): %s", tmp);
    if (!strcmp(tmp, "vdd"))
        setVoltage = tech->vdd;
    else
        sscanf(line, "-SetVoltage (V): %lf", &setVoltage);
    continue;
}
```

### 修改原因

原始代码在解析 `SetVoltage` 时错误地复用了 `ResetVoltage` 的格式串，甚至在 `vdd` 分支里把值写到了 `resetVoltage`。这是一个很典型的 copy/paste bug。

## 8. 同时接受 `AllowDifferentTagTech` 和 `AllowDifferenceTagTech`

### 原始代码位置

README 中使用的是：

```text
-AllowDifferenceTagTech
```

但是解析器只接受：

```cpp
if (!strncmp("-AllowDifferentTagTech", line, strlen("-AllowDifferentTagTech"))) {
    sscanf(line, "-AllowDifferentTagTech: %s", tmp);
    if (!strcmp(tmp, "true"))
        allowDifferentTagTech = true;
    else
        allowDifferentTagTech = false;
    continue;
}
```

### Midterm 修复版本

文件：`InputParameter.cpp`

```cpp
if (!strncmp("-AllowDifferentTagTech", line, strlen("-AllowDifferentTagTech")) ||
    !strncmp("-AllowDifferenceTagTech", line, strlen("-AllowDifferenceTagTech"))) {
    if (!strncmp("-AllowDifferentTagTech", line, strlen("-AllowDifferentTagTech")))
        sscanf(line, "-AllowDifferentTagTech: %s", tmp);
    else
        sscanf(line, "-AllowDifferenceTagTech: %s", tmp);

    if (!strcmp(tmp, "true"))
        allowDifferentTagTech = true;
    else
        allowDifferentTagTech = false;
    continue;
}
```

### 修改原因

这是一个“文档和实现不一致”的问题。用户按照 README 正确填写参数，也可能因为参数名拼写差异而完全没有生效。midterm 修复的目标，是同时兼容两种写法，避免用户踩坑。

## 9. 可用于总结的 patch 范围

如果需要把 midterm 这批改动概括成一组 patch，可以写成：

- `main.cpp`
  - 增加 process-node 合法范围检查
  - 恢复 associativity 非法时的 fail-fast
  - 重新启用 eDRAM 专用 technology path
- `MemCell.h`
  - 增加 `readEnergy` 字段
- `MemCell.cpp`
  - 增加 `ReadEnergy` 解析
  - 修复 `SetVoltage` parser
  - 修复 `CalculateReadPower` 中的负电压差问题
  - 当显式 `readPower` 已提供时直接返回
- `SubArray.cpp`
  - 优先使用显式 `readEnergy`
- `InputParameter.cpp`
  - 同时接受 `AllowDifferentTagTech` 和 `AllowDifferenceTagTech`
- `README`
  - 和 parser 支持的参数名保持一致

## 10. 可直接放进回复老师的话

如果你想在邮件里用一句话概括这些代码改动，可以写成：

> 除了报告中的文字说明之外，我们也已经定位并整理了对应的代码修改点，包括：对非法 process node 和 associativity 的 fail-fast 检查、重新启用 eDRAM 专用路径、增加 `ReadEnergy` 支持、修复 `SetVoltage` 解析错误，以及修复 memristor current-sensing 路径中会导出负 read power 的问题。
