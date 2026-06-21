---
name: database-migrations
description: Modifies database schemas safely with migration strategies, rollback procedures, and zero-downtime deployments using Drizzle ORM.
---
# Database Migrations

Safe schema modifications with rollback procedures.

## Core Principles

1. **Never modify production directly** - Always use migrations
2. **Test migrations on copy first** - Catch issues early
3. **Plan for rollback** - Every migration should be reversible
4. **Zero-downtime when possible** - Expand-contract pattern

## Drizzle ORM Workflow

### Generate Migration

```bash
# After modifying schema.ts
bunx drizzle-kit generate:pg --name add_user_status
```

### Review Generated SQL

```bash
cat drizzle/migrations/XXXX_add_user_status.sql
```

### Apply Migration

```bash
bunx drizzle-kit push:pg
# Or for production:
bunx drizzle-kit migrate
```

## Safe Migration Patterns

### Adding a Column

**Safe:** Add nullable column or with default

```typescript
// schema.ts
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull(),
  status: text('status').default('active'), // Safe: has default
});
```

**Dangerous:** Adding NOT NULL without default

```sql
-- This will FAIL if table has data
ALTER TABLE users ADD COLUMN status TEXT NOT NULL;

-- Safe version:
ALTER TABLE users ADD COLUMN status TEXT;
UPDATE users SET status = 'active' WHERE status IS NULL;
ALTER TABLE users ALTER COLUMN status SET NOT NULL;
```

### Renaming a Column (Zero-Downtime)

**Phase 1: Add new column**
```sql
ALTER TABLE users ADD COLUMN new_name TEXT;
UPDATE users SET new_name = old_name;
```

**Phase 2: Code reads from both, writes to both**
```typescript
// During transition
user.displayName = user.new_name ?? user.old_name;
await db.update(users).set({
  old_name: value,
  new_name: value,
});
```

**Phase 3: Remove old column**
```sql
ALTER TABLE users DROP COLUMN old_name;
```

### Adding Foreign Key

```sql
-- Add column without constraint first
ALTER TABLE posts ADD COLUMN author_id INTEGER;

-- Backfill data
UPDATE posts SET author_id = (SELECT id FROM users WHERE email = posts.author_email);

-- Then add constraint
ALTER TABLE posts ADD CONSTRAINT fk_author
  FOREIGN KEY (author_id) REFERENCES users(id);

-- Finally remove old column
ALTER TABLE posts DROP COLUMN author_email;
```

## Rollback Procedures

### With Drizzle

```bash
# Drizzle doesn't have built-in rollback
# Keep rollback SQL files manually

# drizzle/rollbacks/XXXX_add_user_status.sql
ALTER TABLE users DROP COLUMN status;
```

### Automated Rollback Script

```typescript
import { sql } from 'drizzle-orm';

async function rollback(db: Database, migrationName: string) {
  const rollbackPath = `drizzle/rollbacks/${migrationName}.sql`;
  const rollbackSql = await Bun.file(rollbackPath).text();

  await db.execute(sql.raw(rollbackSql));
  console.log(`Rolled back: ${migrationName}`);
}
```

## Pre-Migration Checklist

- [ ] Backup database
- [ ] Review generated SQL
- [ ] Test on staging/copy
- [ ] Prepare rollback script
- [ ] Schedule during low-traffic
- [ ] Notify team

```bash
# Backup before migration
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Neon Database Specifics

### Branch for Testing

```bash
# Create test branch
neonctl branches create --name migration-test

# Get connection string
neonctl connection-string migration-test

# Test migration
DATABASE_URL=$TEST_URL bunx drizzle-kit push:pg

# If successful, apply to main
# If failed, delete branch
neonctl branches delete migration-test
```

### Point-in-Time Recovery

Neon supports instant recovery. Before risky migrations:

1. Note current timestamp
2. Run migration
3. If failed, restore to timestamp

## Large Table Migrations

For tables with millions of rows:

### Batch Updates

```typescript
async function batchUpdate(
  db: Database,
  batchSize = 1000
) {
  let updated = 0;
  let lastId = 0;

  while (true) {
    const result = await db.execute(sql`
      UPDATE users
      SET status = 'active'
      WHERE id > ${lastId}
        AND status IS NULL
      ORDER BY id
      LIMIT ${batchSize}
      RETURNING id
    `);

    if (result.rowCount === 0) break;

    lastId = result.rows[result.rows.length - 1].id;
    updated += result.rowCount;
    console.log(`Updated ${updated} rows...`);

    // Pause to reduce load
    await new Promise(r => setTimeout(r, 100));
  }

  return updated;
}
```

## Migration Testing

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'bun:test';

describe('Migration: add_user_status', () => {
  let testDb: Database;

  beforeAll(async () => {
    // Create test database
    testDb = await createTestDatabase();
    // Seed with test data
    await seedTestData(testDb);
  });

  afterAll(async () => {
    await testDb.close();
  });

  it('should add status column with default value', async () => {
    await runMigration(testDb, 'add_user_status');

    const users = await testDb.select().from(usersTable);
    expect(users[0].status).toBe('active');
  });

  it('should be reversible', async () => {
    await runMigration(testDb, 'add_user_status');
    await runRollback(testDb, 'add_user_status');

    const columns = await getTableColumns(testDb, 'users');
    expect(columns).not.toContain('status');
  });
});
```
