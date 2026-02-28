import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
import requests

# ══════════════════════════════════════════════════════════════════════════════
# 頁面設定
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="美股即時監控系統",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }

    /* Metric 卡片 */
    [data-testid="stMetric"] {
        background: #1e2235; border-radius: 10px;
        padding: 12px 14px; border: 1px solid #2e3456;
    }
    [data-testid="stMetricLabel"] > div {
        font-size: 0.9rem !important; color: #aab4cc !important;
        font-weight: 600; letter-spacing: 0.03em;
    }
    [data-testid="stMetricValue"] > div {
        font-size: 1.55rem !important; color: #ffffff !important; font-weight: 700;
    }
    [data-testid="stMetricDelta"] > div { font-size: 0.9rem !important; font-weight: 600; }

    /* EMA 數值列 */
    .ema-bar {
        background: #151825; border-radius: 8px; padding: 9px 14px;
        margin: 6px 0 8px 0; display: flex; flex-wrap: wrap;
        gap: 12px; border: 1px solid #252840;
    }
    .ema-item { font-size: 0.9rem; font-weight: 600; white-space: nowrap; }
    .ema-label { opacity: 0.7; font-size: 0.78rem; }

    /* 趨勢卡片 */
    .trend-card {
        background: #1e2235; border-radius: 10px;
        padding: 12px 14px; border: 1px solid #2e3456; text-align: center;
    }
    .trend-title { font-size: 0.9rem; color: #aab4cc; font-weight: 600; margin-bottom: 4px; }
    .trend-bull  { color: #00ee66; font-weight: 800; font-size: 1.45rem; }
    .trend-bear  { color: #ff4455; font-weight: 800; font-size: 1.45rem; }
    .trend-side  { color: #ffcc00; font-weight: 800; font-size: 1.45rem; }

    /* 多週期摘要列 */
    .mtf-header {
        background: #151825; border-radius: 10px; padding: 10px 16px;
        margin: 4px 0; border: 1px solid #252840;
        display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
    }
    .mtf-period { font-size: 0.85rem; color: #aab4cc; font-weight: 700; min-width: 52px; }
    .mtf-price  { font-size: 1.05rem; color: #ffffff; font-weight: 700; }
    .mtf-chg-up { font-size: 0.88rem; color: #00ee66; font-weight: 600; }
    .mtf-chg-dn { font-size: 0.88rem; color: #ff4455; font-weight: 600; }
    .mtf-trend-bull { background:#0d2e18; color:#00ee66; border-radius:4px; padding:2px 8px; font-size:0.82rem; font-weight:700; }
    .mtf-trend-bear { background:#2e0d0d; color:#ff4455; border-radius:4px; padding:2px 8px; font-size:0.82rem; font-weight:700; }
    .mtf-trend-side { background:#28260d; color:#ffcc00; border-radius:4px; padding:2px 8px; font-size:0.82rem; font-weight:700; }
    .mtf-macd-bull  { color:#00ee66; font-size:0.82rem; }
    .mtf-macd-bear  { color:#ff4455; font-size:0.82rem; }
    .mtf-ema-bull   { color:#00ee66; font-size:0.82rem; }
    .mtf-ema-bear   { color:#ff4455; font-size:0.82rem; }
    .mtf-divider    { height:28px; width:1px; background:#2e3456; flex-shrink:0; }

    /* 區塊標題 */
    .mtf-section-title {
        font-size: 1.1rem; font-weight: 700; color: #ddeeff;
        padding: 8px 0 4px 0; border-bottom: 2px solid #2e3456;
        margin: 14px 0 8px 0;
    }

    /* 警示面板 */
    .alert-box {
        padding: 11px 16px; border-radius: 8px; margin: 4px 0;
        font-size: 0.92rem; font-weight: 500; line-height: 1.5;
    }
    .alert-bull { background:#0d2e18; border-left:5px solid #00ee66; color:#88ffbb; }
    .alert-bear { background:#2e0d0d; border-left:5px solid #ff4455; color:#ffaaaa; }
    .alert-vol  { background:#0d1e38; border-left:5px solid #44aaff; color:#aaddff; }
    .alert-info { background:#28260d; border-left:5px solid #ffcc00; color:#fff0aa; }

    /* 市場環境面板 */
    .mkt-panel {
        background: #12151f; border-radius: 12px; padding: 14px 18px;
        border: 1px solid #2a2e48; margin-bottom: 10px;
    }
    .mkt-title {
        font-size: 1rem; font-weight: 700; color: #99aacc;
        letter-spacing: 0.05em; margin-bottom: 10px;
        border-bottom: 1px solid #2a2e48; padding-bottom: 6px;
    }
    .mkt-row { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:6px; }
    .mkt-card {
        background:#1a1e2e; border-radius:8px; padding:8px 14px;
        border:1px solid #252840; flex:1; min-width:100px; text-align:center;
    }
    .mkt-card-label { font-size:0.72rem; color:#7788aa; margin-bottom:2px; }
    .mkt-card-val   { font-size:1.05rem; font-weight:700; color:#eef2ff; }
    .mkt-card-chg-up { font-size:0.78rem; color:#00ee66; }
    .mkt-card-chg-dn { font-size:0.78rem; color:#ff4455; }
    .mkt-card-neu    { font-size:0.78rem; color:#ffcc00; }

    /* VIX 壓力計 */
    .vix-bar-bg  { background:#1a1e2e; border-radius:6px; height:10px; margin:4px 0; overflow:hidden; }
    .vix-bar-fill{ height:100%; border-radius:6px; transition:width 0.4s; }

    /* 情緒儀表 */
    .sentiment-meter {
        display:flex; align-items:center; gap:8px; margin:6px 0;
    }
    .sentiment-label { font-size:0.78rem; color:#7788aa; min-width:52px; }
    .sentiment-bar-bg { flex:1; background:#1a1e2e; border-radius:4px; height:8px; overflow:hidden; }
    .sentiment-bar-fill { height:100%; border-radius:4px; }
    .sentiment-val { font-size:0.78rem; font-weight:700; min-width:40px; text-align:right; }

    /* 新聞條目 */
    .news-item {
        padding: 8px 12px; background:#141824; border-radius:7px;
        margin:4px 0; border-left:3px solid #2a3060;
        font-size:0.82rem; line-height:1.5;
    }
    .news-item:hover { border-left-color:#4466cc; background:#171d2e; }
    .news-src  { font-size:0.7rem; color:#556688; margin-top:2px; }
    .news-bull { border-left-color:#00cc55; }
    .news-bear { border-left-color:#cc3344; }
    .news-neu  { border-left-color:#446688; }

    /* AI 分析面板 */
    .ai-panel {
        background: linear-gradient(135deg, #0e1525 0%, #111e35 100%);
        border-radius: 12px; padding: 20px 22px;
        border: 1px solid #1e3a5f; margin: 12px 0;
        box-shadow: 0 4px 20px rgba(0,100,255,0.08);
    }
    .ai-title {
        font-size: 1.05rem; font-weight: 700; color: #66aaff;
        letter-spacing: 0.04em; margin-bottom: 14px;
        display: flex; align-items: center; gap: 8px;
    }
    .ai-section { margin: 12px 0; }
    .ai-section-title {
        font-size: 0.78rem; font-weight: 700; color: #5577aa;
        text-transform: uppercase; letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .ai-verdict {
        font-size: 1.1rem; font-weight: 800; padding: 8px 16px;
        border-radius: 8px; display: inline-block; margin-bottom: 10px;
    }
    .ai-verdict-bull { background:#0d2e18; color:#00ee66; border:1px solid #00aa44; }
    .ai-verdict-bear { background:#2e0d0d; color:#ff5566; border:1px solid #aa2233; }
    .ai-verdict-side { background:#28260d; color:#ffcc00; border:1px solid #aa9900; }
    .ai-price-row {
        display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0;
    }
    .ai-price-card {
        background: #141c2e; border-radius: 8px; padding: 10px 14px;
        border: 1px solid #1e2e48; flex: 1; min-width: 100px; text-align:center;
    }
    .ai-price-label { font-size: 0.72rem; color: #5577aa; margin-bottom: 4px; }
    .ai-price-val   { font-size: 1.1rem; font-weight: 700; }
    .ai-price-entry { color: #44aaff; }
    .ai-price-tp    { color: #00ee66; }
    .ai-price-sl    { color: #ff5566; }
    .ai-price-rr    { color: #ffcc00; }
    .ai-reasoning {
        font-size: 0.88rem; color: #99aacc; line-height: 1.7;
        background: #0c1220; border-radius: 8px; padding: 12px 14px;
        border-left: 3px solid #2244aa;
    }
    .ai-risk-warning {
        font-size: 0.75rem; color: #445566; margin-top: 10px;
        padding: 6px 10px; border-radius: 4px; background: #0a0e18;
    }
    .ai-loading {
        text-align: center; padding: 30px;
        color: #4466aa; font-size: 0.9rem;
    }
    @keyframes ai-pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    .ai-loading-dot { animation: ai-pulse 1.2s infinite; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 常數
# ══════════════════════════════════════════════════════════════════════════════
INTERVAL_MAP = {
    "1m":  ("1分鐘",  "1d"),
    "5m":  ("5分鐘",  "5d"),
    "15m": ("15分鐘", "10d"),
    "30m": ("30分鐘", "30d"),
    "1d":  ("日K",    "1y"),
    "1wk": ("週K",    "3y"),
    "1mo": ("月K",    "5y"),
}
ALL_INTERVALS   = list(INTERVAL_MAP.keys())
INTERVAL_LABELS = {k: v[0] for k, v in INTERVAL_MAP.items()}

EMA_CONFIGS = [
    (5,   "#00ff88"), (10,  "#ccff00"), (20,  "#ffaa00"),
    (30,  "#ff5500"), (40,  "#cc00ff"), (60,  "#0088ff"),
    (120, "#00ccff"), (200, "#8866ff"),
]
MA_CONFIGS = [(5, "#ffffff", "dash"), (15, "#ffdd66", "dot")]

# ══════════════════════════════════════════════════════════════════════════════
# Session State
# ══════════════════════════════════════════════════════════════════════════════
if "alert_log"   not in st.session_state: st.session_state.alert_log   = []
if "sent_alerts" not in st.session_state: st.session_state.sent_alerts = set()

# ══════════════════════════════════════════════════════════════════════════════
# 市場環境數據
# ══════════════════════════════════════════════════════════════════════════════

# 大盤指數代號
MARKET_TICKERS = {
    "SPY":  ("標普500 ETF", "spy"),
    "QQQ":  ("那斯達克ETF", "qqq"),
    "DIA":  ("道瓊ETF",     "dia"),
    "^VIX": ("VIX恐慌指數", "vix"),
    "^TNX": ("10年期美債", "tnx"),
    "GLD":  ("黃金ETF",     "gld"),
    "UUP":  ("美元指數ETF", "uup"),
}

@st.cache_data(ttl=120)
def fetch_market_data() -> dict:
    """抓取大盤環境數據，快取 2 分鐘"""
    result = {}
    for ticker, (name, key) in MARKET_TICKERS.items():
        try:
            t  = yf.Ticker(ticker)
            df = t.history(period="5d", interval="1d", auto_adjust=True)
            if df.empty:
                # fallback: try download
                df = yf.download(ticker, period="5d", interval="1d",
                                 auto_adjust=True, progress=False)
                if df.empty:
                    continue
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            # normalize columns
            df.columns = [str(c[0]).strip() if isinstance(c, tuple) else str(c).strip()
                          for c in df.columns]
            if "Close" not in df.columns:
                continue
            last  = float(df["Close"].dropna().iloc[-1])
            prev  = float(df["Close"].dropna().iloc[-2]) if len(df["Close"].dropna()) > 1 else last
            chg   = last - prev
            pct   = chg / prev * 100 if prev else 0
            result[key] = {"name": name, "ticker": ticker,
                           "last": last, "chg": chg, "pct": pct}
        except Exception:
            pass
    return result

@st.cache_data(ttl=120)
def fetch_vix_history() -> pd.Series:
    """VIX 近 30 日歷史，用於趨勢判斷"""
    try:
        df = yf.download("^VIX", period="30d", interval="1d",
                         auto_adjust=True, progress=False)
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df["Close"].dropna()
    except Exception:
        return pd.Series(dtype=float)

def get_vix_regime(vix: float) -> tuple:
    """回傳 (狀態描述, 顏色, 條寬%) """
    if vix < 13:   return ("超低波動 😴",  "#00ee66", 10)
    if vix < 18:   return ("低波動 ✅",     "#88ff44", 25)
    if vix < 25:   return ("正常範圍 🟡",  "#ffcc00", 45)
    if vix < 30:   return ("偏高警戒 🟠",  "#ff8800", 62)
    if vix < 40:   return ("恐慌模式 🔴",  "#ff4444", 78)
    return             ("極度恐慌 💀",    "#cc0000", 95)

@st.cache_data(ttl=300)
def fetch_news(max_items: int = 8) -> list:
    """
    多來源財經新聞抓取：
    1. Google News RSS（最可靠，免費）
    2. MarketWatch RSS fallback
    回傳 list of dict: {title, link, date, sentiment}
    """
    import re, html as html_lib

    FEEDS = [
        ("Google Finance News",
         "https://news.google.com/rss/search?q=stock+market+wall+street&hl=en-US&gl=US&ceid=US:en"),
        ("Google Economy News",
         "https://news.google.com/rss/search?q=fed+interest+rate+inflation+nasdaq&hl=en-US&gl=US&ceid=US:en"),
        ("MarketWatch",
         "https://feeds.content.dowjones.io/public/rss/mw_marketpulse"),
    ]
    BEAR_KW = ["crash","fall","drop","decline","slump","fear","recession","selloff",
               "inflation","rate hike","sell-off","warning","risk","loss","tumble",
               "plunge","weak","concern","worry","tariff","yield surge"]
    BULL_KW = ["rally","surge","gain","rise","record","growth","beat","strong",
               "upgrade","buy","bull","positive","profit","rebound","recover",
               "outperform","soar","climb","boost","optimism"]

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36"}
    items = []

    for src_name, feed_url in FEEDS:
        if len(items) >= max_items:
            break
        try:
            resp = requests.get(feed_url, timeout=8, headers=headers)
            if resp.status_code != 200:
                continue
            text = resp.text

            # Parse <item> blocks
            item_blocks = re.findall(r"<item>(.*?)</item>", text, re.DOTALL)
            for block in item_blocks:
                if len(items) >= max_items:
                    break
                # Title
                t_match = re.search(r"<title>(.*?)</title>", block, re.DOTALL)
                if not t_match:
                    continue
                title = t_match.group(1)
                title = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"", title)
                title = re.sub(r"<[^>]+>", "", title)
                title = html_lib.unescape(title).strip()
                if not title or len(title) < 10:
                    continue

                # Link
                l_match = re.search(r"<link>(.*?)</link>", block)
                if not l_match:
                    l_match = re.search(r"<guid[^>]*>(.*?)</guid>", block)
                link = l_match.group(1).strip() if l_match else "#"

                # Date
                d_match = re.search(r"<pubDate>(.*?)</pubDate>", block)
                raw_date = d_match.group(1).strip() if d_match else ""
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(raw_date)
                    date_str = dt.strftime("%m/%d %H:%M")
                except Exception:
                    date_str = raw_date[:16]

                # Sentiment
                tl = title.lower()
                if   any(w in tl for w in BEAR_KW): sentiment = "bear"
                elif any(w in tl for w in BULL_KW): sentiment = "bull"
                else:                                sentiment = "neu"

                items.append({
                    "title": title, "link": link,
                    "date": date_str, "sentiment": sentiment,
                    "source": src_name,
                })
        except Exception:
            continue

    return items

def calc_sentiment_score(mkt: dict, vix_hist: pd.Series) -> dict:
    """
    綜合情緒分數計算（0-100，50為中性）
    組成：
      40% VIX 壓力（VIX 低 → 分數高）
      30% SPY 動能（近5日漲跌）
      30% QQQ 動能
    """
    score = 50.0  # 預設中性

    # VIX 分量（反向：VIX 越高 → 越恐慌 → 分數越低）
    vix_now = mkt.get("vix", {}).get("last", 20)
    if vix_now:
        vix_score = max(0, min(100, 100 - (vix_now - 10) * 3.5))
        score = score * 0.6 + vix_score * 0.4

    # SPY 動能分量
    spy = mkt.get("spy", {})
    if spy:
        spy_score = 50 + spy.get("pct", 0) * 8
        spy_score = max(0, min(100, spy_score))
        score = score * 0.7 + spy_score * 0.3

    # QQQ 動能分量
    qqq = mkt.get("qqq", {})
    if qqq:
        qqq_score = 50 + qqq.get("pct", 0) * 8
        qqq_score = max(0, min(100, qqq_score))
        score = score * 0.7 + qqq_score * 0.3

    # VIX 趨勢加減分
    if len(vix_hist) >= 5:
        vix_5d_chg = float(vix_hist.iloc[-1] - vix_hist.iloc[-5])
        score += -vix_5d_chg * 1.2  # VIX 5日上升 → 扣分

    score = max(0, min(100, score))

    if score >= 70:   label, color = "貪婪 🤑",    "#00ee66"
    elif score >= 55: label, color = "樂觀 😊",    "#88ff44"
    elif score >= 45: label, color = "中性 😐",    "#ffcc00"
    elif score >= 30: label, color = "悲觀 😟",    "#ff8800"
    else:             label, color = "極度恐慌 😱", "#ff4444"

    return {"score": round(score, 1), "label": label, "color": color}

def render_market_environment():
    """渲染市場環境面板（大盤 + VIX + 情緒 + 新聞）"""
    st.markdown("---")
    st.subheader("🌐 市場環境總覽")

    mkt      = fetch_market_data()
    vix_hist = fetch_vix_history()

    # ── 第一行：大盤指數卡片 ─────────────────────────────────────────────
    card_keys = ["spy", "qqq", "dia", "gld", "uup", "tnx"]
    card_cols = st.columns(len(card_keys))
    for col, key in zip(card_cols, card_keys):
        d = mkt.get(key)
        with col:
            if not d:
                st.metric(key.upper(), "N/A")
                continue
            chg_str = f"{d['chg']:+.2f} ({d['pct']:+.2f}%)"
            st.metric(d["name"], f"{d['last']:.2f}", chg_str)

    st.markdown("")

    # ── 第二行：VIX 壓力計 + 情緒儀表 ──────────────────────────────────
    col_vix, col_sent, col_news_hd = st.columns([1, 1, 2])

    with col_vix:
        vix_d = mkt.get("vix", {})
        vix_now = vix_d.get("last", 20)
        vix_chg = vix_d.get("pct", 0)
        regime, bar_color, bar_pct = get_vix_regime(vix_now)

        st.markdown(f"""
        <div class="mkt-panel">
          <div class="mkt-title">😨 VIX 恐慌指數</div>
          <div style="font-size:2rem;font-weight:800;color:{'#ff4444' if vix_now>25 else '#ffcc00' if vix_now>18 else '#00ee66'}">
            {vix_now:.2f}
            <span style="font-size:0.85rem;color:{'#ff4455' if vix_chg>0 else '#00ee66'}">
              {'▲' if vix_chg>0 else '▼'} {abs(vix_chg):.2f}%
            </span>
          </div>
          <div class="vix-bar-bg">
            <div class="vix-bar-fill" style="width:{bar_pct}%;background:{bar_color};"></div>
          </div>
          <div style="font-size:0.85rem;color:{bar_color};margin-top:4px;">{regime}</div>
          <div style="font-size:0.72rem;color:#556688;margin-top:6px;">
            &lt;18 正常　18-25 警戒　&gt;30 恐慌
          </div>
        </div>
        """, unsafe_allow_html=True)

        # VIX 近期走勢迷你圖
        if len(vix_hist) >= 5:
            vix_fig = go.Figure(go.Scatter(
                y=vix_hist.values, mode="lines+markers",
                line=dict(color=bar_color, width=2),
                marker=dict(size=4),
                fill="tozeroy", fillcolor=f"rgba(255,100,100,0.08)",
            ))
            vix_fig.update_layout(
                height=100, margin=dict(l=0,r=0,t=0,b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False, xaxis=dict(visible=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=9, color="#556688")),
            )
            st.plotly_chart(vix_fig, use_container_width=True,
                            config={"displayModeBar": False}, key="vix_mini")

    with col_sent:
        sent = calc_sentiment_score(mkt, vix_hist)
        sc   = sent["score"]
        sc_color = sent["color"]

        # 各分項指標
        indicators = []
        if mkt.get("spy"):
            pct = mkt["spy"]["pct"]
            indicators.append(("SPY 動能", 50 + pct*8, "#4488ff"))
        if mkt.get("qqq"):
            pct = mkt["qqq"]["pct"]
            indicators.append(("QQQ 動能", 50 + pct*8, "#aa44ff"))
        vix_comp = max(0, min(100, 100-(vix_now-10)*3.5)) if vix_now else 50
        indicators.append(("VIX 壓力", vix_comp, "#ff8844"))
        if mkt.get("tnx"):
            tnx_pct = mkt["tnx"]["pct"]
            bond_score = max(0, min(100, 50 - tnx_pct*6))
            indicators.append(("債券安全", bond_score, "#44ccff"))

        # 建立情緒分項 HTML（不使用縮排，避免 Streamlit 把空白當 code block）
        meter_parts = []
        for ind_name, ind_val, ind_color in indicators:
            ind_val = max(0, min(100, ind_val))
            meter_parts.append(
                f'<div class="sentiment-meter">'
                f'<span class="sentiment-label">{ind_name}</span>'
                f'<div class="sentiment-bar-bg">'
                f'<div class="sentiment-bar-fill" style="width:{ind_val:.0f}%;background:{ind_color};"></div>'
                f'</div>'
                f'<span class="sentiment-val" style="color:{ind_color}">{ind_val:.0f}</span>'
                f'</div>'
            )
        meter_rows = "".join(meter_parts)

        gradient = "linear-gradient(90deg,#ff4444 0%,#ffcc00 50%,#00ee66 100%)"
        sent_html = (
            f'<div class="mkt-panel">'
            f'<div class="mkt-title">🧠 投資人情緒指數</div>'
            f'<div style="font-size:1.8rem;font-weight:800;color:{sc_color};margin-bottom:4px;">'
            f'{sc:.0f} <span style="font-size:0.9rem">{sent["label"]}</span>'
            f'</div>'
            f'<div class="vix-bar-bg" style="height:12px;margin-bottom:10px;">'
            f'<div class="vix-bar-fill" style="width:{sc:.0f}%;background:{gradient};"></div>'
            f'</div>'
            f'{meter_rows}'
            f'<div style="font-size:0.68rem;color:#445566;margin-top:6px;">'
            f'綜合 VIX壓力(40%) + SPY動能(30%) + QQQ動能(30%)'
            f'</div>'
            f'</div>'
        )
        st.markdown(sent_html, unsafe_allow_html=True)

    with col_news_hd:
        news = fetch_news()
        icons = {"bull": "🟢", "bear": "🔴", "neu": "⚪"}
        if news:
            news_parts = ['<div class="mkt-panel"><div class="mkt-title">📰 即時財經新聞</div>']
            for n in news:
                icon = icons.get(n["sentiment"], "⚪")
                cls  = "news-" + n["sentiment"]
                src  = n.get("source", "")
                news_parts.append(
                    f'<div class="news-item {cls}">'
                    f'{icon} <a href="{n["link"]}" target="_blank" '
                    f'style="color:#ccd6ee;text-decoration:none;">{n["title"]}</a>'
                    f'<div class="news-src">{n["date"]}　{src}</div>'
                    f'</div>'
                )
            news_parts.append('</div>')
            st.markdown("".join(news_parts), unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="mkt-panel">'
                '<div class="mkt-title">📰 即時財經新聞</div>'
                '<div style="color:#556688;font-size:0.85rem;padding:8px 0;">'
                '⚠️ 新聞暫時無法載入（網路限制），請稍後重試'
                '</div></div>',
                unsafe_allow_html=True
            )

    # ── 第三行：市場環境警示 ──────────────────────────────────────────────
    mkt_alerts = []
    if vix_now > 30:
        mkt_alerts.append(("bear", f"⚠️ VIX 極度恐慌 {vix_now:.1f}，市場波動劇烈，建議謹慎操作"))
    elif vix_now > 25:
        mkt_alerts.append(("info", f"🟠 VIX 偏高 {vix_now:.1f}，市場情緒緊張"))
    elif vix_now < 13:
        mkt_alerts.append(("bull", f"😴 VIX 超低 {vix_now:.1f}，市場過於平靜，注意突發反轉"))

    spy_d = mkt.get("spy", {})
    if spy_d and spy_d.get("pct", 0) < -2:
        mkt_alerts.append(("bear", f"📉 SPY 單日下跌 {spy_d['pct']:.2f}%，大盤走弱"))
    elif spy_d and spy_d.get("pct", 0) > 1.5:
        mkt_alerts.append(("bull", f"📈 SPY 單日上漲 {spy_d['pct']:.2f}%，大盤強勢"))

    qqq_d = mkt.get("qqq", {})
    if qqq_d and qqq_d.get("pct", 0) < -2.5:
        mkt_alerts.append(("bear", f"📉 QQQ 科技股大跌 {qqq_d['pct']:.2f}%"))

    tnx_d = mkt.get("tnx", {})
    if tnx_d and tnx_d.get("last", 0) > 4.8:
        mkt_alerts.append(("bear", f"💸 10年期美債殖利率 {tnx_d['last']:.2f}%，利率壓力大"))

    if mkt_alerts:
        alert_cls = {"bull":"alert-bull","bear":"alert-bear","info":"alert-info","vol":"alert-vol"}
        html_parts = [f'<div class="alert-box {alert_cls.get(t,"alert-info")}">🌐 市場環境　{msg}</div>'
                      for t, msg in mkt_alerts]
        st.markdown("".join(html_parts), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AI 技術分析模組
# ══════════════════════════════════════════════════════════════════════════════

def build_analysis_prompt(symbol: str, interval_label: str, df: pd.DataFrame,
                          mkt: dict = None) -> str:
    """把技術指標數據打包成結構化 prompt 給 Claude 分析"""
    if df.empty:
        return ""

    close = df["Close"]
    last  = float(close.iloc[-1])
    high  = float(df["High"].iloc[-1])
    low_  = float(df["Low"].iloc[-1])
    vol   = int(df["Volume"].iloc[-1])

    # EMA 數值
    ema_vals = {n: round(float(calc_ema(close, n).iloc[-1]), 2) for n, _ in EMA_CONFIGS}
    # MACD
    dif, dea, hist = calc_macd(close)
    dif_val  = round(float(dif.iloc[-1]), 4)
    dea_val  = round(float(dea.iloc[-1]), 4)
    hist_val = round(float(hist.iloc[-1]), 4)
    # 金叉死叉
    macd_sig = "金叉(多)" if dif_val > dea_val else "死叉(空)"
    # 支撐阻力
    pivots_h, pivots_l = calc_pivot(df)
    resist  = round(max(p[1] for p in pivots_h), 2) if pivots_h else None
    support = round(min(p[1] for p in pivots_l), 2) if pivots_l else None
    # 成交量
    vol_ma5    = float(df["Volume"].rolling(5).mean().iloc[-1])
    vol_ratio  = round(vol / vol_ma5, 2) if vol_ma5 > 0 else 1
    # 趨勢
    trend = detect_trend(df)
    # 近期漲跌（5根）
    ret5 = round((last / float(close.iloc[-6]) - 1) * 100, 2) if len(close) > 6 else 0
    # 波動率（近20根ATR簡化版）
    atr = round(float((df["High"] - df["Low"]).tail(20).mean()), 2)

    # 大盤環境
    mkt_ctx = ""
    if mkt:
        spy = mkt.get("spy", {})
        vix = mkt.get("vix", {})
        if spy: mkt_ctx += f"\n- SPY: ${spy.get('last',0):.2f} ({spy.get('pct',0):+.2f}%)"
        if vix: mkt_ctx += f"\n- VIX: {vix.get('last',20):.1f}"

    prompt = f"""你是一位專業的美股技術分析師，請根據以下數據對 {symbol} 進行分析，並給出具體的操作建議。

## 基本資訊
- 股票代號：{symbol}
- 時間週期：{interval_label}
- 最新價格：${last:.2f}
- 本K高/低：${high:.2f} / ${low_:.2f}
- 近5根漲跌幅：{ret5:+.2f}%
- 平均波幅(ATR)：${atr:.2f}

## EMA 均線系統
- EMA5: ${ema_vals[5]} {'↑' if last > ema_vals[5] else '↓'}
- EMA10: ${ema_vals[10]} {'↑' if last > ema_vals[10] else '↓'}
- EMA20: ${ema_vals[20]} {'↑' if last > ema_vals[20] else '↓'}
- EMA60: ${ema_vals[60]} {'↑' if last > ema_vals[60] else '↓'}
- EMA120: ${ema_vals[120]} {'↑' if last > ema_vals[120] else '↓'}
- EMA200: ${ema_vals[200]} {'↑' if last > ema_vals[200] else '↓'}
- 均線排列：{trend}

## MACD (12,26,9)
- DIF: {dif_val}
- DEA: {dea_val}
- MACD柱: {hist_val}
- 信號：{macd_sig}

## 支撐與阻力
- 最近阻力位：{'$' + str(resist) if resist else '未偵測到'}
- 最近支撐位：{'$' + str(support) if support else '未偵測到'}

## 成交量
- 當前成交量：{vol/10000:.1f}萬股
- 相對均量倍數：{vol_ratio:.1f}x {'（異常放量）' if vol_ratio > 2 else ''}

## 大盤環境{mkt_ctx if mkt_ctx else '\n- 數據未載入'}

---

請以 JSON 格式回覆，欄位如下：
{{
  "verdict": "做多/做空/觀望",
  "confidence": 75,
  "trend_analysis": "（2-3句趨勢分析）",
  "entry_price": 123.45,
  "entry_note": "（進場條件說明）",
  "take_profit_1": 128.00,
  "take_profit_2": 132.00,
  "stop_loss": 119.50,
  "risk_reward": "1:2.5",
  "key_risks": "（主要風險1-2點）",
  "reasoning": "（完整分析邏輯，繁體中文，150字以內）"
}}

注意：
1. entry_price / take_profit / stop_loss 必須是數字，根據支撐阻力和ATR計算
2. stop_loss 做多時設在支撐位下方1-2個ATR，做空時設在阻力位上方
3. 只回覆 JSON，不要有任何其他文字或markdown標記
"""
    return prompt


# ── AI 供應商設定 ────────────────────────────────────────────────────────────
AI_PROVIDERS = {
    "Groq LLaMA 3.3（免費）":  "groq",
    "Gemini 2.0 Flash（免費）": "gemini",
    "Claude Sonnet（付費）":   "claude",
}

def get_ai_key(provider: str) -> str:
    """從 secrets 或 session_state 取得指定供應商的 API Key"""
    key_map = {
        "groq":   "GROQ_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
    }
    secret_key = key_map.get(provider, "")
    try:
        return st.secrets[secret_key]
    except Exception:
        pass
    return st.session_state.get(f"ai_key_{provider}", "")


def call_ai_analysis(prompt: str, provider: str) -> dict:
    """呼叫指定 AI 供應商進行技術分析"""
    import json

    api_key = get_ai_key(provider)
    if not api_key:
        return {"error": "NO_KEY"}

    system_msg = (
        "你是專業美股技術分析師，擅長解讀均線、MACD、支撐阻力。"
        "永遠以繁體中文回覆，且只輸出純 JSON，不含任何 markdown 或多餘文字。"
    )

    try:
        # ── Gemini ───────────────────────────────────────────────────────────
        if provider == "gemini":
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.0-flash:generateContent?key={api_key}"
            )
            body = {
                "system_instruction": {"parts": [{"text": system_msg}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "maxOutputTokens": 1000,
                    "temperature": 0.3,
                },
            }
            resp = requests.post(url, json=body, timeout=30)
            if resp.status_code == 400:
                return {"error": "Gemini API Key 無效，請確認後重新輸入"}
            if resp.status_code != 200:
                return {"error": f"Gemini 錯誤 {resp.status_code}: {resp.text[:200]}"}
            raw  = resp.json()
            text = raw["candidates"][0]["content"]["parts"][0]["text"]

        # ── Groq ─────────────────────────────────────────────────────────────
        elif provider == "groq":
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user",   "content": prompt},
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
                timeout=30,
            )
            if resp.status_code == 401:
                return {"error": "Groq API Key 無效，請確認後重新輸入"}
            if resp.status_code != 200:
                return {"error": f"Groq 錯誤 {resp.status_code}: {resp.text[:200]}"}
            raw  = resp.json()
            text = raw["choices"][0]["message"]["content"]

        # ── Claude ───────────────────────────────────────────────────────────
        elif provider == "claude":
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "system": system_msg,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30,
            )
            if resp.status_code == 401:
                return {"error": "Claude API Key 無效，請確認後重新輸入"}
            if resp.status_code != 200:
                return {"error": f"Claude 錯誤 {resp.status_code}: {resp.text[:200]}"}
            raw  = resp.json()
            text = raw.get("content", [{}])[0].get("text", "")

        else:
            return {"error": f"未知供應商：{provider}"}

        # 清除 markdown 殘留並解析 JSON
        text = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(text)

    except json.JSONDecodeError as e:
        return {"error": f"JSON 解析失敗：{e}\n原始回覆：{text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


# 向後相容
def get_anthropic_key(): return get_ai_key("claude")
def call_claude_analysis(prompt): return call_ai_analysis(prompt, "claude")


# 各供應商說明
PROVIDER_INFO = {
    "groq": {
        "name":        "Groq LLaMA 3.3 70B",
        "free":        True,
        "quota":       "每天 14,400 次",
        "url":         "https://console.groq.com/keys",
        "placeholder": "gsk_...",
        "secret_key":  "GROQ_API_KEY",
        "guide":       "前往 console.groq.com → API Keys → Create API Key",
    },
    "gemini": {
        "name":        "Gemini 2.0 Flash",
        "free":        True,
        "quota":       "每天 1,500 次，每分鐘 60 次",
        "url":         "https://aistudio.google.com/apikey",
        "placeholder": "AIza...",
        "secret_key":  "GEMINI_API_KEY",
        "guide":       "前往 aistudio.google.com → Get API Key → Create API Key",
    },
    
    "claude": {
        "name":        "Claude Sonnet",
        "free":        False,
        "quota":       "按用量付費，每次約 $0.003",
        "url":         "https://console.anthropic.com/",
        "placeholder": "sk-ant-api03-...",
        "secret_key":  "ANTHROPIC_API_KEY",
        "guide":       "前往 console.anthropic.com → API Keys → Create Key",
    },
}


def render_ai_analysis(symbol: str, interval_label: str, df: pd.DataFrame,
                       mkt: dict = None):
    """渲染 AI 技術分析面板（支援 Gemini / Groq / Claude）"""

    # ── 供應商選擇（放在 session，跨 symbol 共用）─────────────────────────
    provider_labels = list(AI_PROVIDERS.keys())
    if "ai_provider" not in st.session_state:
        st.session_state["ai_provider"] = "groq"   # 預設免費的 Gemini

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        chosen_label = st.selectbox(
            "🤖 AI 供應商",
            options=provider_labels,
            index=list(AI_PROVIDERS.values()).index(st.session_state["ai_provider"]),
            key=f"ai_provider_sel_{symbol}_{interval_label}",
        )
        provider = AI_PROVIDERS[chosen_label]
        st.session_state["ai_provider"] = provider
        pinfo = PROVIDER_INFO[provider]
        badge = "🆓 免費" if pinfo["free"] else "💳 付費"
        st.caption(f"{badge}　{pinfo['quota']}")

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_key = f"ai_btn_{symbol}_{interval_label}"
        run_ai  = st.button("🔍 執行分析", key=btn_key, use_container_width=True)

    result_key = f"ai_result_{symbol}_{interval_label}_{provider}"

    # ── 若無 API Key，顯示設定引導 ───────────────────────────────────────
    api_key = get_ai_key(provider)
    if not api_key:
        st.markdown(
            f'<div class="ai-panel">'
            f'<div class="ai-title">⚙️ 設定 {pinfo["name"]} API Key</div>'
            f'<div style="color:#ffcc00;font-size:0.88rem;margin-bottom:10px;">'
            f'{badge} · {pinfo["quota"]}</div>'
            f'<div style="font-size:0.83rem;color:#7788aa;line-height:1.9;">'
            f'1. {pinfo["guide"]}<br>'
            f'2. 複製 API Key（格式：<code style="color:#aabbcc">{pinfo["placeholder"][:8]}...</code>）<br>'
            f'3. 貼到下方輸入框，或寫入 secrets.toml 永久保存'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        key_input = st.text_input(
            f"{pinfo['name']} API Key",
            type="password",
            placeholder=pinfo["placeholder"],
            key=f"key_input_{provider}_{symbol}_{interval_label}",
        )
        if key_input:
            st.session_state[f"ai_key_{provider}"] = key_input.strip()
            st.success(f"✅ {pinfo['name']} Key 已儲存，現在可以執行分析")
            st.rerun()
        return

    if run_ai:
        st.session_state[result_key] = None
        with st.spinner(f"🤖 {pinfo['name']} 正在分析..."):
            prompt = build_analysis_prompt(symbol, interval_label, df, mkt)
            result = call_ai_analysis(prompt, provider)
            st.session_state[result_key] = result

    # ── 顯示結果 ────────────────────────────────────────────────────────────
    result = st.session_state.get(result_key)

    if not result:
        st.markdown(
            f'<div class="ai-panel" style="padding:16px 22px;">'
            f'<span style="color:#334466;font-size:0.88rem;">'
            f'點擊「執行分析」，{pinfo["name"]} 將解讀技術指標並給出操作建議</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        return

    if "error" in result:
        err = result["error"]
        if err == "NO_KEY":
            st.session_state.pop(f"ai_key_{provider}", None)
            st.rerun()
        st.error(f"❌ AI 分析失敗：{err}")
        return

    # ── 解析結果 ────────────────────────────────────────────────────────────
    verdict      = result.get("verdict", "觀望")
    confidence   = result.get("confidence", 50)
    trend_txt    = result.get("trend_analysis", "")
    entry        = result.get("entry_price", 0)
    entry_note   = result.get("entry_note", "")
    tp1          = result.get("take_profit_1", 0)
    tp2          = result.get("take_profit_2", 0)
    sl           = result.get("stop_loss", 0)
    rr           = result.get("risk_reward", "—")
    risks        = result.get("key_risks", "")
    reasoning    = result.get("reasoning", "")

    verdict_cls  = {"做多": "ai-verdict-bull",
                    "做空": "ai-verdict-bear"}.get(verdict, "ai-verdict-side")
    verdict_icon = {"做多": "▲ 做多", "做空": "▼ 做空"}.get(verdict, "◆ 觀望")
    conf_color   = "#00ee66" if confidence >= 70 else "#ffcc00" if confidence >= 50 else "#ff5566"

    now = datetime.now().strftime("%m/%d %H:%M")

    html = (
        f'<div class="ai-panel">'

        # 標題列
        f'<div class="ai-title">'
        f'🤖 AI 分析報告　'
        f'<span style="font-size:0.75rem;color:#334466;font-weight:400">'
        f'{symbol} · {interval_label} · {now}</span>'
        f'</div>'

        # 裁決 + 信心度
        f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">'
        f'<span class="ai-verdict {verdict_cls}">{verdict_icon}</span>'
        f'<div>'
        f'<div style="font-size:0.72rem;color:#5577aa;margin-bottom:2px;">信心度</div>'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<div style="width:120px;background:#141c2e;border-radius:4px;height:8px;">'
        f'<div style="width:{confidence}%;height:8px;border-radius:4px;background:{conf_color};"></div>'
        f'</div>'
        f'<span style="color:{conf_color};font-weight:700;font-size:0.9rem;">{confidence}%</span>'
        f'</div>'
        f'</div>'
        f'</div>'

        # 趨勢分析
        f'<div class="ai-section">'
        f'<div class="ai-section-title">📊 趨勢分析</div>'
        f'<div class="ai-reasoning">{trend_txt}</div>'
        f'</div>'

        # 價位建議
        f'<div class="ai-section">'
        f'<div class="ai-section-title">💰 操作價位</div>'
        f'<div class="ai-price-row">'
        f'<div class="ai-price-card">'
        f'<div class="ai-price-label">進場價</div>'
        f'<div class="ai-price-val ai-price-entry">${entry:.2f}</div>'
        f'<div style="font-size:0.7rem;color:#334466;margin-top:3px;">{entry_note}</div>'
        f'</div>'
        f'<div class="ai-price-card">'
        f'<div class="ai-price-label">止盈 ①</div>'
        f'<div class="ai-price-val ai-price-tp">${tp1:.2f}</div>'
        f'<div style="font-size:0.7rem;color:#334466;margin-top:3px;">'
        f'{f"+{((tp1-entry)/entry*100):.1f}%" if entry else ""}</div>'
        f'</div>'
        f'<div class="ai-price-card">'
        f'<div class="ai-price-label">止盈 ②</div>'
        f'<div class="ai-price-val ai-price-tp">${tp2:.2f}</div>'
        f'<div style="font-size:0.7rem;color:#334466;margin-top:3px;">'
        f'{f"+{((tp2-entry)/entry*100):.1f}%" if entry else ""}</div>'
        f'</div>'
        f'<div class="ai-price-card">'
        f'<div class="ai-price-label">止損</div>'
        f'<div class="ai-price-val ai-price-sl">${sl:.2f}</div>'
        f'<div style="font-size:0.7rem;color:#334466;margin-top:3px;">'
        f'{f"{((sl-entry)/entry*100):.1f}%" if entry else ""}</div>'
        f'</div>'
        f'<div class="ai-price-card">'
        f'<div class="ai-price-label">盈虧比</div>'
        f'<div class="ai-price-val ai-price-rr">{rr}</div>'
        f'</div>'
        f'</div>'
        f'</div>'

        # 分析邏輯
        f'<div class="ai-section">'
        f'<div class="ai-section-title">🧠 分析邏輯</div>'
        f'<div class="ai-reasoning">{reasoning}</div>'
        f'</div>'
    )

    # 主要風險
    if risks:
        html += (
            f'<div class="ai-section">'
            f'<div class="ai-section-title">⚠️ 主要風險</div>'
            f'<div class="ai-reasoning" style="border-left-color:#cc4444;">{risks}</div>'
            f'</div>'
        )

    # 免責聲明
    html += (
        f'<div class="ai-risk-warning">'
        f'⚠️ 本分析由 AI 自動生成，僅供技術參考，不構成投資建議。'
        f'投資涉及風險，請自行判斷，並做好資金管理。'
        f'</div>'
        f'</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Telegram
# ══════════════════════════════════════════════════════════════════════════════
def send_telegram(msg: str):
    try:
        token   = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}, timeout=5,
        )
    except Exception:
        pass

def add_alert(symbol: str, period: str, msg: str, atype: str = "info"):
    now = datetime.now().strftime("%H:%M:%S")
    key = f"{symbol}|{period}|{msg}"
    if key not in st.session_state.sent_alerts:
        st.session_state.alert_log.insert(0,
            {"時間": now, "股票": symbol, "週期": period, "訊息": msg, "類型": atype})
        st.session_state.alert_log = st.session_state.alert_log[:200]
        st.session_state.sent_alerts.add(key)
        send_telegram(f"📊 [{symbol} {period}] {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# 數據抓取
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def fetch_data(symbol: str, interval: str) -> pd.DataFrame:
    _, period = INTERVAL_MAP[interval]
    try:
        df = yf.download(symbol, period=period, interval=interval,
                         auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df.dropna(inplace=True)
        return df
    except Exception:
        return pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
# 技術指標
# ══════════════════════════════════════════════════════════════════════════════
def calc_ema(s, n):  return s.ewm(span=n, adjust=False).mean()
def calc_ma(s, n):   return s.rolling(n).mean()

def calc_macd(s, fast=12, slow=26, sig=9):
    dif  = calc_ema(s, fast) - calc_ema(s, slow)
    dea  = calc_ema(dif, sig)
    return dif, dea, (dif - dea) * 2

def calc_pivot(df, interval: str = "1d"):
    """
    依週期動態調整掃描參數，並用「價格合理範圍過濾（±30%）」
    確保阻力/支撐位一定在當前價格附近，不出現歷史舊極值。
    """
    # 依週期決定 left、right、掃描的最近 N 根 K 線
    pivot_cfg = {
        "1m":  (3, 3, 120),
        "5m":  (3, 3, 100),
        "15m": (3, 3, 80),
        "30m": (3, 3, 60),
        "1d":  (5, 5, 60),
        "1wk": (3, 3, 40),
        "1mo": (2, 2, 24),   # 月K只看近24根(2年)，避免抓到5年前低點
    }
    left, right, tail_n = pivot_cfg.get(interval, (3, 3, 60))

    sub = df.tail(tail_n)
    if len(sub) < left + right + 2:
        return [], []

    hi, lo, idx = sub["High"].values, sub["Low"].values, sub.index
    current_price = float(df["Close"].iloc[-1])

    # 只接受距離當前價格 ±30% 以內的 pivot（過濾歷史遠古價位）
    price_lo = current_price * 0.70
    price_hi = current_price * 1.30

    highs, lows = [], []
    for i in range(left, len(sub) - right):
        if hi[i] == max(hi[i-left:i+right+1]) and price_lo <= hi[i] <= price_hi:
            highs.append((idx[i], float(hi[i])))
        if lo[i] == min(lo[i-left:i+right+1]) and price_lo <= lo[i] <= price_hi:
            lows.append((idx[i], float(lo[i])))

    return highs, lows

def detect_trend(df) -> str:
    if len(df) < 60: return "盤整"
    c = df["Close"]
    e5, e20, e60 = calc_ema(c,5).iloc[-1], calc_ema(c,20).iloc[-1], calc_ema(c,60).iloc[-1]
    e200 = calc_ema(c,200).iloc[-1] if len(df) >= 200 else None
    if e200:
        if e5>e20>e60>e200: return "多頭"
        if e5<e20<e60<e200: return "空頭"
    else:
        if e5>e20>e60: return "多頭"
        if e5<e20<e60: return "空頭"
    return "盤整"

def get_macd_signal(df) -> str:
    if len(df) < 30: return "—"
    dif, dea, _ = calc_macd(df["Close"])
    if dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-2] <= dea.iloc[-2]: return "⬆金叉"
    if dif.iloc[-1] < dea.iloc[-1] and dif.iloc[-2] >= dea.iloc[-2]: return "⬇死叉"
    return "DIF↑" if dif.iloc[-1] > dea.iloc[-1] else "DIF↓"

def get_ema_signal(df) -> str:
    if len(df) < 20: return "—"
    c = df["Close"]
    e5, e20 = calc_ema(c,5), calc_ema(c,20)
    if e5.iloc[-1] > e20.iloc[-1] and e5.iloc[-2] <= e20.iloc[-2]: return "多排↑"
    if e5.iloc[-1] < e20.iloc[-1] and e5.iloc[-2] >= e20.iloc[-2]: return "空排↓"
    return "EMA↑" if e5.iloc[-1] > e20.iloc[-1] else "EMA↓"

# ══════════════════════════════════════════════════════════════════════════════
# 警示邏輯
# ══════════════════════════════════════════════════════════════════════════════
def run_alerts(symbol, period_label, df):
    if len(df) < 30: return
    close, vol = df["Close"], df["Volume"]

    dif, dea, _ = calc_macd(close)
    if dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-2] <= dea.iloc[-2]:
        add_alert(symbol, period_label, "MACD 金叉 🟢", "bull")
    if dif.iloc[-1] < dea.iloc[-1] and dif.iloc[-2] >= dea.iloc[-2]:
        add_alert(symbol, period_label, "MACD 死叉 🔴", "bear")

    e5, e20 = calc_ema(close,5), calc_ema(close,20)
    if e5.iloc[-1] > e20.iloc[-1] and e5.iloc[-2] <= e20.iloc[-2]:
        add_alert(symbol, period_label, "EMA5 上穿 EMA20 ⬆️", "bull")
    if e5.iloc[-1] < e20.iloc[-1] and e5.iloc[-2] >= e20.iloc[-2]:
        add_alert(symbol, period_label, "EMA5 下穿 EMA20 ⬇️", "bear")

    emas = [calc_ema(close,n).iloc[-1] for n,_ in EMA_CONFIGS]
    if all(emas[i] > emas[i+1] for i in range(len(emas)-1)):
        add_alert(symbol, period_label, "所有 EMA 多頭排列 🚀", "bull")

    vol_ma5 = vol.rolling(5).mean().iloc[-1]
    if vol.iloc[-1] > vol_ma5 * 2:
        add_alert(symbol, period_label, f"成交量暴增 {vol.iloc[-1]/vol_ma5:.1f}x 均量 📊", "vol")

    # 支撐/阻力突破警示（含週期參數 + 價格合理性過濾）
    itvl_key = {v[0]: k for k, v in INTERVAL_MAP.items()}.get(period_label, "1d")
    pivots_h, pivots_l = calc_pivot(df, interval=itvl_key)
    price      = float(close.iloc[-1])
    prev_price = float(close.iloc[-2]) if len(close) > 1 else price

    if pivots_h:
        # 取「剛被突破」的阻力位：prev <= resist < price（由下往上突破）
        broken = [p[1] for p in pivots_h if prev_price <= p[1] < price]
        if broken:
            add_alert(symbol, period_label, f"突破阻力位 ${max(broken):.2f} ⚡", "bull")

    if pivots_l:
        # 取「剛被跌破」的支撐位：price < support <= prev（由上往下跌破）
        broken = [p[1] for p in pivots_l if price < p[1] <= prev_price]
        if broken:
            add_alert(symbol, period_label, f"跌破支撐位 ${min(broken):.2f} ⚠️", "bear")

# ══════════════════════════════════════════════════════════════════════════════
# 建立 K 線圖
# ══════════════════════════════════════════════════════════════════════════════
def build_chart(symbol, df, interval_label, compact=False, max_bars=90):
    if df.empty: return None

    # ── 限制最多顯示 90 根 K 線，避免圖表擁擠 ──
    # EMA/MACD 用完整數據計算（保留歷史），再截取最後 90 根顯示
    MAX_BARS = max(10, int(max_bars))   # 使用者自訂，最少10根
    close_full, vol_full = df["Close"], df["Volume"]
    ema_s_full = {n: calc_ema(close_full, n) for n, _ in EMA_CONFIGS}
    ma_s_full  = {n: calc_ma(close_full,  n) for n, _, _ in MA_CONFIGS}
    dif_full, dea_full, hist_full = calc_macd(close_full)

    # 截取最後 90 根用於繪圖
    df   = df.tail(MAX_BARS).copy()
    close, vol = df["Close"], df["Volume"]
    ema_s = {n: s.tail(MAX_BARS) for n, s in ema_s_full.items()}
    ma_s  = {n: s.tail(MAX_BARS) for n, s in ma_s_full.items()}
    dif   = dif_full.tail(MAX_BARS)
    dea   = dea_full.tail(MAX_BARS)
    hist  = hist_full.tail(MAX_BARS)

    # 支撐阻力用截取後的資料
    itvl_code = {v[0]: k for k, v in INTERVAL_MAP.items()}.get(interval_label, "1d")
    pivots_h, pivots_l = calc_pivot(df, interval=itvl_code)

    # ── 消除休市空白：把 DatetimeIndex 轉成字串當 category label ──────────
    # Plotly category 軸只顯示實際存在的類別，自動跳過休市間隙
    intraday = interval_label in {"1分鐘","5分鐘","15分鐘","30分鐘"}
    fmt = "%m/%d %H:%M" if intraday else "%y/%m/%d"
    xlabels = [t.strftime(fmt) for t in df.index]
    # 所有 series 也配對成同樣的字串 index，確保對齊
    vol_ma5 = vol.rolling(5).mean()

    chart_h = 520 if compact else 820
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.56, 0.19, 0.25], vertical_spacing=0.02,
        subplot_titles=(f"{symbol} ({interval_label})", "成交量", "MACD"),
    )
    ann_size = 11 if compact else 13
    for ann in fig.layout.annotations:
        ann.font.size  = ann_size
        ann.font.color = "#ccddee"

    # K 線
    fig.add_trace(go.Candlestick(
        x=xlabels, open=df["Open"], high=df["High"], low=df["Low"], close=close,
        increasing_line_color="#00cc44", increasing_fillcolor="#00cc44",
        decreasing_line_color="#ff4444", decreasing_fillcolor="#ff4444",
        name="K線", showlegend=False,
    ), row=1, col=1)

    # EMA 線
    for n, color in EMA_CONFIGS:
        fig.add_trace(go.Scatter(
            x=xlabels, y=ema_s[n],
            line=dict(color=color, width=1.3), name=f"EMA{n}", opacity=0.9,
        ), row=1, col=1)

    # MA 線
    for n, color, dash in MA_CONFIGS:
        fig.add_trace(go.Scatter(
            x=xlabels, y=ma_s[n],
            line=dict(color=color, width=1.8, dash=dash), name=f"MA{n}",
        ), row=1, col=1)

    # 支撐阻力
    if pivots_h:
        r = max(p[1] for p in pivots_h)
        fig.add_hline(y=r, line=dict(color="#ff8888", dash="dash", width=1.5),
                      annotation_text=f"阻力 {r:.2f}",
                      annotation_font=dict(size=12, color="#ff8888"),
                      annotation_bgcolor="rgba(30,10,10,0.8)", row=1, col=1)
    if pivots_l:
        s = min(p[1] for p in pivots_l)
        fig.add_hline(y=s, line=dict(color="#88ff88", dash="dash", width=1.5),
                      annotation_text=f"支撐 {s:.2f}",
                      annotation_font=dict(size=12, color="#88ff88"),
                      annotation_bgcolor="rgba(10,30,10,0.8)", row=1, col=1)

    # 最高最低
    max_pos = int(df["High"].values.argmax())
    min_pos = int(df["Low"].values.argmin())
    fig.add_annotation(x=xlabels[max_pos], y=float(df["High"].max()),
        text=f"▲ {df['High'].max():.2f}", showarrow=True,
        arrowhead=2, arrowcolor="#ff4444", arrowwidth=2,
        font=dict(color="#ff8888", size=11, family="Arial Black"),
        bgcolor="rgba(30,10,10,0.85)", bordercolor="#ff4444", borderwidth=1,
        row=1, col=1)
    fig.add_annotation(x=xlabels[min_pos], y=float(df["Low"].min()),
        text=f"▼ {df['Low'].min():.2f}", showarrow=True,
        arrowhead=2, arrowcolor="#ff4444", arrowwidth=2,
        font=dict(color="#ff8888", size=11, family="Arial Black"),
        bgcolor="rgba(30,10,10,0.85)", bordercolor="#ff4444", borderwidth=1,
        row=1, col=1)

    # ── 成交量 ──────────────────────────────────────────────────────────────
    col_vol = ["#00cc44" if c >= o else "#ff4444"
               for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(x=xlabels, y=vol, marker_color=col_vol,
                         name="成交量", showlegend=False), row=2, col=1)
    vol_ma5 = vol.rolling(5).mean()
    fig.add_trace(go.Scatter(x=xlabels, y=vol_ma5,
                              line=dict(color="#ffaa00", width=1.5), name="VOL MA5"), row=2, col=1)

    # 異常放量：只標記「最顯著的幾根」，用柱子邊框高亮 + 頂部小鑽石
    # 策略：同一段密集放量只取最大的那根，避免連續出現滿屏標注
    anomaly_mask = (vol > vol_ma5 * 2).values
    if anomaly_mask.any():
        # 把連續異常段落找出來，每段只取量最大的那根
        groups, in_group, g_start = [], False, 0
        for i, flag in enumerate(anomaly_mask):
            if flag and not in_group:
                in_group, g_start = True, i
            elif not flag and in_group:
                groups.append((g_start, i - 1))
                in_group = False
        if in_group:
            groups.append((g_start, len(anomaly_mask) - 1))

        # 每段取量最大的 bar 的 integer position
        rep_pos = []
        for g0, g1 in groups:
            seg_vals = vol.values[g0:g1+1]
            rep_pos.append(g0 + int(seg_vals.argmax()))

        rep_x    = [xlabels[p]  for p in rep_pos]
        rep_vol  = [float(vol.values[p])    for p in rep_pos]
        rep_ma   = [float(vol_ma5.values[p]) if not np.isnan(vol_ma5.values[p]) else 1
                    for p in rep_pos]
        mult_txt = [f"異常放量 {v/max(m,1):.1f}x 均量"
                    for v, m in zip(rep_vol, rep_ma)]

        # 柱頂鑽石標記（不加擁擠文字，hover 查看倍數）
        fig.add_trace(go.Scatter(
            x=rep_x, y=rep_vol,
            mode="markers",
            marker=dict(color="#ff00ff", size=11, symbol="diamond",
                        line=dict(color="#ffffff", width=1.2)),
            name="異常放量",
            hovertext=mult_txt,
            hoverinfo="text+x",
        ), row=2, col=1)

    # ── MACD ────────────────────────────────────────────────────────────────
    bar_col = ["#ff4444" if v >= 0 else "#00cc44" for v in hist]
    fig.add_trace(go.Bar(x=xlabels, y=hist, marker_color=bar_col,
                         name="MACD柱", showlegend=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=xlabels, y=dif,
                              line=dict(color="#ffaa00", width=1.5), name="DIF"), row=3, col=1)
    fig.add_trace(go.Scatter(x=xlabels, y=dea,
                              line=dict(color="#0088ff", width=1.5), name="DEA"), row=3, col=1)

    # ── 金叉/死叉（智能去擁擠）────────────────────────────────────────────
    # 收集所有原始交叉點
    raw_crosses = []
    for i in range(1, len(dif)):
        if dif.iloc[i] > dea.iloc[i] and dif.iloc[i-1] <= dea.iloc[i-1]:
            raw_crosses.append((i, "gold"))
        elif dif.iloc[i] < dea.iloc[i] and dif.iloc[i-1] >= dea.iloc[i-1]:
            raw_crosses.append((i, "dead"))

    # 間距過濾：相鄰標注至少 min_gap 根 K 線，且同方向連發只取最新
    total_bars = len(dif)
    min_gap    = max(6, total_bars // 20)
    max_labels = 3 if compact else 5

    filtered, last_pos, last_type = [], -9999, None
    for pos, ctype in reversed(raw_crosses):
        gap_ok  = (pos - last_pos) >= min_gap or last_pos == -9999
        diff_ok = (ctype != last_type) or last_pos == -9999
        if gap_ok and diff_ok:
            filtered.insert(0, (pos, ctype))
            last_pos, last_type = pos, ctype
        if len(filtered) >= max_labels:
            break

    # 繪製：金叉標在底部（ay 正值=往下偏移），死叉標在頂部（ay 負值=往上偏移）
    # 固定像素偏移，不依賴 MACD 數值範圍，確保 compact/full 都清晰
    base_px = 38 if compact else 46

    for seq, (pos, ctype) in enumerate(filtered):
        x_val  = xlabels[pos]
        y_val  = float(dif.iloc[pos])
        extra  = 1 + (seq % 2) * 0.45    # 偶數序號偏移更遠，水平錯開
        if ctype == "gold":
            ay_px  = int(base_px * extra)     # 正 = 箭頭朝上，標籤在下方
            text   = "⬆ 金叉"
            fcol, bgcol, bcol, acol = "#ffee55", "rgba(36,32,0,0.92)", "#bbaa00", "#ddcc00"
        else:
            ay_px  = -int(base_px * extra)    # 負 = 箭頭朝下，標籤在上方
            text   = "⬇ 死叉"
            fcol, bgcol, bcol, acol = "#ff9999", "rgba(36,0,0,0.92)", "#bb3333", "#cc4444"

        fig.add_annotation(
            x=x_val, y=y_val, text=text,
            showarrow=True, arrowhead=2, arrowwidth=1.5,
            ax=0, ay=ay_px,
            arrowcolor=acol,
            font=dict(color=fcol, size=9 if compact else 10, family="Arial Black"),
            bgcolor=bgcol, bordercolor=bcol, borderwidth=1, borderpad=3,
            row=3, col=1,
        )

    leg_sz = 8 if compact else 11

    # ── x 軸刻度標籤：依週期選擇合適格式 ─────────────────────────────────
    # 日K以下用日期+時間，日K及以上只用日期
    intraday_intervals = {"1分鐘","5分鐘","15分鐘","30分鐘"}
    if interval_label in intraday_intervals:
        tick_fmt = "%m/%d %H:%M"
        # 每隔幾根顯示一個刻度，避免密集
        n_ticks  = 8
    else:
        tick_fmt = "%Y/%m/%d"
        n_ticks  = 8

    # 用整數位置作為 x 軸刻度位置（category 模式下 x 軸是 0,1,2,...）
    total   = len(df)
    step    = max(1, total // n_ticks)
    tick_positions = list(range(0, total, step))
    tick_labels    = [df.index[i].strftime(tick_fmt) for i in tick_positions]

    fig.update_layout(
        height=chart_h, template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#111520",
        font=dict(family="Arial, sans-serif", size=10 if compact else 11, color="#ccddee"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
            font=dict(size=leg_sz, color="#ddeeff"),
            bgcolor="rgba(14,17,23,0.85)", bordercolor="#2e3456", borderwidth=1,
            itemsizing="constant",
            traceorder="normal",
        ),
        margin=dict(l=6, r=6, t=36 if compact else 44, b=4),
        xaxis_rangeslider_visible=False,
        # category 類型：plotly 只顯示有數據的 bar，自動跳過休市空白
        xaxis_type="category",
        xaxis2_type="category",
        xaxis3_type="category",
    )

    # 套用自訂刻度到所有 x 軸
    for axis_name in ["xaxis", "xaxis2", "xaxis3"]:
        fig.update_layout(**{
            axis_name: dict(
                type="category",
                showgrid=True, gridcolor="#1a1e30",
                tickfont=dict(size=9 if compact else 10),
                tickmode="array",
                tickvals=tick_positions,
                ticktext=tick_labels,
                tickangle=-35,
            )
        })

    fig.update_yaxes(showgrid=True, gridcolor="#1a1e30",
                     tickfont=dict(size=9 if compact else 10))
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# 多週期摘要列
# ══════════════════════════════════════════════════════════════════════════════
def render_mtf_summary(symbol, selected_intervals, show_alerts):
    st.markdown(f'<div class="mtf-section-title">🔀 多週期總覽 — {symbol}</div>',
                unsafe_allow_html=True)
    rows = []
    for itvl in selected_intervals:
        label, _ = INTERVAL_MAP[itvl]
        df = fetch_data(symbol, itvl)
        if df.empty:
            rows.append(
                f'<div class="mtf-header"><span class="mtf-period">{label}</span>'
                f'<span style="color:#555">數據載入失敗</span></div>')
            continue

        if show_alerts:
            run_alerts(symbol, label, df)

        close   = df["Close"]
        last    = float(close.iloc[-1])
        prev    = float(close.iloc[-2]) if len(close) > 1 else last
        chg     = last - prev
        pct     = chg / prev * 100 if prev else 0
        hi      = float(df["High"].iloc[-1])
        lo      = float(df["Low"].iloc[-1])
        vol_k   = int(df["Volume"].iloc[-1]) // 10000

        chg_cls   = "mtf-chg-up" if chg >= 0 else "mtf-chg-dn"
        chg_arrow = "▲" if chg >= 0 else "▼"

        trend     = detect_trend(df)
        t_cls     = {"多頭":"mtf-trend-bull","空頭":"mtf-trend-bear","盤整":"mtf-trend-side"}[trend]
        t_icon    = {"多頭":"▲","空頭":"▼","盤整":"◆"}[trend]

        macd_s    = get_macd_signal(df)
        macd_cls  = "mtf-macd-bull" if any(x in macd_s for x in ["金叉","↑"]) else "mtf-macd-bear"

        ema_s     = get_ema_signal(df)
        ema_cls   = "mtf-ema-bull" if any(x in ema_s for x in ["↑","多"]) else "mtf-ema-bear"

        rows.append(
            f'<div class="mtf-header">'
            f'  <span class="mtf-period">{label}</span>'
            f'  <div class="mtf-divider"></div>'
            f'  <span class="mtf-price">${last:.2f}</span>'
            f'  <span class="{chg_cls}">{chg_arrow} {chg:+.2f} ({pct:+.2f}%)</span>'
            f'  <div class="mtf-divider"></div>'
            f'  <span style="color:#6688aa;font-size:0.82rem">H:{hi:.2f}　L:{lo:.2f}　量:{vol_k}萬</span>'
            f'  <div class="mtf-divider"></div>'
            f'  <span class="{t_cls}">{t_icon} {trend}</span>'
            f'  <div class="mtf-divider"></div>'
            f'  <span class="{macd_cls}">MACD: {macd_s}</span>'
            f'  <span class="{ema_cls}">EMA: {ema_s}</span>'
            f'</div>'
        )
    st.markdown("".join(rows), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 多週期 K 線圖
# ══════════════════════════════════════════════════════════════════════════════
def render_mtf_charts(symbol, selected_intervals, layout_mode, max_bars=90):
    if not selected_intervals:
        st.info("請至少選擇一個時間週期")
        return
    st.markdown(f'<div class="mtf-section-title">📊 多週期 K 線圖 — {symbol}</div>',
                unsafe_allow_html=True)

    if layout_mode == "並排（2欄）":
        pairs = [selected_intervals[i:i+2] for i in range(0, len(selected_intervals), 2)]
        for pair in pairs:
            cols = st.columns(len(pair))
            for col, itvl in zip(cols, pair):
                label, _ = INTERVAL_MAP[itvl]
                df = fetch_data(symbol, itvl)
                with col:
                    if df.empty:
                        st.error(f"{label} 無數據")
                    else:
                        fig = build_chart(symbol, df, label, compact=True, max_bars=max_bars)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True,
                                            config={"displayModeBar": False},
                                            key=f"mtf_{symbol}_{itvl}")
    else:
        for itvl in selected_intervals:
            label, _ = INTERVAL_MAP[itvl]
            df = fetch_data(symbol, itvl)
            if df.empty:
                st.error(f"{label} 無數據")
            else:
                fig = build_chart(symbol, df, label, compact=False, max_bars=max_bars)
                if fig:
                    st.plotly_chart(fig, use_container_width=True,
                                    config={"displayModeBar": True},
                                    key=f"mtf_{symbol}_{itvl}_full")

# ══════════════════════════════════════════════════════════════════════════════
# 單週期渲染
# ══════════════════════════════════════════════════════════════════════════════
def render_single(symbol, interval, show_alerts, max_bars=90):
    label, _ = INTERVAL_MAP[interval]
    with st.spinner(f"載入 {symbol} {label} 數據中..."):
        df = fetch_data(symbol, interval)

    if df.empty:
        st.error(f"❌ 無法取得 {symbol} 數據")
        return

    close   = df["Close"]
    last    = float(close.iloc[-1])
    prev    = float(close.iloc[-2]) if len(close) > 1 else last
    chg     = last - prev
    pct     = chg / prev * 100 if prev else 0
    vol_now = int(df["Volume"].iloc[-1])
    trend   = detect_trend(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("最新價格",      f"${last:.2f}", f"{chg:+.2f} ({pct:+.2f}%)")
    c2.metric("成交量（萬股）", f"{vol_now/10000:.1f}")
    c3.metric("本K最高",       f"${df['High'].iloc[-1]:.2f}")
    c4.metric("本K最低",       f"${df['Low'].iloc[-1]:.2f}")
    t_cls  = {"多頭":"trend-bull","空頭":"trend-bear","盤整":"trend-side"}[trend]
    t_icon = {"多頭":"▲","空頭":"▼","盤整":"◆"}[trend]
    with c5:
        st.markdown(
            f'<div class="trend-card"><div class="trend-title">趨勢判斷</div>'
            f'<div class="{t_cls}">{t_icon} {trend}</div></div>',
            unsafe_allow_html=True)

    # EMA 列
    items = []
    for n, color in EMA_CONFIGS:
        val   = float(calc_ema(close,n).iloc[-1])
        arrow = "↑" if last > val else "↓"
        items.append(
            f'<span class="ema-item" style="color:{color}">'
            f'<span class="ema-label">EMA{n} </span>{val:.2f}'
            f'<span style="font-size:0.72rem;opacity:0.6"> {arrow}</span></span>')
    st.markdown('<div class="ema-bar">' + "".join(items) + '</div>',
                unsafe_allow_html=True)

    fig = build_chart(symbol, df, label, max_bars=max_bars)
    if fig:
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": True},
                        key=f"single_{symbol}_{interval}")

    if show_alerts:
        run_alerts(symbol, label, df)

    # ── AI 技術分析面板 ─────────────────────────────────────────────────────
    if show_ai:
        mkt = fetch_market_data() if show_market else {}
        st.markdown("---")
        render_ai_analysis(symbol, label, df, mkt=mkt)

# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("📈 美股監控系統")
    st.markdown("---")

    raw_input = st.text_area("股票代號（逗號分隔）", value="TSLA,AAPL,NVDA", height=80)
    symbols   = [s.strip().upper() for s in raw_input.replace("，",",").split(",") if s.strip()]

    st.markdown("---")
    st.markdown("#### 📅 監控模式")
    mode = st.radio("", ["單一週期", "多週期同時監控"], horizontal=True,
                    label_visibility="collapsed")

    if mode == "單一週期":
        single_interval = st.selectbox(
            "時間週期",
            ALL_INTERVALS,
            format_func=lambda x: INTERVAL_LABELS[x],
            index=4,
        )
        layout_mode = None
        selected    = []

    else:
        st.markdown("**勾選要同時顯示的週期：**")
        selected    = []
        defaults    = {"5m", "15m", "1d"}
        left_col, right_col = st.columns(2)
        for i, itvl in enumerate(ALL_INTERVALS):
            col = left_col if i % 2 == 0 else right_col
            if col.checkbox(INTERVAL_LABELS[itvl], value=(itvl in defaults), key=f"cb_{itvl}"):
                selected.append(itvl)
        st.markdown("")
        layout_mode = st.radio("圖表排列方式",
                               ["並排（2欄）", "堆疊（全寬）"], horizontal=True)

    st.markdown("---")
    auto_refresh = st.toggle("自動刷新", value=False)
    refresh_sec  = st.slider("刷新間隔（秒）", 60, 300, 60, step=30, disabled=not auto_refresh)

    st.markdown("---")
    st.markdown("**📊 K 線顯示根數**")
    max_bars = st.number_input(
        "每張圖最多顯示幾根 K 線",
        min_value=20, max_value=500, value=90, step=10,
        help="建議：分鐘圖 60-120 根，日K 60-90 根，週K/月K 40-60 根",
    )

    st.markdown("---")
    show_alerts  = st.toggle("啟用警示偵測",     value=True)
    show_market  = st.toggle("顯示市場環境面板",   value=True)
    show_ai      = st.toggle("啟用 AI 技術分析",  value=True)

    if st.button("🗑️ 清除警示記錄"):
        st.session_state.alert_log   = []
        st.session_state.sent_alerts = set()
        st.toast("警示記錄已清除")

    if st.session_state.alert_log:
        csv_data = pd.DataFrame(st.session_state.alert_log).to_csv(
            index=False, encoding="utf-8-sig")
        st.download_button("📥 匯出警示 CSV", csv_data, "alerts.csv", "text/csv")

    st.markdown("---")
    st.caption("數據來源：Yahoo Finance\n\n⚠️ 僅供參考，不構成投資建議")

# ══════════════════════════════════════════════════════════════════════════════
# 主區域
# ══════════════════════════════════════════════════════════════════════════════
st.title("🇺🇸 美股即時監控系統")

if not symbols:
    st.info("請在左側輸入股票代號")
    st.stop()

# ── 市場環境面板（置頂）──────────────────────────────────────────────────────
if show_market:
    render_market_environment()
    st.markdown("---")

stock_tabs = st.tabs([f"📊 {s}" for s in symbols])

for tab, symbol in zip(stock_tabs, symbols):
    with tab:
        if mode == "單一週期":
            render_single(symbol, single_interval, show_alerts, max_bars=max_bars)

        else:
            if not selected:
                st.warning("⚠️ 請在左側至少勾選一個時間週期")
            else:
                # ① 多週期摘要
                render_mtf_summary(symbol, selected, show_alerts)
                st.markdown("---")
                # ② 多週期 K 線圖
                render_mtf_charts(symbol, selected, layout_mode, max_bars=max_bars)

# ══════════════════════════════════════════════════════════════════════════════
# 警示面板
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.alert_log:
    st.markdown("---")
    st.subheader("🔔 警示訊息記錄")
    cls_map = {"bull":"alert-bull","bear":"alert-bear","vol":"alert-vol","info":"alert-info"}
    for e in st.session_state.alert_log[:40]:
        cls    = cls_map.get(e["類型"], "alert-info")
        p_tag  = f'【{e["週期"]}】' if e.get("週期") else ""
        st.markdown(
            f'<div class="alert-box {cls}">'
            f'🕐 {e["時間"]}　【{e["股票"]}】{p_tag}　{e["訊息"]}'
            f'</div>',
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 自動刷新
# ══════════════════════════════════════════════════════════════════════════════
if auto_refresh:
    time.sleep(refresh_sec)
    st.cache_data.clear()
    st.rerun()
