import streamlit as st
import openai
import random

# Load API Key from Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# Initialize session state for question history
if "asked_questions" not in st.session_state:
    st.session_state["asked_questions"] = set()

# Function to generate a unique quiz question
def generate_question(category):
    try:
        # Generate a unique and varied question
        prompt = (
            f"Generate a unique and creative multiple-choice quiz question about {category}. "
            "Ensure that the question is different from common ones, covering lesser-known aspects. "
            "Avoid repeating previously asked questions and rephrase common ones. "
            "Format the output strictly as:\nQ: <question>\nA: <answer>"
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0  # Higher randomness for more variety
        )

        qa_text = response.choices[0].message.content.strip()

        if "A:" in qa_text:
            question, answer = qa_text.split("A:", 1)
            question = question.strip()
            answer = answer.strip()
        else:
            return "Failed to generate a valid question.", "Answer not available"

        # Check if question was already asked
        if question in st.session_state["asked_questions"]:
            return generate_question(category)  # Try again for a new question

        # Store the new question to prevent repetition
        st.session_state["asked_questions"].add(question)

        return question, answer

    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}", "Answer not available"

# Function to get additional information
def get_more_info(question):
    try:
        prompt = f"Give a detailed explanation and background for this quiz question: {question}"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8  # Slightly lower randomness for accuracy
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"

# Streamlit UI
st.title("Mythology & Cricket Quiz")

# Initialize session state variables
st.session_state.setdefault("question", "")
st.session_state.setdefault("answer", "")
st.session_state.setdefault("show_answer", False)
st.session_state.setdefault("extra_info", "")

# Select category
category = st.selectbox("Choose a category:", ["Hindu Mythology", "Cricket"], index=0)

# Generate question button
if st.button("Generate Question"):
    question, answer = generate_question(category)
    
    st.session_state["question"] = question
    st.session_state["answer"] = answer
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
