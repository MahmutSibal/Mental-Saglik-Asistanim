from typing import Dict, List, TypedDict, Tuple
import re
import unicodedata
from ..core.config import settings
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline, MarianMTModel, MarianTokenizer

# Types for pipeline output
class LabelScore(TypedDict):
    label: str
    score: float

# Simple Turkish keyword map to canonical labels (kept as secondary signal)
EMOTION_KEYWORDS: Dict[str, List[str]] = {
    "anger": ["sinirliyim", "sinirli", "kızgınım", "kizginim", "kızgın", "öfkeliyim", "ofkeliyim", "öfke", "ofke"],
    "sadness": ["üzgünüm", "uzgunum", "üzgün", "uzgun", "hüzünlü", "huzunlu", "mutsuz", "moralim bozuk", "ağlıyorum", "agliyorum"],
    "joy": ["mutluyum", "mutlu", "harika hissediyorum", "seviniyorum", "neşeliyim", "neseliyim", "iyi hissediyorum"],
    "fear": ["korkuyorum", "korku", "endişeliyim", "endiseliyim", "kaygılıyım", "kaygiliyim", "anksiyete", "panik"],
    "surprise": ["şaşırdım", "sasirdim", "şaşkınım", "saskinim", "beklenmedik", "beklemedim"],
    "love": ["seviyorum", "aşığım", "asigim", "aşk", "ask", "sevgi"],
    "neutral": ["nötr", "notr", "fark etmiyor", "normal"],
    "anxiety": ["kaygılıyım", "kaygı", "kaygiliyim", "anksiyete", "panik"],
    "disgust": ["tiksindim", "tiksinti", "iğrenç", "igrenc"],
    "admiration": ["hayranım", "hayranlik", "takdir ediyorum"],
    "curiosity": ["merak ediyorum", "meraklıyım", "merakliyim"],
}

# Crisis patterns (very conservative; expand with care)
CRISIS_PATTERNS: List[re.Pattern] = [
    re.compile(r"intihar|kendimi\s*öldür|yasamak\s*istemiyorum|yaşamak\s*istemiyorum|kendime\s*zarar|bıçaklayacağım|atlayacağım", re.I),
]

# Global singletons
_tokenizer = None
_model = None
_pipeline = None
_mt_tokenizer = None
_mt_model = None
_mt_pipe = None


def get_pipeline():
    global _tokenizer, _model, _pipeline
    if _pipeline is None:
        model_name = settings.HF_MODEL_NAME
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _pipeline = pipeline(
            task="text-classification",
            model=_model,
            tokenizer=_tokenizer,
            return_all_scores=True,
        )
    return _pipeline


def get_mt_pipeline():
    global _mt_tokenizer, _mt_model, _mt_pipe
    if not settings.USE_TR_EN_TRANSLATION:
        return None
    if _mt_pipe is None:
        mt_name = settings.HF_TR_EN_MODEL
        _mt_tokenizer = MarianTokenizer.from_pretrained(mt_name)
        _mt_model = MarianMTModel.from_pretrained(mt_name)
        _mt_pipe = pipeline("translation", model=_mt_model, tokenizer=_mt_tokenizer, src_lang="tr", tgt_lang="en")
    return _mt_pipe


def translate_tr_en(text: str) -> str:
    pipe = get_mt_pipeline()
    if pipe is None:
        return text
    try:
        out = pipe(text, max_length=512)
        return out[0]["translation_text"]
    except Exception:
        return text


def _strip_diacritics(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def _normalize_tr_text(text: str) -> str:
    t = text.strip().lower()
    # fold diacritics: ö->o, ü->u, ğ->g etc. for robust keyword match
    t = _strip_diacritics(t)
    # collapse repeated characters (cooook -> cook -> cok)
    t = re.sub(r"(\w)\1{2,}", r"\1\1", t)
    # common slang/variants
    replacements = {
        'cok': 'çok', 'cokuzgunum': 'çok üzgünüm', 'iyiyim': 'iyi yim',
    }
    for k, v in replacements.items():
        t = t.replace(k, v)
    return t


def detect_crisis(text: str) -> Tuple[bool, str | None]:
    t = text.lower()
    for pat in CRISIS_PATTERNS:
        if pat.search(t):
            return True, "Kriz ifadesi tespit edildi"
    return False, None


def analyze_text(text: str) -> Dict[str, float]:
    # Primary path: translate Turkish to English if enabled, then analyze with English emotion model
    t = text
    if settings.USE_TR_EN_TRANSLATION:
        t = translate_tr_en(text)

    pipe = get_pipeline()
    outputs: List[List[LabelScore]] = pipe(t)  # type: ignore[assignment]
    items: List[LabelScore] = outputs[0]
    scores: Dict[str, float] = {item["label"].lower(): float(item["score"]) for item in items}

    # Secondary hint: if explicit emotion keywords present in original text, bias towards that label
    key = keyword_emotion(text)
    if key and key in scores:
        # Light bias to ensure chosen label becomes top if close
        scores[key] = max(scores[key], 0.95)
    return scores


def top_label(scores: Dict[str, float]) -> str:
    return max(scores.items(), key=lambda kv: kv[1])[0]


def keyword_emotion(text: str) -> str | None:
    t = _normalize_tr_text(text)
    for label, words in EMOTION_KEYWORDS.items():
        for w in words:
            if _strip_diacritics(w) in t:
                return label
    return None


def is_uncertain(scores: Dict[str, float], threshold: float = 0.6, margin: float = 0.1) -> bool:
    if not scores:
        return True
    top = max(scores.values())
    # close second?
    sorted_vals = sorted(scores.values(), reverse=True)
    second = sorted_vals[1] if len(sorted_vals) > 1 else 0.0
    return top < threshold or (top - second) < margin
