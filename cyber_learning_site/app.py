"""Demo shell for testing the content part (Member 2).

Member 1 (the UI developer) owns the real app.py. To plug the animations into the
real page he only needs:

    from content_manager import loader
    from content_manager.viewer import render_lesson_viewer

    loader.list_subjects()                 # subjects for the sidebar
    loader.list_lectures(subject_id)       # lectures of a subject
    render_lesson_viewer(subject_id, lecture_id)   # the animation viewer
"""
import streamlit as st

from content_manager import loader
from content_manager.viewer import render_lesson_viewer

st.set_page_config(page_title="منصة تعلّم الأمن السيبراني", page_icon="\U0001F6E1", layout="wide")

subjects = loader.list_subjects()
if not subjects:
    st.info("لا توجد مواد بعد. أنشئ مادة بالأمر: python manage.py new-subject")
    st.stop()

with st.sidebar:
    st.header("المواد الدراسية")
    subject = st.radio("المادة", subjects, format_func=lambda s: f"{s.icon}  {s.title}", label_visibility="collapsed")
    lectures = loader.list_lectures(subject.id)
    st.divider()
    st.subheader("الملازم")
    lecture = st.radio("الملزمة", lectures, format_func=lambda l: l.title, label_visibility="collapsed") if lectures else None

st.title(f"{subject.icon} {subject.title}")
if not lecture:
    st.info("هذه المادة لا تحتوي ملازم بعد. أضف ملف JSON داخل مجلد المادة.")
    st.stop()

st.subheader(lecture.title)
if lecture.summary:
    st.caption(lecture.summary)
render_lesson_viewer(subject.id, lecture.id)
