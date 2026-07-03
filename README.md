# LLM Wiki Generator

LLM Wiki Generator is friendly to any AI agent, any team workflow, and standalone CLI usage. It turns unstructured documents into a searchable, traceable, Obsidian-compatible LLM Wiki.

It helps you ingest `PDF`, `DOCX`, `PPTX`, `XLSX`, and `TXT` files, preview knowledge updates before writing anything, archive structured wiki pages, build a local retrieval index, and answer questions from stable or draft knowledge.

## Why This Project Exists

Most teams already have a lot of useful knowledge, but it is scattered across long documents, meeting notes, historical writeups, feedback files, and external references.

That creates a few common problems:

- source formats are inconsistent
- reusable knowledge is buried in long files
- new material is hard to merge safely into an existing knowledge base
- direct “chat with documents” setups often lack structure and auditability

LLM Wiki Generator is designed around a safer workflow:

1. convert source files into Markdown
2. preview archive updates first
3. apply only the updates you want
4. build a local retrieval index
5. answer questions from the wiki

## Key Features

- Convert common document formats into Markdown
- Preview archive changes before writing anything
- Write structured wiki pages into an Obsidian-compatible vault
- Build a local SQLite retrieval index
- Answer questions from stable knowledge or include draft knowledge when needed
- Work with an OpenAI-compatible model or fall back to deterministic behavior
- Fit into skill-based installation flows with dependency preflight guidance

## Workflow

```text
Source File
  -> convert
  -> show-updates
  -> apply
  -> index
  -> answer
```

Command meanings:

- `convert`: extract Markdown from a source file
- `show-updates`: preview which wiki pages would be created or updated
- `apply`: copy raw files and write wiki pages
- `index`: build the local SQLite/FTS retrieval index
- `answer`: retrieve from the wiki and answer a question

## Supported Inputs

- `PDF`
- `DOCX`
- `PPTX`
- `XLSX`
- `TXT`

## Quick Start

### 1. Install as a skill

If your host environment supports an `npx install skill` style entrypoint, the recommended flow is to install this project as a skill before using it as a CLI.

For example:

```bash
npx install skill llm-wiki-generator
```

After installation, the skill should run a local preflight check that validates:

- `Python 3` is installed
- `pip` is available
- required Python packages are available
- `.env` exists and core configuration is present

If the environment is incomplete, the skill should clearly tell the user what is missing, for example:

- missing `Python 3`
- missing `pip`
- missing required Python packages: `markitdown[all]`, `openai`, `pydantic`, `python-dotenv`, `pyyaml`, `rich`, `typer`
- missing optional packages for extended document workflows: `pytest`, `python-docx`, `python-pptx`, `openpyxl`, `reportlab`

After the user agrees, the installer can install the missing dependencies and then continue.

Note: this repository already provides `requirements.txt`, but the automatic “check first, ask for consent, then install” flow is better implemented by the skill installer or host platform wrapper.

### 2. Install dependencies manually

```bash
pip install -r requirements.txt
```

### 3. Create your environment file

```bash
cp .env.example .env
```

Important configuration values:

- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `WIKI_ROOT`
- `WIKI_INDEX_DB`
- `WIKI_SCOPE`

If no model is configured, the project still works in deterministic fallback mode.

### 4. Check initialization status

Before your first archive/query flow, check whether the wiki has already been initialized:

```bash
python scripts/cli.py bootstrap-status --as-json
```

If the wiki is not initialized yet, the skill should first ask:

- whether you want to initialize now
- where the wiki vault should be created
- whether the confirmed path is correct

Then initialize it by persisting the chosen location and creating the vault structure:

```bash
python scripts/cli.py bootstrap-init path/to/wiki-vault
```

This writes:

- `WIKI_ROOT=<chosen wiki root>`
- `WIKI_INDEX_DB=<sibling index.sqlite3 path>`

and immediately prepares the folder structure.

### 5. Initialize the vault directly

```bash
python scripts/cli.py init
```

This creates a structure like:

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

If you already know your desired `WIKI_ROOT`, you can still run the original initializer directly:

```bash
python scripts/cli.py init
```

`init` remains deterministic and uses the current `.env` configuration.

## Example Commands

### Convert only

```bash
python scripts/cli.py convert path/to/file.pdf
```

### Preview archive updates

```bash
python scripts/cli.py show-updates path/to/file.docx --source-type team_history
```

### Apply archive updates

```bash
python scripts/cli.py apply path/to/file.docx --source-type team_history
```

### Build the retrieval index

```bash
python scripts/cli.py index
```

### Ask a question

```bash
python scripts/cli.py answer "What business constraints are currently known?"
```

Include draft knowledge when needed:

```bash
python scripts/cli.py answer "What design ideas were mentioned in team history?" --scope stable-draft
```

After a successful first-time initialization, the skill should immediately ask whether you want to provide your first document now. If you do, continue directly into `show-updates` and `apply`.

## Source Types and Boundaries

Supported `source_type` values:

- `business_fact`
- `industry_practice`
- `team_history`
- `feedback`

Boundary rules:

- `business_fact` may become stable business knowledge when evidence is strong
- `industry_practice` may become patterns or synthesis, but should not be treated as customer truth
- `team_history` defaults to `draft`
- `feedback` defaults to `draft`
- conflicts never overwrite older knowledge; they go into `20-wiki/conflicts/`

## Who It Is For

- teams building an auditable local knowledge workflow
- developers who want a reusable Codex skill for archive-and-retrieval flows
- practitioners who prefer “preview before write” instead of direct blind ingestion
- anyone who wants a lightweight bridge from documents to structured wiki knowledge

## Tech Stack

- `Python`
- `Typer`
- `Rich`
- `Pydantic`
- `markitdown`
- `SQLite FTS`
- `OpenAI-compatible API`

## Positioning

This project is primarily designed as a reusable skill, but it is intentionally platform-agnostic and does not depend on one specific agent runtime.

If you want a small, practical pipeline for converting files, reviewing knowledge updates, archiving them safely, and retrieving answers later, this is the core idea of the project.
