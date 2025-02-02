import streamlit as st
import openai

# Load API Key from Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# Function to generate a quiz question
def generate_question(category):
    try:
        prompt = f"Generate a multiple-choice quiz question about {category}. Provide the question and answer without explanation."
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",  # Fixed model name
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.RateLimitError:
        return "OpenAI API quota exceeded. Please check your billing settings."
    except openai.APIConnectionError:
        return "Failed to connect to OpenAI. Please check your internet connection."
    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"

# Function to get additional information
def get_more_info(question):
    try:
        prompt = f"Give a detailed explanation and background for this question: {question}"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",  # Fixed model name
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"

# Streamlit UI
st.title("Mythology & Cricket Quiz")

# Initialize session state variables if not set
if "question_answer" not in st.session_state:
    st.session_state["question_answer"] = ""
if "show_answer" not in st.session_state:
    st.session_state["show_answer"] = False
if "extra_info" not in st.session_state:
    st.session_state["extra_info"] = ""

# Select category
category = st.selectbox("Choose a category:", ["Hindu Mythology", "Cricket"], index=0)

# Button to generate a question
if st.button("Generate Question"):
    st.session_state["question_answer"] = generate_question(category)
    st.session_state["show_answer"] = False
    st.session_state["extra_info"] = ""

# Display the question if generated
if st.session_state["question_answer"]:
    question_parts = st.session_state["question_answer"].split("Answer:")
    question = question_parts[0].strip()
    answer = question_parts[1].strip() if len(question_parts) > 1 else "Answer not available"

    st.write("### Question:")
    st.write(question)

    if st.button("Show Answer"):
        st.session_state["show_answer"] = True

    if st.session_state["show_answer"]:
        st.write("### Answer:")
        st.write(answer)

    if st.button("Say More"):
        st.session_state["extra_info"] = get_more_info(question)

    if st.session_state["extra_info"]:
        st.write("### More Info:")
        st.write(st.session_state["extra_info"])
