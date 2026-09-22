"""Tool schemas exposed to the language model."""


tool_blueprints = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files tracked by Git in the target workspace.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            "strict": True
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the text contents of a specific file path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "The path to the file."}
                },
                "required": ["filepath"]
            }
        }
    }
]
