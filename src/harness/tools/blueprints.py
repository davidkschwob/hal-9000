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
    }
]
