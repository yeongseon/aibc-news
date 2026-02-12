KST_TZ = "Asia/Seoul"

MIN_CHARS = 180
MAX_CHARS = 240
MIN_ITEMS = 1
MAX_ITEMS = 1
MIN_SENTENCES = 2
MAX_SENTENCES = 3
MIN_SOURCES_TOTAL = 1
MAX_SINGLE_SOURCE_RATIO = 1.0

FORBIDDEN_WORDS = ["충격", "대박", "속보", "확정 수익"]

DEFAULT_AUTHOR = "AIBC Desk"
DEFAULT_CATEGORY = "News"

YAHOO_SYMBOLS = [
    {"symbol": "^KS11", "label": "코스피"},
    {"symbol": "KRW=X", "label": "원/달러 환율"},
]

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_CITY = "Seoul"
OPENWEATHER_UNITS = "metric"
OPENWEATHER_LANG = "kr"

GITHUB_MODELS_CHAT_URL = "https://models.inference.ai.azure.com/chat/completions"
GITHUB_MODELS_MODEL = "gpt-4o"
