from __future__ import annotations
import subprocess
from pydantic import BaseModel, Field

class GitListerSchema(BaseModel):
    # No mandatory fields needed; it runs inside the active workspace repository
    repo_path: str = Field(default=".", description="The local path to the Git repository. Defaults to current directory.")

GROQ_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "git_list_files",
        "description": "Lists all files currently tracked in the Git repository using 'git ls-files'.",
        "parameters": GitListerSchema.model_json_schema()
    }
}

def execute(repo_path: str = ".") -> str:
    try:
        # Run system subprocess for git ls-files safely
        result = subprocess.run(
            ["git", "ls-files"], 
            cwd=repo_path, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip() if result.stdout.strip() else "No tracked files found in this Git repository."
    except subprocess.CalledProcessError as e:
        return f"Git Error: {e.stderr.strip() or 'Is this a valid git repository?'}"
    except Exception as e:
        return f"System Error: {str(e)}"

