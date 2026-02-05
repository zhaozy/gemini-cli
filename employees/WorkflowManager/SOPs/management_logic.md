# 系统管理 SOP (复刻 Anthropic Plugin Management)

## 1. 专家入职 (Onboarding)
- 检查新雇员是否包含 `manifest.json` 和 `SOPs/`。
- 确保专家的 `capabilities` 不与现有专家发生严重冲突。

## 2. SOP 进化
- 监听用户反馈，定期在 `memory.md` 中提炼普适逻辑并反馈至 `SOPs/`。

## 3. 全局同步与版本控制
- 定期触发 `sync_to_scaffold.sh`，确保“安装母盘”处于最新状态。
- **原子提交原则**：在每个子任务完成并记录至 `walkthrough.md` 后，应调用 `.gemini/bin/git_save` 执行本地快照。
- **任务隔离**：处理复杂实验性任务前，调用 `.gemini/bin/git_task start` 开启独立分支。
