---
name: llm-wiki-generator
description: Build or query a standalone Obsidian-compatible LLM Wiki from PDF, DOCX, PPTX, XLSX, and TXT sources. Use when you need to convert files to Markdown, preview archive updates, write structured wiki pages, index the stable knowledge base, or answer questions from the wiki without depending on BA-Agent code.
---

# LLM Wiki Generator

## Overview

Use this skill when you want a fully standalone LLM Wiki workflow:

- convert common files into Markdown with bundled document parsers
- archive source documents directly after LLM extraction
- optionally preview what knowledge updates would be archived
- build a local searchable index
- answer questions from stable or draft wiki knowledge

This skill does not depend on BA-Agent code, does not use `WikiUpdatePlan`, and does not require an approval step. By default, run `archive` so the LLM extracts structured knowledge, writes pages, and rebuilds the index for recall.

## Initialization Guard

Before doing any archive, indexing, or answer work, first check whether the wiki has already been initialized.

Use:

```bash
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py bootstrap-status --as-json
```

Behavior:

- if `initialized=true`, continue with the normal workflow
- if `initialized=false`, do not continue directly into archive or answer steps
- instead, start a short onboarding dialogue with the user

When initialization is missing, ask in this order:

1. whether they want to initialize now
2. which filesystem path should hold the wiki vault
3. repeat the chosen path back to them and ask for confirmation

After the user confirms, run:

```bash
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py bootstrap-init /absolute/or/relative/wiki-root
```

This will:

- write `WIKI_ROOT` into `.env`
- write `WIKI_INDEX_DB` into `.env` as a sibling to the chosen wiki root
- create the full vault structure under the confirmed path

Immediately after a successful initialization, ask the user whether they want to provide their first document now.

If the user declines initialization, stop the archive/query flow and explain that initialization is required before the skill can continue.

## Supported Inputs

The archive pipeline accepts exactly these five file types:

- `PDF`
- `DOCX`
- `PPTX`
- `XLSX`
- `TXT`

## Workflow

### 1. Initialize a standalone vault

Run:

```bash
cp skill/llm-wiki-generator/.env.example skill/llm-wiki-generator/.env
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py init
```

This creates an Obsidian-compatible structure under `WIKI_ROOT`:

- `10-raw/`
- `20-wiki/sources/`
- `20-wiki/entities/`
- `20-wiki/concepts/`
- `20-wiki/synthesis/`
- `20-wiki/conflicts/`
- `20-wiki/prd-patterns/`
- `20-wiki/index.md`
- `20-wiki/log.md`

### 2. Convert a file to Markdown

Run:

```bash
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py convert path/to/file.pdf
```

Use this when you only want to inspect the Markdown extraction result.

### 3. Archive a document directly

Run:

```bash
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py archive path/to/file.docx --source-type team_history
```

This step uses:

- bundled parsers for document conversion
- an OpenAI-compatible model if configured

Archive requires a configured OpenAI-compatible model. If the model is missing, unavailable, or returns invalid JSON, stop and ask the user to fix `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` before archiving.

Output is an `ArchivePreview` summary plus the written wiki paths. The command rebuilds the index by default so the archived knowledge is ready for `answer`.

Use `--no-index` only when batching many files and planning to run `index` once at the end.

### 4. Optional preview or manual apply

If the user explicitly wants to inspect the LLM output without writing files, run:

```bash
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py show-updates path/to/file.docx --source-type team_history
```

If the user already wants to write but not rebuild the index, run:


```bash
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py apply path/to/file.docx --source-type team_history
```

The writer is deterministic. It:

- copies the raw source into `10-raw/<source_type>/`
- writes or updates wiki pages under `20-wiki/`
- updates `20-wiki/index.md`
- appends to `20-wiki/log.md`

### 5. Build the local index manually

Run:

```bash
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py index
```

This builds a local SQLite index for wiki retrieval. It is already run by `archive` unless `--no-index` is used.

### 6. Answer from the wiki

Run:

```bash
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py answer "当前已知的业务约束是什么？"
```

Default scope is `stable`. You can override it:

```bash
.venv/bin/python skill/llm-wiki-generator/scripts/cli.py answer "团队历史里提到的设计思路有哪些？" --scope stable-draft
```

## Source Boundary Rules

- `business_fact`: can become factual business knowledge if evidence is strong and there is no conflict
- `industry_practice`: can become `source`, `synthesis`, or `prd_pattern`; it must not become customer fact
- `team_history`: can become `source`, `concept`, `synthesis`, or `prd_pattern`; it always defaults to `draft`
- `feedback`: defaults to `draft`
- conflicts never overwrite older knowledge; they become `20-wiki/conflicts/`

## Environment

Copy `.env.example` and set:

- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `WIKI_ROOT`
- `WIKI_INDEX_DB`

The LLM endpoint must support the OpenAI chat-completions format.

## Resources

### scripts/

Python implementation for conversion, preview, archive, indexing, and answer flows.

### references/

Prompt contracts, source-boundary rules, and vault layout notes for this skill.
