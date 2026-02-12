KST_TZ = "Asia/Seoul"

MIN_CHARS = 700
MAX_CHARS = 1000
MIN_ITEMS = 3
MAX_ITEMS = 5
MIN_SENTENCES = 2
MAX_SENTENCES = 4
MIN_SOURCES_TOTAL = 4
MAX_SINGLE_SOURCE_RATIO = 0.5

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
