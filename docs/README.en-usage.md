# LLM Wiki Generator Usage Guide

[Back to README](../README.md) | [Docs Index](index.md) | [Chinese Overview](README.zh-home.md)

LLM Wiki Generator is friendly to any AI agent, any team workflow, and standalone CLI usage. It can be used as a skill or run directly as a Python CLI. Its goal is not just to “chat with files,” but to convert incoming material into structured wiki knowledge first, then retrieve and answer from that knowledge base in a controlled way.

This guide is written for people who want to ingest files, archive them directly, write wiki pages, and query the resulting knowledge base.

## 1. What It Does

The project provides five core capabilities:

- Markdown conversion with `convert`
- direct archive with `archive`
- optional archive preview with `show-updates`
- write without automatic reindexing with `apply`
- local indexing with `index`
- question answering with `answer`

Supported input formats:

- `PDF`
- `DOCX`
- `PPTX`
- `XLSX`
- `TXT`

## 2. Installation and Setup

### Install as a skill

If your host environment exposes an `npx install skill` style workflow, it is reasonable to install this project through that entrypoint first.

Example:

```bash
npx install skill llm-wiki-generator
```

Recommended post-install behavior:

1. verify that `Python 3` is installed
2. verify that `pip` is available
3. verify that the packages from `requirements.txt` are available
4. verify that `.env` exists and that core configuration values are present

If the environment is not ready, the skill should report what is missing, for example:

- `Python 3 is not installed`
- `pip is not available`
- `Missing Python packages: openai, pydantic, python-dotenv, pyyaml, rich, typer`
- `Optional packages missing for extended document support: pytest, python-docx, python-pptx, openpyxl, reportlab`

Once the user approves, the installer can install all missing dependencies before the skill is used.

Note: this is the recommended installation experience for a skill wrapper. In the current repository, the concrete assets already available are `requirements.txt` and `.env.example`.

### Install dependencies manually

```bash
pip install -r requirements.txt
```

### Create `.env`

```bash
cp .env.example .env
```

Typical configuration:

```env
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
LLM_TIMEOUT=60
WIKI_ROOT=runtime/vault
WIKI_INDEX_DB=runtime/index.sqlite3
WIKI_SCOPE=stable
```

Notes:

- `WIKI_ROOT` is where the wiki vault is written
- `WIKI_INDEX_DB` is the local SQLite index file
- `WIKI_SCOPE` controls the default retrieval scope for `answer`
- `archive`, `show-updates`, and `apply` require `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`; `answer` can still fall back to extractive output without a model

## 3. Initialize the Vault

Before archiving anything, first check whether the workspace has already been initialized:

```bash
python scripts/cli.py bootstrap-status --as-json
```

If initialization is missing, the recommended flow is:

1. ask whether the user wants to initialize now
2. ask where the wiki vault should be created
3. repeat the chosen path for confirmation
4. initialize the vault and persist the location into `.env`
5. immediately ask whether the user wants to provide the first document now

The corresponding initialization command is:

```bash
python scripts/cli.py bootstrap-init path/to/wiki-vault
```

It will:

- write `WIKI_ROOT`
- write `WIKI_INDEX_DB` next to the wiki root
- create the full vault structure

If the desired path is already configured in `.env`, you can still use the original initializer directly.

Before archiving anything, initialize the workspace:

```bash
python scripts/cli.py init
```

Expected structure:

```text
10-raw/
  business_fact/
  industry_practice/
  team_history/
  feedback/
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

Meaning:

- `10-raw/` stores copied source files
- `20-wiki/` stores structured Markdown knowledge pages
- `index.md` acts as a wiki entry page
- `log.md` records archive events

## 4. Command Reference

### `convert`

Convert a source file into Markdown without archiving it.

```bash
python scripts/cli.py convert path/to/file.pdf
```

Useful when you want to:

- inspect the raw conversion result
- validate that the source document can be parsed cleanly
- debug ingestion quality before archive preview

### `archive`

Run LLM extraction, write the result into the wiki, and rebuild the retrieval index by default.

```bash
python scripts/cli.py archive path/to/file.docx --source-type team_history
```

What it does:

1. copies the original file into `10-raw/<source_type>/`
2. writes structured pages into `20-wiki/`
3. merges metadata if a target page already exists
4. appends new content as an update block on existing pages
5. updates `20-wiki/index.md`
6. appends an entry to `20-wiki/log.md`
7. rebuilds the SQLite retrieval index for immediate `answer` recall

If you are importing many files and want to reindex once at the end, use:

```bash
python scripts/cli.py archive path/to/file.docx --source-type team_history --no-index
```

Then run `index` after the batch.

### `show-updates`

Preview archive output without writing any wiki pages.

```bash
python scripts/cli.py show-updates path/to/file.docx --source-type team_history
```

This returns an `ArchivePreview` describing:

- which pages would be created or updated
- page type
- status such as `stable`, `draft`, or `conflict`
- confidence level
- evidence snippets
- archive rationale

This is an optional audit step when you want to inspect what the LLM would write before archiving.
It requires a configured OpenAI-compatible LLM. If model configuration is missing or the model response is invalid, the command fails without writing archive files.

### `apply`

Run LLM extraction and write the result into the wiki without automatically rebuilding the retrieval index.

```bash
python scripts/cli.py apply path/to/file.docx --source-type team_history
```

What it does:

1. copies the original file into `10-raw/<source_type>/`
2. writes structured pages into `20-wiki/`
3. merges metadata if a target page already exists
4. appends new content as an update block on existing pages
5. updates `20-wiki/index.md`
6. appends an entry to `20-wiki/log.md`

If you want the archived knowledge to be immediately available for recall, prefer `archive`.

### `index`

Build the local retrieval index:

```bash
python scripts/cli.py index
```

This scans Markdown files under `20-wiki/` and writes them into a SQLite + FTS index used by `answer`.

### `answer`

Retrieve from the wiki and answer a question:

```bash
python scripts/cli.py answer "What business constraints are currently known?"
```

By default it searches `stable` knowledge only. You can widen the scope:

```bash
python scripts/cli.py answer "What design ideas were mentioned in team history?" --scope stable-draft
```

Supported `scope` values:

- `stable`
- `stable-draft`
- `all`

## 5. Choosing `source_type`

### `business_fact`

Use for:

- business rules
- customer constraints
- confirmed facts

Behavior:

- may become stable knowledge when evidence is strong enough

### `industry_practice`

Use for:

- market references
- general methods
- best practices

Behavior:

- better suited for `source`, `synthesis`, or `prd_pattern`
- should not be treated as customer truth

### `team_history`

Use for:

- historical design notes
- decision evolution
- past solution records

Behavior:

- defaults to `draft`
- may also produce `prd_pattern` pages from historical PRDs, team decisions, requirement structures, review flows, and reusable product judgment patterns

### `feedback`

Use for:

- user feedback
- internal comments
- interview notes

Behavior:

- defaults to `draft`

## 6. End-to-End Example

Assume you have a historical team document at `docs/team-retro.docx`:

```bash
python scripts/cli.py init
python scripts/cli.py archive docs/team-retro.docx --source-type team_history
python scripts/cli.py answer "What architecture ideas kept recurring over time?" --scope stable-draft
```

Recommended habit:

- use `archive` for daily ingestion so LLM output is written and indexed immediately
- use `show-updates` only when you need to audit the proposed output first
- use `archive --no-index` for batch imports, then run `index` once at the end
- use `stable-draft` when historical or exploratory material matters
- after first-time initialization, decide immediately whether to ingest the first document so the onboarding flow can continue without interruption

## 7. Model Requirements

For archive upload flows, an OpenAI-compatible model is required:

- `show-updates` requires a model-generated archive preview
- `archive` and `apply` fail during LLM extraction if the model is unavailable or returns invalid JSON
- failed archive preview does not copy raw files or write wiki pages

For answer flows, no-model mode is still usable:

- `answer` falls back to an extractive response style

That means archiving is strict, while retrieval remains usable for already-indexed content.

## 8. Mental Model

The recommended way to think about the workflow is:

1. `init` prepares the vault
2. `archive` extracts, writes, and indexes knowledge
3. `answer` consumes the archived knowledge

The key distinction is simple:

- `convert` extracts
- `archive` extracts with LLM, archives, and indexes
- `show-updates` optionally reviews
- `apply` archives without automatic reindexing
- `index` prepares retrieval
- `answer` uses the knowledge base
