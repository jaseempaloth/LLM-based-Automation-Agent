import json
import os
from datetime import datetime
import subprocess
from pathlib import Path
import sqlite3
import openai
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def handle_file_operations(task_info: dict) -> str:
    operation = task_info["operation"]
    
    if operation == "count_weekday":
        dates = Path(task_info["input"]).read_text().splitlines()
        count = sum(1 for date in dates if datetime.strptime(date.strip(), "%Y-%m-%d").strftime("%A") == task_info["weekday"])
        Path(task_info["output"]).write_text(str(count))
        
    elif operation == "sort_json":
        with open(task_info["input"]) as f:
            data = json.load(f)
        sorted_data = sorted(data, key=lambda x: (x["last_name"], x["first_name"]))
        with open(task_info["output"], "w") as f:
            json.dump(sorted_data, f, indent=2)
            
    elif operation == "recent_logs":
        log_files = sorted(Path(task_info["input"]).glob("*.log"), key=os.path.getmtime, reverse=True)
        first_lines = []
        for log_file in log_files[:10]:
            with open(log_file) as f:
                first_lines.append(f.readline().strip())
        Path(task_info["output"]).write_text("\n".join(first_lines))
        
    elif operation == "markdown_index":
        index = {}
        for md_file in Path(task_info["input"]).glob("**/*.md"):
            content = md_file.read_text()
            for line in content.splitlines():
                if line.startswith("# "):
                    index[str(md_file.relative_to(task_info["input"]))] = line[2:].strip()
                    break
        Path(task_info["output"]).write_text(json.dumps(index, indent=2))
    
    return "Success"

def handle_llm_operations(task_info: dict, client: openai.OpenAI) -> str:
    if task_info["operation"] == "extract_email":
        content = Path(task_info["input"]).read_text()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "Extract the sender's email address from this email message."
            }, {
                "role": "user",
                "content": content
            }]
        )
        Path(task_info["output"]).write_text(response.choices[0].message.content.strip())
        
    elif task_info["operation"] == "extract_card":
        image = Image.open(task_info["input"])
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [{
                    "type": "image",
                    "source": {"path": task_info["input"]}
                }, "Extract the credit card number from this image"]
            }]
        )
        card_number = "".join(filter(str.isdigit, response.choices[0].message.content))
        Path(task_info["output"]).write_text(card_number)
    
    return "Success"

def handle_database_operations(task_info: dict) -> str:
    conn = sqlite3.connect(task_info["input"])
    cursor = conn.cursor()
    
    if task_info["operation"] == "sum_gold_tickets":
        result = cursor.execute(
            "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"
        ).fetchone()[0]
        Path(task_info["output"]).write_text(str(result))
    
    conn.close()
    return "Success"

def handle_embedding_operations(task_info: dict, client: openai.OpenAI) -> str:
    comments = Path(task_info["input"]).read_text().splitlines()
    
    # Get embeddings for all comments
    embeddings = []
    for comment in comments:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=comment
        )
        embeddings.append(response.data[0].embedding)
    
    # Find most similar pair
    similarities = cosine_similarity(embeddings)
    np.fill_diagonal(similarities, -1)
    i, j = np.unravel_index(similarities.argmax(), similarities.shape)
    
    Path(task_info["output"]).write_text(f"{comments[i]}\n{comments[j]}")
    return "Success"
