import os
MOCK_MODE = os.getenv("TRUSTLENS_MOCK", "true").lower() == "true"
