import json, pathlib
from config import settings

BASE = pathlib.Path(__file__).parent.parent / "locales"

_LOCALES = {
    "uz": json.loads((BASE / "uz.json").read_text(encoding="utf-8")),
    "ru": json.loads((BASE / "ru.json").read_text(encoding="utf-8")),
}

def t(key: str, lang: str | None) -> str:
    lang = (lang or settings.default_lang)
    return _LOCALES.get(lang, _LOCALES[settings.default_lang]).get(key, key)
