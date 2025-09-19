from fastapi import APIRouter
from app.schemas.crisis import CrisisResponse, CrisisResource


router = APIRouter()


@router.get("/", response_model=CrisisResponse)
async def get_crisis_resources():
    # Basic TR resources; user should localize further by region
    resources = [
        CrisisResource(
            title="Acil Yardım",
            description="Acil bir durumdaysanız 112’yi arayın.",
            phone="112",
        ),
        CrisisResource(
            title="ALO 183",
            description="Sosyal destek hattı ve psikososyal destek için.",
            phone="183",
            url="https://www.aile.gov.tr/alo183/",
        ),
        CrisisResource(
            title="Yeşilay Danışmanlık Merkezi (YEDAM)",
            description="Bağımlılık ve psikolojik destek danışma hattı.",
            phone="115",
            url="https://yedam.org.tr/",
        ),
    ]
    return CrisisResponse(resources=resources)
