import streamlit as st
import openai

# Load API Key from Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# Function to generate a quiz question
def generate_question(category):
    try:
        prompt = f"Generate a multiple-choice quiz question about {category}. Format it as follows:\n\nQ: <question>\nA: <answer>"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"

# Function to get additional information
def get_more_info(question):
    try:
        prompt = f"Give a detailed explanation and background for this quiz question: {question}"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"

# Streamlit UI
st.title("Mythology & Cricket Quiz")

# Initialize session state variables
st.session_state.setdefault("question_answer", "")
st.session_state.setdefault("show_answer", False)
st.session_state.setdefault("extra_info", "")

# Select category
category = st.selectbox("Choose a category:", ["Hindu Mythology", "Cricket"], index=0)

# Generate question button
if st.button("Generate Question"):
    qa_text = generate_question(category)
    
    if "A:" in qa_text:
        question, answer = qa_text.split("A:", 1)
        st.session_state["question"] = question.strip()
        st.session_state["answer"] = answer.strip()
    else:
        st.session_state["question"] = qa_text
        st.session_state["answer"] = "Answer not available"

    st.session_state["show_answer"] = False
    st.session_state["extra_info"] = ""

# Display the question
if st.session_state.get("question"):
    st.write("### Question:")
    st.write(st.session_state["question"])

    if st.button("Show Answer"):
        st.session_state["show_answer"] = True

    if st.session_state["show_answer"]:
        st.write("### Answer:")
        st.write(st.session_state["answer"])

    if st.button("Say More"):
        st.session_state["extra_info"] = get_more_info(st.session_state["question"])

    if st.session_state["extra_info"]:
        st.write("### More Info:")
        st.write(st.session_state["extra_info"])
