# 零售全链路经营诊断系统 (V5.0 旗舰版)

> **"从订单流水到战略决策：全时空、全渠道、全SKU的深度穿透。"**

本系统专用于分析复杂的零售交易流水数据。通过“五力诊断模型”，为运营方提供具备咨询级深度的商业见解。

## 🌟 核心诊断模型：五力矩阵

1.  **商品战略人格**：基于渗透率与带动系数，将 SKU 划分为“钩子(Hooks)”、“孤岛(Islands)”与“刺客(Assassins)”。
2.  **价格引力诊断**：基于“清洁基准期”的折扣弹性分析，精准识别对促销敏感的红榜商品。
3.  **篮筐品质指纹**：利用复杂度聚类算法，还原用户的真实购买行为画像。
4.  **时空生活嵌入**：通过 TGI 热力分析，识别不同时间段（晨间、午间、深夜）的心智商品。
5.  **渠道效率矩阵**：横向对比全渠道（App, 美团, 饿了么等）的 GMV 贡献与经营效率。

## 🛡️ 数据严谨性保障 (DataAnalyst Audit)

- **样本显著性校验**：自动过滤促销天数不足（n<3）的 SKU，消除统计偏见。
- **价格稳定性审计**：严格基于“折扣类型”字段识别真实价格波动，不被订单级满减分摊所误导。
- **自动脱敏合规**：报告生成过程符合 `LegalCounsel` 审计规范，不暴露敏感明细数据。

## 🚀 快速运行

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/projects
cd projects/order_analysis
../../.venv/bin/python src/strategic_pipeline.py
../../.venv/bin/python src/generators/strategic_reporter.py
```

## 📂 产出报告

- **战略白皮书**: `reports/diagnostics_v5/report_global_v4.html`
- **渠道深潜**: 各渠道独立的 HTML 诊断书。
