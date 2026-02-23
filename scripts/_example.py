#!/usr/bin/env python3
"""
Example script — delete this once you understand the pattern.

Usage:
    python3 scripts/_example.py

All scripts should:
1. Load environment variables from .env
2. Take clear inputs
3. Produce clear outputs
4. Handle errors gracefully
"""

import os
from pathlib import Path

# Load .env file (requires: pip install python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, using system env vars

def main():
    """Main function — replace with your logic."""
    print("Hello from AIDE!")
    print(f"Working directory: {Path.cwd()}")

    # Example: reading an env var
    api_key = os.getenv("EXAMPLE_API_KEY", "not-set")
    print(f"EXAMPLE_API_KEY is: {'configured' if api_key != 'not-set' else 'not configured'}")

if __name__ == "__main__":
    main()
