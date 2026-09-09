"""Allow ``python -m proof`` to invoke the CLI."""

import sys

from proof.cli import main

sys.exit(main())
