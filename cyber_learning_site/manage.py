"""Command line helper for the content (run from the project folder).

    python manage.py list                      show subjects and lectures
    python manage.py build [--force]           generate all animation images
    python manage.py validate                  check lecture files (and verify code outputs)
    python manage.py new-subject <id> --title "..." --title-en "..."
    python manage.py new-lecture <subject_id> <lecture_id> --title "..." --title-en "..."
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from content_manager import loader, validate

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")


def _check_id(value: str) -> str:
    if not ID_RE.match(value):
        sys.exit(f"Invalid id '{value}': use lowercase English letters, digits and underscores only.")
    return value


def cmd_list(_):
    subjects = loader.list_subjects()
    if not subjects:
        print("No subjects yet. Create one with: python manage.py new-subject <id> --title ...")
    for s in subjects:
        print(f"{s.icon} {s.id}  -  {s.title}  ({s.lecture_count} lectures)")
        for l in loader.list_lectures(s.id):
            print(f"    {l.order}. {l.id}  -  {l.title}  ({l.scene_count} scenes)")


def cmd_build(args):
    total = 0
    for s in loader.list_subjects():
        for l in loader.list_lectures(s.id):
            manifest = loader.build_lecture_images(s.id, l.id, force=args.force)
            total += len(manifest["frames"])
            print(f"built {s.id}/{l.id}: {len(manifest['frames'])} frames")
    print("total frames:", total)


def cmd_validate(_):
    bad = 0
    for name, problems in validate.validate_all().items():
        print(("OK    " if not problems else "FAIL  ") + name)
        for p in problems:
            print("   -", p)
        bad += bool(problems)
    sys.exit(1 if bad else 0)


def cmd_new_subject(args):
    sid = _check_id(args.id)
    folder = loader.CONTENT_DIR / sid
    if folder.exists():
        sys.exit(f"Subject '{sid}' already exists.")
    folder.mkdir(parents=True)
    meta = {"title": args.title, "title_en": args.title_en or sid, "description": args.description,
            "icon": args.icon, "order": args.order}
    (folder / "subject.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created content/{sid}/subject.json  - now add lectures with new-lecture")


def cmd_new_lecture(args):
    sid, lid = _check_id(args.subject), _check_id(args.lecture)
    folder = loader.CONTENT_DIR / sid
    if not folder.exists():
        sys.exit(f"Subject '{sid}' does not exist. Create it first with new-subject.")
    path = folder / f"{lid}.json"
    if path.exists():
        sys.exit(f"{path} already exists.")
    order = args.order or (max([l.order for l in loader.list_lectures(sid)] + [0]) + 1)
    data = {
        "title": args.title,
        "title_en": args.title_en or lid,
        "order": order,
        "summary": "",
        "scenes": [
            {"title": "Intro", "text": "اكتب هنا الشرح القصير بالعربي لهذا المشهد.",
             "bullets": ["First point", "Second point"]},
            {"title": "Example", "text": "شرح المثال.", "code": 'print("Hello")', "output": "Hello", "verify": True},
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created {path.relative_to(loader.ROOT)}  - edit the scenes, then run: python manage.py build")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    b = sub.add_parser("build")
    b.add_argument("--force", action="store_true")
    b.set_defaults(fn=cmd_build)
    sub.add_parser("validate").set_defaults(fn=cmd_validate)
    ns = sub.add_parser("new-subject")
    ns.add_argument("id")
    ns.add_argument("--title", required=True)
    ns.add_argument("--title-en", default="")
    ns.add_argument("--description", default="")
    ns.add_argument("--icon", default="\U0001F4D8")
    ns.add_argument("--order", type=int, default=99)
    ns.set_defaults(fn=cmd_new_subject)
    nl = sub.add_parser("new-lecture")
    nl.add_argument("subject")
    nl.add_argument("lecture")
    nl.add_argument("--title", required=True)
    nl.add_argument("--title-en", default="")
    nl.add_argument("--order", type=int, default=0)
    nl.set_defaults(fn=cmd_new_lecture)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
