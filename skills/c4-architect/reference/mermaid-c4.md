# Mermaid C4 Syntax Reference

## C1 — Context Diagram

```mermaid
C4Context
  title System Context — MyApp

  Person(user, "End User", "Uses the application")
  Person(admin, "Admin", "Manages settings")

  System(myapp, "MyApp", "Core application")

  System_Ext(email, "Email Service", "SendGrid")
  System_Ext(storage, "Cloud Storage", "AWS S3")
  SystemDb_Ext(extdb, "External API", "Third-party data")

  Rel(user, myapp, "Uses", "HTTPS")
  Rel(admin, myapp, "Manages", "HTTPS")
  Rel(myapp, email, "Sends emails", "SMTP/API")
  Rel(myapp, storage, "Stores files", "S3 API")
  Rel(myapp, extdb, "Fetches data", "REST")
```

## C2 — Container Diagram

```mermaid
C4Container
  title Container Diagram — MyApp

  Person(user, "End User")

  Container_Boundary(myapp, "MyApp") {
    Container(web, "Web App", "Next.js", "Serves UI and API routes")
    ContainerDb(db, "Database", "PostgreSQL/Neon", "Stores application data")
    Container(worker, "Background Worker", "Node.js", "Processes async jobs")
    ContainerDb(cache, "Cache", "Redis", "Session and query cache")
    ContainerDb(vectors, "Vector Store", "Qdrant", "Semantic search")
    Container(storage, "File Storage", "R2/S3", "Photos, documents")
  }

  Rel(user, web, "Uses", "HTTPS")
  Rel(web, db, "Reads/writes", "SQL")
  Rel(web, cache, "Caches", "Redis protocol")
  Rel(web, vectors, "Queries", "gRPC")
  Rel(web, storage, "Uploads/downloads", "S3 API")
  Rel(worker, db, "Reads/writes", "SQL")
  Rel(web, worker, "Enqueues jobs", "Queue")
```

## C3 — Component Diagram

```mermaid
C4Component
  title Component Diagram — Web App

  Container_Boundary(web, "Web App") {
    Component(routes, "API Routes", "Next.js API", "REST endpoints")
    Component(auth, "Auth Module", "NextAuth", "Authentication & sessions")
    Component(services, "Service Layer", "TypeScript", "Business logic")
    Component(repo, "Data Access", "Drizzle ORM", "DB queries")
    Component(ai, "AI Pipeline", "Claude/OpenAI", "LLM processing")
    Component(queue, "Job Queue", "BullMQ", "Async task dispatch")
  }

  Rel(routes, auth, "Validates")
  Rel(routes, services, "Delegates to")
  Rel(services, repo, "Queries via")
  Rel(services, ai, "Calls")
  Rel(services, queue, "Enqueues")
  Rel(repo, db, "SQL", "Drizzle")
```

## Conventions

### Node types

| Function | Use for |
|----------|---------|
| `Person(id, label, desc)` | Human actors |
| `System(id, label, desc)` | Your system (C1) |
| `System_Ext(id, label, desc)` | External systems |
| `Container(id, label, tech, desc)` | Apps, services |
| `ContainerDb(id, label, tech, desc)` | Databases, stores |
| `Component(id, label, tech, desc)` | Internal modules |
| `Container_Boundary(id, label)` | Group containers |

### Relationships

```
Rel(from, to, "label")
Rel(from, to, "label", "protocol")
BiRel(a, b, "label")  # bidirectional
```

### Styling tips

- Keep descriptions under 30 chars
- Use tech field for framework/language
- Max 15 nodes per diagram — split if needed
- Group related items with `_Boundary`

### Manual annotations (preserved on refresh)

```mermaid
%% MANUAL: This relationship is planned but not yet implemented
Rel(web, ml, "Will call", "gRPC")
```

Lines starting with `%% MANUAL:` are preserved across regeneration.
Lines starting with `%% UNCERTAIN:` flag relationships the tool couldn't verify.
