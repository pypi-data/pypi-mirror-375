from __future__ import annotations
import argparse
import json
from pathlib import Path

from . import versioning
from .cache import get_cache_info, clear_cache
from .parquetio import jsonl_to_parquet, parquet_to_jsonl
from .terminal import (
    spinner, print_versions_table, enable_plain_mode, print_json,
    download_progress, print_download_summary, enable_json_mode,
    print_devices_table
)
from .devices import get_devices

def main():
    parser = argparse.ArgumentParser("pyforcis")
    parser.add_argument("--plain", action="store_true", help="Disable colors/animations")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress bars")
    parser.add_argument("--summary-only", action="store_true", help="Skip per-file progress; only final summary")
    parser.add_argument("--refresh-index", action="store_true", help="Force refresh of version index (ignore cache)")

    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("list-versions")
    sub.add_parser("index")
    sub.add_parser("refresh-index")
    sub.add_parser("list-devices")

    pmeta = sub.add_parser("metadata", help="Show metadata (defaults to latest version if no selector provided)")
    pmeta.add_argument("--version", help="Version number string (e.g. 10). If omitted uses latest.")
    pmeta.add_argument("--recid", help="Explicit Zenodo record id (overrides --version if given)")
    pmeta.add_argument("--doi", help="Explicit DOI (overrides --version if given)")

    pfetch = sub.add_parser("fetch", help="Download files (defaults to latest version if no version/recid/doi)")
    pfetch.add_argument("--version", help="Version number (e.g. 10). If omitted latest is used.")
    pfetch.add_argument("--recid", help="Record id (overrides --version if provided)")
    pfetch.add_argument("--doi", help="DOI (overrides --version if provided)")
    pfetch.add_argument("--sources", help="Comma substrings", default="")
    pfetch.add_argument("--force", action="store_true")

    pjson2pq = sub.add_parser("jsonl2parquet")
    pjson2pq.add_argument("--in", dest="input_file", required=True)
    pjson2pq.add_argument("--out", required=True)

    ppq2json = sub.add_parser("parquet2jsonl")
    ppq2json.add_argument("--in", dest="input_file", required=True)
    ppq2json.add_argument("--out", required=True)

    pcsv2parquet = sub.add_parser("csv2parquet")
    pcsv2parquet.add_argument("--in", dest="input_file", required=True)
    pcsv2parquet.add_argument("--out", required=True)
    pcsv2parquet.add_argument("--limit", type=int, help="Row limit (preview conversion)")

    pcsv2jsonl = sub.add_parser("csv2jsonl")
    pcsv2jsonl.add_argument("--in", dest="input_file", required=True)
    pcsv2jsonl.add_argument("--out", required=True)
    pcsv2jsonl.add_argument("--limit", type=int)

    pdescribe = sub.add_parser("describe")
    pdescribe.add_argument("--jsonl")
    pdescribe.add_argument("--csv")
    pdescribe.add_argument("--limit", type=int, help="Row limit for loading")
    pdescribe.add_argument("--max-unique", type=int, default=50)
    pdescribe.add_argument("--sample", type=int, default=3)

    pdevdesc = sub.add_parser("device-describe")
    pdevdesc.add_argument("--version")
    pdevdesc.add_argument("--sources", help="Comma-separated device ids (e.g. net,trap)")
    pdevdesc.add_argument("--limit", type=int)
    pdevdesc.add_argument("--max-unique", type=int, default=30)
    pdevdesc.add_argument("--sample", type=int, default=3)

    sub.add_parser("cache-info")
    sub.add_parser("cache-clear")
    # Removed advanced dataset / taxonomy / compute / plugin features in minimal build

    args = parser.parse_args()

    if args.json:
        enable_json_mode()
    elif args.plain:
        enable_plain_mode()

    def load_index():
        return versioning.get_version_index(force=args.refresh_index or args.cmd == "refresh-index")

    if args.cmd == "refresh-index":
        with spinner("Refreshing version index"):
            idx = load_index()
        if args.json:
            print_json(idx)
        else:
            print(f"Refreshed index: {len(idx)} versions.")
        return

    if args.cmd == "list-versions":
        with spinner("Fetching version index"):
            index = load_index()
        if args.json:
            print_json(index)
        else:
            print_versions_table(index)
        return

    if args.cmd == "index":
        idx = load_index()
        print_json(idx) if args.json else print(idx)
        return

    if args.cmd == "list-devices":
        devices = get_devices()
        if args.json:
            print_json(devices)
        else:
            print_devices_table(devices)
        return

    if args.cmd == "metadata":
        with spinner("Fetching metadata"):
            meta = versioning.get_version_metadata(
                version=args.version,
                recid=args.recid,
                doi=args.doi,
                force=args.refresh_index
            )
        print_json(meta) if args.json else print(json.dumps(meta, indent=2))
        return

    if args.cmd == "fetch":
        sources = [s for s in args.sources.split(",") if s] if args.sources else None
        with spinner("Resolving version"):
            index = load_index()
            entry = versioning._resolve_version_entry(args.version, args.recid, args.doi, index)
            files = versioning.select_files_for_sources(entry, sources=sources)
        if not files:
            if args.json:
                print_json({"downloaded": [], "message": "No files matched"})
            else:
                print("No files matched.")
            return
        rows_summary = []
        if args.summary_only or args.no_progress or args.json:
            for f in files:
                key = f["key"]
                version_str = entry["version"]
                target_dir = Path.home() / ".cache" / "pyforcis" / "downloads" / version_str
                target_dir.mkdir(parents=True, exist_ok=True)
                local_path = target_dir / key
                existed = local_path.exists()
                versioning.download_forcis_file(
                    file_key=key,
                    version=entry["version"],
                    force=args.force,
                    progress_cb=None
                )
                size = local_path.stat().st_size if local_path.exists() else 0
                rows_summary.append({
                    "file_key": key,
                    "size": size,
                    "path": str(local_path),
                    "cached": (existed and not args.force)
                })
        else:
            with download_progress(enabled=not args.no_progress) as tracker:
                for f in files:
                    key = f["key"]
                    version_str = entry["version"]
                    target_dir = Path.home() / ".cache" / "pyforcis" / "downloads" / version_str
                    target_dir.mkdir(parents=True, exist_ok=True)
                    local_path = target_dir / key
                    cached_flag = local_path.exists() and not args.force
                    size_hint = f.get("size")
                    update_fn, finalize_fn = tracker(key, size_hint, cached=cached_flag)
                    last_reported = 0
                    def progress_cb(bytes_so_far, total, _key, cached):
                        nonlocal last_reported
                        if cached: return
                        delta = bytes_so_far - last_reported
                        if delta > 0:
                            update_fn(delta)
                            last_reported = bytes_so_far
                    versioning.download_forcis_file(
                        file_key=key,
                        version=entry["version"],
                        force=args.force,
                        progress_cb=progress_cb
                    )
                    finalize_fn()
                    size = local_path.stat().st_size if local_path.exists() else 0
                    rows_summary.append({
                        "file_key": key,
                        "size": size,
                        "path": str(local_path),
                        "cached": cached_flag and not args.force
                    })
        if args.json:
            print_json({"downloaded": rows_summary})
        else:
            print_download_summary(rows_summary)
        return

    # Removed commands: read, compute, normalize-taxonomy, manifest, assign-season

    if args.cmd == "jsonl2parquet":
        jsonl_to_parquet(Path(args.input_file), Path(args.out))
        print("Converted to parquet.")
        return

    if args.cmd == "parquet2jsonl":
        parquet_to_jsonl(Path(args.input_file), Path(args.out))
        print("Converted to jsonl.")
        return

    if args.cmd == "csv2parquet":
        from .dataset import load_csv
        from .parquetio import jsonl_to_parquet
        from pathlib import Path as _P
        ds = load_csv(Path(args.input_file), limit=args.limit)
        tmp_jsonl = Path(args.out).with_suffix('.tmp.jsonl')
        ds.to_jsonl(tmp_jsonl)
        jsonl_to_parquet(tmp_jsonl, Path(args.out))
        tmp_jsonl.unlink(missing_ok=True)
        print("Converted CSV to parquet.")
        return

    if args.cmd == "csv2jsonl":
        from .dataset import load_csv
        ds = load_csv(Path(args.input_file), limit=args.limit)
        ds.to_jsonl(Path(args.out))
        print("Converted CSV to jsonl.")
        return

    if args.cmd == "describe":
        from .dataset import load_jsonl, load_csv
        path = None
        loader = None
        if args.jsonl:
            path = Path(args.jsonl)
            loader = load_jsonl
        elif args.csv:
            path = Path(args.csv)
            loader = lambda p: load_csv(p, limit=args.limit)
        else:
            print("Must provide --jsonl or --csv")
            return
        ds = loader(path)
        summary = ds.describe(max_unique=args.max_unique, sample=args.sample)
        if args.json:
            print_json(summary)
        else:
            # Minimal plain table
            from rich.table import Table
            from rich.console import Console
            table = Table(title=f"Describe: {path.name}")
            for col in ["field","type","non_null","nulls","distinct","sample_values"]:
                table.add_column(col)
            for row in summary:
                table.add_row(
                    str(row['field']),
                    str(row['type']),
                    str(row['non_null']),
                    str(row['nulls']),
                    str(row['distinct']),
                    ", ".join(map(lambda v: str(v), row['sample_values']))
                )
            Console().print(table)
        return

    if args.cmd == "device-describe":
        # For each downloaded file matching device sources, print a schema summary.
        from .versioning import get_version_index, _resolve_version_entry, DOWNLOAD_DIR, select_files_for_sources
        from .dataset import load_csv, load_jsonl
        version_index = get_version_index()
        entry = _resolve_version_entry(args.version, None, None, version_index)
        version_str = entry["version"]
        wanted = [s.strip() for s in (args.sources or "").split(",") if s.strip()] or None
        files_meta = select_files_for_sources(entry, sources=wanted)
        if not files_meta:
            print("No matching files.")
            return
        results = []
        for fm in files_meta:
            key = fm.get("key")
            local_path = (DOWNLOAD_DIR / version_str / key)
            if not local_path.exists():
                # Skip not yet downloaded
                continue
            # Heuristic: choose loader based on extension
            ext = local_path.suffix.lower()
            try:
                if ext == ".csv":
                    ds = load_csv(local_path, limit=args.limit)
                elif ext == ".jsonl" or key.lower().endswith(".jsonl.gz"):
                    ds = load_jsonl(local_path, limit=args.limit)
                else:
                    continue
                summary = ds.describe(max_unique=args.max_unique, sample=args.sample)
                results.append({"file": key, "summary": summary})
            except Exception as e:
                results.append({"file": key, "error": str(e)})
        if args.json:
            print_json(results)
        else:
            from rich.console import Console
            from rich.table import Table
            console = Console()
            for r in results:
                if "error" in r:
                    console.print(f"[red]{r['file']} error: {r['error']}")
                    continue
                table = Table(title=f"{r['file']}")
                for col in ["field","type","non_null","nulls","distinct","sample_values"]:
                    table.add_column(col)
                for row in r["summary"]:
                    table.add_row(
                        str(row['field']),
                        str(row['type']),
                        str(row['non_null']),
                        str(row['nulls']),
                        str(row['distinct']),
                        ", ".join(map(lambda v: str(v), row['sample_values']))
                    )
                console.print(table)
        return

    if args.cmd == "cache-info":
        info = get_cache_info()
        print_json(info) if args.json else print(json.dumps(info, indent=2))
        return

    if args.cmd == "cache-clear":
        clear_cache()
        print("Cache cleared.")
        return

    # Removed commands: list-plugins, compiled-filter

    parser.print_help()

if __name__ == "__main__":
    main()