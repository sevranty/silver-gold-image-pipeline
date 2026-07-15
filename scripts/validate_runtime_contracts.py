#!/usr/bin/env python3
"""CLI entrypoint for deterministic SGP runtime-contract validation."""

from __future__ import annotations

import sys

from runtime_contract_validation import main

if __name__ == "__main__":
    sys.exit(main())
