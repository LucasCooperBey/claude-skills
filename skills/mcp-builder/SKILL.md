---
name: mcp-builder
description: Builds MCP (Model Context Protocol) servers for API integration. Guides the full development lifecycle from research to evaluation.
---
# MCP Server Development

Build Model Context Protocol servers that enable language models to interact with external services.

## Four-Phase Approach

### Phase 1: Deep Research & Planning
- Study MCP design principles and protocol documentation
- Select tech stack (TypeScript recommended)
- Analyze target API thoroughly
- Plan tool organization

### Phase 2: Implementation
- Project setup with proper dependencies
- Core infrastructure (auth, error handling)
- Individual tools with schemas and descriptions

### Phase 3: Review & Testing
- Code quality verification
- Test with MCP Inspector
- Error handling validation

### Phase 4: Evaluation
- Create 10 complex, realistic test questions
- Verify LLMs can effectively use your server

## Project Setup (TypeScript)

```bash
mkdir my-mcp-server && cd my-mcp-server
bun init
bun add @modelcontextprotocol/sdk zod
```

```typescript
// src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server(
  { name: 'my-server', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

// Define tools
server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'my_tool',
      description: 'Does something useful',
      inputSchema: {
        type: 'object',
        properties: {
          param: { type: 'string', description: 'Input parameter' }
        },
        required: ['param']
      }
    }
  ]
}));

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'my_tool') {
    // Implement tool logic
    return { content: [{ type: 'text', text: 'Result' }] };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

## Research with Package Search MCP

Before implementing, use the **package-search** MCP to research SDK patterns:

```
# Find how the official MCP SDK structures servers
package_search_hybrid("@modelcontextprotocol/sdk server setup patterns", registry="npm")

# Look at real tool implementations
package_search_grep("setRequestHandler.*tools/call", package="@modelcontextprotocol/sdk", registry="npm")
```

This grounds your implementation in real source code rather than hallucinated patterns.

## Key Design Principles

**Tool Naming:** Consistent, action-oriented
- Good: `github_create_issue`, `slack_send_message`
- Bad: `doThing`, `handler1`

**Error Messages:** Provide specific suggestions
```typescript
throw new Error(
  `Repository not found: ${repo}. ` +
  `Check that the repository exists and you have access. ` +
  `Try: gh repo view ${repo}`
);
```

**Balance Coverage:** Combine comprehensive API endpoint coverage with specialized workflow tools.

## Input Validation with Zod

```typescript
import { z } from 'zod';

const CreateIssueSchema = z.object({
  repo: z.string().describe('Repository in owner/name format'),
  title: z.string().min(1).describe('Issue title'),
  body: z.string().optional().describe('Issue body in markdown'),
  labels: z.array(z.string()).optional().describe('Labels to apply')
});

// In tool handler
const params = CreateIssueSchema.parse(args);
```

## Testing with MCP Inspector

```bash
bun run build
npx @modelcontextprotocol/inspector dist/index.js
```

## Evaluation Questions

Each evaluation question must be:
- Independent (no dependencies on other questions)
- Read-only (doesn't modify external state)
- Complex enough to require multiple tool calls
- Realistic (matches actual use cases)
- Verifiable (single clear answer)
- Temporally stable (answer doesn't change)

Example:
> "Find all open issues in repo X labeled 'bug' and summarize their common themes"

## Claude Code Integration

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/dist/index.js"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```
