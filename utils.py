"""Helper functions"""
import csv
import re
import os

#load previous data
def load_history(history_file: str) -> list:
    """
    Loads history

    :param history_file: path to the prompt history file
    :type history_file: str
    :returns: a list of dictionaries, each element structure following {prompt: <prompt>, score: <score>}

    """

    history = []
    if os.path.exists(history_file):
        with open(history_file, "r", newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert score from string to float
                row["score"] = float(row["score"])
                history.append(row)
    return history

# save the prompt data
def save_history(history_file,history,fields):
    """
    Saves current history to a csv file

    :param history_file: path to the prompt history file
    :type history_file: str
    :param history: list of dictionaries of prompts with its scores
    :type history: List[Dict]
    :param fields: headers of the csv file
    :type fields: list

    """
    with open(history_file, "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for entry in history:
            writer.writerow(entry)


def format_prompt_history(history) -> str:
    ''' 
    Converts the current history to a string format, to pass it to the AI model

    :param history: list of dictionaries of prompts with its scores
    :type history: List[Dict]
    :returns: string format of prompts and its score

    '''
    if not history:
        return "No prior prompts found. Enter a prompt to start!"
    return "\n".join([f"- Prompt: {h['prompt']}, Score: {h['score']}" for h in history])

def format_bulletins(text: str) -> str:
    """
    reads the AI-generated response, and filters bullets for neat presentation.

    :param text: AI's response, passed as a markdown string
    :type text: str
    :returns text: the formatted markdown rendition of the response

    """
    # Normalize bullet points
    bullet_lines = re.findall(r'^\s*[-*]\s+.+', text, flags=re.MULTILINE)       #find the bullets
    if not bullet_lines:
        return text  # No bullets found

    html = "<ul>"
    for line in bullet_lines:
        item = re.sub(r'^\s*[-*]\s+', '', line)     #convert to html list
        html += f"<li>{item.strip()}</li>"
    html += "</ul>"

    # Replace the original bullet section in text
    bullet_block = "\n".join(bullet_lines)
    text = text.replace(bullet_block, html)

    return text

def parse_ai_response(response) -> tuple:
    """
    parse AI's response, split into two sections for better readability

    :param response: AI model's generated response to the user's prompt
    :returns: a tuple consisting of evaluation, answer, score

    """
    score_match = re.search(r"[-+]?\d*\.?\d+", response)
    if score_match:
        score = round(float(score_match.group()), 2)
    else:
        score=0.0
    match = re.search(
                    r"(?:###|\*)\s*Prompt evaluation\s*(?:###|\*)?\s*(.*?)\s*(?:###|\*)\s*Answer Section\s*(?:###|\*)?\s*(.*)", 
                    response, 
                    re.DOTALL | re.IGNORECASE)
    
    if match:
        evaluation = match.group(1).strip()
        answer = match.group(2).strip()
    else:
        evaluation=response
        answer=None         #to avoid AttributeError incase of incorrect parsing
    
    return evaluation, answer, score

def validate_prompt(prompt: str) -> str:
    """
    Validate prompt input. Returns error message or empty string if valid.
    
    :params: prompt: the prompt given by the user
    :returns error: returns the type of error, if any, which the prompt encompasses
    
    """
    if not prompt or not prompt.strip():
        return "Prompt cannot be empty"
    if len(prompt.strip()) < 3:
        return "Prompt must be at least 3 characters long"
    if len(prompt.strip()) > 5000:
        return "Prompt too long (max 5000 characters)"
    return ""
