# 🌐 HTTP Status Codes: The Web's Diagnostic Language

**Author:** Eng. Ali (Baghi Channel)
**Field:** Software Engineering & Web Architecture
**Date:** April 2026

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Quick Reference Table](#2-quick-reference-table)
3. [1xx — Informational](#3-1xx--informational)
4. [2xx — Success](#4-2xx--success)
5. [3xx — Redirection](#5-3xx--redirection)
6. [4xx — Client Errors](#6-4xx--client-errors)
7. [5xx — Server Errors](#7-5xx--server-errors)
8. [Summary Cheat Sheet](#8-summary-cheat-sheet)

---

## 1. Overview

HTTP status codes are the primary way a server communicates the outcome of a client's request. Understanding these codes — especially the error ranges (**4xx** and **5xx**) — is a fundamental skill for debugging and building resilient backend architectures.

> **Rule of Thumb:** The first digit of the status code defines the category of response.

---

## 2. Quick Reference Table

| Range | Category | Meaning |
|-------|----------|---------|
| **1xx** | 🔵 Informational | Request received, process continuing |
| **2xx** | 🟢 Success | Action successfully received and accepted |
| **3xx** | 🟡 Redirection | Further action needed to complete request |
| **4xx** | 🔴 Client Error | The request contains bad syntax or cannot be fulfilled |
| **5xx** | 🟣 Server Error | The server failed to fulfill an apparently valid request |

---

## 3. 1xx — Informational

| Code | Name | Description |
|------|------|-------------|
| `100` | Continue | Server received headers, client should proceed |
| `101` | Switching Protocols | Server agrees to switch to requested protocol (e.g., WebSocket) |
| `102` | Processing (WebDAV) | Server has received and is processing the request |
| `103` | Early Hints | Used to preload resources while server prepares a response |

---

## 4. 2xx — Success

| Code | Name | Description |
|------|------|-------------|
| `200` | OK | Standard successful response |
| `201` | Created | Resource successfully created (e.g., POST request) |
| `202` | Accepted | Request accepted but not yet completed (async jobs) |
| `204` | No Content | Success but no body returned (e.g., DELETE) |
| `206` | Partial Content | Response is partial (used with range requests) |

---

## 5. 3xx — Redirection

| Code | Name | Description |
|------|------|-------------|
| `301` | Moved Permanently | Resource has been permanently moved to a new URL |
| `302` | Found | Temporary redirect |
| `304` | Not Modified | Cached version is still valid, no data transferred |
| `307` | Temporary Redirect | Temporary redirect, method must not change |
| `308` | Permanent Redirect | Permanent redirect, method must not change |

---

## 6. 4xx — Client Errors

These errors indicate that the problem lies with the **sender** (the client).

---

### 🔴 400 — Bad Request

The server cannot process the request due to a client error (e.g., malformed syntax, invalid JSON).

**Common Causes:**
- Malformed JSON body
- Missing required fields
- Invalid query parameters

```python
import requests

# Sending invalid JSON body
response = requests.post(
    "https://api.example.com/data",
    data="{'missing_bracket': "  # ← broken JSON
)
print(response.status_code)  # => 400
```

---

### 🔴 401 — Unauthorized *(means: Unauthenticated)*

> **Key Concept:** Although called "Unauthorized", this code technically means **"Unauthenticated"** — the server does not know **who you are**.

#### 🛡️ Authentication vs. Authorization

| Term | Code | Question | Meaning |
|------|------|----------|---------|
| **Authentication** | 401 | "Who are you?" | Verify your identity first |
| **Authorization** | 403 | "What can you do?" | Identity known, but access denied |

#### ✈️ Real-World Analogy: The Airport

```
You → Try to enter the departure gates
❌ Security stops you (401) → "Show your Passport / ID first!"
✅ You show your ID (Authentication)
→ 401 Error is resolved
```

#### 💻 Technical Example

**Request (no token):**
```http
GET /admin/dashboard HTTP/1.1
Host: example.com
```

**Response:**
```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="Access to admin panel"
Content-Type: application/json

{
  "error": "Authentication Required",
  "message": "You must be logged in to access this page."
}
```

**Request (with token):**
```http
GET /admin/dashboard HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 🔴 402 — Payment Required

Originally intended for digital payment systems. Rarely used and lacks a standard implementation. Some APIs use it for exceeded subscription limits.

---

### 🔴 403 — Forbidden

The client is **authenticated** but does **not have permission** to access the resource. Unlike 401, the server **knows who you are**.

```
You → Show your Passport (authenticated ✅)
❌ Guard says: "You're not on the VIP list" (403)
→ Identity confirmed, but access is denied
```

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "error": "Forbidden",
  "message": "You do not have permission to access this resource."
}
```

---

### 🔴 404 — Not Found

The server cannot find the requested resource. The URL or endpoint simply does not exist.

**Common Uses:**
- In browsers: URL not recognized
- In APIs: Resource or record does not exist
- Sometimes used instead of `403` to hide resource existence

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "Not Found",
  "message": "The resource you requested does not exist."
}
```

---

### 🔴 405 — Method Not Allowed

The HTTP method is recognized but **not allowed** for the target resource.

**Example:** Sending `DELETE` to a read-only endpoint.

```http
DELETE /articles HTTP/1.1   ← Not allowed (read-only)

Response:
HTTP/1.1 405 Method Not Allowed
Allow: GET, POST
```

---

### 🔴 406 — Not Acceptable

The server cannot produce a response matching the client's `Accept` headers (e.g., client asks for XML but server only returns JSON).

---

### 🔴 407 — Proxy Authentication Required

Similar to `401`, but authentication must be performed through a **proxy server** before reaching the actual server.

---

### 🔴 408 — Request Timeout

The server timed out waiting for the client to send the full request. Often used to close idle connections.

---

### 🔴 409 — Conflict

The request conflicts with the current state of the server.

**Common in:**
- Duplicate data submissions (e.g., unique email already exists)
- Version control merge conflicts

```http
HTTP/1.1 409 Conflict
{
  "error": "Conflict",
  "message": "A user with this email already exists."
}
```

---

### 🔴 410 — Gone

The resource has been **permanently removed** and will never be available again. Clients should remove cached references. Different from `404` — this is intentional and permanent.

---

### 🔴 411 — Length Required

The server requires the `Content-Length` header in the request, but it was not provided.

---

### 🔴 412 — Precondition Failed

The server does not meet one or more conditions specified in the request headers (e.g., `If-Match`, `If-Unmodified-Since`). Used for optimistic concurrency control.

---

### 🔴 413 — Content Too Large

The request body exceeds the server's size limits. The server may close the connection or return a `Retry-After` header.

**Example:** Uploading a file larger than the allowed limit.

---

### 🔴 414 — URI Too Long

The requested URL exceeds the server's maximum allowed length. Usually caused by extremely long query strings.

---

### 🔴 415 — Unsupported Media Type

The format of the request data is not supported by the server.

**Example:** Sending `application/xml` when server only accepts `application/json`.

```http
HTTP/1.1 415 Unsupported Media Type
{
  "error": "Unsupported Media Type",
  "message": "Content-Type must be application/json."
}
```

---

### 🔴 416 — Range Not Satisfiable

The client requested a specific byte range that is outside the bounds of the target resource.

---

### 🔴 417 — Expectation Failed

The server cannot meet the requirements of the `Expect` request header field.

---

### 🔴 418 — I'm a Teapot ☕

A humorous status code from April Fools' RFC 2324 (1998). The server refuses to brew coffee because it is, permanently, a teapot. Occasionally used by developers to reject requests they don't want to handle.

---

### 🔴 421 — Misdirected Request

The request was directed at a server that is not able to produce a response. May occur in HTTP/2 connection reuse situations.

---

### 🔴 422 — Unprocessable Content *(WebDAV)*

The request is **well-formed** (valid syntax) but contains **semantic errors** — the server understands the request but cannot process the instructions inside it.

**Example:** Sending valid JSON with logically invalid values.

```json
POST /users
{
  "age": -5,         ← valid JSON, invalid logic
  "email": "not-an-email"
}
→ 422 Unprocessable Content
```

---

### 🔴 423 — Locked *(WebDAV)*

The resource being accessed is locked and cannot be modified.

---

### 🔴 424 — Failed Dependency *(WebDAV)*

The request failed because a previous request it depended on also failed.

---

### 🔴 425 — Too Early

The server refuses to process a request that might be replayed (related to TLS early data).

---

### 🔴 426 — Upgrade Required

The client must switch to a different protocol (e.g., from HTTP/1.1 to HTTP/2 or WebSocket). The server specifies the required protocol in the `Upgrade` header.

---

### 🔴 428 — Precondition Required

The server requires the request to be **conditional** to prevent the "lost update" problem (race conditions on shared resources).

---

### 🔴 429 — Too Many Requests

The client has sent **too many requests** in a given period — rate limiting triggered.

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Content-Type: application/json

{
  "error": "Rate Limit Exceeded",
  "message": "You have exceeded the request limit. Try again in 60 seconds."
}
```

---

### 🔴 431 — Request Header Fields Too Large

One or more request header fields are too large for the server to process.

---

### 🔴 451 — Unavailable For Legal Reasons

The requested resource is unavailable due to **legal restrictions** such as government censorship or a court order. Named after Ray Bradbury's *Fahrenheit 451*.

---

## 7. 5xx — Server Errors

These errors indicate that the **server failed** to fulfill a valid request. The client did everything right — the problem is on the server side.

---

### 🟣 500 — Internal Server Error

A generic catch-all error. The server encountered an unexpected condition that prevented it from fulfilling the request.

**Common Causes:**
- Unhandled exceptions in code
- Database connection failures
- Null pointer errors / crashes

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "Internal Server Error",
  "message": "Something went wrong on our end. Please try again later."
}
```

```python
# Example: unhandled exception causes 500
@app.route("/divide")
def divide():
    result = 10 / 0   # ← ZeroDivisionError → 500 Internal Server Error
    return str(result)
```

---

### 🟣 501 — Not Implemented

The server does not support the **HTTP method** used in the request. Different from `405` — here, the server doesn't implement the method at all, not just for this resource.

```http
PATCH /resource HTTP/1.1
→ 501 Not Implemented (if server doesn't support PATCH anywhere)
```

---

### 🟣 502 — Bad Gateway

The server was acting as a **gateway or proxy** and received an invalid response from an upstream server.

```
Client → Load Balancer / Nginx → Backend App Server
                                     ↑ App Server crashes or returns garbage
                                  → Nginx returns 502 to Client
```

**Common Causes:**
- Backend service crashed
- Upstream server returned an invalid response
- Network issues between services

---

### 🟣 503 — Service Unavailable

The server is **temporarily unable** to handle the request — usually due to being overloaded or under maintenance.

```http
HTTP/1.1 503 Service Unavailable
Retry-After: 120
Content-Type: application/json

{
  "error": "Service Unavailable",
  "message": "Server is under maintenance. Back online in 2 minutes."
}
```

**Common Causes:**
- Server is overwhelmed with traffic
- Scheduled maintenance window
- Resource exhaustion (memory, CPU, DB connections)

---

### 🟣 504 — Gateway Timeout

The server, acting as a **gateway or proxy**, did not receive a timely response from an upstream server.

```
Client → Nginx → Backend (takes too long to respond)
                     ↑ timeout exceeded (e.g., 30s)
         Nginx → Returns 504 to Client
```

**Difference: 502 vs 504**

| Code | Meaning |
|------|---------|
| `502` | Upstream returned a **bad/invalid** response |
| `504` | Upstream **didn't respond in time** (timeout) |

---

### 🟣 505 — HTTP Version Not Supported

The server does not support the HTTP protocol version used in the request.

---

### 🟣 507 — Insufficient Storage *(WebDAV)*

The server cannot store the representation needed to complete the request — storage quota exceeded.

---

### 🟣 508 — Loop Detected *(WebDAV)*

The server detected an **infinite loop** while processing the request (e.g., circular redirects in a WebDAV operation).

---

### 🟣 510 — Not Extended

Further extensions to the request are required for the server to fulfill it.

---

### 🟣 511 — Network Authentication Required

The client must **authenticate to gain network access** — typically used by captive portals (e.g., hotel/airport Wi-Fi login pages).

---

## 8. Summary Cheat Sheet

### 4xx — Client Errors (Your Fault)

| Code | Name | Quick Meaning |
|------|------|---------------|
| `400` | Bad Request | Malformed syntax or invalid data |
| `401` | Unauthorized | Who are you? Login first |
| `402` | Payment Required | Pay to access |
| `403` | Forbidden | I know you, but you can't enter |
| `404` | Not Found | Resource doesn't exist |
| `405` | Method Not Allowed | Wrong HTTP method |
| `406` | Not Acceptable | Wrong response format requested |
| `408` | Request Timeout | Client took too long |
| `409` | Conflict | Duplicate or conflicting data |
| `410` | Gone | Permanently deleted |
| `413` | Content Too Large | File/body too big |
| `415` | Unsupported Media Type | Wrong content type |
| `418` | I'm a Teapot | Easter egg ☕ |
| `422` | Unprocessable Content | Valid format, invalid logic |
| `429` | Too Many Requests | Slow down — rate limited |
| `451` | Unavailable For Legal Reasons | Legally blocked |

### 5xx — Server Errors (Server's Fault)

| Code | Name | Quick Meaning |
|------|------|---------------|
| `500` | Internal Server Error | Generic server crash |
| `501` | Not Implemented | Server doesn't support this method |
| `502` | Bad Gateway | Upstream returned invalid response |
| `503` | Service Unavailable | Server overloaded or in maintenance |
| `504` | Gateway Timeout | Upstream took too long |
| `505` | HTTP Version Not Supported | Unsupported HTTP version |
| `507` | Insufficient Storage | Server ran out of disk space |
| `511` | Network Auth Required | Wi-Fi login required |

---

> 💡 **Pro Tip for Debugging:**
> - Got a **4xx**? Check your request — headers, body, URL, method, authentication.
> - Got a **5xx**? Check the server — logs, database, memory, upstream services.

---

*Document prepared by **Eng. Ali** — Baghi Channel | April 2026*