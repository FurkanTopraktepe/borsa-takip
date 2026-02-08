import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Trader Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STİL (CSS) ---
# Biraz makyaj yapalım (Tablo başlıkları ve renkler)
st.markdown("""
<style>
    .stMetric {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    div[data-testid="stSidebar"] {
        background-color: #111;
    }
</style>
""", unsafe_allow_html=True)

# --- YAN MENÜ (SIDEBAR) ---
st.sidebar.title("🚀 VIBE TRADER")
st.sidebar.caption("By Vibe Coder")

# Kullanıcıdan hisse listesi al
varsayilanlar = "BTC-USD, ETH-USD, XU100.IS, THYAO.IS, GARAN.IS, ASELS.IS, TUPRS.IS"
sembol_girdisi = st.sidebar.text_area("Takip Listesi (Virgül ile ayır):", value=varsayilanlar, height=100)
sembol_listesi = [s.strip() for s in sembol_girdisi.split(',')]

# Hangi hissenin grafiğini çizelim?
secilen_hisse = st.sidebar.selectbox("Grafiğini Çiz:", sembol_listesi)

# Zaman aralığı seçimi
periyot = st.sidebar.select_slider("Zaman Aralığı", options=["1d", "5d", "1mo", "3mo", "1y"], value="1mo")
aralik = "1h" if periyot in ["1mo", "3mo"] else ("1d" if periyot == "1y" else "15m")

st.sidebar.divider()
auto_refresh = st.sidebar.checkbox("🔴 Canlı Veri Akışı", value=False)

# --- ANA FONKSİYONLAR ---

def grafik_ciz(symbol, period, interval):
    """Seçilen hissenin mum grafiğini çizer"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            st.error("Veri alınamadı!")
            return None

        # Hareketli Ortalama (Trendi görmek için)
        df['SMA20'] = df['Close'].rolling(window=20).mean()

        fig = go.Figure()

        # Mum Çubukları (Candlestick)
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            name='Fiyat'
        ))

        # Hareketli Ortalama Çizgisi
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA20'], 
            line=dict(color='orange', width=1), 
            name='20 Günlük Ort.'
        ))

        fig.update_layout(
            title=f"{symbol} - Teknik Analiz",
            yaxis_title=f"Fiyat ({'USD' if 'USD' in symbol else 'TL'})",
            template="plotly_dark",
            height=500,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig, df.iloc[-1] # Grafigi ve son veriyi döndür

    except Exception as e:
        st.error(f"Grafik hatası: {e}")
        return None, None

# --- ANA EKRAN DÜZENİ ---

# 1. Üst Kısım: Seçilen Hissenin Detayı
st.title(f"📊 {secilen_hisse} Analizi")

col1, col2 = st.columns([3, 1])

with col1:
    fig, son_veri = grafik_ciz(secilen_hisse, periyot, aralik)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if son_veri is not None:
        st.subheader("Son Durum")
        
        fiyat = son_veri['Close']
        acilis = son_veri['Open']
        degisim = fiyat - acilis
        yuzde = (degisim / acilis) * 100
        renk = "normal" if yuzde == 0 else ("inverse" if yuzde > 0 else "off")
        
        st.metric(label="Anlık Fiyat", value=f"{fiyat:.2f}", delta=f"{yuzde:.2f}%")
        st.metric(label="Günün En Yükseği", value=f"{son_veri['High']:.2f}")
        st.metric(label="Günün En Düşüğü", value=f"{son_veri['Low']:.2f}")
        st.metric(label="Hacim", value=f"{son_veri['Volume']:,}")

# 2. Alt Kısım: Hızlı Piyasa Bakışı (Tüm Liste)
st.divider()
st.subheader("📋 Piyasa Genel Bakış")

# Burası sürekli güncellenecek alan
placeholder = st.empty()

def tabloyu_guncelle():
    veriler = []
    for s in sembol_listesi:
        try:
            t = yf.Ticker(s)
            h = t.history(period="1d", interval="1m") # Son 1 dakika
            if not h.empty:
                last = h['Close'].iloc[-1]
                open_p = h['Open'].iloc[0]
                diff = ((last - open_p) / open_p) * 100
                veriler.append({
                    "Sembol": s,
                    "Fiyat": f"{last:.2f}",
                    "Değişim %": diff,
                    "Trend": "🟢" if diff > 0 else "🔴"
                })
        except:
            pass
    
    if veriler:
        df_ozet = pd.DataFrame(veriler)
        # Tabloyu şık gösterelim
        st.dataframe(
            df_ozet.style.format({"Değişim %": "{:.2f}"}).background_gradient(subset=["Değişim %"], cmap="RdYlGn"),
            use_container_width=True,
            hide_index=True
        )

# Döngü Mantığı
if auto_refresh:
    while True:
        with placeholder.container():
            tabloyu_guncelle()
            time.sleep(5) # 5 saniyede bir tabloyu yenile
            st.toast("Veriler Güncellendi!", icon="🔄")
else:
    with placeholder.container():
        tabloyu_guncelle()
