import streamlit as st

from Parallel_chain import study_material_chain, final_chain


st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)


st.title("📚 StudyMate AI")
st.write(
    "Generate short notes and quiz questions "
    "from your study material using AI."
)


text = st.text_area(
    "Enter your study material",
    height=300,
    placeholder="Paste your study material here..."
)


if st.button("Generate Study Material"):

    if not text.strip():

        st.warning("Please enter some study material.")

    else:

        with st.spinner("Generating study material..."):

            result = study_material_chain.invoke({
                "text": text
            })

            final_result = final_chain.invoke(result)

        st.success("Study material generated!")

        st.subheader("📝 Short Notes")
        st.write(result["notes"])

        st.subheader("❓ Quiz")
        st.write(result["quiz"])

        st.subheader("📚 Final Study Material")
        st.write(final_result)