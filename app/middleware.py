# Third-party Library imports
from slowapi import Limiter


# Always return same key to share the limit across all clients
global_limiter = Limiter(key_func=lambda request: "global")