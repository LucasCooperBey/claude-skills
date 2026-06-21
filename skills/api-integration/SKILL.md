---
name: api-integration
description: Integrates with external APIs including REST, GraphQL, and webhooks. Covers authentication patterns, error handling, rate limiting, and type-safe clients.
---
# API Integration

Patterns for integrating with external APIs.

## Research First

Before integrating, use **package-search MCP** to ground your implementation in real source code:

```
# Find auth patterns in popular HTTP clients
package_search_hybrid("authentication headers bearer token", package="axios", registry="npm")

# See how retries are implemented
package_search_grep("retry|backoff", package="ky", registry="npm")
```

This reduces hallucinations and ensures you're using current API patterns.

## REST API Client

### Basic Fetch with Types

```typescript
interface ApiResponse<T> {
  data: T;
  error?: string;
}

async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const baseUrl = process.env.API_BASE_URL;

  try {
    const response = await fetch(`${baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.API_KEY}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      return { data: null as T, error };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    return { data: null as T, error: String(error) };
  }
}
```

### Usage

```typescript
interface User {
  id: string;
  email: string;
  name: string;
}

const { data, error } = await apiClient<User>('/users/123');
if (error) {
  console.error('Failed to fetch user:', error);
} else {
  console.log('User:', data);
}
```

## Authentication Patterns

### API Key (Header)

```typescript
headers: {
  'X-API-Key': process.env.API_KEY,
}
```

### Bearer Token

```typescript
headers: {
  'Authorization': `Bearer ${token}`,
}
```

### OAuth 2.0 Client Credentials

```typescript
async function getAccessToken(): Promise<string> {
  const response = await fetch('https://auth.example.com/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: process.env.CLIENT_ID!,
      client_secret: process.env.CLIENT_SECRET!,
    }),
  });

  const { access_token } = await response.json();
  return access_token;
}
```

## Error Handling

```typescript
class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body: unknown
  ) {
    super(`API Error: ${status} ${statusText}`);
  }
}

async function fetchWithErrorHandling<T>(url: string): Promise<T> {
  const response = await fetch(url);

  if (!response.ok) {
    const body = await response.json().catch(() => response.text());
    throw new ApiError(response.status, response.statusText, body);
  }

  return response.json();
}
```

## Rate Limiting

### Simple Rate Limiter

```typescript
class RateLimiter {
  private queue: (() => Promise<void>)[] = [];
  private processing = false;
  private lastRequest = 0;

  constructor(private minInterval: number) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        const now = Date.now();
        const wait = Math.max(0, this.minInterval - (now - this.lastRequest));
        await new Promise(r => setTimeout(r, wait));
        this.lastRequest = Date.now();
        try {
          resolve(await fn());
        } catch (e) {
          reject(e);
        }
      });
      this.process();
    });
  }

  private async process() {
    if (this.processing) return;
    this.processing = true;
    while (this.queue.length > 0) {
      const fn = this.queue.shift()!;
      await fn();
    }
    this.processing = false;
  }
}

// Usage: max 2 requests per second
const limiter = new RateLimiter(500);
const data = await limiter.execute(() => fetch('/api/data'));
```

## Retry with Exponential Backoff

```typescript
async function fetchWithRetry<T>(
  url: string,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url);
      if (response.ok) return response.json();

      // Don't retry client errors
      if (response.status >= 400 && response.status < 500) {
        throw new Error(`Client error: ${response.status}`);
      }
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }

    // Exponential backoff with jitter
    const delay = baseDelay * Math.pow(2, i) + Math.random() * 1000;
    await new Promise(r => setTimeout(r, delay));
  }

  throw new Error('Max retries exceeded');
}
```

## Webhook Handling

```typescript
import { createHmac } from 'crypto';

function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const expected = createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return signature === `sha256=${expected}`;
}

// Express handler
app.post('/webhook', express.raw({ type: '*/*' }), (req, res) => {
  const signature = req.headers['x-signature'] as string;
  const payload = req.body.toString();

  if (!verifyWebhookSignature(payload, signature, process.env.WEBHOOK_SECRET!)) {
    return res.status(401).send('Invalid signature');
  }

  const event = JSON.parse(payload);
  // Process event...

  res.status(200).send('OK');
});
```

## GraphQL Client

```typescript
async function graphqlClient<T>(
  query: string,
  variables?: Record<string, unknown>
): Promise<T> {
  const response = await fetch(process.env.GRAPHQL_ENDPOINT!, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.API_KEY}`,
    },
    body: JSON.stringify({ query, variables }),
  });

  const { data, errors } = await response.json();

  if (errors) {
    throw new Error(errors.map((e: { message: string }) => e.message).join(', '));
  }

  return data;
}
```
