import requests
import git
import sqlite3
import duckdb
import bs4
from PIL import Image
import whisper
import markdown
import pandas as pd
from pathlib import Path
from security import SecurityValidator
import subprocess
import json

def handle_api_fetch(task_info: dict) -> str:
    output_path = Path(task_info["output"])
    SecurityValidator.validate_path(output_path)
    
    response = requests.get(task_info["api_url"])
    response.raise_for_status()
    output_path.write_text(response.text)
    return "Success"

def handle_git_operations(task_info: dict) -> str:
    repo_path = Path(task_info["output"])
    SecurityValidator.validate_path(repo_path)
    
    repo = git.Repo.clone_from(task_info["repo_url"], repo_path)
    if task_info.get("commit_changes"):
        repo.index.add(task_info["files"])
        repo.index.commit(task_info["commit_message"])
    return "Success"

def handle_database_query(task_info: dict) -> str:
    SecurityValidator.validate_path(task_info["input"])
    SecurityValidator.validate_path(task_info["output"])
    
    if task_info["db_type"] == "sqlite":
        conn = sqlite3.connect(task_info["input"])
    else:  # duckdb
        conn = duckdb.connect(task_info["input"])
    
    result = pd.read_sql(task_info["query"], conn)
    result.to_csv(task_info["output"], index=False)
    conn.close()
    return "Success"

def handle_web_scraping(task_info: dict) -> str:
    output_path = Path(task_info["output"])
    SecurityValidator.validate_path(output_path)
    
    response = requests.get(task_info["url"])
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    data = [elem.text for elem in soup.select(task_info["selector"])]
    output_path.write_text('\n'.join(data))
    return "Success"

def handle_image_processing(task_info: dict) -> str:
    input_path = Path(task_info["input"])
    output_path = Path(task_info["output"])
    SecurityValidator.validate_path(input_path)
    SecurityValidator.validate_path(output_path)
    
    image = Image.open(input_path)
    if task_info["operation"] == "resize":
        image = image.resize((task_info["width"], task_info["height"]))
    elif task_info["operation"] == "compress":
        image.save(output_path, optimize=True, quality=task_info["quality"])
    return "Success"

def handle_audio_transcription(task_info: dict) -> str:
    input_path = Path(task_info["input"])
    output_path = Path(task_info["output"])
    SecurityValidator.validate_path(input_path)
    SecurityValidator.validate_path(output_path)
    
    model = whisper.load_model("base")
    result = model.transcribe(str(input_path))
    output_path.write_text(result["text"])
    return "Success"

def handle_markdown_conversion(task_info: dict) -> str:
    input_path = Path(task_info["input"])
    output_path = Path(task_info["output"])
    SecurityValidator.validate_path(input_path)
    SecurityValidator.validate_path(output_path)
    
    md_content = input_path.read_text()
    html_content = markdown.markdown(md_content)
    output_path.write_text(html_content)
    return "Success"

def handle_code_formatting(task_info: dict) -> str:
    input_path = Path(task_info["input"])
    SecurityValidator.validate_path(input_path)
    
    # Setup node environment if not exists
    if not Path('.nodeenv').exists():
        subprocess.run(['nodeenv', '.nodeenv'], check=True)
        subprocess.run(['.nodeenv/bin/npm', 'install', '-g', f'prettier@{task_info["version"]}'], check=True)
    
    # Run prettier
    result = subprocess.run(
        ['.nodeenv/bin/prettier', '--write', str(input_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Prettier failed: {result.stderr}")
    
    return "Success"
