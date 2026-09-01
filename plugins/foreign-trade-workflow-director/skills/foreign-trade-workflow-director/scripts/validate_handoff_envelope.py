#!/usr/bin/env python3
"""Compatibility entrypoint for the full customer-flow transition validator.

Envelope-only validation is intentionally unavailable because it would let a
caller bypass the registered predecessor state, receipts, and hash bindings.
"""

from __future__ import annotations

import sys

from validate_customer_flow_transition import main


if __name__ == "__main__":
    sys.exit(main())
