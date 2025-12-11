# Railway Deploy Yönergeleri

## Proje Özellikleri

Bu proje iki ana özellik sunar:

### 1. Barkod & Etiket Oluşturucu
- Ürün bilgilerini girerek barkod oluşturma
- Logo yükleme desteği
- Profesyonel PDF etiket çıktısı

### 2. Dijital Evrak & Rapor Oluşturucu
- Kurumsal belgeler oluşturma
- Logo ve imza yükleme desteği
- Profesyonel PDF rapor çıktısı

## Railway Deploy Adımları

### 1. Railway Hesabı Oluşturun
- [Railway](https://railway.app) adresine gidin
- GitHub hesabınızla kaydolun

### 2. Proje Yükleyin
```bash
# Yerel proje klasörünüzde
git init
git add .
git commit -m "Initial commit"

# GitHub'a yükleyin (önce GitHub'da repo oluşturun)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 3. Railway'de Deploy Edin
1. Railway dashboard'a gidin
2. "New Project" → "Deploy from GitHub" seçin
3. Projenizi seçin
4. Deploy işlemi otomatik başlayacak

### 4. Ortam Değişkenleri (Opsiyonel)
Railway ortam değişkenleri eklemenize gerek yok, proje zaten Railway'in sağladığı PORT değişkenini kullanıyor.

### 5. Siteyi Görüntüleyin
Deploy tamamlandıktan sonra Railway size bir URL sağlayacak. Bu URL üzerinden projenize erişebilirsiniz.

## Proje Yapısı

```
├── app.py                 # Ana Flask uygulaması
├── requirements.txt       # Python bağımlılıkları
├── runtime.txt           # Python versiyonu
├── Procfile              # Railway deploy komutu
├── templates/            # HTML şablonları
│   ├── index.html       # Ana sayfa
│   ├── barcode_generator.html  # Barkod oluşturucu
│   └── document_generator.html # Evrak oluşturucu
├── static/              # Statik dosyalar
│   └── css/
│       └── style.css    # Ana CSS dosyası
├── uploads/             # Geçici dosya yükleme klasörü
└── RAILWAY_DEPLOY.md    # Bu dosya
```

## Kullanılan Teknolojiler

- **Flask**: Python web framework
- **python-barcode**: Barkod oluşturma
- **Pillow**: Resim işleme
- **reportlab**: PDF oluşturma
- **Werkzeug**: Dosya yükleme güvenliği

## Özellikler

- ✅ Modern ve responsive tasarım
- ✅ Dosya yükleme (Logo, İmza)
- ✅ Otomatik barkod oluşturma
- ✅ Profesyonel PDF çıktısı
- ✅ 5MB dosya yükleme limiti
- ✅ Geçici dosya temizleme
- ✅ Railway deploy hazır

## Sorun Giderme

### Eğer deploy sırasında hata alırsanız:
1. `requirements.txt` dosyasının eksiksiz olduğundan emin olun
2. `runtime.txt` dosyasının Python versiyonunu belirttiğinden emin olun
3. `Procfile` dosyasının doğru formatta olduğundan emin olun

### Uygulama çalışmazsa:
1. Railway dashboard'dan logs sekmesini kontrol edin
2. Ortam değişkenlerinin doğru ayarlandığından emin olun
3. Port ayarlarını kontrol edin (app.py'de PORT değişkeni kullanılıyor)

## Destek

Herhangi bir sorunuz veya sorununuz varsa, Railway dashboard'undan logs sekmesini kontrol edin veya proje dosyalarını inceleyin.