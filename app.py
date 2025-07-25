from groq import Groq
import streamlit as st
import pandas as pd
import config
from utils import *

if not config.API_KEY:
    st.warning("API key not defined! Please define your API key in your .env file and retry!")

client= Groq(api_key=config.API_KEY)
new_entry={"prompt":"","score":0}

def run_prompt(prompt):
    user_history=format_prompt_history(st.session_state.get("history")[-config.MAX_HISTORY_ITEMS:])     #considers 5 recent prompts
    model_prompt= f"""You are a senior prompt engineer, 
    and your task is to go through the prompt given by the user, and evaluate it out of 10.
    Depending on their prompting history, give the user a score, and guide them accordingly.
    Separate the output into two subheaders: 'Prompt evaluation', where you talk about the prompt itself and return a 
    better prompt if necessary, and 'Answer Section', where you solve the user's query, provided the score is over 5.
    Do not include any standalone * or - characters on a line by themselves. Only use bullet points with actual content.
    
    Given, user's prompting history:
    {user_history}
"""

    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {"role": "system", "content": model_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

#UI definition
if "history" not in st.session_state:
    st.session_state["history"] = load_history(config.HISTORY_CSV)        #session state init

st.set_page_config(page_title="🪶 The AI Whisperer", layout="wide")

#custom CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat+Alternates:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Winky+Rough:ital,wght@0,300..900;1,300..900&display=swap');
        * {
            box-sizing: border-box;
            font-family: 'Winky Rough', cursive;
        }
        
        /* the body has one font */
        html, body, [class*="st-"] {
            font-family: 'Winky Rough', cursive;
        }
        
        /* and markdown headers have a different font */
        div[data-testid="stMarkdown"] h1,
        div[data-testid="stMarkdown"] h2,
        div[data-testid="stMarkdown"] h3,
        div[data-testid="stMarkdown"] h4,
        div[data-testid="stMarkdown"] h5,
        div[data-testid="stMarkdown"] h6 {
            font-family: 'Montserrat Alternates', sans-serif !important;
        }
            
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🧠 The AI Whisperer: Your personal, AI based Prompt Critique!")
st.markdown("## Learn prompt engineering from a model that does both: Answers your query, and rates your prompt!")

tab1, tab2, tab3= st.tabs(["📜 Prompt Evaluation", "⏳ Prompt History","🪶 Golden Rules for better prompting"])
with tab1:
    prompt=st.text_area("Enter your prompt",height=68)
    if st.button("Evaluate Prompt",type="primary"):
        response=run_prompt(prompt)
        evaluation, answer, score = parse_ai_response(response)
        if evaluation:
            with st.container():
                    st.markdown("### 📝 Prompt Evaluation")
                    evaluation_cleaned= re.sub(r'^\s*[\*\-]\s*$', '', evaluation, flags=re.MULTILINE)
                    formatted_evaluation=format_bulletins(evaluation_cleaned)
                    st.markdown(formatted_evaluation, unsafe_allow_html=True)

        if answer:
            with st.container():
                st.markdown("### 📌 Answer Section")
                answer_cleaned = re.sub(r'^\s*[\*\-]\s*$', '', answer, flags=re.MULTILINE)
                formatted_answer=format_bulletins(answer_cleaned)
                st.markdown(formatted_answer, unsafe_allow_html=True)
        new_entry["prompt"] = prompt
        new_entry["score"] = score

        # Save to session history
        st.session_state["history"].append(new_entry)
        st.success(f"Prompt evaluated! Score: {new_entry['score']}")

with tab2:
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

    st.markdown("## 📂 Save Progress")
    if st.button("🔽 Save Progress to CSV"):
        save_history(config.HISTORY_CSV, st.session_state["history"], config.FIELDNAMES)
        st.success("History saved to CSV!")

with tab3:
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