from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
import numpy as np
import cv2
from ..deps import get_current_user_id

router = APIRouter()

detector = None  # lazy init


@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id)):
    content = await file.read()
    # Convert bytes to numpy image
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    # FER expects RGB
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    try:
        global detector
        if detector is None:
            from fer import FER  # lazy import
            detector = FER(mtcnn=False)
        res = detector.detect_emotions(rgb)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FER error: {e}")

    if not res:
        return {"label": "neutral", "scores": {"neutral": 1.0}}

    # Take highest scoring face if multiple
    best = max(res, key=lambda r: max(r.get('emotions', {"neutral": 0}).values()))
    scores = best.get('emotions', {})
    label = max(scores, key=scores.get)
    return {"label": label, "scores": scores}
