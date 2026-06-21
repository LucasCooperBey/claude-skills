---
name: webapp-testing
description: Provides Playwright patterns and best practices for web application testing. Covers DOM inspection, screenshot capture, form interaction, and API mocking. Works with the Playwright plugin for browser automation.
---
# Web Application Testing

Test local web applications using browser automation.

## Tool Selection

| Use Case | Tool | Why |
|----------|------|-----|
| AI agent browser interaction | **agent-browser** | AI-optimized refs, low token cost |
| Automated test suites (CI/CD) | Playwright | Rich assertions, parallelization |
| PDF generation from HTML | Puppeteer | Specialized PDF APIs |
| Visual regression testing | Playwright | Screenshot comparison |

**Default: Use `agent-browser` for interactive testing, Playwright for test suites.**

## Decision Tree

1. **Is this AI-driven exploration or automated test suite?**
   - AI exploration: Use `agent-browser` (refs system, AI-optimized)
   - Automated tests: Use Playwright (assertions, CI/CD)

2. **Is target static HTML or dynamic webapp?**
   - Static: Direct page load and inspect
   - Dynamic: Use `with_server.py` helper for server lifecycle

3. **Do you need visual or programmatic testing?**
   - Visual: Screenshots and visual comparison
   - Programmatic: DOM queries and assertions

---

## Agent-Browser (AI Agent Testing)

Install globally: `bun add -g agent-browser`

### Quick Start

```bash
# Navigate and get AI-optimized snapshot
agent-browser navigate "http://localhost:3000"
agent-browser snapshot

# Interact using refs from snapshot
agent-browser click @e3
agent-browser fill @e5 "test@example.com"
agent-browser snapshot  # Verify changes
```

### The Refs Advantage

After `snapshot`, each element gets a unique ref (`@e1`, `@e2`):
- **Deterministic**: No CSS selector guessing
- **Fast**: No DOM re-querying
- **AI-friendly**: LLMs parse refs reliably

### Common Patterns

```bash
# Login flow
agent-browser navigate "http://localhost:3000/login"
agent-browser snapshot
agent-browser fill @e2 "user@example.com"
agent-browser fill @e3 "password123"
agent-browser click @e4
agent-browser wait-for "Dashboard"
agent-browser snapshot

# Form submission
agent-browser navigate "http://localhost:3000/contact"
agent-browser snapshot
agent-browser fill @e1 "John Doe"
agent-browser fill @e2 "john@example.com"
agent-browser type @e3 "Hello, this is my message"
agent-browser click @e4  # Submit button
agent-browser wait-for "Thank you"
```

See `~/.claude/context/agent-browser.md` for full command reference.

---

## Playwright (Automated Test Suites)

## Setup

```bash
bun add -D playwright @playwright/test
bunx playwright install
```

## Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test('homepage loads correctly', async ({ page }) => {
  await page.goto('http://localhost:3000');

  // Wait for dynamic content
  await page.waitForLoadState('networkidle');

  // Check title
  await expect(page).toHaveTitle(/My App/);

  // Check element exists
  await expect(page.locator('h1')).toContainText('Welcome');
});
```

## Critical Practice

**Always wait for network idle on dynamic apps:**
```typescript
await page.waitForLoadState('networkidle');
```
This prevents testing incomplete page states caused by ongoing JavaScript execution.

## Element Selection

```typescript
// By text
await page.getByText('Submit').click();

// By role
await page.getByRole('button', { name: 'Submit' }).click();

// By test ID (recommended)
await page.getByTestId('submit-button').click();

// By CSS selector
await page.locator('.submit-btn').click();

// By placeholder
await page.getByPlaceholder('Enter email').fill('test@example.com');
```

## Screenshots

```typescript
// Full page
await page.screenshot({ path: 'screenshot.png', fullPage: true });

// Specific element
await page.locator('.header').screenshot({ path: 'header.png' });

// Hide elements
await page.screenshot({
  path: 'clean.png',
  mask: [page.locator('.ads')]
});
```

## Form Interaction

```typescript
// Fill form
await page.getByLabel('Email').fill('user@example.com');
await page.getByLabel('Password').fill('secret123');

// Select dropdown
await page.getByLabel('Country').selectOption('US');

// Checkbox
await page.getByLabel('Remember me').check();

// Submit
await page.getByRole('button', { name: 'Sign In' }).click();
```

## API Mocking

```typescript
await page.route('**/api/users', async (route) => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Test User' }])
  });
});
```

## Console Logging

```typescript
page.on('console', msg => {
  console.log(`Browser console [${msg.type()}]: ${msg.text()}`);
});

page.on('pageerror', err => {
  console.error('Page error:', err.message);
});
```

## Testing Dynamic Content

```typescript
// Wait for element to appear
await page.waitForSelector('.loading', { state: 'hidden' });
await page.waitForSelector('.content', { state: 'visible' });

// Wait for specific text
await page.waitForFunction(() =>
  document.body.innerText.includes('Data loaded')
);

// Wait for network request
const responsePromise = page.waitForResponse('**/api/data');
await page.click('#load-button');
const response = await responsePromise;
```

## Workflow Pattern

1. **Reconnaissance:** Capture screenshots, inspect DOM
2. **Identify:** Find selectors from rendered state
3. **Execute:** Automate using discovered selectors
4. **Verify:** Assert expected outcomes

```typescript
// Reconnaissance
await page.screenshot({ path: 'before.png' });
console.log(await page.content());

// Find and interact
const buttons = await page.locator('button').all();
for (const btn of buttons) {
  console.log(await btn.textContent());
}
```
