# Layout

├── __init__.py      # Package indicator exposes clean module entry points
├── cli.py           # Extracts terminal run paths and boots the system
├── agent.py         # Main ReAct loop controller and state processor
│
├── brain/           # Model interface layer
│   ├── __init__.py
│   └── client.py    # Authenticates and configures Groq connection
│
├── sandbox/         # Code execution environment
│   ├── __init__.py
│   └── executor.py  # Run system subprocess scripts securely
│
└── tools/           # Structural discovery and text tools
    ├── __init__.py
    ├── blueprints.py# JSON schema blueprints for tool detection
    └── registry.py  # Map schemas back to direct Python functions
