                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            # api_keys.py
import os

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DISCORD_WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL",
    "https://discord.com/api/webhooks/1325728507938213969/wvDTSWiEuMXPL4VyzEdkIJSYsfccOtf4OZV8kIcc11yHLeT3nPpFMhpfWwFFWWAC7ZHL"
)