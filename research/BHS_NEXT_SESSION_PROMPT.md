# NEW CHAT — START HERE / Copy-paste prompt (Turkish)

**Bu dosyayı yeni ChatGPT sohbetine yükle veya aşağıdaki metni ilk mesaj olarak gönder.** İdeal yol: GitHub bağlantısını açmak için ilgili GitHub bağlantısını etkinleştir ve master ZIP'i de referans olarak ekle. Yeni sohbetin eski sohbetin her mesajını ve araç çıktılarını otomatik görmesi garanti değildir; bu yüzden dosya + immutable commit + doğrulanmış JSON kanıtı kullan.

---

Aşağıdaki **uzun süreli bağımsız bilimsel araştırma projemiz Bayesian Hypothesis Search (BHS)** için önceki çalışma bağlamını koruyarak doğrudan kaldığımız yerden devam et. Bu bir sıfırdan başlama isteği değildir.

**Ana repo:** https://github.com/busrakisik/inverse-materials-design  
**Branch:** `bhs-scientific-audit`  
**Son doğrulanmış SHA:** `c540a3dbc05f527e4a360deecb310bde68b2c47c` (5 Kasım 2026; güncel HEAD değişmiş olabilir).  
**Ana devir belgesi:** `research/BHS_MASTER_CONTEXT_2026-11-05.md`  
**Diğer zorunlu kayıtlar:** `research/BHS_PROJECT_HANDOFF.md`, `research/BHS_EVIDENCE_REGISTER.json`, `research/BHS_EXPERIMENTS_AND_DECISIONS_2026-11-05.md`, `research/BHS_EXTERNAL_VALIDATION_V5_RESEARCH_PLAN.md`, `research/BHS_V1_V4_AGGREGATED_RESULTS_SNAPSHOT.json` ve `research/verified_results/*.json`. Eğer henüz repoya yüklenmemişlerse, eklediğim BHS_FULL_CONTINUITY ZIP'inden oku.

**Misyon ve vizyon:** Hipotezleri açıkça temsil eden, Bayesçi kanıtlarla güncelleyen, faydalı sonraki bilimsel deneyleri seçen, güvenilmeyen tahmin durumunu tespit eden, sonuçları izlenebilir ve yeniden üretilebilir kılan AI-for-Science araştırma çerçevesi. İlk uygulama inverse materials design; amaç *yayınlanabilir gerçek bilimsel kanıt + gerçek laboratuvar/müşteri problemi + doğrulanabilir teknolojik üstünlük*. Aynı zamanda doktora ve araştırmacı portföyü. Ancak hiçbir üstünlük, fiziksel keşif, maliyet tasarrufu, ölçüm kalibrasyonu veya müşteri değeri henüz doğrulanmış değil. EGC ayrı ama ilişkili; tesis yeri bitirme tezi ayrı.

**En son doğrulanan teknik başarı:** NIST Fe–Co–Ni anonim koordinatlarında 921 uygun Kerr (mrad) örneğiyle v1–v4 karşılaştırmalı geliştirme deneyleri. v1 27/27 (`41977734103`), v2 28/28 (`41988359209`), v3 31/31 (`41992614426`), v4 36/36 (`42046318788`, artifact `13425230747`). v3 900 gözlem öncesi tahmin, v4 540 tanı skoru. v1/v2: mevcut BHS standart GP–EI karşısında ortalama regret'te zayıf; v3/v4: BHS posterior belirsizliği ciddi şekilde gereğinden dar, GP de düşük kapsama gösteriyor. V4'te rassal kampanyalarda hipotezler-arası varyans toplamın çok azı; uzak kompozisyonlarda tahmin hatası daha kötü. Tüm bunlar önceden görülmüş geliştirme verisi, **bağımsız bilimsel doğrulama değil**. Dört tam aggregate rapor ZIP'te mevcut, gerekirse GitHub Actions artifact'larını da kontrol et.

**Bilimsel korumalar:** NIST fiziksel Fe/Co/Ni sütun sırası, ölçüm belirsizliği, maliyet, yeniden dağıtım izinleri ve fiziksel mekanizma anlamı kesinleşmedi. Üç hipotez ailesi fenomenolojik matematiksel şekiller. `scored_validation_allowed=false`, `independent_holdout_used=false`, `physical_validation=false` kalsın; bağımsız holdout seed `10000..10099` aralığını kullanma, başlatma veya dolaylı olarak tüketme. Yeniden üretilmiş geliştirme testleri bağımsız üstünlük sağlamaz. Bilimsel olumsuz sonuçları saklama.

**Yapılacak ilk iş:** (1) GitHub'da güncel HEAD, önceki v4 çalışma sonucu ve artifact kanıtlarını doğrula. (2) Master devir belgesini tam oku; teknik/stratejik misyonu ve kararları koru. (3) Sonraki nitelikli adım: **v5 dış bilimsel doğrulama için gerçek anlamda bağımsız bir soru ve izinli yeni veri/lab işbirliği** seç; hipotez ayrımı ile Kerr-property optimizasyonunu karıştırma. Aynı NIST verisini sonradan aşırı ayarlama. Dikkatli, bağımsız teyit edilen yeni araştırma bulguları varsa gerçek bir karar tablosu ve gerekirse testli kod oluştur. Kullanıcı 'devam' dediğinde yalnız fikir sıralama; yapılabilir bir bilimsel iş üret. (4) Kod geliştirirsen scripts+tests+research raporu+`.github/workflows/*.yml` içeren gerçek ZIP hazırla; `.yml` dosyasını **ayrı ver ve gerekirse kodu kopyalanabilir biçimde göster**. Kullanıcı yüklediğinde GitHub CI ve artifact'ını doğrudan incele. (5) Her başarılı aşamadan sonra master handoff ve kanıt kaydını kalıcı güncelle.

**Çalışma dili:** Türkçe. Eski konuyu tekrar tekrar sorma. Sonuçları özenli, ölçülü ve açık anlat. Bu proje sürekliliği kullanıcı için kritik; hiçbir doğrulanmış sonucu planlanmış sonuçla karıştırma.

---

**Not:** Repo'ya bu yeni belgeler henüz yüklenmemişse ilk adım, aynı paket içindeki `research/` dosyalarını `bhs-scientific-audit` dalına eklemek; artık gelecek sohbetlerde bu dosyaları GitHub kaynağı olarak kullan.
