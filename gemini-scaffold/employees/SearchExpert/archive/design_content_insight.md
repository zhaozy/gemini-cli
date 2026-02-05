# ContentInSight: 智能 URL 内容处理系统设计文档

## 1. 目标 (Objective)
建立一个统一的入口工具，能够根据输入的 URL 自动识别内容类型（MIME Type 或平台特征），并路由到特定的处理管线（Pipeline），最终输出结构化的内容摘要或洞察。

## 2. 架构概览 (Architecture)

```mermaid
graph TD
    A[用户输入 URL] --> B{Dispatcher (调度器)};
    B -->|检测为 YouTube/Video| C[Video Handler];
    B -->|检测为 PDF| D[PDF Handler];
    B -->|检测为 HTML/Text| E[Web/Article Handler];
    
    C --> C1[提取字幕/音频 (需外部工具)];
    C --> C2[生成: 视频时间轴摘要];
    
    D --> D1[提取文本 (PDF Parsing)];
    D --> D2[生成: 核心论点总结];
    
    E --> E1[提取正文 (Readability)];
    E --> E2[生成: 文章摘要];
```

## 3. 组件设计 (Component Design)

### 3.1 核心调度器 (Dispatcher)
- **职责**：不处理具体业务，只负责“分类”。
- **逻辑**：
    1. 正则匹配：优先检查 URL 模式（如 `youtube.com`, `.pdf` 结尾）。
    2. HTTP HEAD 探测：发送轻量级请求获取 `Content-Type` 头部。

### 3.2 处理器 (Handlers)
每个处理器不仅是一个函数，更是一个**Prompt Generator**。因为最终的“总结”和“转写”工作是由 Gemini 模型完成的，Python 脚本的角色是**数据搬运工**和**上下文构建者**。

- **VideoHandler**: 
    - 依赖：`yt-dlp` (建议) 用于获取字幕。
    - 输出：包含字幕文本的 Prompt。
- **PDFHandler**:
    - 依赖：标准库或轻量级 PDF 解析。
    - 输出：提取出的纯文本。
- **WebHandler**:
    - 依赖：`requests` + `BeautifulSoup` (可选) 或直接交给 Gemini 的 `web_fetch`。

## 4. 扩展性
未来可以轻松添加 `ImageHandler` (OCR) 或 `PodcastHandler` (音频转写)。
