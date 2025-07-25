# 🪶 The AI Whisperer: A tool to learn prompt engineering with everyday queries
This app was designed to teach everyone- not just AI engineers- the concept of prompt engineering best practices, through a simple chatbot powered by the LLaMA3-70B model.

---
## ✨ Features:
- 🔍 Prompt evaluation out of 10, with reasoning.
- ✍️ Suggestions for better prompt structuring.
- ✅ Executes and returns results if score > 5.
- 💭 Retains memory of 5 recent prompts, to support iterative thinking.
- ⏳ History tracking with scores.
- 💾 Save to CSV and load across sessions.
- 📐 Clean, responsive Streamlit UI.

---
## 💻 Installation
```bash
#1. Clone the repository
git clone https://github.com/sponaiyur/the-ai-whisperer.git
cd the-ai-whisperer

#2. Activate your virtual environment:
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

#3. Install dependencies
pip install -r requirements.txt

#4. Set up your .env file to hold your api key
cp .env.template .env      #open .env to fill you actual key!

#5. run the application
streamlit run app.py
```
---
## 🚀 Usage
Once the app is running, enter your prompt in the input field. The app will evaluate it, suggest improvements, and respond to your query if the score is above 5. Use the Prompt History tab to view or download your previous prompts and scores.
Note: If you want the model to retain more than 5 prompts for iterations, please modify the `MAX_HISTORY_ITEMS` constant in `config.py`.

---
## Tech Stack
- [Streamlit](https://streamlit.io/)
- [LLaMA3-70B via Groq API](https://console.groq.com/)
- Python 3.10+

---

## 🛡️ License
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

This project is licensed under the [MIT License](LICENSE).

Feel free to use, modify and share — with proper attribution. 

---
## 🙋‍♀️ Contributions
Pull requests are welcome! For major changes, please open an issue first.
