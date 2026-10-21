"""pip-audit wrapper: `python scripts/run_pip_audit.py -r requirements.txt [...]`.

If `truststore` is installed, TLS verification uses the operating-system certificate store. That is what
makes pip-audit work on networks whose antivirus/proxy re-signs HTTPS (the interceptor's root CA is in the
OS store but not in certifi). Verification is ALWAYS on: this never disables checks or passes verify=False.
"""

import runpy
import sys

try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:  # CI runners: certifi is enough
    pass

sys.argv = ["pip-audit", *sys.argv[1:]]
runpy.run_module("pip_audit", run_name="__main__")
