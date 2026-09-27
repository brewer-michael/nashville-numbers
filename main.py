#!/usr/bin/env python3
"""Run Nashville Numbers from a source checkout without installing it:

    python3 main.py --simulate --demo

After `pip install .` the same program is available as `nashville-numbers`.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from nashville_numbers.cli import main  # noqa: E402

if __name__ == '__main__':
    sys.exit(main())
