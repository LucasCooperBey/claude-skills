---
name: e2b-sandbox
description: Secure cloud sandbox execution for AI coding agents using E2B. Isolated containers for safe untrusted code execution.
---

# E2B Sandbox Skill

> Secure cloud sandbox execution for AI coding agents using E2B (e2b.dev).

## What is E2B?

E2B provides isolated cloud sandboxes where AI agents can safely execute untrusted code. Key benefits:
- **Isolation**: Code runs in a container, can't affect your system
- **Persistence**: Sandboxes can maintain state between calls
- **File System**: Full file read/write capabilities
- **Web Hosting**: Can serve websites from sandbox
- **Multi-Language**: Python, JavaScript, and more

---

## Quick Start

### Installation
```bash
pip install e2b-code-interpreter
```

### Environment
```bash
# Get API key from https://e2b.dev
export E2B_API_KEY="your_api_key"
```

### Basic Usage
```python
from e2b_code_interpreter import Sandbox

# Create sandbox (default 5 min timeout)
sbx = Sandbox.create(timeout=60 * 60)  # 1 hour

# Execute code
result = sbx.run_code("print('Hello from sandbox!')")
print(result.results)  # ['Hello from sandbox!\n']

# Execute JavaScript
sbx.run_code("console.log('Hello JS!')", language="javascript")
```

---

## Core Operations

### Code Execution
```python
from e2b_code_interpreter import Sandbox, Execution

sbx = Sandbox.create()

# Simple execution
execution = sbx.run_code("2 + 2")
print(execution.results)  # Results list

# With error handling
execution = sbx.run_code("1/0")
if execution.error:
    print(f"Error: {execution.error}")

# Return as JSON for agent consumption
result = execution.to_json()
```

### File Operations
```python
# Create directory
sbx.files.make_dir("/home/user/data")

# Write file
sbx.files.write("/home/user/data/hello.txt", "Hello from sandbox")

# Read file
content = sbx.files.read("/home/user/data/hello.txt")

# Remove file
sbx.files.remove("/home/user/data/hello.txt")

# List directory
files = sbx.files.list("/home/user")
```

### Running Commands
```python
# Foreground command (waits for completion)
result = sbx.commands.run("pip install pandas")

# Background command (returns immediately)
process = sbx.commands.run(
    "python -m http.server 3000 --bind 0.0.0.0",
    background=True
)
```

---

## Sandbox Management

### Creating with Metadata
```python
from e2b_code_interpreter import Sandbox, SandboxQuery, SandboxState

# Create with metadata for later querying
sbx = Sandbox.create(
    metadata={
        "project": "my-project",
        "user": "alice",
        "purpose": "data-analysis"
    }
)
```

### Querying Sandboxes
```python
# Find sandboxes by metadata
running = Sandbox.list(SandboxQuery(
    metadata={"project": "my-project"},
    state=[SandboxState.RUNNING]
))

for sbx in running.next_items():
    print(f"Found: {sbx.sandbox_id}")
```

### Reconnecting to Sandbox
```python
# Save sandbox ID
sandbox_id = sbx.sandbox_id

# Later, reconnect
sbx = Sandbox.connect(sandbox_id)
```

### Caching Pattern
```python
def create_sandbox(template=None, metadata=None):
    """Create or reconnect to existing sandbox."""
    if metadata:
        existing = Sandbox.list(SandboxQuery(
            metadata=metadata,
            state=[SandboxState.RUNNING]
        )).next_items()
        if existing:
            return Sandbox.connect(existing[0].sandbox_id)

    return Sandbox.create(
        template=template,
        metadata=metadata,
        timeout=60 * 60
    )
```

---

## Web Applications

### Serving Static Files
```python
# Create HTML file
html = """<!DOCTYPE html>
<html>
<head><title>Sandbox App</title></head>
<body><h1>Hello from E2B!</h1></body>
</html>"""

sbx.files.write("index.html", html)

# Start server
sbx.commands.run(
    "python -m http.server 3000 --bind 0.0.0.0",
    background=True
)

# Get public URL
host = sbx.get_host(3000)
url = f"https://{host}/index.html"
print(f"Access at: {url}")
```

### Templates
```python
# Use pre-configured template (e.g., Next.js)
sbx = Sandbox.create(template="dlai-nextjs-developer")

# Template has Next.js pre-installed
host = sbx.get_host(3000)  # Next.js dev server port
```

---

## Integration with Coding Agents

### Execute Code Tool (Cloud Version)
```python
from e2b_code_interpreter import Execution, Sandbox
from typing import Tuple

def execute_code(code: str, sbx: Sandbox) -> Tuple[dict, dict]:
    """Execute code in E2B sandbox."""
    execution = sbx.run_code(code)
    return execution.to_json(), {}

# Use in agent
tools = {"execute_code": lambda code: execute_code(code, sbx)}
```

### Full Agent Integration
```python
from lib.coding_agent import coding_agent
from lib.tools_schemas import execute_code_schema
from openai import OpenAI

client = OpenAI()
sbx = Sandbox.create()

system = """You are a senior python programmer.
You must run the code using the `execute_code` tool."""

def execute_code_sandboxed(code: str):
    execution = sbx.run_code(code)
    return execution.to_json()

tools = {"execute_code": execute_code_sandboxed}

# Run agent
messages = coding_agent(
    client=client,
    query="Create a function to generate random passwords",
    system=system,
    tools=tools,
    tools_schemas=[execute_code_schema],
    max_steps=10
)
```

---

## Creating Plots

```python
code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.random.randn(100)
y = np.random.randn(100)

plt.scatter(x, y, alpha=0.7)
plt.title('Random Scatter')
plt.show()
"""

execution = sbx.run_code(code)

# Display in Jupyter/notebook
from IPython.display import Image, display
import base64

if execution.results:
    for result in execution.results:
        if hasattr(result, 'png') and result.png:
            display(Image(data=base64.b64decode(result.png)))
```

---

## Full Stack Agent Tools

For web development agents, provide these tools:

```python
full_stack_tools = {
    "list_directory": lambda path: sbx.files.list(path),
    "read_file": lambda path: sbx.files.read(path),
    "write_file": lambda path, content: sbx.files.write(path, content),
    "search_file_content": search_in_sandbox,  # custom impl
    "replace_in_file": replace_in_sandbox,     # custom impl
    "glob": glob_in_sandbox,                   # custom impl
}
```

---

## Best Practices

### 1. Set Appropriate Timeouts
```python
# Short task
sbx = Sandbox.create(timeout=60)  # 1 minute

# Development session
sbx = Sandbox.create(timeout=60 * 60)  # 1 hour

# Long-running service
sbx = Sandbox.create(timeout=60 * 60 * 24)  # 24 hours
```

### 2. Use Metadata for Organization
```python
sbx = Sandbox.create(metadata={
    "project": "project-name",
    "task": "data-analysis",
    "session": "abc123"
})
```

### 3. Clean Up Sandboxes
```python
# Kill sandbox when done
sbx.kill()

# Or set auto-timeout
sbx = Sandbox.create(timeout=300)  # Auto-kill after 5 min
```

### 4. Handle Errors
```python
execution = sbx.run_code(code)
if execution.error:
    return {"error": str(execution.error)}
return {"results": execution.results}
```

---

## Common Patterns

### Data Analysis Sandbox
```python
sbx = Sandbox.create()

# Upload data file
with open("local_data.csv", "r") as f:
    content = f.read()
sbx.files.write("data.csv", content)

# Analyze in sandbox
execution = sbx.run_code("""
import pandas as pd
df = pd.read_csv('data.csv')
print(df.describe())
""")
```

### Web App Sandbox
```python
sbx = Sandbox.create(template="dlai-nextjs-developer")

# Modify files
sbx.files.write("pages/index.tsx", new_page_content)

# Server already running on template
host = sbx.get_host(3000)
```

### Testing Sandbox
```python
sbx = Sandbox.create()

# Write test file
sbx.files.write("test_code.py", test_content)

# Run tests
execution = sbx.run_code("""
import subprocess
result = subprocess.run(['python', '-m', 'pytest', 'test_code.py', '-v'],
                       capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
""")
```

---

## Environment Variables

```bash
# Required
E2B_API_KEY=your_api_key

# Optional - custom domain
E2B_DOMAIN=custom.e2b.dev
```

---

## TypeScript SDK

```typescript
import { Sandbox } from '@e2b/code-interpreter';

const sbx = await Sandbox.create({ timeout: 3600 });

const execution = await sbx.runCode('print("Hello!")');
console.log(execution.results);

await sbx.files.write('/home/user/test.txt', 'content');
const content = await sbx.files.read('/home/user/test.txt');

await sbx.kill();
```

---

## Links

- Documentation: https://e2b.dev/docs
- Dashboard: https://e2b.dev/dashboard
- Templates: https://e2b.dev/docs/sandbox-template
- Python SDK: https://pypi.org/project/e2b-code-interpreter/
- TypeScript SDK: https://www.npmjs.com/package/@e2b/code-interpreter

## Source

Inspired by https://e2b.dev/docs and the DeepLearning.AI course Building Coding Agents with Tool Execution.
