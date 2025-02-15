import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Callable, Dict
import openai
from task_handlers import (
    handle_file_operations,
    handle_llm_operations,
    handle_database_operations,
    handle_embedding_operations,
    handle_code_formatting
)
from security import SecurityValidator
from business_handlers import (
    handle_api_fetch,
    handle_git_operations,
    handle_database_query,
    handle_web_scraping,
    handle_image_processing,
    handle_audio_transcription,
    handle_markdown_conversion
)

class AutomationAgent:
    def __init__(self):
        self.openai_client = openai.OpenAI(
            base_url="https://ai-proxy.superagi.com/v1",
            api_key=os.environ["AIPROXY_TOKEN"]
        )
        
    def _parse_task(self, task: str) -> dict:
        # Ask LLM to identify task type and parameters
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4o-Mini as specified
            messages=[{
                "role": "system",
                "content": "Parse the task and identify: 1) task type 2) input file/data 3) output file 4) operation"
            }, {
                "role": "user",
                "content": task
            }],
            timeout=15  # Ensure we stay within 20s limit
        )
        return json.loads(response.choices[0].message.content)

    def execute_task(self, task: str) -> str:
        try:
            task_info = self._parse_task(task)
            
            # Validate paths if present
            if "input" in task_info:
                SecurityValidator.validate_path(task_info["input"])
            if "output" in task_info:
                SecurityValidator.validate_path(task_info["output"])
            
            handlers = {
                "file_operation": handle_file_operations,
                "llm_operation": lambda x: handle_llm_operations(x, self.openai_client),
                "database_operation": handle_database_operations,
                "embedding_operation": lambda x: handle_embedding_operations(x, self.openai_client),
                "api_fetch": handle_api_fetch,
                "git_operation": handle_git_operations,
                "database_query": handle_database_query,
                "web_scraping": handle_web_scraping,
                "image_processing": handle_image_processing,
                "audio_transcription": handle_audio_transcription,
                "markdown_conversion": handle_markdown_conversion,
                "code_formatting": handle_code_formatting
            }
            
            handler = handlers.get(task_info["type"])
            if not handler:
                raise ValueError(f"Unknown task type: {task_info['type']}")
            
            return handler(task_info)
                
        except Exception as e:
            raise Exception(f"Task execution failed: {str(e)}")
