KST_TZ = "Asia/Seoul"

MIN_CHARS = 180
MAX_CHARS = 240
MIN_ITEMS = 1
MAX_ITEMS = 1
MIN_SENTENCES = 2
MAX_SENTENCES = 4
MIN_SOURCES_TOTAL = 1
MAX_SINGLE_SOURCE_RATIO = 1.0

CATEGORY_RULES = {
    "politics": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
    "economy": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
    "society": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
    "world": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
    "tech": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
    "culture": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
    "sports": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
    "entertainment": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
    "life": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
    "weather": {
        "min_chars": 160,
        "max_chars": 240,
        "min_items": 1,
        "max_items": 1,
        "min_sentences": 2,
        "max_sentences": 4,
        "min_sources_total": 1,
        "max_single_source_ratio": 1.0,
    },
}

FORBIDDEN_WORDS = ["충격", "대박", "속보", "확정 수익"]

DEFAULT_AUTHOR = "AIBC Desk"
DEFAULT_CATEGORY = "정치"

CATEGORY_LABELS = {
    "politics": "정치",
    "economy": "경제",
    "society": "사회",
    "world": "세계",
    "tech": "기술",
    "culture": "문화",
    "sports": "스포츠",
    "entertainment": "연예",
    "life": "생활",
    "weather": "날씨",
}

YAHOO_SYMBOLS = [
    {"symbol": "^KS11", "label": "코스피"},
    {"symbol": "KRW=X", "label": "원/달러 환율"},
]

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_CITIES = ["Seoul", "Busan", "Daegu", "Daejeon", "Gwangju"]
OPENWEATHER_UNITS = "metric"
OPENWEATHER_LANG = "kr"

GITHUB_MODELS_CHAT_URL = "https://models.inference.ai.azure.com/chat/completions"
GITHUB_MODELS_MODEL = "gpt-4o"
