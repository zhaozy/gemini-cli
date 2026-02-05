# 系统管理 SOP (复刻 Anthropic Plugin Management)

## 1. 专家入职 (Onboarding)
- 检查新雇员是否包含 `manifest.json` 和 `SOPs/`。
- 确保专家的 `capabilities` 不与现有专家发生严重冲突。

## 2. SOP 进化
- 监听用户反馈，定期在 `memory.md` 中提炼普适逻辑并反馈至 `SOPs/`。

## 3. 全局同步与版本控制
- **自动总结原则**：在调用 `.gemini/bin/git_save` 前，Agent 必须：
    1. 汇总 `walkthrough.md` 中的近期关键动作。
    2. 更新 `CHANGELOG.md`，记录版本号与变更细节。
    3. 更新 `README.md` 的“最新状态”章节。
    4. 将该总结作为参数传递给 `git_save`。
- **线性历史**：保持主分支的整洁。
