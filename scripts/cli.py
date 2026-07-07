from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from llm_wiki_generator.answer import answer_question
from llm_wiki_generator.archive import ArchiveLLMRequiredError, apply_preview, archive_source
from llm_wiki_generator.bootstrap import initialize_wiki_location, inspect_bootstrap
from llm_wiki_generator.config import load_settings
from llm_wiki_generator.indexer import build_index
from llm_wiki_generator.markdown import convert_to_markdown
from llm_wiki_generator.models import Scope, SourceType
from llm_wiki_generator.vault import init_vault


app = typer.Typer(help="Standalone LLM Wiki Generator")
console = Console()


def print_archive_error(error: ArchiveLLMRequiredError) -> None:
    console.print(f"[red]error[/red] {error}")


def parse_source_type(source_type: str) -> SourceType:
    try:
        return SourceType(source_type)
    except ValueError as exc:
        raise typer.BadParameter(f"Invalid source type: {source_type}") from exc


def parse_scope(scope: str) -> Scope:
    try:
        return Scope(scope)
    except ValueError as exc:
        raise typer.BadParameter(f"Invalid scope: {scope}") from exc


@app.command()
def init() -> None:
    settings = load_settings()
    created = init_vault(settings)
    for path in created:
        console.print(f"[green]ready[/green] {path}")


@app.command("bootstrap-status")
def bootstrap_status(as_json: bool = False) -> None:
    skill_root = Path(__file__).resolve().parents[1]
    status = inspect_bootstrap(skill_root)
    payload = status.to_dict()
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False))
        return

    console.print(
        Panel.fit(
            "\n".join(
                [
                    f"Configured: {status.configured}",
                    f"Initialized: {status.initialized}",
                    f"Env file: {status.env_path}",
                    f"Wiki root: {status.wiki_root or '(unset)'}",
                    f"Index DB: {status.index_db or '(unset)'}",
                    f"Missing paths: {', '.join(status.missing_paths) or '(none)'}",
                ]
            ),
            title="Bootstrap Status",
        )
    )


@app.command("bootstrap-init")
def bootstrap_init(wiki_root: Path) -> None:
    skill_root = Path(__file__).resolve().parents[1]
    settings, created, env_path = initialize_wiki_location(skill_root, wiki_root)
    console.print(f"[green]configured[/green] {env_path}")
    console.print(f"[green]wiki-root[/green] {settings.wiki_root}")
    console.print(f"[green]index-db[/green] {settings.index_db}")
    for path in created:
        console.print(f"[green]ready[/green] {path}")


@app.command()
def convert(source: Path, output: Optional[Path] = None) -> None:
    document = convert_to_markdown(source)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(document.markdown, encoding="utf-8")
        console.print(f"[green]written[/green] {output}")
        return
    console.print(Panel.fit(document.markdown, title=document.title))


def render_preview(preview: dict) -> None:
    table = Table(title=preview["title"])
    table.add_column("Title")
    table.add_column("Page Type")
    table.add_column("Status")
    table.add_column("Confidence")
    table.add_column("Reason")
    for update in preview["updates"]:
        table.add_row(
            update["title"],
            update["page_type"],
            update["status"],
            update["confidence"],
            update["reason"],
        )
    console.print(table)


def load_archive_preview(source: Path, source_type: str):
    settings = load_settings()
    try:
        preview = archive_source(source, parse_source_type(source_type), settings)
    except ArchiveLLMRequiredError as exc:
        print_archive_error(exc)
        raise typer.Exit(code=1) from exc
    return settings, preview


@app.command("show-updates")
def show_updates(
    source: Path,
    source_type: str = typer.Option(..., "--source-type"),
    as_json: bool = False,
) -> None:
    _, preview = load_archive_preview(source, source_type)
    payload = preview.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False))
        return
    render_preview(payload)


@app.command("archive")
def archive(
    source: Path,
    source_type: str = typer.Option(..., "--source-type"),
    reindex: bool = typer.Option(True, "--index/--no-index", help="Rebuild the retrieval index after archiving."),
) -> None:
    settings, preview = load_archive_preview(source, source_type)
    written = apply_preview(preview, source.resolve(), settings)
    payload = preview.model_dump(mode="json")
    render_preview(payload)
    for path in written:
        console.print(f"[green]archived[/green] {path}")
    if reindex:
        count = build_index(settings)
        console.print(f"[green]indexed[/green] {count} documents into {settings.index_db}")


@app.command()
def apply(source: Path, source_type: str = typer.Option(..., "--source-type")) -> None:
    settings, preview = load_archive_preview(source, source_type)
    written = apply_preview(preview, source.resolve(), settings)
    payload = preview.model_dump(mode="json")
    render_preview(payload)
    for path in written:
        console.print(f"[green]archived[/green] {path}")


@app.command()
def index() -> None:
    settings = load_settings()
    count = build_index(settings)
    console.print(f"[green]indexed[/green] {count} documents into {settings.index_db}")


@app.command()
def answer(question: str, scope: Optional[str] = None, limit: int = 5) -> None:
    settings = load_settings()
    resolved_scope = parse_scope(scope or settings.default_scope)
    response = answer_question(settings, question, resolved_scope, limit=limit)
    console.print(Panel.fit(response, title="Wiki Answer"))


if __name__ == "__main__":
    app()
