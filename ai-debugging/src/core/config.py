"""Global configuration. Mixed styles on purpose."""

DEFAULT_TAX_RATE = 0.08
CACHE_TTL_SECONDS = 30
MAX_WORKERS = 4
DB_PATH = ":memory:"  # in real life this was a file path

# "Feature flags" that never got cleaned up
USE_NEW_PRICING = True
USE_LEGACY_DISCOUNT = False
