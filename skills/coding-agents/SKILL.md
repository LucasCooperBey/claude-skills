---
name: coding-agents
description: Core patterns for building AI coding agents with tool calling, agent loops, and autonomous code execution — plus expert guidance on agent frameworks and production patterns. Use for AI agent development, agent architecture, framework selection, and production agent considerations.
---

# Coding Agents Skill

> Core patterns for building AI coding agents with tool calling, agent loops, and autonomous code execution. Absorbed `ai-agent-expert` (framework + production-pattern guidance) — same domain.

## Quick Reference

### Agent Loop Pattern
```python
def coding_agent(
    client: OpenAI,
    query: str,
    system: str,
    tools: dict[str, Callable],
    tools_schemas: list[dict],
    messages: list[dict] = None,
    max_steps: int = 10,
):
    if messages is None:
        messages = []
    messages.append({"role": "user", "content": query})
    steps = 0

    while steps < max_steps:
        response = llm(client, messages, system, tools=tools_schemas)
        has_function_call = False

        for part in response.output:
            messages.append(part)
            if part.type == "message":
                print(f"[agent] {response.output_text}")
            elif part.type == "function_call":
                has_function_call = True
                name = part.name
                result = execute_tool(name, part.arguments, tools)
                messages.append({
                    "type": "function_call_output",
                    "call_id": part.call_id,
                    "output": json.dumps(result),
                })

        if not has_function_call:
            break  # Agent finished - no more tool calls
        steps += 1

    return messages
```

### Tool Execution Handler
```python
def execute_tool(name: str, args: str, tools: dict[str, Callable]):
    try:
        args = json.loads(args)
        if name not in tools:
            return {"error": f"Tool {name} doesn't exist."}
        result = tools[name](**args)
    except json.JSONDecodeError as e:
        result = {"error": f"{name} failed to parse arguments: {str(e)}"}
    except KeyError as e:
        result = {"error": f"Missing key in arguments: {str(e)}"}
    except Exception as e:
        result = {"error": str(e)}
    return result
```

---

## Tool Schema Patterns

### Execute Code Tool
```python
execute_code_schema = {
    "type": "function",
    "name": "execute_code",
    "description": "Execute Python code and return the result or error.",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute as a string",
            }
        },
        "required": ["code"],
        "additionalProperties": False,
    },
}
```

### Read File Tool
```python
read_file_schema = {
    "type": "function",
    "name": "read_file",
    "description": "Reads content from a file with optional offset and limit.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute path to the file to read",
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of characters to read",
            },
            "offset": {
                "type": "number",
                "description": "Starting position in the file",
            },
        },
        "required": ["file_path"],
        "additionalProperties": False,
    },
}
```

### Write File Tool
```python
write_file_schema = {
    "type": "function",
    "name": "write_file",
    "description": "Writes content to a file, creating directories if needed.",
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Content to write to the file",
            },
            "file_path": {
                "type": "string",
                "description": "Absolute path where the file will be written",
            },
        },
        "required": ["content", "file_path"],
        "additionalProperties": False,
    },
}
```

### Search File Content Tool
```python
search_file_content_schema = {
    "type": "function",
    "name": "search_file_content",
    "description": "Search for text patterns in files.",
    "parameters": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Text pattern to search for",
            },
            "path": {
                "type": "string",
                "description": "Directory or file path to search in",
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of results",
            },
        },
        "required": ["pattern"],
        "additionalProperties": False,
    },
}
```

### Replace In File Tool
```python
replace_in_file_schema = {
    "type": "function",
    "name": "replace_in_file",
    "description": "Replace text in a file.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file",
            },
            "old_text": {
                "type": "string",
                "description": "Text to find and replace",
            },
            "new_text": {
                "type": "string",
                "description": "Replacement text",
            },
        },
        "required": ["file_path", "old_text", "new_text"],
        "additionalProperties": False,
    },
}
```

---

## Tool Implementations

### Execute Code (Local)
```python
from typing import TypedDict
import sys
from io import StringIO

class Execution(TypedDict):
    results: list[str]
    errors: list[str]

def execute_code(code: str) -> Execution:
    """Execute Python code locally with stdout capture."""
    execution = {"results": [], "errors": []}
    old_stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        exec(code)
        result = sys.stdout.getvalue()
        sys.stdout = old_stdout
        execution["results"] = [result]
    except Exception as e:
        execution["errors"] = [str(e)]
    finally:
        sys.stdout = old_stdout
        return execution
```

### Read File
```python
import os
from typing import Optional, Dict, Any

class ToolError(Exception):
    """Custom exception for tool failures"""
    pass

def read_file(
    file_path: str,
    limit: Optional[int] = None,
    offset: int = 0
) -> Dict[str, Any]:
    """Read file content with optional offset and limit."""
    if not os.path.exists(file_path):
        raise ToolError(f"File does not exist: {file_path}")
    if not os.path.isfile(file_path):
        raise ToolError(f"Path is not a file: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            if offset > 0:
                f.seek(offset)
            content = f.read(limit) if limit else f.read()
        return {"content": content, "size": len(content)}
    except PermissionError:
        raise ToolError(f"Permission denied: {file_path}")
```

### Write File
```python
def write_file(content: str, file_path: str) -> Dict[str, Any]:
    """Write content to file, creating directories if needed."""
    try:
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        file_size = os.path.getsize(file_path)
        return {
            "message": f"Written {file_size} bytes to {file_path}",
            "size": file_size,
        }
    except PermissionError:
        raise ToolError(f"Permission denied: {file_path}")
```

---

## System Prompts

### Basic Coding Agent
```python
system = """You are a Senior Python programmer.
You must always use the `execute_code` tool to run code.
You collect user's inputs by using the `input` python function.
"""
```

### Data Analyst Agent
```python
system = """You are a senior python programmer.
You must run the code using the `execute_code` tool.
The user has uploaded a data.csv.
You help the user understanding the data
by creating interesting plots.
"""
```

### Full Stack Web Developer
```python
# See fullstack-agent skill for comprehensive prompt
```

---

## Message History Structure

```python
# User message
{"role": "user", "content": "Create a function to calculate fibonacci"}

# Assistant message (text)
{"type": "message", "content": "I'll create a fibonacci function..."}

# Assistant message (tool call)
{
    "type": "function_call",
    "name": "execute_code",
    "call_id": "call_abc123",
    "arguments": '{"code": "def fib(n):\\n    if n <= 1:\\n        return n\\n    return fib(n-1) + fib(n-2)\\nprint(fib(10))"}'
}

# Tool result
{
    "type": "function_call_output",
    "call_id": "call_abc123",
    "output": '{"results": ["55\\n"], "errors": []}'
}
```

---

## Best Practices

### 1. Always Set max_steps
Prevent infinite loops with a reasonable cap (5-20 for simple tasks, up to 100 for complex ones).

### 2. Preserve Message History
Pass `messages` between calls to maintain context for multi-turn conversations.

### 3. Handle Errors Gracefully
Use ToolError class to return clean error messages, not stack traces.

### 4. Use Descriptive Tool Schemas
Clear descriptions help the LLM choose the right tool and parameters.

### 5. Log Tool Execution
Print/log tool calls and results for debugging:
```python
print(f"[{name}] executing...")
print(f"[{name}] {result}")
```

---

## Integration Points

- **E2B Sandbox**: Use `e2b-sandbox` skill for cloud execution
- **Data Analysis**: Use `data-analyst-agent` skill for CSV/data work
- **Full Stack**: Use `fullstack-agent` skill for web app generation
- **Gradio UI**: Wrap agent in Gradio for chat interface

---

## TypeScript Equivalent (Agent SDK)

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const tools = [
  {
    name: "execute_code",
    description: "Execute Python code and return the result.",
    input_schema: {
      type: "object",
      properties: {
        code: { type: "string", description: "Python code to execute" }
      },
      required: ["code"]
    }
  }
];

async function codingAgent(query: string, maxSteps = 10) {
  const messages = [{ role: "user", content: query }];

  for (let step = 0; step < maxSteps; step++) {
    const response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 4096,
      tools,
      messages,
    });

    // Process response, execute tools, append to messages
    if (response.stop_reason === "end_turn") break;
  }
}
```

## Source

Inspired by the DeepLearning.AI short course Building Coding Agents with Tool Execution (E2B). No canonical public repo was found; a student copy is at https://github.com/jose-deblas/building-coding-agents, and the original owner is unconfirmed.
