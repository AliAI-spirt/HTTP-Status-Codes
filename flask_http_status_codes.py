#   ____              _     _ 
#  | __ )  __ _  __ _| |__ (_)
#  |  _ \ / _` |/ _` | '_ \| |
#  | |_) | (_| | (_| | | | | |
#  |____/ \__,_|\__, |_| |_|_|
#               |___/         
"""
=============================================================
  HTTP Status Codes — Flask Demo Server
  Author: Eng. Ali (Baghi Channel)
  Description: Flask server demonstrating all HTTP status
               codes from 1xx to 5xx with real examples.
=============================================================

Install dependencies:
    pip install flask requests

Run the server:
    python flask_http_status_codes.py

Test all endpoints:
    python flask_http_status_codes.py --test
=============================================================
"""

import sys
import time
import json
from functools import wraps
from flask import Flask, request, jsonify, redirect, Response , g
sys.stdout.reconfigure(encoding='utf-8') #type: ignore
app = Flask(__name__)

# Fake data stores
USERS = {
    1: {"id": 1, "name": "Ali",   "email": "ali@example.com"},
    2: {"id": 2, "name": "Sara",  "email": "sara@example.com"},
}
LOCKED_RESOURCES = {"/locked-file"}
RATE_LIMIT_STORE: dict[str, list] = {}   # ip → [timestamps]

# Simple token check
VALID_TOKENS = {"secret-token-123", "admin-token-456"}
ADMIN_TOKENS = {"admin-token-456"}



def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()
        
        if not token or token not in VALID_TOKENS:
            return jsonify({
                "status_code": 401,
                "error": "Unauthorized",
                "message": "You must be logged in.",
            }), 401
            
        # تخزين البيانات في كائن g (المخصص لهذا الغرض)
        g.current_token = token
        return f(*args, **kwargs)
    return wrapper

def require_admin(f):
    """Decorator: returns 403 when non-admin token is used."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()
        if token not in VALID_TOKENS:
            return jsonify({
                "status_code": 401,
                "error": "Unauthorized",
                "message": "Token missing or invalid."
            }), 401
        if token not in ADMIN_TOKENS:
            return jsonify({
                "status_code": 403,
                "error": "Forbidden",
                "message": "You are authenticated but not authorized. Admin token required.",
                "hint": f"Admin tokens: {list(ADMIN_TOKENS)}"
            }), 403
        return f(*args, **kwargs)
    return wrapper


def rate_limit(max_requests: int = 3, window_seconds: int = 60):
    """Decorator: returns 429 after max_requests within window_seconds."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr or "unknown"
            now = time.time()
            timestamps = RATE_LIMIT_STORE.get(ip, [])
            timestamps = [t for t in timestamps if now - t < window_seconds]
            if len(timestamps) >= max_requests:
                retry_after = int(window_seconds - (now - timestamps[0]))
                return jsonify({
                    "status_code": 429,
                    "error": "Too Many Requests",
                    "message": f"Rate limit: {max_requests} requests per {window_seconds}s",
                    "retry_after_seconds": retry_after,
                }), 429, {"Retry-After": str(retry_after)}
            timestamps.append(now)
            RATE_LIMIT_STORE[ip] = timestamps
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ─────────────────────────────────────────────
#  Root — Index of all routes
# ─────────────────────────────────────────────

@app.route("/")
def index():
    routes = {
        "info": "HTTP Status Codes Demo — Eng. Ali (Baghi Channel)",
        "endpoints": {
            # 1xx
            "GET /status/101":  "101 Switching Protocols",
            # 2xx
            "GET /status/200":  "200 OK",
            "POST /status/201": "201 Created",
            "GET /status/202":  "202 Accepted",
            "DELETE /status/204": "204 No Content",
            "GET /status/206":  "206 Partial Content",
            # 3xx
            "GET /status/301":  "301 Moved Permanently",
            "GET /status/302":  "302 Found (Temp Redirect)",
            "GET /status/304":  "304 Not Modified",
            "GET /status/307":  "307 Temporary Redirect",
            "GET /status/308":  "308 Permanent Redirect",
            # 4xx
            "POST /status/400": "400 Bad Request",
            "GET /status/401":  "401 Unauthorized (no token)",
            "GET /status/402":  "402 Payment Required",
            "GET /status/403":  "403 Forbidden (user token only)",
            "GET /status/404":  "404 Not Found",
            "POST /status/405": "405 Method Not Allowed",
            "GET /status/406":  "406 Not Acceptable",
            "GET /status/408":  "408 Request Timeout",
            "POST /status/409": "409 Conflict",
            "GET /status/410":  "410 Gone",
            "POST /status/411": "411 Length Required",
            "GET /status/412":  "412 Precondition Failed",
            "POST /status/413": "413 Content Too Large",
            "GET /status/414":  "414 URI Too Long",
            "POST /status/415": "415 Unsupported Media Type",
            "GET /status/416":  "416 Range Not Satisfiable",
            "GET /status/418":  "418 I'm a Teapot",
            "GET /status/422":  "422 Unprocessable Content",
            "GET /status/423":  "423 Locked",
            "GET /status/425":  "425 Too Early",
            "GET /status/426":  "426 Upgrade Required",
            "GET /status/428":  "428 Precondition Required",
            "GET /status/429":  "429 Too Many Requests (rate limited)",
            "GET /status/431":  "431 Request Header Fields Too Large",
            "GET /status/451":  "451 Unavailable For Legal Reasons",
            # 5xx
            "GET /status/500":  "500 Internal Server Error",
            "GET /status/501":  "501 Not Implemented",
            "GET /status/502":  "502 Bad Gateway",
            "GET /status/503":  "503 Service Unavailable",
            "GET /status/504":  "504 Gateway Timeout",
            "GET /status/505":  "505 HTTP Version Not Supported",
            "GET /status/507":  "507 Insufficient Storage",
            "GET /status/508":  "508 Loop Detected",
            "GET /status/511":  "511 Network Authentication Required",
        }
    }
    return jsonify(routes), 200


# ═══════════════════════════════════════════════
#  1xx — Informational
# ═══════════════════════════════════════════════

@app.route("/status/101")
def status_101():
    """
    101 Switching Protocols
    Real usage: WebSocket upgrade (handled by the HTTP layer,
    not Flask directly). We simulate the concept here.
    """
    wants_upgrade = request.headers.get("Upgrade", "")
    if wants_upgrade.lower() == "websocket":
        return jsonify({
            "status_code": 101,
            "name": "Switching Protocols",
            "message": "Server agrees to upgrade to WebSocket.",
            "note": "In a real app this is handled by the WSGI layer, not Flask."
        }), 101
    return jsonify({
        "status_code": 101,
        "name": "Switching Protocols",
        "message": "Simulated — send header 'Upgrade: websocket' to trigger this.",
    }), 200


# ═══════════════════════════════════════════════
#  2xx — Success
# ═══════════════════════════════════════════════

@app.route("/status/200")
@require_auth
def status_200():
    """200 OK — Standard successful GET with authenticated user."""
    return jsonify({
        "status_code": 200,
        "name": "OK",
        "message": "Request succeeded.",
        "data": list(USERS.values()),
    }), 200


@app.route("/status/201", methods=["POST"])
def status_201():
    """201 Created — Resource successfully created via POST."""
    body = request.get_json(silent=True) or {}
    name  = body.get("name",  "New User")
    email = body.get("email", "user@example.com")
    new_id = max(USERS.keys(), default=0) + 1
    USERS[new_id] = {"id": new_id, "name": name, "email": email}
    return jsonify({
        "status_code": 201,
        "name": "Created",
        "message": "User created successfully.",
        "data": USERS[new_id],
    }), 201, {"Location": f"/users/{new_id}"}


@app.route("/status/202")
def status_202():
    """202 Accepted — Async job accepted but not yet done."""
    return jsonify({
        "status_code": 202,
        "name": "Accepted",
        "message": "Your request has been queued for processing.",
        "job_id": "job-7f3a9c",
        "check_status_url": "/jobs/job-7f3a9c",
    }), 202


@app.route("/status/204", methods=["DELETE"])
@require_auth
def status_204():
    """204 No Content — DELETE succeeded, nothing to return."""
    user_id = request.args.get("id", type=int)
    if user_id and user_id in USERS:
        del USERS[user_id]
    # 204 must have no body
    return "", 204


@app.route("/status/206")
def status_206():
    """206 Partial Content — Range request (e.g., video streaming)."""
    full_data = list(range(1, 101))   # simulate 100 items
    range_header = request.headers.get("Range", "items=0-9")
    try:
        start, end = map(int, range_header.split("=")[1].split("-"))
    except Exception:
        start, end = 0, 9
    chunk = full_data[start: end + 1]
    return jsonify({
        "status_code": 206,
        "name": "Partial Content",
        "message": f"Returning items {start}-{end} of {len(full_data)}.",
        "data": chunk,
    }), 206, {"Content-Range": f"items {start}-{end}/{len(full_data)}"}


# ═══════════════════════════════════════════════
#  3xx — Redirection
# ═══════════════════════════════════════════════

@app.route("/status/301")
def status_301():
    """301 Moved Permanently — Resource lives at a new URL forever."""
    return redirect("/status/200", code=301)


@app.route("/status/302")
def status_302():
    """302 Found — Temporary redirect."""
    return redirect("/status/200", code=302)


@app.route("/status/304")
def status_304():
    """304 Not Modified — Client's cached version is still fresh."""
    client_etag = request.headers.get("If-None-Match", "")
    current_etag = '"v1.0-users"'
    if client_etag == current_etag:
        return "", 304   # no body on 304
    return jsonify({
        "status_code": 304,
        "name": "Not Modified",
        "message": "Send 'If-None-Match: \"v1.0-users\"' header to trigger a real 304.",
        "hint": "ETag: " + current_etag,
    }), 200, {"ETag": current_etag}


@app.route("/status/307")
def status_307():
    """307 Temporary Redirect — Method must not change."""
    return redirect("/status/200", code=307)


@app.route("/status/308")
def status_308():
    """308 Permanent Redirect — Method must not change."""
    return redirect("/status/200", code=308)


# ═══════════════════════════════════════════════
#  4xx — Client Errors
# ═══════════════════════════════════════════════

@app.route("/status/400", methods=["POST"])
def status_400():
    """
    400 Bad Request
    Triggered when request body is missing required fields
    or contains malformed JSON.
    """
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({
            "status_code": 400,
            "error": "Bad Request",
            "message": "Request body must be valid JSON.",
            "hint": 'Send: {"name": "Ali", "email": "ali@example.com"}',
        }), 400
    missing = [f for f in ("name", "email") if f not in body]
    if missing:
        return jsonify({
            "status_code": 400,
            "error": "Bad Request",
            "message": f"Missing required fields: {missing}",
        }), 400
    return jsonify({
        "status_code": 200,
        "message": "Valid request! No 400 this time.",
        "received": body,
    }), 200


@app.route("/status/401")
@require_auth
def status_401():
    """
    401 Unauthorized (Unauthenticated)
    Missing or invalid Authorization token.
    The @require_auth decorator handles this automatically.
    """
    return jsonify({
        "status_code": 200,
        "message": "You are authenticated! No 401 here.",
        "note": "Remove the Authorization header to get a 401.",
    }), 200


@app.route("/status/402")
def status_402():
    """
    402 Payment Required
    Simulates a freemium API — premium feature requires payment.
    """
    plan = request.args.get("plan", "free")
    if plan != "premium":
        return jsonify({
            "status_code": 402,
            "error": "Payment Required",
            "message": "This feature requires a premium plan.",
            "upgrade_url": "https://example.com/pricing",
            "hint": "Add ?plan=premium to bypass this demo check.",
        }), 402
    return jsonify({
        "status_code": 200,
        "message": "Welcome, premium user! Feature unlocked.",
    }), 200


@app.route("/status/403")
@require_admin
def status_403():
    """
    403 Forbidden
    User is authenticated but lacks admin privileges.
    Use: Authorization: Bearer secret-token-123 → 403
    Use: Authorization: Bearer admin-token-456 → 200
    """
    return jsonify({
        "status_code": 200,
        "message": "Welcome, admin! You have full access.",
        "admin_data": {"users_count": len(USERS), "server": "flask-demo"},
    }), 200


@app.route("/status/404")
def status_404():
    """404 Not Found — Requested user ID does not exist."""
    user_id = request.args.get("id", type=int)
    if user_id is None:
        return jsonify({
            "status_code": 404,
            "error": "Not Found",
            "message": "Pass ?id=<number> — unknown IDs return 404.",
            "existing_ids": list(USERS.keys()),
        }), 404
    user = USERS.get(user_id)
    if not user:
        return jsonify({
            "status_code": 404,
            "error": "Not Found",
            "message": f"User with id={user_id} does not exist.",
            "existing_ids": list(USERS.keys()),
        }), 404
    return jsonify({"status_code": 200, "data": user}), 200


@app.route("/status/405")
def status_405_get():
    """405 — GET is not allowed here; only POST."""
    return jsonify({
        "status_code": 405,
        "error": "Method Not Allowed",
        "message": "This endpoint only accepts POST requests.",
        "allowed_methods": ["POST"],
    }), 405, {"Allow": "POST"}


@app.route("/status/405", methods=["POST"])
def status_405_post():
    """POST is the only allowed method on this endpoint."""
    return jsonify({
        "status_code": 200,
        "message": "POST accepted! This endpoint only allows POST.",
    }), 200


@app.route("/status/406")
def status_406():
    """
    406 Not Acceptable
    Client asks for XML but server only speaks JSON.
    """
    accept = request.headers.get("Accept", "application/json")
    if "application/xml" in accept and "application/json" not in accept:
        return jsonify({
            "status_code": 406,
            "error": "Not Acceptable",
            "message": "This server only produces application/json.",
            "supported_types": ["application/json"],
            "hint": "Remove 'Accept: application/xml' header.",
        }), 406
    return jsonify({
        "status_code": 200,
        "message": "application/json accepted. Here is your data.",
        "hint": "Send 'Accept: application/xml' header to trigger 406.",
    }), 200


@app.route("/status/408")
def status_408():
    """
    408 Request Timeout
    Simulated: we immediately return 408 as if the request timed out.
    In production this is often set by the server/proxy configuration.
    """
    return jsonify({
        "status_code": 408,
        "error": "Request Timeout",
        "message": "The server timed out waiting for the request.",
        "note": "In production, Nginx/Gunicorn triggers this automatically.",
    }), 408


@app.route("/status/409", methods=["POST"])
def status_409():
    """409 Conflict — Email already exists."""
    body = request.get_json(silent=True) or {}
    email = body.get("email", "")
    existing_emails = {u["email"] for u in USERS.values()}
    if email in existing_emails:
        return jsonify({
            "status_code": 409,
            "error": "Conflict",
            "message": f"A user with email '{email}' already exists.",
        }), 409
    return jsonify({
        "status_code": 200,
        "message": "Email is available — no conflict.",
        "email_checked": email or "(none sent)",
        "hint": 'Send {"email": "ali@example.com"} to trigger 409.',
    }), 200


@app.route("/status/410")
def status_410():
    """410 Gone — Resource was permanently deleted."""
    return jsonify({
        "status_code": 410,
        "error": "Gone",
        "message": "This resource has been permanently removed.",
        "note": "Unlike 404, this will never come back. Remove your bookmarks.",
    }), 410


@app.route("/status/411", methods=["POST"])
def status_411():
    """411 Length Required — Content-Length header missing."""
    if "Content-Length" not in request.headers:
        return jsonify({
            "status_code": 411,
            "error": "Length Required",
            "message": "Content-Length header is required for this request.",
        }), 411
    return jsonify({
        "status_code": 200,
        "message": "Content-Length header found. Request accepted.",
        "content_length": request.headers["Content-Length"],
    }), 200


@app.route("/status/412")
def status_412():
    """
    412 Precondition Failed
    Client sends If-Match header; we compare with our current ETag.
    """
    current_etag = '"v2.0"'
    client_etag  = request.headers.get("If-Match", "")
    if client_etag and client_etag != current_etag:
        return jsonify({
            "status_code": 412,
            "error": "Precondition Failed",
            "message": "ETag mismatch. The resource has been modified since you last fetched it.",
            "your_etag":    client_etag,
            "current_etag": current_etag,
        }), 412
    return jsonify({
        "status_code": 200,
        "message": "Precondition passed (or no If-Match sent).",
        "current_etag": current_etag,
        "hint": "Send 'If-Match: \"wrong-etag\"' to trigger 412.",
    }), 200, {"ETag": current_etag}


@app.route("/status/413", methods=["POST"])
def status_413():
    """413 Content Too Large — Payload exceeds 1 KB limit."""
    max_size = 1024   # 1 KB
    data = request.get_data()
    if len(data) > max_size:
        return jsonify({
            "status_code": 413,
            "error": "Content Too Large",
            "message": f"Payload is {len(data)} bytes. Maximum allowed is {max_size} bytes.",
        }), 413
    return jsonify({
        "status_code": 200,
        "message": "Payload size is within limits.",
        "received_bytes": len(data),
        "max_allowed_bytes": max_size,
    }), 200


@app.route("/status/414")
def status_414():
    """414 URI Too Long — URL exceeds 100-character limit (demo)."""
    max_length = 100
    url_length = len(request.url)
    if url_length > max_length:
        return jsonify({
            "status_code": 414,
            "error": "URI Too Long",
            "message": f"Request URL is {url_length} chars. Max allowed: {max_length}.",
        }), 414
    return jsonify({
        "status_code": 200,
        "message": "URL length is acceptable.",
        "url_length": url_length,
        "max_allowed": max_length,
        "hint": "Add a very long query string to trigger 414.",
    }), 200


@app.route("/status/415", methods=["POST"])
def status_415():
    """415 Unsupported Media Type — Only application/json is accepted."""
    content_type = request.content_type or ""
    if "application/json" not in content_type:
        return jsonify({
            "status_code": 415,
            "error": "Unsupported Media Type",
            "message": f"Content-Type '{content_type}' is not supported.",
            "supported_types": ["application/json"],
        }), 415
    return jsonify({
        "status_code": 200,
        "message": "Content-Type is valid.",
        "received_content_type": content_type,
    }), 200


@app.route("/status/416")
def status_416():
    """416 Range Not Satisfiable — Requested byte range is out of bounds."""
    total_size = 500   # simulate 500-byte resource
    range_header = request.headers.get("Range", "")
    if range_header:
        try:
            start, end = map(int, range_header.replace("bytes=", "").split("-"))
            if start > total_size or end > total_size:
                return jsonify({
                    "status_code": 416,
                    "error": "Range Not Satisfiable",
                    "message": f"Requested range {start}-{end} exceeds resource size {total_size}.",
                }), 416, {"Content-Range": f"bytes */{total_size}"}
        except ValueError:
            pass
    return jsonify({
        "status_code": 200,
        "message": "Range is satisfiable (or no Range header sent).",
        "total_size_bytes": total_size,
        "hint": "Send 'Range: bytes=600-900' to trigger 416.",
    }), 200


@app.route("/status/418")
def status_418():
    """418 I'm a Teapot — RFC 2324 April Fools joke."""
    if request.args.get("brew") == "coffee":
        return jsonify({
            "status_code": 418,
            "error": "I'm a Teapot",
            "message": "I refuse to brew coffee. I am, and always will be, a teapot. ☕",
            "rfc": "https://datatracker.ietf.org/doc/html/rfc2324",
        }), 418
    return jsonify({
        "status_code": 200,
        "message": "Brewing tea... 🍵",
        "hint": "Add ?brew=coffee to trigger 418.",
    }), 200


@app.route("/status/422")
def status_422():
    """
    422 Unprocessable Content
    JSON is valid but semantically wrong (e.g., negative age).
    """
    body = request.get_json(silent=True) or {}
    age   = body.get("age",   25)
    email = body.get("email", "valid@example.com")
    errors = []
    if isinstance(age, int) and age < 0:
        errors.append("'age' must be a positive integer.")
    if "@" not in str(email):
        errors.append("'email' is not a valid email address.")
    if errors:
        return jsonify({
            "status_code": 422,
            "error": "Unprocessable Content",
            "message": "Request is well-formed but contains semantic errors.",
            "validation_errors": errors,
        }), 422
    return jsonify({
        "status_code": 200,
        "message": "Data is valid.",
        "data": {"age": age, "email": email},
        "hint": "Send JSON body with age=-1 or bad email to trigger 422.",
    }), 200


@app.route("/status/423")
def status_423():
    """423 Locked — Resource is currently locked for editing."""
    resource = request.args.get("resource", "/locked-file")
    if resource in LOCKED_RESOURCES:
        return jsonify({
            "status_code": 423,
            "error": "Locked",
            "message": f"Resource '{resource}' is locked by another user.",
            "hint": "Try ?resource=/other-file for an unlocked resource.",
        }), 423
    return jsonify({
        "status_code": 200,
        "message": f"Resource '{resource}' is available.",
        "hint": "Try ?resource=/locked-file to trigger 423.",
    }), 200


@app.route("/status/425")
def status_425():
    """425 Too Early — Request might be replayed (TLS early data context)."""
    return jsonify({
        "status_code": 425,
        "error": "Too Early",
        "message": "The server is unwilling to process this request as it may be replayed.",
        "note": "This is typically triggered by TLS 0-RTT early data.",
    }), 425


@app.route("/status/426")
def status_426():
    """426 Upgrade Required — Client must switch to a newer protocol."""
    upgrade = request.headers.get("Upgrade", "")
    if "HTTP/2" in upgrade or "websocket" in upgrade.lower():
        return jsonify({
            "status_code": 200,
            "message": "Upgraded protocol accepted.",
        }), 200
    return jsonify({
        "status_code": 426,
        "error": "Upgrade Required",
        "message": "This endpoint requires HTTP/2 or WebSocket.",
    }), 426, {"Upgrade": "HTTP/2, websocket", "Connection": "Upgrade"}


@app.route("/status/428")
def status_428():
    """428 Precondition Required — Request must be conditional."""
    has_condition = any(h in request.headers for h in ("If-Match", "If-None-Match", "If-Unmodified-Since"))
    if not has_condition:
        return jsonify({
            "status_code": 428,
            "error": "Precondition Required",
            "message": "This request must be conditional to prevent conflicts.",
            "hint": "Add one of: If-Match, If-None-Match, or If-Unmodified-Since header.",
        }), 428
    return jsonify({
        "status_code": 200,
        "message": "Conditional header found. Request accepted.",
        "condition_header": {k: v for k, v in request.headers if k in ("If-Match", "If-None-Match", "If-Unmodified-Since")},
    }), 200


@app.route("/status/429")
@rate_limit(max_requests=3, window_seconds=60)
def status_429():
    """429 Too Many Requests — Hit this endpoint 4+ times to trigger the limit."""
    ip = request.remote_addr
    ip_list = RATE_LIMIT_STORE[ip] if ip in RATE_LIMIT_STORE else []
    count = len(ip_list)
    return jsonify({
        "status_code": 200,
        "message": f"Request accepted. You have used {count}/3 of your rate limit.",
        "hint": "Hit this endpoint 4 times within 60s to get 429.",
    }), 200


@app.route("/status/431")
def status_431():
    """431 Request Header Fields Too Large — Headers exceed 500 bytes (demo)."""
    max_header_size = 500
    total_header_size = sum(len(k) + len(v) for k, v in request.headers)
    if total_header_size > max_header_size:
        return jsonify({
            "status_code": 431,
            "error": "Request Header Fields Too Large",
            "message": f"Headers are {total_header_size} bytes. Max allowed: {max_header_size}.",
        }), 431
    return jsonify({
        "status_code": 200,
        "message": "Header size is acceptable.",
        "total_header_bytes": total_header_size,
        "max_allowed_bytes": max_header_size,
    }), 200


@app.route("/status/451")
def status_451():
    """451 Unavailable For Legal Reasons — Blocked by legal order."""
    blocked_regions = {"IQ", "IR", "CN"}
    region = request.args.get("region", "").upper()
    if region in blocked_regions:
        return jsonify({
            "status_code": 451,
            "error": "Unavailable For Legal Reasons",
            "message": f"This content is legally restricted in region '{region}'.",
            "reference": "Court Order #2026-451",
            "named_after": "Fahrenheit 451 by Ray Bradbury",
        }), 451
    return jsonify({
        "status_code": 200,
        "message": "Content is available in your region.",
        "hint": "Add ?region=IQ or ?region=CN to trigger 451.",
    }), 200


# ═══════════════════════════════════════════════
#  5xx — Server Errors
# ═══════════════════════════════════════════════

@app.route("/status/500")
def status_500():
    """500 Internal Server Error — Unhandled exception in server code."""
    trigger = request.args.get("trigger", "false")
    if trigger == "true":
        # Deliberately raise an unhandled exception
        raise ZeroDivisionError("Intentional crash: division by zero!")
    return jsonify({
        "status_code": 200,
        "message": "Server is fine.",
        "hint": "Add ?trigger=true to cause a real 500 crash.",
    }), 200


@app.errorhandler(500)
def handle_500(error):
    return jsonify({
        "status_code": 500,
        "error": "Internal Server Error",
        "message": "An unexpected error occurred on the server.",
        "detail": str(error),
    }), 500


@app.route("/status/501")
def status_501():
    """501 Not Implemented — Method or feature not supported by this server."""
    return jsonify({
        "status_code": 501,
        "error": "Not Implemented",
        "message": "The server does not support the functionality required to fulfill this request.",
        "note": "PATCH and TRACE methods are not implemented on this server.",
    }), 501


@app.route("/status/502")
def status_502():
    """
    502 Bad Gateway
    Simulates: this server (proxy) asked an upstream service
    and received an invalid/empty response.
    """
    import urllib.request, urllib.error
    upstream_url = request.args.get("upstream", "http://localhost:9999/nonexistent")
    try:
        urllib.request.urlopen(upstream_url, timeout=1)
        # If somehow reachable, fall through
    except Exception as exc:
        return jsonify({
            "status_code": 502,
            "error": "Bad Gateway",
            "message": "The upstream service returned an invalid response.",
            "upstream_url": upstream_url,
            "upstream_error": str(exc),
        }), 502
    return jsonify({
        "status_code": 200,
        "message": "Upstream responded successfully.",
    }), 200


@app.route("/status/503")
def status_503():
    """503 Service Unavailable — Server is overloaded or in maintenance."""
    maintenance = request.args.get("maintenance", "true")
    if maintenance == "true":
        return jsonify({
            "status_code": 503,
            "error": "Service Unavailable",
            "message": "Server is temporarily under maintenance. Please try again later.",
            "retry_after_seconds": 120,
        }), 503, {"Retry-After": "120"}
    return jsonify({
        "status_code": 200,
        "message": "Service is available.",
        "hint": "Add ?maintenance=true to simulate 503.",
    }), 200


@app.route("/status/504")
def status_504():
    """
    504 Gateway Timeout
    Simulates: proxy waited for upstream but it took too long.
    Pass ?slow=true to see the timeout behaviour.
    """
    slow = request.args.get("slow", "false")
    timeout_seconds = 2
    if slow == "true":
        # Simulate upstream being too slow
        time.sleep(timeout_seconds + 1)
    # In the demo we always return 504 when ?slow=true
    # (in reality the sleep above would be in the upstream call)
    if slow == "true":
        return jsonify({
            "status_code": 504,
            "error": "Gateway Timeout",
            "message": f"Upstream service did not respond within {timeout_seconds}s.",
        }), 504
    return jsonify({
        "status_code": 200,
        "message": "Upstream responded in time.",
        "hint": "Add ?slow=true to simulate a 504 timeout.",
    }), 200


@app.route("/status/505")
def status_505():
    """505 HTTP Version Not Supported."""
    http_version = request.environ.get("SERVER_PROTOCOL", "HTTP/1.1")
    if http_version == "HTTP/0.9":
        return jsonify({
            "status_code": 505,
            "error": "HTTP Version Not Supported",
            "message": f"Protocol '{http_version}' is not supported.",
        }), 505
    return jsonify({
        "status_code": 200,
        "message": f"Protocol '{http_version}' is supported.",
        "note": "This server requires HTTP/1.1 or higher.",
    }), 200


@app.route("/status/507")
def status_507():
    """507 Insufficient Storage — Server storage quota exceeded."""
    import shutil
    total, used, free = shutil.disk_usage("/")
    free_mb = free / (1024 ** 2)
    threshold_mb = 0   # demo: set very low so we can control with ?force=true
    force = request.args.get("force", "false")
    if force == "true" or free_mb < threshold_mb:
        return jsonify({
            "status_code": 507,
            "error": "Insufficient Storage",
            "message": "The server does not have enough storage to complete the request.",
            "free_mb": round(free_mb, 2),
        }), 507
    return jsonify({
        "status_code": 200,
        "message": "Sufficient storage available.",
        "free_mb": round(free_mb, 2),
        "hint": "Add ?force=true to simulate 507.",
    }), 200


@app.route("/status/508")
def status_508():
    """508 Loop Detected — Infinite redirect/dependency loop detected."""
    depth = request.args.get("depth", type=int, default=0)
    max_depth = 5
    if depth >= max_depth:
        return jsonify({
            "status_code": 508,
            "error": "Loop Detected",
            "message": f"Infinite loop detected after {depth} iterations.",
            "depth": depth,
        }), 508
    return jsonify({
        "status_code": 200,
        "message": "No loop detected.",
        "current_depth": depth,
        "hint": f"Add ?depth={max_depth} or higher to trigger 508.",
    }), 200


@app.route("/status/511")
def status_511():
    """511 Network Authentication Required — Captive portal (e.g., hotel Wi-Fi)."""
    authenticated = request.cookies.get("network_auth", "false")
    if authenticated != "true":
        return jsonify({
            "status_code": 511,
            "error": "Network Authentication Required",
            "message": "You must authenticate with the network before accessing the internet.",
            "login_url": "http://captive.example.com/login",
        }), 511
    return jsonify({
        "status_code": 200,
        "message": "Network access granted.",
        "hint": "Set cookie 'network_auth=true' to bypass this check.",
    }), 200


# ═══════════════════════════════════════════════
#  Generic error handlers
# ═══════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status_code": 404,
        "error": "Not Found",
        "message": "The route you requested does not exist on this server.",
        "available_routes": "GET /",
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "status_code": 405,
        "error": "Method Not Allowed",
        "message": str(e),
    }), 405


# ═══════════════════════════════════════════════
#  Quick test client (run with --test flag)
# ═══════════════════════════════════════════════

def run_tests(base_url: str = "http://127.0.0.1:5000"):
    """Quick smoke-test all endpoints and print results."""
    import requests as req

    tests = [
        # (method, path, kwargs, expected_status)
        ("GET",    "/",                    {},                                          200),
        # 1xx
        ("GET",    "/status/101",          {"headers": {"Upgrade": "websocket"}},       101),
        # 2xx
        ("GET",    "/status/200",          {"headers": {"Authorization": "Bearer secret-token-123"}}, 200),
        ("POST",   "/status/201",          {"json": {"name": "Bob", "email": "bob@x.com"}}, 201),
        ("GET",    "/status/202",          {},                                          202),
        ("DELETE", "/status/204",          {"headers": {"Authorization": "Bearer secret-token-123"}, "params": {"id": 1}}, 204),
        ("GET",    "/status/206",          {"headers": {"Range": "items=0-4"}},         206),
        # 3xx
        ("GET",    "/status/301",          {"allow_redirects": False},                  301),
        ("GET",    "/status/302",          {"allow_redirects": False},                  302),
        ("GET",    "/status/304",          {"headers": {"If-None-Match": '"v1.0-users"'}}, 304),
        # 4xx
        ("POST",   "/status/400",          {"data": "not json"},                        400),
        ("GET",    "/status/401",          {},                                          401),
        ("GET",    "/status/402",          {},                                          402),
        ("GET",    "/status/403",          {"headers": {"Authorization": "Bearer secret-token-123"}}, 403),
        ("GET",    "/status/404",          {"params": {"id": 9999}},                   404),
        ("GET",    "/status/405",          {},                                          405),
        ("GET",    "/status/406",          {"headers": {"Accept": "application/xml"}},  406),
        ("GET",    "/status/408",          {},                                          408),
        ("POST",   "/status/409",          {"json": {"email": "ali@example.com"}},      409),
        ("GET",    "/status/410",          {},                                          410),
        ("POST",   "/status/411",          {"data": "hello"},                           411),
        ("GET",    "/status/412",          {"headers": {"If-Match": '"wrong-etag"'}},   412),
        ("POST",   "/status/413",          {"data": "x" * 2000},                        413),
        ("GET",    "/status/415",          {"headers": {"Content-Type": "text/plain"}}, 415),
        ("GET",    "/status/416",          {"headers": {"Range": "bytes=600-900"}},     416),
        ("GET",    "/status/418",          {"params": {"brew": "coffee"}},              418),
        ("GET",    "/status/422",          {"json": {"age": -5, "email": "bad-email"}}, 422),
        ("GET",    "/status/423",          {"params": {"resource": "/locked-file"}},    423),
        ("GET",    "/status/425",          {},                                          425),
        ("GET",    "/status/426",          {},                                          426),
        ("GET",    "/status/428",          {},                                          428),
        ("GET",    "/status/451",          {"params": {"region": "CN"}},                451),
        # 5xx
        ("GET",    "/status/500",          {"params": {"trigger": "true"}},             500),
        ("GET",    "/status/501",          {},                                          501),
        ("GET",    "/status/502",          {},                                          502),
        ("GET",    "/status/503",          {"params": {"maintenance": "true"}},         503),
        ("GET",    "/status/505",          {},                                          200),  # can't force old protocol in requests
        ("GET",    "/status/507",          {"params": {"force": "true"}},               507),
        ("GET",    "/status/508",          {"params": {"depth": 5}},                   508),
        ("GET",    "/status/511",          {},                                          511),
    ]

    pad = 45
    print("\n" + "=" * 65)
    print(f"  HTTP Status Codes — Test Run against {base_url}")
    print("=" * 65)
    passed = failed = 0
    for method, path, kwargs, expected in tests:
        url = base_url + path
        try:
            resp = getattr(req, method.lower())(url, timeout=5, **kwargs)
            ok = resp.status_code == expected
            icon = "✅" if ok else "❌"
            label = f"{method} {path}"
            print(f"  {icon}  {label:<{pad}}  got {resp.status_code}  (expected {expected})")
            if ok:
                passed += 1
            else:
                failed += 1
        except Exception as exc:
            print(f"  ⚠️  {method} {path:<{pad}}  ERROR: {exc}")
            failed += 1

    print("-" * 65)
    print(f"  Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 65 + "\n")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        print("""
╔══════════════════════════════════════════════════════════╗
║   HTTP Status Codes — Flask Demo Server                  ║
║   Author: Eng. Ali (Baghi Channel)                       ║
╠══════════════════════════════════════════════════════════╣
║   GET  http://127.0.0.1:5000/        → full route list   ║
║   GET  http://127.0.0.1:5000/status/<code>               ║
╠══════════════════════════════════════════════════════════╣
║   To run tests (Server must be active):                  ║
║    python flask_http_status_codes.py --test              ║
╚══════════════════════════════════════════════════════════╝
""")
        app.run(debug=True, port=5000)