# DataInsightAnalyst 方法论：实证主义分析指南

## 1. 三维实证模型 (The Triple-Reference Model)

任何单一指标的趋势判定，必须基于以下三维坐标系：

### 1.1 纵向：季节性校准 (Seasonality Calibration)
- **公式**：$YoY_Gap_t = Value_{Y,t} - Value_{Y-1,t}$
- **逻辑**：只有当 $YoY_Gap$ 的斜率发生改变时，才认为趋势发生了结构性变化。

### 1.2 横向：市场博弈校准 (Market Calibration)
- **指标**：$SPI_t = \frac{Value_{target,t}}{Value_{benchmark,t}}$
- **逻辑**：SPI 向上代表跑赢大盘（Alpha），SPI 持平代表随大流（Beta）。

### 1.3 动能：加速度校准 (Momentum Calibration)
- **方法**：计算 3 个月滚动斜率（Rolling Slope）。
- **逻辑**：斜率从负转正（Red to Green）是“触底反弹”的第一信号。

## 2. 序列结构变迁模型 (Sequential Structural Shift)

### 2.1 轨迹追踪 (The Trace)
- 拒绝两点式对比（Pre/Post），采用三点或多点式追踪：$T_{pre} \to T_{interim} \to T_{post}$。
- 观察每个 Segment（画像/品类）的绝对人数曲线。

### 2.2 置换效应计算 (Displacement Effect)
- **净变动**：$\Delta Total = \sum \Delta Segment_i$
- **置换率**：$Churn = \frac{\sum | \Delta Segment_i | - | \Delta Total |}{2 \times Total_{pre}}$
- **解读**：高 Churn 代表发生了剧烈的“腾笼换鸟”，即使 Total 保持不变。

## 3. 效能背离诊断 (Divergence Diagnosis)

- **流量-效率矩阵**：
    - **Traffic $\uparrow$ & Conv $\uparrow$**：良性扩张（明星）。
    - **Traffic $\uparrow$ & Conv $\downarrow$**：流量稀释（虚胖）。
    - **Traffic $\downarrow$ & Conv $\uparrow$**：客群提纯（缩编）。
    - **Traffic $\downarrow$ & Conv $\downarrow$**：全面衰退（危机）。

## 4. 分析红线与纪律

1. **逻辑一致性测试**：在计算占比前，必须验证 $\sum Parts = Total$。
2. **拒绝过度推论**：
    - *错误*：“客流涨了是因为服务变好了。”
    - *正确*：“客流涨了，且此时段新客占比提升 X%，转化率保持平稳，实现了高质量吸纳。”
3. **因果隔离**：利用 24 个月全量数据提取各月斜率，观察动作发生前的“惯性”，判定动作是否真的“改变了物理轨迹”。
