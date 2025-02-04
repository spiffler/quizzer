import streamlit as st
import openai
import random

# Load API Key from Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# Initialize session state for question history
if "asked_questions" not in st.session_state:
    st.session_state["asked_questions"] = set()

# Function to generate a unique multiple-choice quiz question
def generate_question(category):
    try:
        # Prompt for a unique multiple-choice question with four answer options
        prompt = (
            f"Generate a unique and creative multiple-choice quiz question about {category}. "
            "Ensure that the question is different from common ones, covering lesser-known aspects. "
            "Format the output strictly as:\n\n"
            "Q: <question>\n"
            "A) <option 1>\n"
            "B) <option 2>\n"
            "C) <option 3>\n"
            "D) <option 4>\n"
            "Correct Answer: <letter of the correct answer>"
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0  # Increase randomness for variety
        )

        qa_text = response.choices[0].message.content.strip()

        # Parse the response into question, options, and answer
        lines = qa_text.split("\n")
        question = lines[0].replace("Q: ", "").strip()
        options = [line.strip() for line in lines[1:5]]  # Extracts A, B, C, D choices
        correct_answer = lines[5].replace("Correct Answer:", "").strip()

        # Ensure no repeated questions
        if question in st.session_state["asked_questions"]:
            return generate_question(category)  # Retry for a new question

        # Store the new question to prevent repetition
        st.session_state["asked_questions"].add(question)

        return question, options, correct_answer

    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}", ["Error retrieving options"], "N/A"

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
st.session_state.setdefault("options", [])
st.session_state.setdefault("correct_answer", "")
st.session_state.setdefault("show_answer", False)
st.session_state.setdefault("extra_info", "")

# Select category
category = st.selectbox("Choose a category:", ["Hindu Mythology", "Cricket"], index=0)

# Generate question button
if st.button("Generate Question"):
    question, options, correct_answer = generate_question(category)
    
    st.session_state["question"] = question
    st.session_state["options"] = options
    st.session_state["correct_answer"] = correct_answer
    st.session_state["show_answer"] = False
    st.session_state["extra_info"] = ""

# Display the question and options
if st.session_state.get("question"):
    st.write("### Question:")
    st.write(st.session_state["question"])

    # Display multiple-choice options
    for option in st.session_state["options"]:
        st.write(option)

    if st.button("Show Answer"):
        st.session_state["show_answer"] = True

    if st.session_state["show_answer"]:
        st.write("### Correct Answer:")
        st.write(f"**{st.session_state['correct_answer']}**")

    if st.button("Say More"):
        st.session_state["extra_info"] = get_more_info(st.session_state["question"])

    if st.session_state["extra_info"]:
        st.write("### More Info:")
        st.write(st.session_state["extra_info"])
