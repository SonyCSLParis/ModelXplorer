"""
App mode configuration.

Allows easy toggling between "onefit" and "batch" when running in Docker
by reading an environment variable.
"""
import os

try:
	# Optional: load env vars from .env in local dev
	from dotenv import load_dotenv
	load_dotenv()
except Exception:
	pass

ALLOWED = {"onefit", "batch"}

# Prefer APP_VERSION, but accept legacy VERSION for backward compatibility
_mode = os.getenv("APP_VERSION", os.getenv("VERSION", "onefit")).lower()
VERSION = _mode if _mode in ALLOWED else "onefit"

# Optional debug output; set CONFIG_DEBUG=1 to print selected version
if os.getenv("CONFIG_DEBUG", "0").lower() in ("1", "true", "yes"):
	print(f"[config] Using app version '{VERSION}'")
# Example usage:
# docker compose --env-file .env up -d
# and set APP_VERSION=onefit or APP_VERSION=batch in .env or environment

