#!/usr/bin/env python3
"""FB-OSINT Investigator Pro command line interface."""
import argparse, json, sys
from fbosint.storage import Store
from fbosint.reports import export_case

def main(argv=None):
    parser = argparse.ArgumentParser(description="FB-OSINT Investigator Pro — authorized, public-source case management")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init", help="Create an investigation case")
    p.add_argument("--case", required=True); p.add_argument("--owner", required=True)
    p = sub.add_parser("add-url", help="Record a public Facebook URL")
    p.add_argument("--case-id", type=int, required=True); p.add_argument("--url", required=True); p.add_argument("--label", default="Public URL")
    p = sub.add_parser("add-note", help="Add a case note")
    p.add_argument("--case-id", type=int, required=True); p.add_argument("--note", required=True)
    p = sub.add_parser("add-evidence", help="Hash a local evidence file and record metadata")
    p.add_argument("--case-id", type=int, required=True); p.add_argument("--path", required=True); p.add_argument("--description", default="")
    sub.add_parser("list", help="List cases")
    p = sub.add_parser("show", help="Show a case")
    p.add_argument("--case-id", type=int, required=True)
    p = sub.add_parser("export", help="Export a case as JSON or CSV")
    p.add_argument("--case-id", type=int, required=True); p.add_argument("--format", choices=["json","csv"], required=True)
    args = parser.parse_args(argv)
    store = Store()
    try:
        if args.cmd == "init":
            print(f"Created case #{store.create_case(args.case, args.owner)}")
        elif args.cmd == "add-url":
            store.add_url(args.case_id, args.url, args.label); print("Public URL recorded.")
        elif args.cmd == "add-note":
            store.add_note(args.case_id, args.note); print("Note recorded.")
        elif args.cmd == "add-evidence":
            store.add_evidence(args.case_id, args.path, args.description); print("Evidence metadata and SHA-256 recorded.")
        elif args.cmd == "list":
            print(json.dumps(store.list_cases(), indent=2))
        elif args.cmd == "show":
            print(json.dumps(store.get_case(args.case_id), indent=2, ensure_ascii=False))
        elif args.cmd == "export":
            print(f"Report written to: {export_case(store.get_case(args.case_id), args.format)}")
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr); return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
