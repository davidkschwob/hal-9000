from __future__ import annotations
import subprocess
from pydantic import BaseModel, Field

class GitViewerSchema(BaseModel):
    filepath: str = Field(..., description="The relative path of the tracked file to view.")
    revision: str = Field(default="HEAD", description="The Git revision identifier like 'HEAD', a branch name, or a commit hash.")
    repo_path: str = Field(default=".", description="The local path to the Git repository.")

GROQ_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "git_show_file",
        "description": "Retrieves the content of a tracked file at a specific revision using 'git show'.",
        "parameters": GitViewerSchema.model_json_schema()
    }
}

def execute(filepath: str, revision: str = "HEAD", repo_path: str = ".") -> str:
    try:
        # Format for git show is 'revision:filepath' (e.g., 'HEAD:README.md')
        git_target = f"{revision}:{filepath}"
        
        result = subprocess.run(
            ["git", "show", git_target], 
            cwd=repo_path, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Git Error: Failed to show '{filepath}' at revision '{revision}'.\n{e.stderr.strip()}"
    except Exception as e:
        return f"System Error: {str(e)}"

