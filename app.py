import streamlit as st
from pypdf import PdfReader

from Parallel_chain import parallel_chain


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "result" not in st.session_state:

    st.session_state.result = None


if "quiz_answers" not in st.session_state:

    st.session_state.quiz_answers = {}


if "quiz_checked" not in st.session_state:

    st.session_state.quiz_checked = {}


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("📚 StudyMate AI")

st.write(
    "Upload a PDF or enter your study material "
    "to generate notes, question answers and an interactive quiz."
)


# --------------------------------------------------
# Input Section
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your study PDF",
    type=["pdf"]
)


text = st.text_area(
    "Or enter your study material",
    height=250,
    placeholder="Paste your study material here..."
)


# --------------------------------------------------
# Generate Button
# --------------------------------------------------

if st.button(
    "Generate Study Material",
    type="primary"
):

    # --------------------------------------------------
    # Read PDF
    # --------------------------------------------------

    if uploaded_file is not None:

        reader = PdfReader(uploaded_file)

        pdf_text = ""

        for page in reader.pages:

            pdf_text += page.extract_text() or ""

        text = pdf_text


    # --------------------------------------------------
    # Check Input
    # --------------------------------------------------

    if not text.strip():

        st.warning(
            "Please upload a PDF or enter some study material."
        )

    else:

        with st.spinner(
            "Generating study material..."
        ):

            st.session_state.result = (
                parallel_chain.invoke({
                    "text": text
                })
            )


        # Reset quiz state for a new quiz

        st.session_state.quiz_answers = {}

        st.session_state.quiz_checked = {}

        st.success(
            "Study material generated successfully!"
        )


# --------------------------------------------------
# Display Results
# --------------------------------------------------

if st.session_state.result is not None:

    result = st.session_state.result


    # ==================================================
    # NOTES
    # ==================================================

    st.subheader("📝 Short Notes")

    st.markdown(
        result["notes"]
    )


    # ==================================================
    # QUESTION ANSWERS
    # ==================================================

    st.subheader("❓ Question Answers")

    st.markdown(
        result["question_answers"]
    )


    # ==================================================
    # QUIZ
    # ==================================================

    st.subheader("🎯 Interactive Quiz")

    quiz = result["quiz"]


    # --------------------------------------------------
    # Calculate Current Score
    # --------------------------------------------------

    score = 0

    for i, question in enumerate(quiz.questions):

        if i in st.session_state.quiz_checked:

            selected_index = (
                st.session_state.quiz_answers[i]
            )

            if selected_index == question.correct_answer:

                score += 1


    # --------------------------------------------------
    # Score Display
    # --------------------------------------------------

    st.info(
        f"🏆 Score: {score}/{len(quiz.questions)}"
    )


    # --------------------------------------------------
    # Questions
    # --------------------------------------------------

    for i, question in enumerate(quiz.questions):

        st.markdown(
            f"### Question {i + 1}"
        )

        st.write(
            question.question
        )


        # --------------------------------------------------
        # Options
        # --------------------------------------------------

        selected_option = st.radio(

            "Choose your answer:",

            question.options,

            key=f"question_{i}",

            index=None
        )


        # --------------------------------------------------
        # Check Answer Button
        # --------------------------------------------------

        if st.button(

            f"Check Answer {i + 1}",

            key=f"check_{i}"

        ):

            if selected_option is None:

                st.warning(
                    "Please select an answer first."
                )

            else:

                selected_index = (
                    question.options.index(
                        selected_option
                    )
                )


                # Store answer

                st.session_state.quiz_answers[i] = (
                    selected_index
                )

                st.session_state.quiz_checked[i] = True


        # --------------------------------------------------
        # Show Feedback
        # --------------------------------------------------

        if i in st.session_state.quiz_checked:

            selected_index = (
                st.session_state.quiz_answers[i]
            )


            # Correct

            if selected_index == question.correct_answer:

                st.success(
                    "✅ Correct answer!"
                )


            # Wrong

            else:

                st.error(
                    "❌ Wrong answer!"
                )

                correct_option = (
                    question.options[
                        question.correct_answer
                    ]
                )

                st.info(
                    f"Correct answer: {correct_option}"
                )


        st.divider()


    # --------------------------------------------------
    # Final Score
    # --------------------------------------------------

    if len(
        st.session_state.quiz_checked
    ) == len(quiz.questions):

        final_score = 0

        for i, question in enumerate(
            quiz.questions
        ):

            if (
                st.session_state.quiz_answers[i]
                == question.correct_answer
            ):

                final_score += 1


        st.success(
            f"🎉 Quiz Completed! "
            f"Your Final Score: "
            f"{final_score}/{len(quiz.questions)}"
        )