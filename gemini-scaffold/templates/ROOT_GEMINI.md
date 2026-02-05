# Workspace Global: 全局工作区规范

本文件定义了 `gemini-files` 工作区的最高准则。它是所有子项目、引擎和实验的“宪法”。

## 1. 认知层级与目录规范 (Cognition Hierarchy)

为了确保复杂系统开发的清晰度，我们采用**分层管理模式**：

### 1.1 全局层 (Global Level - 根目录)
- **职责**：定义工程哲学 ([THE_CODE_TAO.md](docs/THE_CODE_TAO.md))、通用环境规范 (uv, Python)、数字雇员阵列 (`employees/`) 的协调。
- **持久化**：根目录下的 `.gemini/tasks/` 用于记录涉及工作区架构、全局配置或跨项目协作的任务。
- **上下文**：根目录下的 `GEMINI.md` (即本文件)。

### 1.2 协作层 (Collaboration Level - projects/ 目录)
- **职责**：所有与用户合作完成的**独立工作单元**。包括但不限于：业务分析、工具开发、技术研究、文档创作、实验项目等。
- **原则**：任何具有独立生命周期的新话题，必须在 `projects/` 下拥有专属目录。
- **持久化**：每个协作单元目录下的 `.gemini/tasks/`。

### 1.3 自动化初始化原则 (Automated Initialization)
**强制指令**：当 Agent 识别到进入一个新话题、需要开启一项独立工作或创建新项目时，必须遵循以下物理约束：
1. **路径强制**：所有新协作单元**必须**创建在根目录的 `projects/` 文件夹下。
2. **自动仓库化**：通过 `gh` CLI 自动为新项目创建 GitHub 私有仓库并执行首次推送。
3. **创建上下文**：在 `projects/{{unit_name}}/` 根目录下生成 `GEMINI.md`。
3. **建立认知锚点**：创建 `.gemini/tasks/` 目录及其初始化文件（`current_task.md` 等）。

## 2. 环境规范 (Environment Standards)

- **语言偏好**：始终使用**简体中文**（回复、注释、文档、推理、记忆文件）。
- **工具链 (The Astral Stack)**：
    - **包管理器**：必须使用 `uv`。
    - **代码质量**：使用 `ruff` 进行 Lint 和 Formatting。
    - **测试框架**：统一使用 `pytest`。
    - **类型安全**：强制要求静态类型注解（Type Hints），确保符合 `mypy` 或 `pyright` 标准。
- **环境隔离**：必须使用项目根目录的 `.venv`。

## 3. 核心架构：核壳分离与数字雇员 (Core-Shell & Workforce)

所有代码必须遵循此物理定律：
- **The Core (核)**：纯计算逻辑，无 IO，无副作用，100% 可测试。
- **The Shell (壳)**：负责 IO、日志、配置加载及异常拦截。
- **不可变性**：禁止 `inplace=True`，坚持 `Output = Function(Input)`。
- **显式契约**：禁止传递裸 `dict`，必须使用 `dataclass`。
- **统计自适应 (Statistical Adaptation)**：**严禁硬编码**业务判定阈值（如 `AOV > 50`）。必须使用统计学分位数（如 `Q3/80分位`）或标准分（`Z-Score`）来定义指标的“高/低/强/弱”，确保算法能自动适配不同分布的数据。
- **计算-叙事解耦 (Decoupling)**：分析流程必须分为“数据计算层”（输出纯净、无结论的结构化 JSON）与“认知表达层”（基于数据由 Agent 撰写具备逻辑叙事性的报告）。
- **Digital Workforce (数字雇员)**：位于 `employees/` 目录。Agent 在处理任务时必须遵循“联合办公 (Co-working) 协议”。

## 4. 专家联合办公协议 (Co-working Protocol)
当任务涉及多个领域时，Agent 必须启动“接力式处理”：
1. **定义流水线**：例如，处理数据合规任务，必须按顺序激活 `DataAnalyst` (提取逻辑) -> `LegalCounsel` (审核风险)。
2. **跨专家校验**：后一个专家必须审计前一个专家的输出。
3. **一致性汇总**：最终报告必须标注所有参与贡献的专家名称。

## 5. 执行状态持久化 (Persistence of Cognition)

在执行任何任务前，Agent 必须在**对应层级**的 `.gemini/tasks/` 中初始化并**持续维护**以下文件。

### 5.1 层级职责差异
- **全局层 (`root/.gemini/tasks/`)**：
    - `current_task.md`: **全局焦点**。记录当前用户关注的主项目或工作区级的维护任务。
    - `memory.md`: **用户画像与全局状态**。记录用户偏好、工作区技术栈变迁历史。
- **协作层 (`projects/unit/.gemini/tasks/`)**：
    - 关注该具体任务内部的开发进度。

### 5.2 核心文件定义
- `current_task.md`: 原始需求与子任务。
- `implementation_plan.md`: 详细执行路径。
- `walkthrough.md`: 关键决策与执行记录。
- `memory.md`: **任务级长期记忆**。记录跨任务的业务知识、技术债、架构决策 (ADR) 及长期规划。

**主动同步原则 (Active Syncing)**：
- **无需用户提醒**：Agent 承担维护认知一致性的第一责任。
- **阶段性汇报**：在每一个子任务完成、决策发生转折或遇到阻塞时，Agent 必须主动更新上述文件，并在回复中简要告知用户当前在持久化层面的进展。

## 6. 认知生命周期 (Cognitive Lifecycle)

### 6.1 沉淀 (Sedimentation): Task -> Memory
- **触发时机**：`current_task` 结束或关键子任务完成时。
- **执行动作**：提炼 `walkthrough.md` 中的复用性高信息写入 `memory.md`。

### 6.2 升华 (Sublimation): Memory -> Standard
- **触发时机**：当某条记忆被验证具有普适性。
- **执行动作**：将规则提升至 `Project GEMINI.md` 或根目录 `GEMINI.md`。

### 6.3 全局同步 (Global Sync): Action -> Global State
- **触发时机与原子交接 (Atomic Handover)**：
    1. **焦点切换**：切换工作目录时必须先存档、更焦点、再唤醒。
    2. **偏好习得**：收到用户纠正时实时记录至全局 `memory.md`。
    3. **版图变迁**：新项目创建或旧项目归档。

## 7. 引导启动与记忆唤醒 (Bootstrap & Context Recovery)

当 CLI 重启或 Agent 首次进入该工作区时，Agent 必须遵循以下**自动唤醒逻辑**：
1. **全局嗅探**：检查根目录下的 `GEMINI.md`，理解全局工程哲学和环境规范。
2. **项目定位**：识别当前工作的子目录。
3. **认知恢复**：优先读取最近修改的 `.gemini/tasks/current_task.md`，重建上一次会话的“认知现场”。
4. **主动汇报**：简要概述“上一次状态”及“建议的后续步骤”。

## 9. 版本控制工作流 (Git Workflow)

所有协作单元和系统层必须遵循“先存档、后变更”的原则：

1. **自动快照**：利用 `.gemini/bin/git_save` 进行阶段性提交。

2. **分支开发**：重大功能变更或风险实验必须使用 `git_task start` 开启分支。

3. **线性历史**：保持主分支的整洁，通过 Merge Commit 记录任务合并。
