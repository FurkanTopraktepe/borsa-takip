import yfinance as yf
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from datetime import datetime
import os

# --- AYARLAR ---
# Takip Listesi
semboller = ['XU100.IS', 'THYAO.IS', 'GARAN.IS', 'ASELS.IS', 'BTC-USD', 'ETH-USD']

# Hedef Fiyat Alarmı (Örnek: THY 300'ü geçerse haber ver)
hedefler = {
    'THYAO.IS': {'fiyat': 300.0, 'yon': 'ust'}, # 300'ün üstüne çıkarsa
    'BTC-USD': {'fiyat': 90000.0, 'yon': 'ust'}  # 90k doları geçerse
}

console = Console()

def mac_bildirim(baslik, mesaj):
    # Mac'in kendi bildirim sistemini kullanır
    os.system(f"""
              osascript -e 'display notification "{mesaj}" with title "{baslik}" sound name "Glass"'
              """)

def tablo_olustur():
    table = Table(title="🚀 VIBE FINANCE TERMINAL", box=box.ROUNDED, style="cyan")

    table.add_column("Sembol", style="white", no_wrap=True)
    table.add_column("Son Fiyat", justify="right")
    table.add_column("Değişim %", justify="right")
    table.add_column("Durum", justify="center")

    for sembol in semboller:
        try:
            ticker = yf.Ticker(sembol)
            # Hızlı veri için son 1 günü çekiyoruz
            data = ticker.history(period="1d", interval="1m")
            
            if data.empty:
                continue

            son_fiyat = data['Close'].iloc[-1]
            acilis = data['Open'].iloc[0]
            
            # Yüzde hesapla
            yuzde = ((son_fiyat - acilis) / acilis) * 100
            
            # Renk ve İkon Ayarı
            if yuzde > 0:
                renk = "green"
                ikon = "🔼"
            elif yuzde < 0:
                renk = "red"
                ikon = "🔽"
            else:
                renk = "yellow"
                ikon = "➖"

            # Para birimi (Crypto için dolar, BIST için TL)
            para_birimi = "$" if "USD" in sembol else "₺"
            
            # Tabloya satır ekle
            table.add_row(
                sembol.replace('.IS', ''), 
                f"{son_fiyat:.2f} {para_birimi}", 
                f"[{renk}]%{yuzde:.2f}[/{renk}]",
                ikon
            )

            # --- ALARM KONTROL ---
            if sembol in hedefler:
                hedef = hedefler[sembol]
                if hedef['yon'] == 'ust' and son_fiyat >= hedef['fiyat']:
                    mac_bildirim("HEDEF GELDİ! 💰", f"{sembol} hedefi vurdu: {son_fiyat}")
                    # Bildirimden sonra hedefi listeden sil (sürekli ötmesin)
                    del hedefler[sembol]

        except Exception:
            table.add_row(sembol, "Hata", "-", "⚠️")

    return table

# --- ANA DÖNGÜ ---
if __name__ == "__main__":
    console.clear()
    console.print(Panel.fit("[bold yellow]Finansal Takip Başlatılıyor...[/bold yellow]"))
    
    # Live özelliği ekranı titretmeden tabloyu günceller
    with Live(tablo_olustur(), refresh_per_second=1) as live:
        while True:
            live.update(tablo_olustur())
            time.sleep(5) # 5 saniyede bir verileri tazele
