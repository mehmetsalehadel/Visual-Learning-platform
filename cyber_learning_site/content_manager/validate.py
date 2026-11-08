"""Checks lecture files: structure, and (for scenes marked "verify": true) runs the
code and compares its real output with the "output" written in the JSON."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile

from . import loader

KINDS = ("flow", "table", "bullets", "code", "image")


def _check_scene(i: int, scene: dict) -> list[str]:
    problems = []
    tag = f"scene {i + 1} ({scene.get('title', '?')})"
    if not scene.get("title"):
        problems.append(f"{tag}: missing 'title'")
    if not any(scene.get(k) is not None and scene.get(k) != "" for k in KINDS):
        problems.append(f"{tag}: needs one of {KINDS}")
    if not scene.get("text"):
        problems.append(f"{tag}: missing Arabic 'text' (the short explanation)")
    table = scene.get("table")
    if table:
        width = len(table.get("headers", []))
        for r, row in enumerate(table.get("rows", [])):
            if len(row) != width:
                problems.append(f"{tag}: table row {r + 1} has {len(row)} cells, expected {width}")
    if scene.get("flow") and not isinstance(scene["flow"], list):
        problems.append(f"{tag}: 'flow' must be a list of step names")
    if scene.get("verify"):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                res = subprocess.run([sys.executable, "-I", "-c", scene["code"]], cwd=tmp,
                                     capture_output=True, text=True, timeout=15)
            except subprocess.TimeoutExpired:
                problems.append(f"{tag}: verify timed out")
                return problems
        if res.returncode != 0:
            problems.append(f"{tag}: code failed: {res.stderr.strip().splitlines()[-1] if res.stderr else '?'}")
        elif res.stdout.rstrip("\n") != scene.get("output", "").rstrip("\n"):
            problems.append(f"{tag}: output in JSON differs from real output:\n--- real ---\n{res.stdout}--- json ---\n{scene.get('output')}")
    return problems


def validate_lecture(subject_id: str, lecture_id: str) -> list[str]:
    path = loader.CONTENT_DIR / subject_id / f"{lecture_id}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    problems = []
    for key in ("title", "title_en", "scenes"):
        if key not in data:
            problems.append(f"missing '{key}'")
    for i, scene in enumerate(data.get("scenes", [])):
        problems += _check_scene(i, scene)
    return problems


def validate_all() -> dict[str, list[str]]:
    report = {}
    for subject in loader.list_subjects():
        for lec in loader.list_lectures(subject.id):
            report[f"{subject.id}/{lec.id}"] = validate_lecture(subject.id, lec.id)
    return report
