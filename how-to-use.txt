# Discord Botu Kurulum ve Kullanım Kılavuzu

## Giriş
Bu kılavuz, Discord botunun nasıl kurulacağını ve kullanılacağını adım adım açıklamaktadır. Lütfen adımları dikkatlice takip edin.

## Gereksinimler
- Python 3.8 veya üstü
- İnternet bağlantısı

## 1. Python Yükleme
1. Python'u indirmek için şu adrese gidin: https://www.python.org/downloads/
2. Python'u yüklerken "Add Python to PATH" seçeneğini işaretlemeyi unutmayın.
3. Yükleme tamamlandıktan sonra, Komut İstemi'ni (`cmd`) açarak Python'un kurulu olup olmadığını kontrol edin:
   ```
   python --version
   ```
   Bu komut, yüklü Python sürümünü göstermelidir.

## 2. Proje Dosyalarını İndirme
1. Bu proje klasörünü bilgisayarınıza indirin veya kopyalayın.
2. İndirilen veya kopyalanan klasörü, masaüstüne veya istediğiniz bir dizine yerleştirin.

## 3. Gerekli Python Paketlerini Kurma
1. Komut İstemi'ni (`cmd`) açın.
2. Komut İstemi'nde proje klasörünün bulunduğu dizine gidin:
   ```
   cd masaüstü\discord_bot
   ```
   (Not: "discord_bot" dizin adını, projenizin bulunduğu dizin adıyla değiştirin.)
3. Gerekli paketleri kurmak için aşağıdaki komutu çalıştırın:
   ```
   pip install -r requirements.txt
   ```
   Bu komut, projede kullanılan tüm Python paketlerini otomatik olarak kuracaktır.

## 4. .env Dosyasını Düzenleme
1. Proje klasörünün içinde bulunan `.env` dosyasını bir metin editörü (örneğin Not Defteri) ile açın.
2. Aşağıdaki satırı bulun ve kendi bot tokeninizi buraya yapıştırın:
   ```
   DISCORD_BOT_TOKEN=your-bot-token-here
   ```
3. Dosyayı kaydedin ve kapatın.

## 5. Discord Developer Portal Ayarları
1. Discord Developer Portal'da bir bot uygulaması oluştururken, Bot kısmına gidin ve aşağıdaki izinleri aktif edin:
   - **Public Bot**
   - **Presence Intent**
   - **Server Members Intent**
   - **Message Content Intent**

2. Botun davet linkini oluştururken aşağıdaki seçeneklerin işaretli olduğundan emin olun:
   - **applications.commands**
   - **bot**
   - **admin**

## 6. Botu Başlatmak
1. Proje klasörünün içinde bulunan `start_bot.bat` dosyasına çift tıklayın.
2. Komut İstemi açılacak ve botunuz çalışmaya başlayacaktır.
3. Botun başarılı bir şekilde başlatıldığını görmek için, "Logged in as ..." mesajını göreceksiniz.

## 7. Bot Komutları
- `/play <url>`: Bir müzik veya oynatma listesini çalar.
- `/pause`: Çalan şarkıyı duraklatır.
- `/resume`: Duraklatılmış şarkıyı devam ettirir.
- `/skip`: Sıradaki şarkıyı atlar.
- `/queue`: Sıradaki şarkıları listeler.
- `/shuffle`: Sıradaki şarkıları karıştırır.
- `/loop`: Döngü modunu açar/kapatır.
- `/stop`: Müziği durdurur ve kanaldan ayrılır.
- `/nowplaying`: Şu anda çalan şarkıyı gösterir.
- `/previous`: Önceki şarkıyı çalar.
- `/commands`: Tüm komutları listeler.

## 8. Sorun Giderme
- **Python sürümü eskiyse**: Python'u güncelleyip tekrar deneyin.
- **Bot çalışmıyorsa**: `.env` dosyasındaki tokeni kontrol edin ve internet bağlantınızı doğrulayın.
- **FFmpeg hatası alıyorsanız**: FFmpeg'in doğru şekilde kurulu olduğundan emin olun.

## 9. İletişim
Herhangi bir sorunla karşılaşırsanız veya destek ihtiyacınız olursa, lütfen şu adresten benimle iletişime geçin:
discord: karabatik

Başarılar!
