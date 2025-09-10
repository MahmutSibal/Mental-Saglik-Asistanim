import asyncio
import argparse
from datetime import datetime
from typing import Dict, List

from app.db.mongodb import connect_to_mongo, close_mongo_connection, suggestions_collection, get_db

# Canonical emotions and multiple suggestion variants per emotion
SUGGESTIONS: Dict[str, List[str]] = {
    # Temel duygular
    "joy": [
        "Mutluluğunuzu paylaşın: minnettar olduğunuz 3 şeyi yazın ve yakınınızla paylaşın.",
        "Gününüze küçük bir kutlama ekleyin: sevdiğiniz bir tatlıyı yiyin veya sevdiklerinizle paylaşın.",
    ],
    "sadness": [
        "Hafif bir egzersiz yapın, sevdiğiniz bir şarkıyı dinleyin ve duygularınızı bir günlükte ifade edin.",
        "Nazik bir öz-şefkat pratiği yapın: kendinize iyi davranan 3 cümle yazın.",
    ],
    "anger": [
        "10 derin nefes alın, kısa bir yürüyüş yapın ve düşüncelerinizi yeniden çerçevelemeyi deneyin.",
        "Öfkeyi güvenli bir yere yönlendirin: 5 dakikalık serbest yazım, sonra kağıdı sakince kapatın.",
    ],
    "fear": [
        "Nefese odaklı 4-7-8 tekniğini deneyin ve kaygılarınızı küçük adımlara bölün.",
        "Korkunuzu 3 parçaya ayırın ve her biri için 1 küçük adım planlayın.",
    ],
    "love": [
        "Sevdiğiniz kişiye takdir mesajı gönderin veya küçük bir jest yapın.",
        "Kendinize sevgi dolu bir not yazın: bugün neyi iyi yaptınız?",
    ],
    "surprise": [
        "Beklenmedik durumu fırsata çevirin: ne öğrendiniz, üç cümlede yazın.",
        "Hoş sürprizi paylaşın veya küçük bir anı defterinize not edin.",
    ],
    "neutral": [
        "Gün içinde 5 dakikalık mindful mola verin ve vücut taraması yapın.",
        "Bugün için tek bir küçük hedef seçin ve bitirince kendinizi tebrik edin.",
    ],

    # Pozitif duygular
    "optimism": [
        "Bugün için ulaşılabilir tek bir hedef belirleyin ve tamamlayınca kendinizi ödüllendirin.",
        "Olumlu bir iç konuşma cümlesi seçin ve gün içinde 3 kez tekrarlayın.",
    ],
    "admiration": [
        "İlham aldığınız kişiden bir öğretiyi bugün uygulayın ve küçük bir ilerleme kaydedin.",
        "Hayran olduğunuz özelliği kendinizde güçlendirmek için 1 adım belirleyin.",
    ],
    "gratitude": [
        "Bugün teşekkür etmek istediğiniz bir kişiyi arayın veya mesaj atın.",
        "Minnettar olduğunuz 3 şeyi yazın ve birini paylaşın.",
    ],
    "confidence": [
        "Başarılarınızı yazın ve kendinizle gurur duymak için 5 dakika ayırın.",
        "Kendinize güven veren bir anınızı hatırlayın ve detaylarını yazın.",
    ],
    "hope": [
        "Gelecek için umut dolu bir hayali defterinize yazın ve küçük bir adım atın.",
        "Umudu besleyen bir sembol seçin (resim, müzik) ve bugün kullanın.",
    ],
    "pride": [
        "Bugün gurur duyduğunuz bir anınızı yazın ve kendinizi ödüllendirin.",
        "Emeğinizin değerini görün: katkı sağladığınız 2 şeyi yazın.",
    ],
    "excitement": [
        "Bugün için sizi mutlu edecek küçük bir etkinlik planlayın.",
        "Heyecanınızı paylaşın: yakınınızla planınızı konuşun.",
    ],
    "serenity": [
        "10 dakika meditasyon yapın ve huzurlu bir müzik açın.",
        "Yavaş bir yürüyüş yapın; adımlarınızı ve nefesinizi eşleştirin.",
    ],
    "contentment": [
        "Kendinize bir fincan çay veya kahve hazırlayıp keyifli bir mola verin.",
        "Bugünün küçük güzel anını fotoğraflayın veya yazın.",
    ],
    "inspiration": [
        "Motivasyon verici bir podcast veya video izleyin ve öğrendiklerinizi yazın.",
        "Yaratıcı bir fikir yakalayın ve 10 dakikada kaba bir taslak çıkarın.",
    ],

    # Negatif duygular
    "disgust": [
        "Temas etmekten kaçındığınız şeyi yazın ve bunun yerine size iyi hissettiren temiz bir alan oluşturun.",
        "Duyguyu fark edin, yargılamadan adlandırın ve kısa bir mola verin.",
    ],
    "shame": [
        "Hatalarınızı bir arkadaşınızla paylaşın, destek alın ve dersleri yazın.",
        "Kendinize şefkatle yaklaşın: herkes hata yapar; düzeltici 1 adım seçin.",
    ],
    "guilt": [
        "Suçluluk hissettiğiniz konuda küçük bir düzeltici adım atın.",
        "Gerekiyorsa özür mesajı yazın ve daha iyi bir yaklaşım belirleyin.",
    ],
    "envy": [
        "Kıskandığınız kişinin özelliklerini ilham kaynağı olarak yazın ve kendi planınızı yapın.",
        "Kendinizde geliştirmek istediğiniz 1 beceriyi seçin ve ilk adımı atın.",
    ],
    "loneliness": [
        "Bir arkadaşınıza mesaj atın veya çevrim içi bir toplulukta sohbet edin.",
        "Kısa bir görüntülü arama planlayın veya bir yürüyüşe davet edin.",
    ],
    "resentment": [
        "Duygularınızı yazın ve kendinize nazik bir dil kullanarak ifade edin.",
        "Sınır koymanız gerekiyorsa, net ve saygılı bir cümle planlayın.",
    ],
    "frustration": [
        "Beyninizdeki baskıyı azaltmak için kısa bir mola verin ve nefes egzersizi yapın.",
        "Görevi parçalara ayırın; 10 dakikalık tek odak zamanı başlatın.",
    ],
    "overwhelm": [
        "Görevlerinizi küçük parçalara bölün ve bir tanesini hemen yapın.",
        "Yüksek beklentiyi yeniden çerçeveleyin: ‘Yeterince iyi’yi tanımlayın.",
    ],
    "anxiety": [
        "5 dakika nefes egzersizi yapın ve kaygınızı 1-10 arasında puanlayıp değişimi not edin.",
        "Endişe düşüncesine ‘dur’ deyin ve dikkati duyulara getirin (5-4-3-2-1).",
    ],
    "stress": [
        "Boyun ve omuzlarınıza masaj yapın veya esneme hareketleri yapın.",
        "Pomodoro tekniğiyle 25 dakika odaklanın, 5 dakika dinlenin.",
    ],
    "insecurity": [
        "Kendiniz hakkında sevdiğiniz 3 özelliği yazın.",
        "‘Ben yeterliyim’ onay cümlesini gün içinde tekrarlayın.",
    ],
    "jealousy": [
        "Kıskançlık hislerinizi yazın ve bunları geliştirmek için ilham alın.",
        "Kendinize adil hedefler koyun ve küçük bir ilerleme kaydedin.",
    ],
    "boredom": [
        "Yeni bir hobi hakkında 10 dakikalık araştırma yapın ve ilk adımı atın.",
        "Kısa bir tempolu yürüyüş yapın ve dönüşte yeni bir fikir yazın.",
    ],

    # Sosyal/ilişkisel duygular
    "trust": [
        "Yakın bir arkadaşınıza güveninizi belirten bir mesaj gönderin.",
        "Birine küçük bir sorumluluk verin ve süreci birlikte değerlendirin.",
    ],
    "compassion": [
        "Bugün birine yardım edin veya küçük bir iyilik yapın.",
        "Kendinize de şefkat gösterin: dinlenme molası verin.",
    ],
    "empathy": [
        "Yakınınızın yaşadığı bir olayı dinleyin ve ona destek olun.",
        "‘Seni duyuyorum’ cümlesini kurun ve yargısız dinleyin.",
    ],
    "connection": [
        "Ailenizle birlikte keyifli bir etkinlik planlayın.",
        "Uzun zamandır görüşmediğiniz biriyle iletişime geçin.",
    ],
    "forgiveness": [
        "Küçük bir kırgınlığı affetmek için kendinize izin verin.",
        "Affetmenin sizin için anlamını yazın ve küçük bir adım planlayın.",
    ],
    "belonging": [
        "İlgilendiğiniz bir toplulukla iletişime geçin veya bir etkinliğe katılın.",
        "Toplulukta katkı sunabileceğiniz küçük bir rol belirleyin.",
    ],
    "respect": [
        "Saygı duyduğunuz biri için takdir dolu bir mesaj yazın.",
        "Kendi sınırlarınıza saygı gösteren bir davranış seçin ve uygulayın.",
    ],

    # Merak ve keşif
    "curiosity": [
        "Merak ettiğiniz bir konuyu 15 dakika araştırın ve öğrendiklerinizi 3 maddeyle özetleyin.",
        "Bugün yeni bir ‘neden?’ sorusu yazın ve izi sürün.",
    ],
    "wonder": [
        "Doğada 10 dakika geçirin ve dikkatinizi detaylara verin.",
        "Gökyüzünü 3 dakika izleyin ve zihninizi sakinleştirin.",
    ],
    "creativity": [
        "Yeni bir fikir yazın veya 10 dakikalık bir çizim deneyin.",
        "Yapılacaklar listenizde yaratıcı bir maddeye 15 dakika ayırın.",
    ],
    "motivation": [
        "Kendiniz için küçük bir ödül belirleyin ve ilk hedefinize başlayın.",
        "Günün ilk 10 dakikasını en önemli işe ayırın.",
    ],

    # Karmaşık ve yoğun duygular
    "nostalgia": [
        "Geçmişte sizi mutlu eden bir fotoğrafa bakın ve hatıralarınızı yazın.",
        "Eski bir dostla iletişime geçin ve güzel bir anıyı paylaşın.",
    ],
    "regret": [
        "Pişmanlık duyduğunuz bir konuyu yazın ve bundan çıkardığınız 1 ders ekleyin.",
        "Gelecekte benzer durumda atacağınız yapıcı adımı planlayın.",
    ],
    "confusion": [
        "Düşüncelerinizi yazılı olarak düzenleyin ve önceliklerinizi belirleyin.",
        "Karar için artı-eksi listesi yapın; ilk küçük adımı seçin.",
    ],
    "anticipation": [
        "Yakında olacak güzel bir etkinliği planlayın ve heyecanınızı artırın.",
        "Beklentiyi dengeleyin: ‘kontrol edebildiklerim / edemediklerim’ listesi.",
    ],
    "relief": [
        "Derin bir nefes alın ve şu an güvende olduğunuzu fark edin.",
        "Vücudunuzda rahatlama hissettiğiniz 3 noktayı fark edin.",
    ],
    "vulnerability": [
        "Güvendiğiniz bir kişiyle açıkça konuşun ve hislerinizi paylaşın.",
        "Duygularınızı yargısızca adlandırın ve kabul edin.",
    ],
    "burnout": [
        "Bugün mutlaka 1 saatlik bir dinlenme molası planlayın ve işten uzak durun.",
        "Yükü azaltmak için devredeceğiniz 1 görevi seçin.",
    ],
}

# İsteğe bağlı eşanlam/alias haritası (örn. angry->anger)
ALIASES: Dict[str, str] = {
    "angry": "anger",
    "sad": "sadness",
    "happy": "joy",
}

CATEGORIES: Dict[str, str] = {
    # Temel
    "joy": "basic",
    "sadness": "basic",
    "anger": "basic",
    "fear": "basic",
    "love": "basic",
    "surprise": "basic",
    "neutral": "basic",
    # Diğerleri
    "optimism": "positive",
    "admiration": "positive",
    "gratitude": "positive",
    "confidence": "positive",
    "hope": "positive",
    "pride": "positive",
    "excitement": "positive",
    "serenity": "positive",
    "contentment": "positive",
    "inspiration": "positive",
    "disgust": "negative",
    "shame": "negative",
    "guilt": "negative",
    "envy": "negative",
    "loneliness": "negative",
    "resentment": "negative",
    "frustration": "negative",
    "overwhelm": "negative",
    "anxiety": "negative",
    "stress": "negative",
    "insecurity": "negative",
    "jealousy": "negative",
    "boredom": "negative",
    "trust": "social",
    "compassion": "social",
    "empathy": "social",
    "connection": "social",
    "forgiveness": "social",
    "belonging": "social",
    "respect": "social",
    "curiosity": "explore",
    "wonder": "explore",
    "creativity": "explore",
    "motivation": "explore",
    "nostalgia": "complex",
    "regret": "complex",
    "confusion": "complex",
    "anticipation": "complex",
    "relief": "complex",
    "vulnerability": "complex",
    "burnout": "complex",
}


async def ensure_indexes():
    db = get_db()
    col = db["suggestions"]
    # emotion alanında unique index
    await col.create_index("emotion", unique=True)


def normalize_emotion(label: str) -> str:
    l = label.strip().lower()
    return ALIASES.get(l, l)


async def seed(append: bool = True, include_aliases: bool = False) -> Dict[str, int]:
    await ensure_indexes()
    col = suggestions_collection()
    inserted = 0
    updated = 0

    async def upsert_one(emotion: str, variants: List[str]):
        nonlocal inserted, updated
        emo = normalize_emotion(emotion)
        doc = await col.find_one({"emotion": emo})
        now = datetime.utcnow()
        payload = {
            "emotion": emo,
            "suggestion_texts": variants,
            "category": CATEGORIES.get(emo, "other"),
            "language": "tr",
            "updated_at": now,
        }
        if doc:
            if append:
                # Birleştir, tekrarları çıkar
                existing = list(dict.fromkeys((doc.get("suggestion_texts") or []) + variants))
                await col.update_one({"emotion": emo}, {"$set": {**payload, "suggestion_texts": existing}})
            else:
                await col.update_one({"emotion": emo}, {"$set": payload})
            updated += 1
        else:
            payload["created_at"] = now
            await col.insert_one(payload)
            inserted += 1

    # Asıl etiketler
    for emotion, texts in SUGGESTIONS.items():
        await upsert_one(emotion, texts)

    # Alias’lar (opsiyonel): angry -> anger kaydı da yazılsın istenirse
    if include_aliases:
        for alias, target in ALIASES.items():
            await upsert_one(alias, SUGGESTIONS.get(target, []))

    return {"inserted": inserted, "updated": updated}


async def purge():
    col = suggestions_collection()
    res = await col.delete_many({})
    return res.deleted_count


async def list_items(limit: int = 20):
    col = suggestions_collection()
    cur = col.find({}).sort("emotion", 1).limit(limit)
    out = []
    async for d in cur:
        out.append({
            "emotion": d.get("emotion"),
            "n": len(d.get("suggestion_texts") or []),
            "category": d.get("category"),
            "language": d.get("language"),
        })
    return out


async def main():
    parser = argparse.ArgumentParser(description="Seed suggestions collection")
    parser.add_argument("action", choices=["seed", "purge", "list"], help="Action to perform")
    parser.add_argument("--replace", action="store_true", help="Replace existing suggestions instead of appending")
    parser.add_argument("--aliases", action="store_true", help="Also seed alias keys (angry->anger vb.)")
    parser.add_argument("--limit", type=int, default=50, help="List limit")
    args = parser.parse_args()

    await connect_to_mongo()

    if args.action == "purge":
        n = await purge()
        print(f"Purged {n} documents from suggestions")
    elif args.action == "list":
        items = await list_items(limit=args.limit)
        for it in items:
            print(it)
    else:
        stats = await seed(append=not args.replace, include_aliases=args.aliases)
        print(f"Seed done. Inserted={stats['inserted']} Updated={stats['updated']}")

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
