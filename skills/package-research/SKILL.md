---
name: package-research
description: Researches packages, dependencies, and APIs before integration. Leverages package-search MCP to ground responses in real source code.
---
# Package Research Workflow

Ground your package research in real source code using the Package Search MCP.

## When to Use This Skill

- Evaluating packages before adding as dependencies
- Finding correct API usage patterns
- Understanding package internals
- Comparing packages for decision-making
- Validating that a package supports needed features

## Available Tools

### 1. Semantic Search (Discovery)

```
package_search_hybrid(
  query="how to validate schemas",
  package="zod",
  registry="npm"
)
```

Best for: General questions, exploring functionality, "how do I...?"

### 2. Exact Match (Precision)

```
package_search_grep(
  pattern="export.*function",
  package="drizzle-orm",
  registry="npm"
)
```

Best for: Finding specific patterns, function signatures, imports

### 3. Read Source (Deep Dive)

```
package_search_read_file(
  file_path="src/index.ts",
  package="hono",
  registry="npm"
)
```

Best for: Understanding implementation, reading exports, studying patterns

## Supported Registries

| Registry | Languages |
|----------|-----------|
| `npm` | JavaScript, TypeScript |
| `pypi` | Python |
| `go` | Golang |
| `crates.io` | Rust |
| `rubygems` | Ruby |
| `terraform` | Infrastructure as Code |

## Research Workflow

### Phase 1: Discovery
```
# What does this package offer?
package_search_hybrid("main features exports", package="<name>", registry="<reg>")
```

### Phase 2: API Patterns
```
# How do I use the main API?
package_search_grep("export.*class|export.*function", package="<name>", registry="<reg>")
```

### Phase 3: Implementation Details
```
# How does this specific feature work?
package_search_read_file(file_path="src/core.ts", package="<name>", registry="<reg>")
```

## Example Research Sessions

### Evaluating a New ORM

```
# 1. What query patterns does it support?
package_search_hybrid("query builder select where join", package="kysely", registry="npm")

# 2. How does it handle migrations?
package_search_grep("migration|migrate", package="kysely", registry="npm")

# 3. Read the migration implementation
package_search_read_file(file_path="src/migration/migrator.ts", package="kysely", registry="npm")
```

### Finding Authentication Patterns

```
# 1. How does this auth library handle JWT?
package_search_hybrid("jwt token verify decode", package="jose", registry="npm")

# 2. Find the exact function signatures
package_search_grep("export.*verify|export.*sign", package="jose", registry="npm")
```

### Python Package Research

```
# 1. How does requests handle retries?
package_search_hybrid("retry backoff session", package="requests", registry="pypi")

# 2. Find retry adapter implementation
package_search_grep("class.*Retry|def.*retry", package="urllib3", registry="pypi")
```

## Why Use This Over Web Search?

- **Source of truth**: Real source code, not outdated blog posts
- **No hallucinations**: Grounded in actual implementations
- **Version-specific**: See how the package actually works
- **Deep dive**: Access internal implementation details
- **Cross-language**: Same workflow for all supported registries

## Integration with Other Skills

- **api-integration**: Research package patterns before implementing clients
- **mcp-builder**: Study MCP SDK internals before building servers
- **test-driven-development**: Find test patterns in packages you use
