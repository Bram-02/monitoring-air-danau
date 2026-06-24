import streamlit as st
import pandas as pd
from supabase import create_client
import plotly.express as px
import time
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Water Monitoring - Danau Toba", page_icon="🌊", layout="wide")

# CSS SAKTI: Memaksa elemen tetap solid 100% (Menghilangkan kedipan putih/abu-abu)
st.markdown("""
    <style>
    /* 1. Menghilangkan efek 'gray-out' saat fragment sedang update */
    [data-testid="stFragment"] {
        opacity: 1 !important;
    }
    
    /* 2. Memaksa grafik dan metric tetap tampil solid tanpa transisi */
    .stPlotlyChart, [data-testid="stMetricValue"], .metric-card {
        opacity: 1 !important;
        transition: none !important;
    }

    /* 3. Menyembunyikan indikator loading di pojok kanan atas */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* Sidebar Center */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        align-items: center;
        text-align: center;
    }
    
    [data-testid="stSidebar"] .stImage {
        display: flex;
        justify-content: center;
    }

    /* Desain Kartu Sensor */
    .metric-card {
        background-color: #0e1117; 
        padding: 15px; border-radius: 12px; text-align: center; 
        border: 2px solid #3b82f6; margin-bottom: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .metric-label { color: #3b82f6; font-size: 14px; font-weight: bold; margin-bottom: 5px; }
    .metric-value { color: #ffffff !important; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 1. KONEKSI SUPABASE
URL = "https://qdlwjdbfeeaamufjxhfg.supabase.co"
KEY = "sb_publishable_uf9ZbRwkXfF4WT22BpNfLg_aFnTH4zY"
supabase = create_client(URL, KEY)

def get_data():
    try:
        res = supabase.table("water_quality").select("*").order("created_at", desc=True).limit(30).execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

# --- FUNGSI GRAFIK ANTI-KEDIP ---
def draw_grafana_chart(df, y_col, title, color, unique_key):
    fig = px.area(df, x="created_at", y=y_col, title=title, template="plotly_dark")
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=250,
        colorway=[color],
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=None),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        # PENTING: Mematikan durasi transisi agar grafik tidak melompat (penyebab kedipan)
        transition_duration=0 
    )
    st.plotly_chart(
        fig, 
        use_container_width=True, 
        config={'displayModeBar': False, 'scrollZoom': True},
        # PENTING: Menggunakan key yang stabil agar komponen tidak di-render ulang dari nol
        key=unique_key 
    )

# --- BAGIAN 1: SIDEBAR (STATIS) ---
with st.sidebar:
    st.image("logo_del.jpeg", width=130)
    st.markdown("## Proyek Akhir")
    st.info("""
**Kelompok 13:**
- Bram Modestus Naibaho
- Bonifasius Geraldo
- Michael Julianto Sipahutar

**Pembimbing:**
Istas Pratomo Manalu, S.Si., M.Sc.
""")
    st.divider()
    st.write("📍 **Posisi Terakhir Buoy:**")
    df_init = get_data()
    if not df_init.empty:
        lp = df_init.iloc[[0]]
        fig_m = px.scatter_mapbox(lp, lat="latitude", lon="longitude", zoom=12, height=200)
        fig_m.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_m, use_container_width=True, config={'displayModeBar': False}, key="sidebar_map")
    st.write("🛰️ **Koneksi:** LoRa to Cloud")

# --- BAGIAN 2: JUDUL & JAM (HTML) ---
st.components.v1.html(
    """
    <style>
        .header-container {
            background: linear-gradient(90deg, #0e1117 0%, #1f2937 100%);
            padding: 15px; border-radius: 15px; border: 2px solid #3b82f6;
            text-align: center; font-family: 'Segoe UI', sans-serif; color: white;
        }
        h1 { margin: 0; font-size: clamp(28px, 6vw, 38px); letter-spacing: 1px; }
        #clock { color: #3b82f6; font-size: clamp(18px, 5vw, 24px); font-weight: bold; margin-top: 10px; line-height: 1.5; }
    </style>
    <div class="header-container">
        <h1>Dashboard Kualitas Air Danau</h1>
        <div id="clock">Memuat Waktu...</div>
    </div>
    <script>
    function u(){
        const d = new Date();
        const hari = ["Minggu","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"];
        const bulan = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"];
        let j = d.getHours(), m = d.getMinutes(), s = d.getSeconds();
        j = (j<10?'0':'') + j; m = (m<10?'0':'') + m; s = (s<10?'0':'') + s;
        const format = hari[d.getDay()] + ", " + d.getDate() + " " + bulan[d.getMonth()] + " " + d.getFullYear() + "<br>" + j + ":" + m + ":" + s;
        document.getElementById('clock').innerHTML = format;
    }
    setInterval(u, 1000); u();
    </script>
    """,
    height=180,
)

# --- BAGIAN 3: FRAGMENT UPDATE (ZONA ANTI-KEDIP) ---
@st.fragment(run_every=5)
def sensor_updates():
    df_live = get_data()
    if not df_live.empty:
        df_plot = df_live.sort_values('created_at', ascending=True)
        latest = df_plot.iloc[-1]
        
        # 1. METRICS
        m1, m2, m3, m4, m5 = st.columns(5)
        params = [("🌡️ Temp", "suhu", "°C"), ("🧪 pH", "ph", "pH"), ("☁️ Turb", "turbidity", "NTU"), 
                  ("⚡ Cond", "conductivity", "µS"), ("🐟 DO", "dissolved_oxygen", "mg/L")]
        cols = [m1, m2, m3, m4, m5]
        for i, (lab, key, unit) in enumerate(params):
            cols[i].markdown(f"""<div class="metric-card"><div class="metric-label">{lab}</div><div class="metric-value">{latest[key]} {unit}</div></div>""", unsafe_allow_html=True)

        # 2. STATUS
        if 6.5 <= latest['ph'] <= 8.5 and latest['dissolved_oxygen'] >= 5:
            st.success("### ✅ STATUS: AIR AMAN")
        else: st.error("### ⚠️ STATUS: BAHAYA")

        st.markdown("### 📈 Panel Monitoring")
        
        # 3. GRAFIK DENGAN KEY STABIL (Mencegah Kedipan)
        r1c1, r1c2 = st.columns(2)
        with r1c1: draw_grafana_chart(df_plot, "suhu", "Suhu (°C)", "#f87171", "chart_temp")
        with r1c2: draw_grafana_chart(df_plot, "ph", "Keasaman (pH)", "#4ade80", "chart_ph")

        r2c1, r2c2 = st.columns(2)
        with r2c1: draw_grafana_chart(df_plot, "turbidity", "Kekeruhan (NTU)", "#fbbf24", "chart_turb")
        with r2c2: draw_grafana_chart(df_plot, "conductivity", "Konduktivitas (µS)", "#60a5fa", "chart_cond")

        draw_grafana_chart(df_plot, "dissolved_oxygen", "Oksigen Terlarut (mg/L)", "#a78bfa", "chart_do")

        with st.expander("📋 Lihat Tabel Data Mentah"):
            st.dataframe(df_live, use_container_width=True)

        st.divider()
        f1, f2, f3 = st.columns(3)
        f1.write(f"🔋 Baterai: {latest['battery']}%")
        f2.write(f"📶 Sinyal: {latest['rssi']} dBm")
        f3.write(f"🔄 Sync: Real-time")

# Jalankan fragment
sensor_updates()