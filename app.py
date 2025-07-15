from dotenv import load_dotenv
from groq import Groq
import re
import streamlit as st
import csv
import os
import pandas as pd

HISTORY_CSV = "prompt_history.csv"
FIELDNAMES = ["prompt", "score"]
new_entry={
    "prompt": "",
    "score": 0
}

load_dotenv()  #load API key
key= os.getenv('API_KEY')
if not key:
    st.warning("API Key not found. Please enter your API key in your .env file.")

client= Groq(api_key=key)

#run the prompt evaluation
def run_prompt(prompt):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": """You are a senior prompt engineer, 
            and your task is to go through the prompt given by the user, and evaluate it out of 10.
            Depending on their prompting history, give the user a score, and guide them accordingly.
             Separate the output into two subheaders: 'Prompt evaluation', where you talk about the prompt itself and return a 
             better prompt if necessary, and 'Answer Section', where you solve the user's query, provided the score is over 5.
             Do not include any standalone * or - characters on a line by themselves. Only use bullet points with actual content."""},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

#load previous data
def load_history():
    history = []
    if os.path.exists(HISTORY_CSV):
        with open(HISTORY_CSV, "r", newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert score from string to float
                row["score"] = float(row["score"])
                history.append(row)
    return history

# save the prompt data
def save_history(history):
    with open(HISTORY_CSV, "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        for entry in history:
            writer.writerow(entry)

# Session state init
if "history" not in st.session_state:
    st.session_state["history"] = load_history()

#interface code
st.title("🧠 The AI Whisperer: Your personal, AI based Prompt Critique!")
st.subheader("Learn prompt engineering from a model that does both: Answers your query, and rates your prompt!")

tab1, tab2= st.tabs(["📜 Prompt Evaluation", "⏳ Prompt History"])
with tab1:
    st.subheader("📜 Prompt Evaluation")
    prompt = st.text_input("Enter your prompt:")
    if st.button("Evaluate Prompt"):
        result=run_prompt(prompt)

        match = re.search(
                        r"(?:###|\*)\s*Prompt evaluation\s*(?:###|\*)?\s*(.*?)\s*(?:###|\*)\s*Answer Section\s*(?:###|\*)?\s*(.*)", 
                        result, 
                        re.DOTALL | re.IGNORECASE)
        
        
        if match:
            evaluation = match.group(1).strip()
            answer = match.group(2).strip()

            with st.container():
                st.markdown("### 📝 Prompt Evaluation")
                evaluation_cleaned= re.sub(r'^\s*[\*\-]\s*$', '', evaluation, flags=re.MULTILINE)
                st.markdown(evaluation_cleaned)

            with st.container():
                st.markdown("### 📌 Answer Section")
                answer_cleaned = re.sub(r'^\s*[\*\-]\s*$', '', answer, flags=re.MULTILINE)
                st.markdown(answer_cleaned)
        else:
            # If parsing fails, just show full output
            #st.warning("⚠️ Could not split output. Displaying full response:")
            with st.container():
                st.markdown("### Model Response")
                st.markdown(result)

        new_entry["prompt"] = prompt
        new_entry["score"] = round(float(re.search(r"[-+]?\d*\.?\d+", result).group()),2)

        # Save to session history
        st.session_state["history"].append(new_entry)
        st.success(f"Prompt evaluated! Score: {new_entry['score']}")

with tab2:
    st.subheader("⏳ Prompt History")
    if st.session_state["history"]:
        display_history = pd.DataFrame([
        {
            "prompt": entry["prompt"],
            "score": f"{entry['score']:.2f}"  # format only for UI
        }
        for entry in st.session_state["history"]
        ])
        st.dataframe(display_history,use_container_width=True)
    else:
        st.write("No history available yet. Enter a prompt to start.")
    
    st.subheader("📂 Save Progress")
    if st.button("🔽 Save Progress to CSV"):
        save_history(st.session_state["history"])
        st.success("History saved to CSV!")