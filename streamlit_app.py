import streamlit as st
import openai

# Load API Key from Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# Function to generate a quiz question
def generate_question(category):
    prompt = f"Generate a multiple-choice quiz question about {category}. Provide the question and answer without explanation."
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

# Function to get additional information
def get_more_info(question):
    prompt = f"Give a detailed explanation and background for this question: {question}"
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

# Streamlit UI
st.title("Mythology & Cricket Quiz")

# Select category
category = st.selectbox("Choose a category:", ["Hindu Mythology", "Cricket"], index=0)

# Button to generate a question
if st.button("Generate Question"):
    question_answer = generate_question(category)
    st.session_state["question_answer"] = question_answer
    st.session_state["show_answer"] = False
    st.session_state["extra_info"] = ""

# Display the question if generated
if "question_answer" in st.session_state:
    question_parts = st.session_state["question_answer"].split("Answer:")
    question = question_parts[0].strip()
    answer = question_parts[1].strip() if len(question_parts) > 1 else "Answer not available"

    st.write("### Question:")
    st.write(question)

    if st.button("Show Answer"):
        st.session_state["show_answer"] = True

    if st.session_state.get("show_answer", False):
        st.write("### Answer:")
        st.write(answer)

    if st.button("Say More"):
        st.session_state["extra_info"] = get_more_info(question)

    if "extra_info" in st.session_state and st.session_state["extra_info"]:
        st.write("### More Info:")
        st.write(st.session_state["extra_info"])
