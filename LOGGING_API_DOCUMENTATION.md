# API Documentation - Auto Screen Share Logging (Client Integration)

## Overview

This document describes the API contracts that the external logging server exposes, and how the Auto Screen Share clients should call them. Server implementation details (code, database schema, ops) are out of scope and live elsewhere.

## Base URL

```
https://your-domain.com/api/logs
```

## Authentication

All requests should include an API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### 1. Application Startup Log

**Endpoint:** `POST /api/logs/startup`

**Description:** Logs when the application starts up with system information.

**Request Body:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "application_type": "python_desktop" | "chrome_extension",
  "version": "1.0.5",
  "system_info": {
    "computer_name": "DESKTOP-ABC123",
    "os_version": "Windows 10.0.26100",
    "python_version": "3.9.7" // only for python_desktop
  },
  "update_info": {
    "update_check_performed": true,
    "update_available": false,
    "current_version": "1.0.5",
    "latest_version": "1.0.5"
  }
}
```

**Response:**
```json
{
  "success": true,
  "log_id": "log_12345",
  "message": "Startup log recorded successfully"
}
```

### 2. Window Detection Log

**Endpoint:** `POST /api/logs/window-detection`

**Description:** Logs when the application detects or fails to detect Google Meet windows.

**Request Body:**
```json
{
  "timestamp": "2024-01-15T10:35:00Z",
  "application_type": "python_desktop" | "chrome_extension",
  "version": "1.0.5",
  "detection_result": {
    "meet_window_found": true,
    "window_title": "Meet - abcd-efgh-ijkl",
    "window_count": 1,
    "search_duration_ms": 150
  },
  "action_taken": "window_activated" | "no_action_needed" | "error_occurred",
  "error_details": null // or error message if action_taken is "error_occurred"
}
```

**Response:**
```json
{
  "success": true,
  "log_id": "log_12346",
  "message": "Window detection log recorded successfully"
}
```

### 3. Screen Share Action Log

**Endpoint:** `POST /api/logs/screen-share`

**Description:** Logs when screen sharing actions are performed.

**Request Body:**
```json
{
  "timestamp": "2024-01-15T10:36:00Z",
  "application_type": "python_desktop" | "chrome_extension",
  "version": "1.0.5",
  "action_type": "join_meeting" | "present_now" | "select_screen" | "confirm_share",
  "action_result": "success" | "failed" | "timeout",
  "meet_window_title": "Meet - abcd-efgh-ijkl",
  "action_details": {
    "attempts_made": 1,
    "duration_ms": 2500,
    "error_message": null // or error details if action_result is "failed"
  }
}
```

**Response:**
```json
{
  "success": true,
  "log_id": "log_12347",
  "message": "Screen share action log recorded successfully"
}
```

### 4. Update Check Log

**Endpoint:** `POST /api/logs/update-check`

**Description:** Logs update check results and update operations.

**Request Body:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "application_type": "python_desktop",
  "version": "1.0.5",
  "update_check_result": {
    "check_performed": true,
    "update_available": true,
    "current_version": "1.0.4",
    "latest_version": "1.0.5",
    "download_url": "https://your-domain.com/updates/auto-screen-share_1.0.5.exe"
  },
  "update_action": "download_started" | "download_completed" | "download_failed" | "restart_initiated",
  "update_details": {
    "download_size_bytes": 15728640,
    "download_duration_ms": 5000,
    "error_message": null // or error details if update failed
  }
}
```

**Response:**
```json
{
  "success": true,
  "log_id": "log_12348",
  "message": "Update check log recorded successfully"
}
```

### 5. Error Log

**Endpoint:** `POST /api/logs/error`

**Description:** Logs application errors and exceptions.

**Request Body:**
```json
{
  "timestamp": "2024-01-15T10:37:00Z",
  "application_type": "python_desktop" | "chrome_extension",
  "version": "1.0.5",
  "error_type": "window_activation_failed" | "network_error" | "permission_denied" | "unknown_error",
  "error_message": "Failed to activate Meet window: Access denied",
  "error_context": {
    "function_name": "monitor_meet",
    "meet_window_title": "Meet - abcd-efgh-ijkl",
    "system_info": {
      "computer_name": "DESKTOP-ABC123",
      "os_version": "Windows 10.0.26100"
    }
  },
  "stack_trace": "Traceback (most recent call last):\n  File \"auto_screen_share.py\", line 53, in monitor_meet\n    pywinctl.getWindowsWithTitle(current_title)[0].activate()\nException: Access denied"
}
```

**Response:**
```json
{
  "success": true,
  "log_id": "log_12349",
  "message": "Error log recorded successfully"
}
```

### 6. Heartbeat Log

**Endpoint:** `POST /api/logs/heartbeat`

**Description:** Periodic heartbeat to confirm the application is running.

**Request Body:**
```json
{
  "timestamp": "2024-01-15T10:40:00Z",
  "application_type": "python_desktop" | "chrome_extension",
  "version": "1.0.5",
  "uptime_seconds": 600,
  "status": "monitoring" | "idle" | "processing",
  "meet_windows_detected": 1,
  "last_action_timestamp": "2024-01-15T10:36:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "log_id": "log_12350",
  "message": "Heartbeat log recorded successfully"
}
```

## Error Responses

All endpoints return the following error format:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST" | "AUTHENTICATION_FAILED" | "RATE_LIMITED" | "SERVER_ERROR",
    "message": "Human readable error message",
    "details": "Additional error details if available"
  }
}
```

## HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - Missing or invalid API key
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

- Maximum 100 requests per minute per IP address
- Maximum 1000 requests per hour per API key

## Data Retention

- Logs are retained for 90 days
- Error logs are retained for 1 year
- Heartbeat logs are retained for 30 days

## Implementation Notes

1. **Timestamp Format**: All timestamps should be in ISO 8601 format (UTC)
2. **Version Format**: Use semantic versioning (e.g., "1.0.5")
3. **Computer Name**: Should be sanitized to remove sensitive information
4. **Error Handling**: Applications should gracefully handle network failures and continue operation
5. **Retry Logic**: Failed requests should be retried with exponential backoff (max 3 retries)
6. **Batch Logging**: Consider implementing batch logging for high-frequency events

## Security Considerations

1. **API Key Rotation**: Implement regular API key rotation
2. **Data Sanitization**: Ensure no sensitive data is logged (passwords, personal info)
3. **HTTPS Only**: All communication must use HTTPS
4. **Input Validation**: Validate all incoming data on the server side
5. **Rate Limiting**: Implement proper rate limiting to prevent abuse

## Client Responsibilities

- Send requests over HTTPS with the Authorization header.
- Sanitize and avoid sensitive data in payloads.
- Implement retry with exponential backoff (max 3 retries) and continue app operation if logging fails.
- Keep `version` consistent with app release.








