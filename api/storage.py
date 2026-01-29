"""
Simple storage layer: Uses Vercel KV when available, falls back to dict
"""
import os
import json
from typing import Dict, List, Optional

# Check for Vercel KV
KV_URL = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN")
USE_KV = KV_URL and KV_TOKEN

if USE_KV:
    try:
        from upstash_redis import Redis
        kv = Redis(url=KV_URL, token=KV_TOKEN)
        print("✅ Using Vercel KV - data will persist!")
    except Exception as e:
        print(f"⚠️  KV connection failed: {e}, falling back to in-memory")
        USE_KV = False
        kv = None
else:
    kv = None
    print("⚠️  No KV configured - data will be inconsistent on Vercel")


class Storage:
    """Simple key-value storage that works with KV or in-memory dict"""
    
    def __init__(self):
        if not USE_KV:
            self._memory = {}
    
    def set(self, key: str, value: str) -> None:
        if USE_KV:
            kv.set(key, value)
        else:
            self._memory[key] = value
    
    def get(self, key: str) -> Optional[str]:
        if USE_KV:
            result = kv.get(key)
            return result.decode() if isinstance(result, bytes) else result
        else:
            return self._memory.get(key)
    
    def delete(self, key: str) -> None:
        if USE_KV:
            kv.delete(key)
        else:
            self._memory.pop(key, None)
    
    def keys(self, pattern: str = "*") -> List[str]:
        if USE_KV:
            keys = kv.keys(pattern)
            return [k.decode() if isinstance(k, bytes) else k for k in keys]
        else:
            # Simple pattern matching for in-memory
            if pattern == "*":
                return list(self._memory.keys())
            prefix = pattern.replace("*", "")
            return [k for k in self._memory.keys() if k.startswith(prefix)]


# Global storage instance
storage = Storage()
