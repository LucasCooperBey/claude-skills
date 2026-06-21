# Tool Implementations for Full Stack Agent

Complete Python implementations and JSON schemas for all sandbox tools.

## 1. List Directory
```python
list_directory_schema = {
    "type": "function",
    "name": "list_directory",
    "description": "List files and directories in a path.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to list",
            }
        },
        "required": ["path"],
        "additionalProperties": False,
    },
}

def list_directory(path: str, sbx) -> dict:
    """List directory contents."""
    try:
        files = sbx.files.list(path)
        return {
            "files": [f.name for f in files if f.is_file],
            "directories": [f.name for f in files if f.is_dir]
        }
    except Exception as e:
        return {"error": str(e)}
```

## 2. Read File
```python
read_file_schema = {
    "type": "function",
    "name": "read_file",
    "description": "Read content from a file.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read",
            }
        },
        "required": ["file_path"],
        "additionalProperties": False,
    },
}

def read_file(file_path: str, sbx) -> dict:
    """Read file content."""
    try:
        content = sbx.files.read(file_path)
        return {"content": content, "size": len(content)}
    except Exception as e:
        return {"error": str(e)}
```

## 3. Write File
```python
write_file_schema = {
    "type": "function",
    "name": "write_file",
    "description": "Write content to a file, creating directories if needed.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path where file will be written",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file",
            }
        },
        "required": ["file_path", "content"],
        "additionalProperties": False,
    },
}

def write_file(file_path: str, content: str, sbx) -> dict:
    """Write content to file."""
    try:
        sbx.files.write(file_path, content)
        return {"message": f"Written to {file_path}", "size": len(content)}
    except Exception as e:
        return {"error": str(e)}
```

## 4. Search File Content
```python
search_file_content_schema = {
    "type": "function",
    "name": "search_file_content",
    "description": "Search for text patterns across files.",
    "parameters": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Text pattern to search for",
            },
            "path": {
                "type": "string",
                "description": "Directory to search in",
            },
            "limit": {
                "type": "number",
                "description": "Maximum results to return",
            }
        },
        "required": ["pattern"],
        "additionalProperties": False,
    },
}

def search_file_content(pattern: str, path: str = ".", limit: int = 20, sbx) -> dict:
    """Search for pattern in files."""
    code = f"""
import os
import re

results = []
pattern = re.compile(r'{pattern}', re.IGNORECASE)
search_path = '{path}'

for root, dirs, files in os.walk(search_path):
    # Skip node_modules and hidden dirs
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']

    for file in files:
        if file.endswith(('.ts', '.tsx', '.js', '.jsx', '.json', '.css', '.html', '.md')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    for i, line in enumerate(f, 1):
                        if pattern.search(line):
                            results.append({{
                                'file': filepath,
                                'line': i,
                                'content': line.strip()[:100]
                            }})
                            if len(results) >= {limit}:
                                break
            except:
                pass
        if len(results) >= {limit}:
            break
    if len(results) >= {limit}:
        break

print(results)
"""
    execution = sbx.run_code(code)
    return {"results": execution.results}
```

## 5. Replace In File
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
                "description": "Text to find",
            },
            "new_text": {
                "type": "string",
                "description": "Replacement text",
            }
        },
        "required": ["file_path", "old_text", "new_text"],
        "additionalProperties": False,
    },
}

def replace_in_file(file_path: str, old_text: str, new_text: str, sbx) -> dict:
    """Replace text in file."""
    try:
        content = sbx.files.read(file_path)
        if old_text not in content:
            return {"error": f"Text not found in {file_path}"}
        new_content = content.replace(old_text, new_text)
        sbx.files.write(file_path, new_content)
        count = content.count(old_text)
        return {"message": f"Replaced {count} occurrence(s)", "file": file_path}
    except Exception as e:
        return {"error": str(e)}
```

## 6. Glob (File Pattern Search)
```python
glob_schema = {
    "type": "function",
    "name": "glob",
    "description": "Find files matching a glob pattern.",
    "parameters": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob pattern like '**/*.tsx' or 'src/**/*.js'",
            }
        },
        "required": ["pattern"],
        "additionalProperties": False,
    },
}

def glob_files(pattern: str, sbx) -> dict:
    """Find files matching glob pattern."""
    code = f"""
import glob
files = glob.glob('{pattern}', recursive=True)
# Filter out node_modules
files = [f for f in files if 'node_modules' not in f]
print(files[:50])  # Limit results
"""
    execution = sbx.run_code(code)
    return {"files": execution.results}
```

## Complete Tools Dictionary

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
    list_directory_schema,
    read_file_schema,
    write_file_schema,
    search_file_content_schema,
    replace_in_file_schema,
    glob_schema,
]
```
