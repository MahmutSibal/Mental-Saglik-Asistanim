from typing import Optional
import random
from ..db.mongodb import suggestions_collection

# Label normalization and specific fallbacks for common emotion models
LABEL_ALIASES = {
    "sad": "sadness",
    "happy": "joy",
    "angry": "anger",
}

SUGGESTION_FALLBACKS = {
    "joy": "Mutluluğunuzu paylaşın: minnettar olduğunuz 3 şeyi yazın ve yakınınızla paylaşın.",
    "sadness": "Hafif bir egzersiz yapın, sevdiğiniz bir şarkıyı dinleyin ve duygularınızı bir günlükte ifade edin.",
    "anger": "10 derin nefes alın, kısa bir yürüyüş yapın ve düşüncelerinizi yeniden çerçevelemeyi deneyin.",
    "fear": "4-7-8 nefes tekniğini deneyin ve kaygınızı küçük adımlara bölün.",
    "disgust": "Hoşnutsuzluğun kaynağını yazın ve uzaklaşmak yerine küçük bir iyileştirme adımı belirleyin.",
    "surprise": "Beklenmedik durumdan ne öğrendiniz? 3 maddeyle not alın ve bir fırsat belirleyin.",
    "neutral": "5 dakikalık mindful mola verin ve vücut taraması yapın.",
}


def normalize(label: str) -> str:
    l = label.lower()
    return LABEL_ALIASES.get(l, l)


async def fetch_suggestion_text(emotion: str) -> str:
    """Return a suggestion text for the given normalized or raw emotion.

    Order of precedence:
    - Random pick from DB document.suggestion_texts if present and non-empty
    - DB document.suggestion_text if present
    - Label-specific fallback from SUGGESTION_FALLBACKS
    - Generic final fallback
    """
    emo = normalize(emotion)

    # Try DB first
    col = suggestions_collection()
    doc = await col.find_one({"emotion": emo})
    if doc:
        texts = doc.get("suggestion_texts")
        if isinstance(texts, list) and len(texts) > 0:
            return random.choice(texts)
        single = doc.get("suggestion_text")
        if isinstance(single, str) and single.strip():
            return single

    # Label-specific fallback
    text = SUGGESTION_FALLBACKS.get(emo)
    if text:
        return text

    # Final generic fallback
    return (
        "Kendinize iyi davranın: kısa bir yürüyüş, derin nefes ve güvendiğiniz biriyle sohbet iyi gelebilir."
    )
