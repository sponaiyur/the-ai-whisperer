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

tab1, tab2, tab3= st.tabs(["📜 Prompt Evaluation", "⏳ Prompt History","🪶 Golden Rules for better prompting"])
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
with tab3:
    st.subheader("🪶 Golden Rules for Better Prompting")
    st.markdown(""" 
#### 1. 🎯 Be Purposeful — Don’t Just Ask, Aim
- ❌ "Tell me about inflation"
- ✅ "Explain inflation as if I’m a high school student. Give a real-world example and 3 key effects it has on everyday life."

#### 2. 🎭 Set the Scene
- Define roles: who *you* are and who *the model* should be.
- ✅ "Act as a university professor giving a crash course on superconductors."
- ✅ "I’m a beginner Python student. Explain in simple terms."

#### 3. 🧱 Control Output Format
- ✅ "Use bullet points with bold keywords and one-liner explanations."
- ✅ "Give a markdown table comparing X vs Y."

#### 4. 🪜 Break It Down
- ❌ "Write a full research paper on LLMs."
- ✅ "First give an outline. Then expand each point into ~150 words."

#### 5. 🔁 Refine Iteratively
- Start simple:  
  `"Explain quantum tunneling in simple terms."`  
- Follow up:  
  `"Nice—now add an analogy."`  
  `"Now give me a 2-line summary."`

#### 6. 🎨 Embrace Weirdly Specific Prompts
- ✅ “Explain this like I’m a cat trying to understand economic policies.”
- ✅ “Summarize the Bhagavad Gita in a tweet thread format.”

#### 7. 📚 Use Few-Shot Prompting
- Provide examples of desired output.
- ✅ "Here’s a poem I like. Generate another in this style."

#### 8. 🙋‍♂️ Signal Uncertainty If Needed
- ✅ "I'm not sure what I want yet, but I’m exploring AI use-cases in agriculture. Can you suggest a few?"

#### 9. 🧠 Use Conditional Instructions
- ✅ "If the topic seems too advanced, simplify it with analogies."
- ✅ "If any step needs prior knowledge, explain that first."

#### 10. 📓 Keep a Prompt Scratchpad
- Log:
  - Prompts that worked well
  - What failed
  - Templates for code, summaries, MCQs, explanations

---

### 💡 Summary Quote:
> **“Be specific in goal, structured in request, flexible in tone, and iterative in thinking.”** """)