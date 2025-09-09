from __future__ import annotations
import sys
from contextlib import contextmanager
from typing import List, Dict, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import (
        Progress, SpinnerColumn, TimeElapsedColumn,
        BarColumn, DownloadColumn, TransferSpeedColumn, TextColumn
    )
    from rich.json import JSON as RichJSON
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

PLAIN = False
JSON_MODE = False

def enable_plain_mode():
    global PLAIN
    PLAIN = True

def enable_json_mode():
    global JSON_MODE
    JSON_MODE = True
    enable_plain_mode()

def is_tty() -> bool:
    return sys.stdout.isatty()

def console() -> Optional["Console"]:
    if not RICH_AVAILABLE or PLAIN:
        return None
    return Console()

@contextmanager
def spinner(message: str):
    if JSON_MODE:
        yield
        return
    if RICH_AVAILABLE and not PLAIN and is_tty():
        con = console()
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}"),
            TimeElapsedColumn(),
            transient=True,
            console=con,
        ) as progress:
            task_id = progress.add_task(message, total=None)
            try:
                yield
            finally:
                progress.update(task_id, description=message + " ✔")
    else:
        print(f"{message} ...", flush=True)
        try:
            yield
        finally:
            print(f"{message} done.", flush=True)

def print_versions_table(index: List[Dict]):
    if not RICH_AVAILABLE or PLAIN:
        print("Version  RecID      Date        #Files  Access  DOI")
        for e in index:
            access = e.get('access_right') or '-'
            print(
                f"{e['version']:>7}  {e['recid']:<9}  {e.get('publication_date','-'):10}  "
                f"{len(e['files']):>6}  {access:<7} {e.get('doi','')}"
            )
        return
    con = console()
    table = Table(title="FORCIS Versions", expand=False)
    table.add_column("Version", justify="right")
    table.add_column("RecID")
    table.add_column("Date")
    table.add_column("#Files", justify="right")
    table.add_column("Access", justify="center")
    table.add_column("DOI", overflow="fold")
    for e in index:
        access = e.get('access_right') or '-'
        table.add_row(
            e['version'],
            str(e['recid']),
            e.get('publication_date') or "-",
            str(len(e['files'])),
            access,
            e.get('doi', "")
        )
    con.print(table)

def human_size(num: int) -> str:
    n = num
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"

@contextmanager
def download_progress(enabled: bool = True):
    if JSON_MODE or not enabled or not RICH_AVAILABLE or PLAIN or not is_tty():
        def noop_track(file_key, total, cached=False):
            def update(n): pass
            def finalize(): pass
            return update, finalize
        yield noop_track
        return
    con = console()
    columns = [
        SpinnerColumn(),
        TextColumn("[bold blue]{task.fields[file]}"),
        BarColumn(bar_width=24),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeElapsedColumn(),
    ]
    with Progress(*columns, console=con, transient=False) as progress:
        def make_tracker(file_key, total, cached=False):
            if cached:
                task_id = progress.add_task(description="", total=1, file=f"{file_key} (cached)")
                progress.update(task_id, completed=1)
                return (lambda n: None), (lambda: None)
            task_id = progress.add_task(description="", total=total or 0, file=file_key)
            def update(n):
                try:
                    progress.update(task_id, advance=n)
                except Exception:
                    pass
            def finalize():
                try:
                    progress.update(task_id, completed=progress.tasks[task_id].total)
                except Exception:
                    pass
            return update, finalize
        yield make_tracker

def print_download_summary(rows: List[Dict[str, str]]):
    if JSON_MODE:
        return
    total = sum(r.get("size", 0) for r in rows)
    cached_count = sum(1 for r in rows if r.get("cached"))
    if not RICH_AVAILABLE or PLAIN or not is_tty():
        print("\nDownloaded files:")
        for r in rows:
            cached_tag = " (cached)" if r.get("cached") else ""
            print(f" - {r['file_key']}{cached_tag} ({human_size(r['size'])}) -> {r['path']}")
        print(f"Total: {human_size(total)} in {len(rows)} files ({cached_count} cached).")
        return
    con = console()
    table = Table(title="Download Summary")
    table.add_column("File")
    table.add_column("Size", justify="right")
    table.add_column("Cached", justify="center")
    table.add_column("Path")
    for r in rows:
        table.add_row(r["file_key"], human_size(r["size"]), "yes" if r.get("cached") else "no", r["path"])
    con.print(table)
    con.print(f"[bold green]Total:[/] {human_size(total)} in {len(rows)} files "
              f"([cyan]{cached_count} cached[/]).")

def print_json(obj):
    if RICH_AVAILABLE and not PLAIN and is_tty():
        con = console()
        if isinstance(obj, str):
            con.print(obj)
        else:
            con.print(RichJSON.from_data(obj))
    else:
        import json as _json
        print(_json.dumps(obj, indent=2))

def print_devices_table(devices: List[Dict]):
    # Plain fallback
    if not RICH_AVAILABLE or PLAIN:
        print("ID   Label                           Match        Note")
        for d in devices:
            print(f"{d['id']:<4} {d['label'][:28]:<28} {d['file_substring']:<12} {d['notes']}")
        return
    con = console()
    table = Table(title="Devices", expand=False, show_header=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Label")
    table.add_column("Match", justify="left", no_wrap=True)
    table.add_column("Note", overflow="fold")
    for d in devices:
        table.add_row(d["id"], d["label"], d["file_substring"], d["notes"])
    con.print(table)