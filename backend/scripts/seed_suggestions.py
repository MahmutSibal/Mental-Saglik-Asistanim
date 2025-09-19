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
        "Bugünün en güzel anını yazın ve neden önemli olduğunu 2 cümleyle açıklayın.",
        "Kendinize küçük bir armağan verin: 10 dakikalık favori aktivitenize zaman ayırın.",
    ],
    "sadness": [
        "Hafif bir egzersiz yapın, sevdiğiniz bir şarkıyı dinleyin ve duygularınızı bir günlükte ifade edin.",
        "Nazik bir öz-şefkat pratiği yapın: kendinize iyi davranan 3 cümle yazın.",
        "Güvendiğiniz biriyle 10 dakikalık bir sohbet planlayın.",
        "Duygunuzu isimlendirin ve bedendeki yerini fark edin; 2 dakika nefese odaklanın.",
    ],
    "anger": [
        "10 derin nefes alın, kısa bir yürüyüş yapın ve düşüncelerinizi yeniden çerçevelemeyi deneyin.",
        "Öfkeyi güvenli bir yere yönlendirin: 5 dakikalık serbest yazım, sonra kağıdı sakince kapatın.",
        "Vücuttaki gerginliği atmak için 30 saniyelik hızlı sallanma/gerinme yapın.",
        "Öfkenin ihtiyacını sorun: korunma mı, sınır mı? 1 net adım belirleyin.",
    ],
        # Belirsiz
        "uncertain": [
            "Duygunuzu adlandırmak zor olabilir. 3 nefes alın ve ‘Şu an bedende ne hissediyorum?’ sorusunu yazın.",
            "Duygunuza bir ad veremiyorsanız sorun değil. Kısa bir yürüyüş yapın, sonra 3 kelimeyle özetlemeyi deneyin.",
            "Bir dakika durun, not alın: Ne oldu? Ne hissediyorum? Ne istiyorum? Küçük bir adım seçin.",
        ],
    "fear": [
        "Nefese odaklı 4-7-8 tekniğini deneyin ve kaygılarınızı küçük adımlara bölün.",
        "Korkunuzu 3 parçaya ayırın ve her biri için 1 küçük adım planlayın.",
        "Bir güven cümlesi seçin: ‘Şu anda güvendeyim’ ve 10 kez tekrarlayın.",
        "En kötü senaryoyu yazın, sonra olası ve yönetilebilir senaryoyu belirleyin.",
    ],
    "love": [
        "Sevdiğiniz kişiye takdir mesajı gönderin veya küçük bir jest yapın.",
        "Kendinize sevgi dolu bir not yazın: bugün neyi iyi yaptınız?",
        "Başkası için küçük bir iyilik yapın ve hissi gözlemleyin.",
        "Yakınınızla 10 dakikalık kaliteli sohbet planlayın.",
    ],
    "surprise": [
        "Beklenmedik durumu fırsata çevirin: ne öğrendiniz, üç cümlede yazın.",
        "Hoş sürprizi paylaşın veya küçük bir anı defterinize not edin.",
        "Şaşkınlık hissini meraka dönüştürün: ‘Bundan ne öğrenebilirim?’",
    ],
    "neutral": [
        "Gün içinde 5 dakikalık mindful mola verin ve vücut taraması yapın.",
        "Bugün için tek bir küçük hedef seçin ve bitirince kendinizi tebrik edin.",
        "Nötr enerjiyle basit bir işi bitirin (evi toplama, kısa dosyalama).",
    ],

    # Pozitif duygular
    "optimism": [
        "Bugün için ulaşılabilir tek bir hedef belirleyin ve tamamlayınca kendinizi ödüllendirin.",
        "Olumlu bir iç konuşma cümlesi seçin ve gün içinde 3 kez tekrarlayın.",
        "Yarın için umut veren 1 küçük plan yazın.",
    ],
    "admiration": [
        "İlham aldığınız kişiden bir öğretiyi bugün uygulayın ve küçük bir ilerleme kaydedin.",
        "Hayran olduğunuz özelliği kendinizde güçlendirmek için 1 adım belirleyin.",
        "Rol modelinizin bir röportajını izleyin ve 1 içgörü çıkarın.",
    ],
    "gratitude": [
        "Bugün teşekkür etmek istediğiniz bir kişiyi arayın veya mesaj atın.",
        "Minnettar olduğunuz 3 şeyi yazın ve birini paylaşın.",
        "Günün ‘küçük iyi an’ fotoğrafını çekin ve adlandırın.",
    ],
    "confidence": [
        "Başarılarınızı yazın ve kendinizle gurur duymak için 5 dakika ayırın.",
        "Kendinize güven veren bir anınızı hatırlayın ve detaylarını yazın.",
        "Bugün ‘yapabilirim’ dediğiniz 1 iş için ilk adımı atın.",
    ],
    "hope": [
        "Gelecek için umut dolu bir hayali defterinize yazın ve küçük bir adım atın.",
        "Umudu besleyen bir sembol seçin (resim, müzik) ve bugün kullanın.",
        "Umutlu olduğunuz 3 şeyi yazın; biri için mikro adım planlayın.",
    ],
    "pride": [
        "Bugün gurur duyduğunuz bir anınızı yazın ve kendinizi ödüllendirin.",
        "Emeğinizin değerini görün: katkı sağladığınız 2 şeyi yazın.",
        "Bir başarıyı sade bir kutlamayla onurlandırın (teşekkür, anı).",
    ],
    "excitement": [
        "Bugün için sizi mutlu edecek küçük bir etkinlik planlayın.",
        "Heyecanınızı paylaşın: yakınınızla planınızı konuşun.",
        "Enerjinizi kanalize edin: 10 dakikalık yaratıcı bir mini sprint yapın.",
    ],
    "serenity": [
        "10 dakika meditasyon yapın ve huzurlu bir müzik açın.",
        "Yavaş bir yürüyüş yapın; adımlarınızı ve nefesinizi eşleştirin.",
        "Uyku hijyeninizi güçlendirin: ekranı 30 dk erken bırakın.",
    ],
    "contentment": [
        "Kendinize bir fincan çay veya kahve hazırlayıp keyifli bir mola verin.",
        "Bugünün küçük güzel anını fotoğraflayın veya yazın.",
        "‘Yeterince iyi’ listesi yapın ve tamamlananları işaretleyin.",
    ],
    "inspiration": [
        "Motivasyon verici bir podcast veya video izleyin ve öğrendiklerinizi yazın.",
        "Yaratıcı bir fikir yakalayın ve 10 dakikada kaba bir taslak çıkarın.",
        "İlham panonuza (moodboard) 1 görsel ekleyin.",
    ],

    # Negatif duygular
    "disgust": [
        "Temas etmekten kaçındığınız şeyi yazın ve bunun yerine size iyi hissettiren temiz bir alan oluşturun.",
        "Duyguyu fark edin, yargılamadan adlandırın ve kısa bir mola verin.",
        "Kendinizi güvenli ve temiz hissettiren bir küçük düzenleme yapın.",
    ],
    "shame": [
        "Hatalarınızı bir arkadaşınızla paylaşın, destek alın ve dersleri yazın.",
        "Kendinize şefkatle yaklaşın: herkes hata yapar; düzeltici 1 adım seçin.",
        "‘Büyüme zihniyeti’ ile yeniden çerçeveleyin: bugün ne öğrendim?",
    ],
    "guilt": [
        "Suçluluk hissettiğiniz konuda küçük bir düzeltici adım atın.",
        "Gerekiyorsa özür mesajı yazın ve daha iyi bir yaklaşım belirleyin.",
        "Değerlerinizi yazın ve davranışınızı onlarla hizalamak için 1 adım seçin.",
    ],
    "envy": [
        "Kıskandığınız kişinin özelliklerini ilham kaynağı olarak yazın ve kendi planınızı yapın.",
        "Kendinizde geliştirmek istediğiniz 1 beceriyi seçin ve ilk adımı atın.",
        "Karşılaştırma tuzağını azaltın: bugün kendinizle kıyas yapın.",
    ],
    "loneliness": [
        "Bir arkadaşınıza mesaj atın veya çevrim içi bir toplulukta sohbet edin.",
        "Kısa bir görüntülü arama planlayın veya bir yürüyüşe davet edin.",
        "Topluluk etkinliği takvimine göz atın ve 1 katılım planlayın.",
    ],
    "resentment": [
        "Duygularınızı yazın ve kendinize nazik bir dil kullanarak ifade edin.",
        "Sınır koymanız gerekiyorsa, net ve saygılı bir cümle planlayın.",
        "Gerekiyorsa mola verin; sonra ‘ben dili’yle konuşmayı prova edin.",
    ],
    "frustration": [
        "Beyninizdeki baskıyı azaltmak için kısa bir mola verin ve nefes egzersizi yapın.",
        "Görevi parçalara ayırın; 10 dakikalık tek odak zamanı başlatın.",
        "Engeli yazın ve tek bir çözüm denemesi belirleyin (1 deney).",
    ],
    "overwhelm": [
        "Görevlerinizi küçük parçalara bölün ve bir tanesini hemen yapın.",
        "Yüksek beklentiyi yeniden çerçeveleyin: ‘Yeterince iyi’yi tanımlayın.",
        "Zihinsel yükü boşaltın: 5 dakikalık beyin boşaltma listesi yapın.",
    ],
    "anxiety": [
        "5 dakika nefes egzersizi yapın ve kaygınızı 1-10 arasında puanlayıp değişimi not edin.",
        "Endişe düşüncesine ‘dur’ deyin ve dikkati duyulara getirin (5-4-3-2-1).",
        "Zihinsel çiğneme yerine hareket: 2 dakikalık tempolu yürüyüş yapın.",
        "Korku yerine değer: ‘Benim için önemli olan ne?’yi yazın.",
    ],
    "stress": [
        "Boyun ve omuzlarınıza masaj yapın veya esneme hareketleri yapın.",
        "Pomodoro tekniğiyle 25 dakika odaklanın, 5 dakika dinlenin.",
        "Günlük stres kaynağını yazın ve 1 azaltıcı mikro adım belirleyin.",
    ],
    "insecurity": [
        "Kendiniz hakkında sevdiğiniz 3 özelliği yazın.",
        "‘Ben yeterliyim’ onay cümlesini gün içinde tekrarlayın.",
        "Korktuğunuz alanda 1 küçük pratik yapın (düşük riskli ortam).",
    ],
    "jealousy": [
        "Kıskançlık hislerinizi yazın ve bunları geliştirmek için ilham alın.",
        "Kendinize adil hedefler koyun ve küçük bir ilerleme kaydedin.",
        "İlişkide ihtiyacınızı netleştirip nazikçe ifade edin.",
    ],
    "boredom": [
        "Yeni bir hobi hakkında 10 dakikalık araştırma yapın ve ilk adımı atın.",
        "Kısa bir tempolu yürüyüş yapın ve dönüşte yeni bir fikir yazın.",
        "Rutin kırıcı 10 dakikalık ‘deneysel’ görev seçin.",
    ],

    # Sosyal/ilişkisel duygular
    "trust": [
        "Yakın bir arkadaşınıza güveninizi belirten bir mesaj gönderin.",
        "Birine küçük bir sorumluluk verin ve süreci birlikte değerlendirin.",
        "Güven sözleşmesi yapın: beklenti ve sınırları 3 maddeyle yazın.",
    ],
    "compassion": [
        "Bugün birine yardım edin veya küçük bir iyilik yapın.",
        "Kendinize de şefkat gösterin: dinlenme molası verin.",
        "Şefkatli nefes: ‘İçeri şefkat, dışarı gerilim’ 10 tekrar.",
    ],
    "empathy": [
        "Yakınınızın yaşadığı bir olayı dinleyin ve ona destek olun.",
        "‘Seni duyuyorum’ cümlesini kurun ve yargısız dinleyin.",
        "Yansıtıcı dinleme: duyduğunuzu özetleyin ve doğrulayın.",
    ],
    "connection": [
        "Ailenizle birlikte keyifli bir etkinlik planlayın.",
        "Uzun zamandır görüşmediğiniz biriyle iletişime geçin.",
        "Varlıkla bağ kurun: biriyle 5 dakika göz teması kurun ve dinleyin.",
    ],
    "forgiveness": [
        "Küçük bir kırgınlığı affetmek için kendinize izin verin.",
        "Affetmenin sizin için anlamını yazın ve küçük bir adım planlayın.",
        "Öfke döngüsünü bırakma egzersizi: 3 derin nefes, 1 nazik cümle.",
    ],
    "belonging": [
        "İlgilendiğiniz bir toplulukla iletişime geçin veya bir etkinliğe katılın.",
        "Toplulukta katkı sunabileceğiniz küçük bir rol belirleyin.",
        "Aidiyetinizi besleyen 3 ortamı yazın; birinde 10 dk geçirin.",
    ],
    "respect": [
        "Saygı duyduğunuz biri için takdir dolu bir mesaj yazın.",
        "Kendi sınırlarınıza saygı gösteren bir davranış seçin ve uygulayın.",
        "Sınır ifadenizi ‘ben dili’yle, kısa ve net yazın ve prova edin.",
    ],

    # Merak ve keşif
    "curiosity": [
        "Merak ettiğiniz bir konuyu 15 dakika araştırın ve öğrendiklerinizi 3 maddeyle özetleyin.",
        "Bugün yeni bir ‘neden?’ sorusu yazın ve izi sürün.",
        "Bir uzman videoyu 5 dk izleyin ve 1 uygulama deneyin.",
    ],
    "wonder": [
        "Doğada 10 dakika geçirin ve dikkatinizi detaylara verin.",
        "Gökyüzünü 3 dakika izleyin ve zihninizi sakinleştirin.",
        "Gün batımını farkındalıkla izleyin ve hissi 1 kelimeyle adlandırın.",
    ],
    "creativity": [
        "Yeni bir fikir yazın veya 10 dakikalık bir çizim deneyin.",
        "Yapılacaklar listenizde yaratıcı bir maddeye 15 dakika ayırın.",
        "Kısıtlı kaynakla yaratım: 2 malzemeyle mini üretim yapın.",
    ],
    "motivation": [
        "Kendiniz için küçük bir ödül belirleyin ve ilk hedefinize başlayın.",
        "Günün ilk 10 dakikasını en önemli işe ayırın.",
        "2 dakikalık kural: başlamak için sadece 2 dakika ayırın.",
    ],

    # Karmaşık ve yoğun duygular
    "nostalgia": [
        "Geçmişte sizi mutlu eden bir fotoğrafa bakın ve hatıralarınızı yazın.",
        "Eski bir dostla iletişime geçin ve güzel bir anıyı paylaşın.",
        "Çocukluk kokusunu çağrıştıran bir şey bulun ve anıyı yazın.",
    ],
    "regret": [
        "Pişmanlık duyduğunuz bir konuyu yazın ve bundan çıkardığınız 1 ders ekleyin.",
        "Gelecekte benzer durumda atacağınız yapıcı adımı planlayın.",
        "Kendinize affedici bir cümle yazın ve ilerleme odağı seçin.",
    ],
    "confusion": [
        "Düşüncelerinizi yazılı olarak düzenleyin ve önceliklerinizi belirleyin.",
        "Karar için artı-eksi listesi yapın; ilk küçük adımı seçin.",
        "Bir arkadaşınıza durumu anlatın; 5 dakikada yansıtıcı geri bildirim alın.",
    ],
    "anticipation": [
        "Yakında olacak güzel bir etkinliği planlayın ve heyecanınızı artırın.",
        "Beklentiyi dengeleyin: ‘kontrol edebildiklerim / edemediklerim’ listesi.",
        "Takvime minik bir geri sayım oluşturun ve paylaşın.",
    ],
    "relief": [
        "Derin bir nefes alın ve şu an güvende olduğunuzu fark edin.",
        "Vücudunuzda rahatlama hissettiğiniz 3 noktayı fark edin.",
        "Omuzları gevşetin, çeneyi bırakın, 1 dakika yavaş nefes alın.",
    ],
    "vulnerability": [
        "Güvendiğiniz bir kişiyle açıkça konuşun ve hislerinizi paylaşın.",
        "Duygularınızı yargısızca adlandırın ve kabul edin.",
        "Küçük bir kırılganlık anı planlayın: bir ricada bulunun.",
    ],
    "burnout": [
        "Bugün mutlaka 1 saatlik bir dinlenme molası planlayın ve işten uzak durun.",
        "Yükü azaltmak için devredeceğiniz 1 görevi seçin.",
        "Enerji envanteri yapın: dolduran/boşaltan 3 şey yazın ve 1 değiştirin.",
    ],

    # Yeni kanonik duygular
    "embarrassment": [
        "Kırmızılaşma/utanma anını yargılamadan adlandırın ve 1 nazik cümle kurun.",
        "Durumdan bir öğrenim çıkarın ve kendinize şefkat gösterin.",
    ],
    "hurt": [
        "İhtiyacınızı tanımlayın ve ‘ben dili’yle ifade etmek için 1 cümle yazın.",
        "Kendinize yatıştırıcı bir bakım verin (sıcak duş, rahat müzik).",
    ],
    "disappointment": [
        "Beklenti ile gerçek arasını yazın ve bir esnek hedef belirleyin.",
        "Küçük bir teselli planlayın ve tekrar denemek için mikro adım seçin.",
    ],
    "grief": [
        "Yasınızı onurlandırın: kaybettiğiniz şey hakkında 5 dakika yazın.",
        "Duyguyu dalga gibi kabul edin; dayanma penceresi için nefes alın.",
    ],
    "apathy": [
        "Çok küçük bir eylem seçin (2 dakika) ve sadece başlayın.",
        "Duyularınızı uyaran bir şey ekleyin: koku, müzik, ışık.",
    ],
    "melancholy": [
        "Hüzünlü hissi nazikçe karşılayın; sevdiğiniz sakin bir müzik açın.",
        "Zihni rahatlatan yavaş bir yürüyüş yapın.",
    ],
    "despair": [
        "Güvenli birine ulaşın ve destek isteyin; yalnız kalmayın.",
        "Zor an kartı oluşturun: yardım hatları, destek kişiler, sakinleştiriciler.",
    ],
    "panic": [
        "4-4-4-4 kutu nefes tekniği: 4 say nefes al, tut, ver, bekle.",
        "Topraklama: 5 şey gör, 4 şey hisset, 3 şey duy, 2 şey kokla, 1 şey tat.",
    ],
    "impatience": [
        "Zaman algısını düzenleyin: geri sayım kurun ve tek işe odaklanın.",
        "Beklerken mikro görev yapın (mail yanıtı, masa düzenleme).",
    ],
    "annoyance": [
        "Tetikleyiciyi yazın ve önem derecesini 0-10 arası puanlayın.",
        "Mizah ekleyin: ufak bir esneme/şaka ile gerginliği yumuşatın.",
    ],
    "irritation": [
        "Duyusal yükü azaltın: ses/ışık/uyaranları kısın, kısa mola verin.",
        "İhtiyacı belirleyin: su, atıştırmalık, hava, hareket.",
    ],
    "homesickness": [
        "Evinizi hatırlatan bir yemek/müzik deneyin.",
        "Yakın biriyle görüntülü görüşün ve kısa bir plan yapın.",
    ],
}

# İsteğe bağlı eşanlam/alias haritası (örn. angry->anger)
ALIASES: Dict[str, str] = {
    "angry": "anger",
    "sad": "sadness",
    "happy": "joy",
    # English common
    "joyful": "joy",
    "happiness": "joy",
    "rage": "anger",
    "mad": "anger",
    "furious": "anger",
    "afraid": "fear",
    "scared": "fear",
    "worry": "anxiety",
    "worried": "anxiety",
    "panic attack": "panic",
    "calm": "serenity",
    "relaxed": "serenity",
    "satisfaction": "contentment",
    "fulfilled": "contentment",
    "energized": "excitement",
    "tense": "stress",
    "overwhelmed": "overwhelm",
    "burned out": "burnout",
    "embarrassed": "embarrassment",
    "hurt feelings": "hurt",
    "disappointed": "disappointment",
    "grieving": "grief",
    "hopeless": "despair",
    "apathetic": "apathy",
    "blue": "melancholy",
    "annoyed": "annoyance",
    "irritated": "irritation",
    "homesick": "homesickness",

    # Turkish common
    "mutlu": "joy",
    "mutluluk": "joy",
    "sevinç": "joy",
    "üzgün": "sadness",
    "üzüntü": "sadness",
    "keder": "sadness",
    "öfkeli": "anger",
    "öfke": "anger",
    "sinir": "anger",
    "korku": "fear",
    "korkmuş": "fear",
    "kaygı": "anxiety",
    "kaygili": "anxiety",
    "anksiyete": "anxiety",
    "endişe": "anxiety",
    "şaşkınlık": "surprise",
    "sevgi": "love",
    "aşk": "love",
    "nötr": "neutral",
    "iyimser": "optimism",
    "iyimserlik": "optimism",
    "hayranlık": "admiration",
    "minnettarlık": "gratitude",
    "şükür": "gratitude",
    "özgüven": "confidence",
    "kendine güven": "confidence",
    "umut": "hope",
    "umutlu": "hope",
    "gurur": "pride",
    "heyecan": "excitement",
    "coşku": "excitement",
    "huzur": "serenity",
    "dinginlik": "serenity",
    "sükunet": "serenity",
    "memnuniyet": "contentment",
    "tatmin": "contentment",
    "ilham": "inspiration",
    "esin": "inspiration",
    "iğrenme": "disgust",
    "tiksinti": "disgust",
    "utanç": "shame",
    "suçluluk": "guilt",
    "haset": "envy",
    "kıskançlık": "jealousy",
    "yalnızlık": "loneliness",
    "kin": "resentment",
    "hınç": "resentment",
    "hayal kırıklığı": "disappointment",
    "hayal kırıklığına uğramış": "disappointment",
    "bunalmış": "overwhelm",
    "stres": "stress",
    "stresli": "stress",
    "güvensizlik": "insecurity",
    "sıkılmış": "boredom",
    "sıkıntı": "boredom",
    "güven": "trust",
    "şefkat": "compassion",
    "merhamet": "compassion",
    "empati": "empathy",
    "bağ": "connection",
    "bağlantı": "connection",
    "aidiyet": "belonging",
    "saygı": "respect",
    "merak": "curiosity",
    "hayret": "wonder",
    "yaratıcılık": "creativity",
    "motivasyon": "motivation",
    "nostalji": "nostalgia",
    "pişmanlık": "regret",
    "kafa karışıklığı": "confusion",
    "kararsızlık": "confusion",
    "beklenti": "anticipation",
    "rahatlama": "relief",
    "kırılganlık": "vulnerability",
    "tükenmişlik": "burnout",
    "utanma": "embarrassment",
    "incinmiş": "hurt",
    "yas": "grief",
    "kederli": "melancholy",
    "umutsuz": "despair",
    "panik": "panic",
    "sabırsızlık": "impatience",
    "rahatsızlık": "annoyance",
    "tahriş": "irritation",
    "eve özlem": "homesickness",
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
        # Slang / variants
        "cok mutluyum": "joy",
        "coook uzgunum": "sadness",
        "yikildim": "sadness",
        "kahroldum": "sadness",
        "bayagi sinirliyim": "anger",
        "sinirim tepemde": "anger",
        "kafam karisik": "confusion",
        "bunaldi m": "overwhelm",
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
    # Yeni kanonikler
    "embarrassment": "negative",
    "hurt": "negative",
    "disappointment": "negative",
    "grief": "complex",
    "apathy": "negative",
    "melancholy": "complex",
    "despair": "complex",
    "panic": "negative",
    "impatience": "negative",
    "annoyance": "negative",
    "irritation": "negative",
    "homesickness": "complex",
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
        "uncertain": "other",
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
