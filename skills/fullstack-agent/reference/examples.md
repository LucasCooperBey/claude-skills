# Examples and Workflows

## Example Workflows

### Create a Landing Page
```
User: "Create a landing page for a SaaS product"

Agent will:
1. list_directory("/app") - explore structure
2. read_file("/app/page.tsx") - see existing home
3. write_file("/app/page.tsx", new_content) - create landing
4. read_file("/app/globals.css") - check styles
5. write_file("/components/Hero.tsx") - create hero section
6. write_file("/components/Features.tsx") - create features
7. write_file("/components/CTA.tsx") - create call-to-action
```

### Add Authentication
```
User: "Add a login page with form"

Agent will:
1. list_directory("/app") - explore
2. write_file("/app/login/page.tsx") - create login page
3. write_file("/components/LoginForm.tsx") - create form component
4. read_file("/app/layout.tsx") - check layout
5. Maybe update layout with auth context
```

### Modify Existing Feature
```
User: "Change the header color to blue"

Agent will:
1. search_file_content("header", limit=10) - find header
2. read_file the header file
3. replace_in_file to change color classes
```

---

## Gradio UI with Live Preview

```python
from lib.ui import ui

demo = ui(
    coding_agent,
    messages=[],
    host=f"https://{sbx.get_host(3000)}",  # Live preview URL
    client=client,
    sbx=sbx,
    max_steps=100,
    system=SYSTEM_PROMPT_WEB_DEV,
    tools=create_tools(sbx),
    tools_schemas=tools_schemas,
    model="gpt-4o-mini",
)

# UI shows:
# - Chat interface for prompts
# - Live preview iframe of the app
# - Token usage statistics
# - Tool execution logs

demo.launch(share=True, height=800)
```

---

## Tips for Better Results

1. **Set Higher max_steps**: Web dev needs more iterations (50-100)
2. **Use Templates**: Pre-configured sandboxes save time
3. **Provide Context**: Tell the agent about existing patterns
4. **Incremental Requests**: Build features step by step
5. **Review Changes**: Check modified files before next prompt
