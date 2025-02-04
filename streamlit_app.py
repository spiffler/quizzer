import streamlit as st
import openai
import time
import threading

# ✅ Load API Key from Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# ✅ Ensure session state variables are initialized
if "asked_questions" not in st.session_state:
    st.session_state["asked_questions"] = set()
if "score" not in st.session_state:
    st.session_state["score"] = 0
if "total_questions" not in st.session_state:
    st.session_state["total_questions"] = 0
if "question" not in st.session_state:
    st.session_state["question"] = ""
if "options" not in st.session_state:
    st.session_state["options"] = []
if "correct_answer" not in st.session_state:
    st.session_state["correct_answer"] = ""
if "user_answer" not in st.session_state:
    st.session_state["user_answer"] = None
if "show_answer" not in st.session_state:
    st.session_state["show_answer"] = False
if "result_message" not in st.session_state:
    st.session_state["result_message"] = ""
if "timer_running" not in st.session_state:
    st.session_state["timer_running"] = False
if "time_left" not in st.session_state:
    st.session_state["time_left"] = 10
if "timer_start" not in st.session_state:
    st.session_state["timer_start"] = None
if "extra_info" not in st.session_state:
    st.session_state["extra_info"] = ""  # ✅ Store extra explanation

# API Usage Tracking
class APIUsageTracker:
    def __init__(self, max_calls_per_minute=20):
        self.calls = 0
        self.max_calls = max_calls_per_minute
        self.lock = threading.Lock()
        self.reset_timer = threading.Timer(60, self.reset_calls)

    def track_call(self):
        with self.lock:
            if not self.reset_timer.is_alive():
                self.reset_timer = threading.Timer(60, self.reset_calls)
                self.reset_timer.start()
            
            if self.calls >= self.max_calls:
                raise Exception("API rate limit exceeded")
            
            self.calls += 1
    
    def reset_calls(self):
        with self.lock:
            self.calls = 0

# Initialize API tracker
api_tracker = APIUsageTracker()

def generate_question(category):
    try:
        api_tracker.track_call()  # Track API usage

        prompt = (
            f"Generate a unique multiple-choice quiz question about {category}. "
            "Ensure the question is different from common ones. "
            "Format strictly as:\n\n"
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
            temperature=1.0
        )

        qa_text = response.choices[0].message.content.strip()
        lines = qa_text.split("\n")

        if len(lines) < 6:
            return "Error generating question.", ["A) Error", "B) Error", "C) Error", "D) Error"], "N/A"

        question = lines[0].replace("Q: ", "").strip()
        options = [lines[1].strip(), lines[2].strip(), lines[3].strip(), lines[4].strip()]
        correct_answer = lines[5].replace("Correct Answer:", "").strip()

        if question in st.session_state["asked_questions"]:
            return generate_question(category)  # Retry for a unique question

        st.session_state["asked_questions"].add(question)
        return question, options, correct_answer

    except Exception as e:
        st.error(f"Question generation error: {e}")
        return "An error occurred", ["A) Error", "B) Error", "C) Error", "D) Error"], "N/A"

# ✅ Function to get additional information
def get_more_info(question):
    try:
        api_tracker.track_call()  # Track API usage

        prompt = f"Provide an informative explanation for this quiz question: {question}"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error fetching more info: {e}"

# Streamlit UI
st.title("Mythology & Cricket Quiz")

# Initialize session state with reset mechanism
def reset_question_state():
    st.session_state["question"] = ""
    st.session_state["options"] = []
    st.session_state["correct_answer"] = ""
    st.session_state["user_answer"] = None
    st.session_state["show_answer"] = False
    st.session_state["result_message"] = ""
    st.session_state["timer_running"] = False
    st.session_state["time_left"] = 10
    st.session_state["timer_start"] = None  # Ensure fresh timer start
    st.session_state["extra_info"] = ""  # ✅ Reset additional explanation

# Scoreboard
st.markdown(f"**Score: {st.session_state.get('score', 0)} / {st.session_state.get('total_questions', 0)}**")

# Select category
category = st.selectbox("Choose a category:", ["Hindu Mythology", "Cricket"], index=0)

# Generate question
if st.button("Generate Question"):
    reset_question_state()  # Reset state before new question
    
    question, options, correct_answer = generate_question(category)

    st.session_state["question"] = question
    st.session_state["options"] = options
    st.session_state["correct_answer"] = correct_answer
    st.session_state["total_questions"] = st.session_state.get("total_questions", 0) + 1
    st.session_state["timer_running"] = True
    st.session_state["timer_start"] = time.time()  # Store start time

# Show the question
if st.session_state.get("question"):
    st.write("### Question:")
    st.write(st.session_state["question"])

    # Display multiple-choice options
    user_choice = st.radio(
        "Select your answer:",
        st.session_state["options"], 
        index=None, 
        key=f"question_{st.session_state['total_questions']}"
    )

    # Timer Logic
    if st.session_state["timer_running"]:
        elapsed_time = int(time.time() - st.session_state["timer_start"])
        st.session_state["time_left"] = max(0, 10 - elapsed_time)

        if st.session_state["time_left"] == 0:
            st.session_state["timer_running"] = False
            st.warning("⏳ **Time Over!**")

        st.markdown(f"**⏳ Time Left: {st.session_state['time_left']} seconds**")

    # Process user answer
    if user_choice and st.session_state["user_answer"] is None:
        st.session_state["user_answer"] = user_choice
        st.session_state["timer_running"] = False

        if user_choice.startswith(st.session_state["correct_answer"]):
            st.session_state["result_message"] = "<p style='color: green; font-size: 18px;'>✅ Correct!</p>"
            st.session_state["score"] += 1
        else:
            st.session_state["result_message"] = f"<p style='color: red; font-size: 18px;'>❌ Incorrect! The correct answer is {st.session_state['correct_answer']}.</p>"

    if st.session_state.get("result_message"):
        st.markdown(st.session_state["result_message"], unsafe_allow_html=True)

    # ✅ "Say More" Button
    if st.button("Say More"):
        st.session_state["extra_info"] = get_more_info(st.session_state["question"])

    if st.session_state["extra_info"]:
        st.write("### More Info:")
        st.write(st.session_state["extra_info"])
