import streamlit as st
import pandas as pd

# ==========================================
# 1. DATABASE CONNECTION
# ==========================================

try:
    from database import save_score, get_leaderboard  # type: ignore[import-not-found]
    database_available = True

except (ImportError, ModuleNotFoundError):
    database_available = False
    save_score = None
    get_leaderboard = None


# ==========================================
# 2. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# 3. CUSTOM CSS
# ==========================================

st.markdown("""
<style>

/* Main application */
.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--secondary-background-color);
}

/* General text */
.stMarkdown,
.stText,
label,
[data-testid="stWidgetLabel"] {
    color: var(--text-color);
}

/* Main title */
.main-title {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    color: var(--primary-color);
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 18px;
    color: var(--text-color);
    margin-bottom: 30px;
}

/* Welcome box */
.welcome-box {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 25px;
}

.welcome-box h2,
.welcome-box p {
    color: var(--text-color);
}

/* Section titles */
.section-title {
    color: var(--primary-color);
    font-size: 27px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SUBJECTS
# ==========================================

subjects = [
    "Python Programming",
    "Computer Fundamentals",
    "Cybersecurity",
    "Networking"
]


# ==========================================
# 5. SIDEBAR
# ==========================================

st.sidebar.title("🎓 Learning Platform")

st.sidebar.markdown("---")

st.sidebar.subheader("Choose a Subject")

selected_subject = st.sidebar.selectbox(
    "Select your subject:",
    subjects
)

st.sidebar.markdown("---")

st.sidebar.subheader("Navigation")

page = st.sidebar.radio(
    "Go to:",
    [
        "Home",
        "Theory",
        "Animation",
        "Practical Lab",
        "Quizzes",
        "Leaderboard"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption("Interactive Educational Platform")


# ==========================================
# 6. HOME PAGE
# ==========================================

if page == "Home":

    st.markdown(
        '<div class="main-title">Welcome to Our Learning Platform!</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Learn, Practice, and Improve Your Skills</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="welcome-box">
        <h2>Welcome!</h2>
        <p>
        This platform helps students understand their lessons
        through explanations, animations, practical exercises,
        and quizzes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📚 Available Subjects")

    col1, col2 = st.columns(2)

    with col1:
        st.info("🐍 Python Programming")
        st.info("💻 Computer Fundamentals")

    with col2:
        st.info("🔐 Cybersecurity")
        st.info("🌐 Networking")

    st.markdown("---")

    st.subheader("✨ What can you do here?")

    st.write("""
    - **Theory:** Read simplified explanations of your lessons.
    - **Animation:** Understand concepts through visual steps.
    - **Practical Lab:** Practice using code examples and exercises.
    - **Quizzes:** Test your knowledge.
    - **Leaderboard:** See the highest student scores.
    """)

    st.success(
        f"Currently selected subject: {selected_subject}"
    )


# ==========================================
# 7. THEORY SECTION
# ==========================================

elif page == "Theory":

    st.markdown(
        '<div class="section-title">📖 Theory Lessons</div>',
        unsafe_allow_html=True
    )

    st.write(f"Selected Subject: **{selected_subject}**")

    st.markdown("---")

    st.info(
        "Lesson explanations and study materials "
        "will be added here."
    )

    # Member 2 will add the theory content here.


# ==========================================
# 8. ANIMATION SECTION
# ==========================================

elif page == "Animation":

    st.markdown(
        '<div class="section-title">🎞️ Step-by-Step Animation</div>',
        unsafe_allow_html=True
    )

    st.write(f"Selected Subject: **{selected_subject}**")

    st.markdown("---")

    st.info(
        "Visual explanations and step-by-step images "
        "will be displayed here."
    )

    # Member 2 will add the animation and images here.


# ==========================================
# 9. PRACTICAL LAB SECTION
# ==========================================

elif page == "Practical Lab":

    st.markdown(
        '<div class="section-title">💻 Practical Lab</div>',
        unsafe_allow_html=True
    )

    st.write(f"Selected Subject: **{selected_subject}**")

    st.markdown("---")

    st.info(
        "Coding exercises, practical examples, "
        "and code checking will be added here."
    )

    # Member 3 will add the practical exercises here.


# ==========================================
# 10. QUIZZES SECTION
# ==========================================

elif page == "Quizzes":

    st.markdown(
        '<div class="section-title">📝 Quizzes</div>',
        unsafe_allow_html=True
    )

    st.write(f"Selected Subject: **{selected_subject}**")

    st.markdown("---")

    st.info(
        "Interactive quizzes and automatic score "
        "calculation will be added here."
    )

    # Member 3 will add the quiz questions and scoring here.
    # After calculating a student's score, the result
    # can be saved using save_score().


# ==========================================
# 11. LEADERBOARD SECTION
# ==========================================

elif page == "Leaderboard":

    st.markdown(
        '<div class="section-title">🏆 Leaderboard</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Here you can see the students with the highest scores."
    )

    st.markdown("---")

    if not database_available:

        st.warning(
            "Database connection is not available. "
            "Make sure database.py is in the project folder "
            "and the required packages are installed."
        )

    else:

        try:

            df = get_leaderboard()

            if df is not None and not df.empty:

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No scores have been recorded yet."
                )

            if st.button("🔄 Refresh Leaderboard"):

                st.rerun()

        except Exception as e:

            st.error(
                f"Could not load the leaderboard: {e}"
            )


# ==========================================
# 12. FOOTER
# ==========================================

st.markdown("---")

st.markdown(
    "<p style='text-align:center; color:gray;'>"
    "Educational Learning Platform | University Project"
    "</p>",
    unsafe_allow_html=True
)