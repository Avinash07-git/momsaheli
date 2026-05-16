"""Sponsor adapters. Each has the same shape:
- async function calling the real API
- automatic fallback to a cached fixture on error OR when USE_FIXTURES=true
- structured logging so judges can trace every call
"""
