# 实施计划: 战略诊断系统

## 阶段 0: 工程治理 (已完成)
- [x] 将旧报告归档至 `reports/archive/`。
- [x] 删除冗余脚本。
- [x] 建立模块化目录结构 `src/strategies/`。

## 阶段 1: 整体概览与渠道效率 (已完成)
- [x] 实现 `overview_strategy.py`。
- [x] 计算大盘核心指标与渠道排名。
- [x] 实现自适应生态位判定。

## 阶段 2: 商品与价格策略 (已完成)
- [x] 实现 `product_strategy.py` (渗透-带动矩阵, ABC-XYZ)。
- [x] 实现 `pricing_strategy.py` (价格审计, 偏态分析, 动态弹性)。

## 阶段 3: 时空与篮筐特征 (已完成)
- [x] 实现 `temporal_strategy.py` (TGI 热力, 异动系数)。
- [x] 实现 `basket_strategy.py` (复杂度聚类, 孤儿单诊断)。

## 阶段 4: 报告生成与交付 (已完成)
- [x] 开发 `strategic_reporter.py` 渲染引擎。
- [x] 产出 Markdown 与 HTML 格式的全套报告。