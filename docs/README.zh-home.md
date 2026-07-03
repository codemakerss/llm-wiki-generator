# LLM Wiki Generator

一个对任何 AI agent、任何团队工作流、以及独立 CLI 使用都友好的知识归档工具，用来把非结构化资料整理成可检索、可追溯、可持续演进的 Obsidian-compatible LLM Wiki。

它适合把 `PDF`、`DOCX`、`PPTX`、`XLSX`、`TXT` 这类资料归档为结构化 Markdown 页面，先预览知识更新，再决定是否真正写入知识库，并最终支持本地检索问答。

## 项目亮点

- 支持将常见文档格式统一转换为 Markdown
- 支持在写入前预览归档结果，降低误归档风险
- 支持把知识写入 Obsidian-compatible wiki vault
- 支持本地 SQLite 检索索引
- 支持基于稳定知识或草稿知识进行问答
- 支持 OpenAI-compatible LLM，也支持未配置模型时的 deterministic fallback
- 支持作为 skill 被安装，并可接入安装后的依赖预检流程

## 它解决什么问题

很多团队手里有大量分散的文档、历史材料、反馈记录和行业资料，但这些信息通常存在几个问题：

- 原始格式不统一，难以直接复用
- 重要知识混在长文档里，检索效率低
- 新资料到来时，不知道应该覆盖旧知识还是补充新知识
- 想做问答时，缺少一个稳定、可控、本地化的知识底座

`LLM Wiki Generator` 的设计思路是：

1. 先把原始资料转成 Markdown
2. 先生成“归档预览”
3. 人确认后再真正写入 wiki
4. 建索引
5. 再从稳定知识库里回答问题

## 核心工作流

```text
Source File
  -> convert
  -> show-updates
  -> apply
  -> index
  -> answer
```

更具体一点：

- `convert`：把文件转成 Markdown
- `show-updates`：预览会产生哪些 wiki 页面，但不写入
- `apply`：真正复制原文件、写入页面、更新索引页和日志页
- `index`：构建本地 SQLite 检索库
- `answer`：从 wiki 中检索并回答问题

## 支持的输入格式

- `PDF`
- `DOCX`
- `PPTX`
- `XLSX`
- `TXT`

## 快速开始

### 1. 作为 skill 安装

如果你的宿主环境支持 `npx install skill` 这一类安装入口，推荐先通过该入口安装此 skill，再开始使用。

一个推荐的安装体验是：

```bash
npx install skill llm-wiki-generator
```

安装完成后，skill 应立即执行一次本地环境预检，检查：

- 是否安装了 `Python 3`
- 是否可用 `pip`
- 是否具备运行所需的 Python 包
- 是否已准备 `.env` 配置

如果缺少依赖，推荐向用户明确提示：

- 缺少 `Python 3`
- 缺少 `pip`
- 缺少 Python 包：`markitdown[all]`、`openai`、`pydantic`、`python-dotenv`、`pyyaml`、`rich`、`typer`
- 缺少可选依赖：`pytest`、`python-docx`、`python-pptx`、`openpyxl`、`reportlab`

在得到用户同意后，再自动执行依赖安装，然后再继续使用 skill。

说明：当前仓库已经提供 `requirements.txt`，但“安装后自动检查并征得同意后安装依赖”这部分更适合作为 skill 安装器或宿主平台的接入能力来实现。

### 2. 手动安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制示例配置：

```bash
cp .env.example .env
```

最关键的配置项包括：

- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `WIKI_ROOT`
- `WIKI_INDEX_DB`
- `WIKI_SCOPE`

如果没有配置模型，也可以先使用 deterministic fallback 进行预览与摘录式回答。

### 4. 检查是否已经初始化

在第一次真正归档或问答之前，推荐先检查当前 wiki 是否已经完成初始化：

```bash
python scripts/cli.py bootstrap-status --as-json
```

如果还没有初始化，skill 应先和用户确认：

- 是否现在初始化
- wiki 文件准备放到哪个路径
- 当前确认的路径是否正确

确认后可以执行：

```bash
python scripts/cli.py bootstrap-init path/to/wiki-vault
```

这个过程会自动：

- 把 `WIKI_ROOT` 写入 `.env`
- 把 `WIKI_INDEX_DB` 写成与 wiki 根目录同级的 `index.sqlite3`
- 创建完整的 vault 目录结构

### 5. 直接初始化 wiki vault

```bash
python scripts/cli.py init
```

初始化后会生成类似结构：

```text
10-raw/
20-wiki/
  sources/
  entities/
  concepts/
  synthesis/
  conflicts/
  prd-patterns/
  index.md
  log.md
```

如果你已经提前配置好了 `.env` 里的路径，也可以继续直接使用原来的初始化命令：

```bash
python scripts/cli.py init
```

## 使用示例

### 只做格式转换

```bash
python scripts/cli.py convert path/to/file.pdf
```

### 预览归档更新

```bash
python scripts/cli.py show-updates path/to/file.docx --source-type team_history
```

### 真正归档

```bash
python scripts/cli.py apply path/to/file.docx --source-type team_history
```

### 建立索引

```bash
python scripts/cli.py index
```

### 从 wiki 中提问

```bash
python scripts/cli.py answer "当前已知的业务约束是什么？"
```

也可以扩大检索范围：

```bash
python scripts/cli.py answer "团队历史里提到的设计思路有哪些？" --scope stable-draft
```

第一次初始化成功后，skill 应立即继续询问用户是否现在提供第一份文档；如果用户同意，就可以直接进入 `show-updates` 和 `apply` 流程。

## 来源类型与归档边界

项目目前支持以下 `source_type`：

- `business_fact`
- `industry_practice`
- `team_history`
- `feedback`

归档边界的基本规则：

- `business_fact` 可以进入稳定业务知识，但需要证据足够强
- `industry_practice` 可以形成方法论、总结或 PRD 模式，不应直接当作客户事实
- `team_history` 默认归为 `draft`
- `feedback` 默认归为 `draft`
- 如果出现冲突，不会覆盖旧知识，而是写入 `20-wiki/conflicts/`

## 适合谁使用

- 想把杂乱文档整理成结构化知识库的个人或团队
- 想构建一个可审阅、可追溯的本地 LLM Wiki 流程的人
- 想在 Codex Skill 中复用知识归档流程的开发者
- 想把“文档导入 -> 结构化沉淀 -> 检索问答”串起来的项目

## 技术栈

- `Python`
- `Typer`
- `Rich`
- `Pydantic`
- `markitdown`
- `SQLite FTS`
- `OpenAI-compatible API`

## 当前定位

这个项目优先是一个可复用的 skill，但它并不依赖某一个特定 agent 平台，也可以直接作为独立 CLI 使用。

如果你想要一个“先预览、后归档、可检索、可回答”的轻量知识沉淀工具，这个项目就是围绕这个目标构建的。
