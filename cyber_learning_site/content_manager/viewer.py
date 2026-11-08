"""Streamlit image-sequence viewer: Previous / Next buttons + slider.

Usage (this is all the main app needs):

    from content_manager.viewer import render_lesson_viewer
    render_lesson_viewer("python_security", "lec1_intro_python")
"""
from __future__ import annotations

import html

import streamlit as st

from . import loader


def _show_image(path):
    try:
        st.image(str(path), width="stretch")
    except TypeError:  # older Streamlit versions
        st.image(str(path), use_container_width=True)


def render_lesson_viewer(subject_id: str, lecture_id: str, key: str | None = None) -> None:
    try:
        frames = loader.get_frames(subject_id, lecture_id)
    except FileNotFoundError:
        st.error("ملف الملزمة غير موجود: " + f"{subject_id}/{lecture_id}")
        return
    if not frames:
        st.info("هذه الملزمة لا تحتوي على مشاهد بعد.")
        return

    n = len(frames)
    pos_key = (key or f"viewer_{subject_id}_{lecture_id}") + "_pos"
    st.session_state.setdefault(pos_key, 1)
    st.session_state[pos_key] = max(1, min(n, st.session_state[pos_key]))

    def step(delta: int):
        st.session_state[pos_key] = max(1, min(n, st.session_state[pos_key] + delta))

    def restart():
        st.session_state[pos_key] = 1

    frame = frames[st.session_state[pos_key] - 1]

    _show_image(frame.path)

    prev_col, mid_col, next_col = st.columns([1, 4, 1], vertical_alignment="center")
    prev_col.button("⬅ السابق", on_click=step, args=(-1,), disabled=st.session_state[pos_key] == 1,
                    key=pos_key + "_prev")
    next_col.button("التالي ➡", on_click=step, args=(1,), disabled=st.session_state[pos_key] == n,
                    key=pos_key + "_next", type="primary")
    with mid_col:
        if n > 1:
            st.slider("الخطوة", 1, n, key=pos_key, label_visibility="collapsed")
        st.caption(f"الإطار {st.session_state[pos_key]} من {n}")

    if frame.text:
        title = html.escape(frame.scene_title)
        body = html.escape(frame.text)
        st.markdown(
            f"""<div dir="rtl" style="text-align:right;padding:14px 18px;border-right:4px solid #60a5fa;
            background:rgba(96,165,250,.08);border-radius:10px;line-height:1.9;font-size:1.1rem">
            <div style="opacity:.65;font-size:.85rem">المشهد {frame.scene_index + 1} من {frame.scene_total} · {title}</div>
            {body}</div>""",
            unsafe_allow_html=True,
        )

    if st.session_state[pos_key] == n:
        st.button("↺ إعادة من البداية", on_click=restart, key=pos_key + "_restart")
