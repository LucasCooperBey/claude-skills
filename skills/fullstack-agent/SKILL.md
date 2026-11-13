---
name: fullstack-agent
description: Enables AI agents to create complete web applications with file system operations, code execution, template sandboxes, and live preview through sandbox URL hosting.
---

# Full Stack Agent Skill

## Overview

Full Stack Agents combine:
- **File system operations** (read, write, search, replace)
- **Code execution** for running build tools, tests
- **Template sandboxes** with frameworks pre-installed
- **Live preview** through sandbox URL hosting

---

## Quick Start

### Setup with Next.js Template
```python
from lib.coding_agent import coding_agent
from lib.tools_schemas import tools_schemas
from lib.tools import tools
from lib.prompts import SYSTEM_PROMPT_WEB_DEV
from lib.ui import ui
from lib.utils import create_sandbox
from openai import OpenAI

# Create sandbox with Next.js pre-installed
sbx = create_sandbox(template="dlai-nextjs-developer")

client = OpenAI()
messages = []

# Launch with UI
demo = ui(
    coding_agent,
    messages,
    host=f"https://{sbx.get_host(3000)}",  # Next.js dev server
    client=client,
    sbx=sbx,
    max_steps=100,
    system=SYSTEM_PROMPT_WEB_DEV,
    tools=tools,
    tools_schemas=tools_schemas,
    model="gpt-4o-mini",
)
demo.launch(share=True, height=800)
```

---

## Available Tools

Six sandbox tools handle all file system operations:

| Tool | Purpose |
|------|---------|
| `list_directory` | Explore project structure |
| `read_file` | Read existing files |
| `write_file` | Create or update files (auto-creates directories) |
| `search_file_content` | Regex search across files (skips node_modules) |
| `replace_in_file` | Find-and-replace text in a file |
| `glob` | Find files by glob pattern (e.g., `**/*.tsx`) |

Each tool accepts a sandbox instance (`sbx`) and returns a dict with results or `{"error": ...}`.

See [reference/tool-implementations.md](reference/tool-implementations.md) for complete Python implementations and JSON schemas.

### Tools Dictionary (binding tools to sandbox)

```python
def create_tools(sbx):
    """Create tools bound to a sandbox."""
    return {
        "list_directory": lambda path: list_directory(path, sbx),
        "read_file": lambda file_path: read_file(file_path, sbx),
        "write_file": lambda file_path, content: write_file(file_path, content, sbx),
        "search_file_content": lambda pattern, path=".", limit=20: search_file_content(pattern, path, limit, sbx),
        "replace_in_file": lambda file_path, old_text, new_text: replace_in_file(file_path, old_text, new_text, sbx),
        "glob": lambda pattern: glob_files(pattern, sbx),
    }

tools_schemas = [
    list_directory_schema, read_file_schema, write_file_schema,
    search_file_content_schema, replace_in_file_schema, glob_schema,
]
```

---

## System Prompts

Two pre-built system prompts are available:

### SYSTEM_PROMPT_WEB_DEV
General-purpose Next.js 14+ / React / TypeScript / Tailwind prompt. Instructs the agent to explore before modifying, make incremental changes, and preserve existing code style. Includes Next.js App Router project structure and common patterns (pages, components, API routes).

See [reference/system-prompts.md](reference/system-prompts.md) for the complete prompt text and code pattern examples.

---

## Agent Workflow Patterns

The agent follows an explore-then-modify pattern:

1. **Explore** -- `list_directory` and `read_file` to understand structure
2. **Plan** -- Identify which files to create or modify
3. **Execute** -- `write_file` or `replace_in_file` one file at a time
4. **Verify** -- Read modified files, check for errors

### Common Scenarios

| Scenario | Key Tools Used |
|----------|---------------|
| Create landing page | `list_directory` -> `read_file` -> `write_file` (page + components) |
| Add authentication | `list_directory` -> `write_file` (login page + form component) -> update layout |
| Modify existing feature | `search_file_content` -> `read_file` -> `replace_in_file` |

See [reference/examples.md](reference/examples.md) for detailed step-by-step workflow examples and Gradio UI setup.

---

## Gradio UI Integration

The UI provides chat interface, live preview iframe, token usage stats, and tool execution logs:

```python
demo = ui(
    coding_agent, messages=[],
    host=f"https://{sbx.get_host(3000)}",
    client=client, sbx=sbx, max_steps=100,
    system=SYSTEM_PROMPT_WEB_DEV,
    tools=create_tools(sbx),
    tools_schemas=tools_schemas,
    model="gpt-4o-mini",
)
demo.launch(share=True, height=800)
```

---

## Tips for Better Results

1. **Set Higher max_steps**: Web dev needs more iterations (50-100)
2. **Use Templates**: Pre-configured sandboxes save time
3. **Provide Context**: Tell the agent about existing patterns
4. **Incremental Requests**: Build features step by step
5. **Review Changes**: Check modified files before next prompt

## Source

Inspired by the DeepLearning.AI course Building Coding Agents with Tool Execution, lesson L6. No canonical public repo was found.
