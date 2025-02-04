import streamlit as st
import openai
import random
import time

# Load API Key from Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# Initialize session state for question history
if "asked_questions" not in st.session_state:
    st.session_state["asked_questions"] = set()

# Initialize session state for quiz mechanics
st.session_state.setdefault("question", "")
st.session_state.setdefault("options", [])
st.session_state.setdefault("correct_answer", "")
st.session_state.setdefault("user_answer", None)
st.session_state.setdefault("show_answer", False)
st.session_state.setdefault("extra_info", "")
st.session_state.setdefault("score", 0)
st.session_state.setdefault("total_questions", 0)
st.session_state.setdefault("time_left", 10)
st.session_state.setdefault("timer_running", False)

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

# Display Scoreboard
st.markdown(f"**Score: {st.session_state['score']} / {st.session_state['total_questions']}**")

# Select category
category = st.selectbox("Choose a category:", ["Hindu Mythology", "Cricket"], index=0)

# Generate question button
if st.button("Generate Question"):
    question, options, correct_answer = generate_question(category)

    st.session_state["question"] = question
    st.session_state["options"] = options
    st.session_state["correct_answer"] = correct_answer
    st.session_state["user_answer"] = None
    st.session_state["show_answer"] = False
    st.session_state["extra_info"] = ""
    st.session_state["total_questions"] += 1

    # Start Timer
    st.session_state["time_left"] = 10
    st.session_state["timer_running"] = True

# Display the question and options
if st.session_state.get("question"):
    st.write("### Question:")
    st.write(st.session_state["question"])

    # Timer
    if st.session_state["timer_running"]:
        with st.empty():
            while st.session_state["time_left"] > 0 and st.session_state["user_answer"] is None:
                st.write(f"**Time Left: {st.session_state['time_left']} seconds**")
                time.sleep(1)
                st.session_state["time_left"] -= 1

            st.session_state["timer_running"] = False

    # Display multiple-choice options with color feedback
    user_choice = st.radio("Select your answer:", st.session_state["options"], index=None)

    if user_choice:
        st.session_state["user_answer"] = user_choice

        if user_choice.startswith(st.session_state["correct_answer"]):
            st.markdown(f"<p style='color: green; font-size: 18px;'>✅ Correct!</p>", unsafe_allow_html=True)
            st.session_state["score"] += 1
        else:
            st.markdown(f"<p style='color: red; font-size: 18px;'>❌ Incorrect! The correct answer is {st.session_state['correct_answer']}.</p>", unsafe_allow_html=True)

    # "Say More" button
    if st.button("Say More"):
        st.session_state["extra_info"] = get_more_info(st.session_state["question"])

    if st.session_state["extra_info"]:
        st.write("### More Info:")
        st.write(st.session_state["extra_info"])
