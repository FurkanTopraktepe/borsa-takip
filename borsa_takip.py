import yfinance as yf
import time
import os
from colorama import Fore, Style, init
from datetime import datetime

# Renkleri başlat (Windows/Mac uyumu için)
init()

# Takip edilecek hisseler (Sonuna .IS eklemeyi unutma)
# XU100.IS -> BIST 100 Endeksi
hisseler = ['XU100.IS', 'THYAO.IS', 'GARAN.IS', 'ASELS.IS', 'EREGL.IS', 'SASA.IS']

def ekran_temizle():
    # Windows ise 'cls', Mac/Linux ise 'clear' çalıştırır
    os.system('cls' if os.name == 'nt' else 'clear')

def veri_getir():
    print(f"{Fore.CYAN}=== BIST CANLI TAKİP PANELİ (Vibe Coding Edition) ==={Style.RESET_ALL}")
    print(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 50)
    print(f"{'HİSSE':<10} {'FİYAT (TL)':<15} {'DEĞİŞİM (%)':<15}")
    print("-" * 50)

    try:
        # Verileri yfinance üzerinden çek
        for sembol in hisseler:
            ticker = yf.Ticker(sembol)
            # Son 1 günlük veriyi al (Hızlı çekim için)
            data = ticker.history(period="1d")
            
            if data.empty:
                print(f"{sembol:<10} Veri yok...")
                continue

            # Son kapanış fiyatı
            son_fiyat = data['Close'].iloc[-1]
            # Önceki gün kapanış (Değişimi hesaplamak için)
            # Not: yfinance bazen Open'ı baz alır, basit hesap için açılış-son kıyaslıyoruz
            acilis = data['Open'].iloc[-1] 
            
            degisim_yuzde = ((son_fiyat - acilis) / acilis) * 100
            
            # Renk Ayarı: Yükseliş Yeşil, Düşüş Kırmızı
            renk = Fore.GREEN if degisim_yuzde >= 0 else Fore.RED
            sembol_temiz = sembol.replace('.IS', '') # .IS yazısını sil temiz görünsün

            print(f"{renk}{sembol_temiz:<10} {son_fiyat:.2f} TL       %{degisim_yuzde:.2f}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Hata oluştu: {e}{Style.RESET_ALL}")

    print("-" * 50)
    print(f"{Fore.YELLOW}Veriler 15dk gecikmeli olabilir. Yenileniyor... (Ctrl+C ile çık){Style.RESET_ALL}")

# Sonsuz döngü (Programı sürekli çalıştırır)
if __name__ == "__main__":
    while True:
        ekran_temizle()
        veri_getir()
        time.sleep(10) # 10 saniyede bir yenile
