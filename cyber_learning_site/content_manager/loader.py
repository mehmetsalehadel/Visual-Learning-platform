"""Reads subjects / lectures from the content/ folder and prepares animation frames.

Folder convention (nothing needs registering in code):

    content/<subject_id>/subject.json        <- the subject (مادة)
    content/<subject_id>/<lecture_id>.json   <- one file per lecture (ملزمة)
    assets/animations/<subject_id>/<lecture_id>/   <- generated images (auto)

Folders starting with "_" or "." (e.g. content/_template) are ignored.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
ASSETS_DIR = ROOT / "assets" / "animations"
RENDERER_FILE = Path(__file__).with_name("renderer.py")


@dataclass
class Subject:
    id: str
    title: str
    title_en: str
    description: str
    icon: str
    order: int
    lecture_count: int


@dataclass
class Lecture:
    id: str
    subject_id: str
    title: str
    title_en: str
    summary: str
    order: int
    scene_count: int


@dataclass
class Frame:
    path: Path
    scene_index: int  # 0-based
    scene_total: int
    scene_title: str
    text: str  # short Arabic explanation of the scene


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _lecture_files(subject_dir: Path) -> list[Path]:
    return [p for p in subject_dir.glob("*.json") if p.name != "subject.json"]


# ---------------------------------------------------------------- subjects
def load_subject(subject_id: str) -> Subject:
    folder = CONTENT_DIR / subject_id
    meta = _read_json(folder / "subject.json") if (folder / "subject.json").exists() else {}
    return Subject(
        id=subject_id,
        title=meta.get("title", subject_id),
        title_en=meta.get("title_en", subject_id),
        description=meta.get("description", ""),
        icon=meta.get("icon", "\U0001F4D8"),
        order=int(meta.get("order", 999)),
        lecture_count=len(_lecture_files(folder)),
    )


def list_subjects() -> list[Subject]:
    if not CONTENT_DIR.exists():
        return []
    subjects = [
        load_subject(p.name)
        for p in CONTENT_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(("_", "."))
    ]
    return sorted(subjects, key=lambda s: (s.order, s.id))


# ---------------------------------------------------------------- lectures
def load_lecture_raw(subject_id: str, lecture_id: str) -> dict:
    return _read_json(CONTENT_DIR / subject_id / f"{lecture_id}.json")


def list_lectures(subject_id: str) -> list[Lecture]:
    lectures = []
    for path in _lecture_files(CONTENT_DIR / subject_id):
        data = _read_json(path)
        lectures.append(
            Lecture(
                id=path.stem,
                subject_id=subject_id,
                title=data.get("title", path.stem),
                title_en=data.get("title_en", path.stem),
                summary=data.get("summary", ""),
                order=int(data.get("order", 999)),
                scene_count=len(data.get("scenes", [])),
            )
        )
    return sorted(lectures, key=lambda l: (l.order, l.id))


# ---------------------------------------------------------------- frames
def _digest(subject_id: str, lecture_id: str) -> str:
    h = hashlib.sha1()
    for p in (CONTENT_DIR / subject_id / "subject.json", CONTENT_DIR / subject_id / f"{lecture_id}.json", RENDERER_FILE):
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()


def build_lecture_images(subject_id: str, lecture_id: str, force: bool = False) -> dict:
    """Generate the PNG frames of a lecture (skipped when nothing changed)."""
    from . import renderer  # imported lazily so the loader works without Pillow

    out_dir = ASSETS_DIR / subject_id / lecture_id
    manifest_path = out_dir / "manifest.json"
    digest = _digest(subject_id, lecture_id)
    if not force and manifest_path.exists():
        manifest = _read_json(manifest_path)
        if manifest.get("hash") == digest and all((ROOT / f["file"]).exists() for f in manifest["frames"]):
            return manifest

    subject, data = load_subject(subject_id), load_lecture_raw(subject_id, lecture_id)
    scenes = data.get("scenes", [])
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("s*.png"):
        old.unlink()

    frames = []
    for i, scene in enumerate(scenes):
        if scene.get("image"):  # a hand-made image replaces the generated frames
            frames.append({"file": Path(scene["image"]).as_posix(), "scene": i})
            continue
        ctx = {
            "subject_en": subject.title_en,
            "lesson_en": data.get("title_en", lecture_id),
            "index": i + 1,
            "total": len(scenes),
        }
        for k, img in enumerate(renderer.render_scene(scene, ctx), start=1):
            path = out_dir / f"s{i + 1:02d}_{k}.png"
            img.save(path, optimize=True)
            frames.append({"file": path.relative_to(ROOT).as_posix(), "scene": i})

    manifest = {"hash": digest, "frames": frames}
    manifest_path.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


def get_frames(subject_id: str, lecture_id: str) -> list[Frame]:
    """Ordered animation frames of a lecture (builds the images if needed)."""
    manifest = build_lecture_images(subject_id, lecture_id)
    scenes = load_lecture_raw(subject_id, lecture_id).get("scenes", [])
    return [
        Frame(
            path=ROOT / f["file"],
            scene_index=f["scene"],
            scene_total=len(scenes),
            scene_title=scenes[f["scene"]].get("title", ""),
            text=scenes[f["scene"]].get("text", ""),
        )
        for f in manifest["frames"]
    ]


def get_lecture_data(subject_id: str, lecture_id: str) -> dict:
    """Per-lecture data file for the other team members:
    title + for each scene: title, short text and the image paths of its animation."""
    frames = get_frames(subject_id, lecture_id)
    raw = load_lecture_raw(subject_id, lecture_id)
    scenes = []
    for i, scene in enumerate(raw.get("scenes", [])):
        scenes.append(
            {
                "title": scene.get("title", ""),
                "text": scene.get("text", ""),
                "images": [str(f.path) for f in frames if f.scene_index == i],
            }
        )
    return {"id": lecture_id, "title": raw.get("title", lecture_id), "summary": raw.get("summary", ""), "scenes": scenes}
