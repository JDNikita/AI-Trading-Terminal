import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import ollama
import openai
import json
import requests
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Institutional Terminal & Stock Copilot", 
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# INJECT INSTITUTIONAL DARK BLUE GRADIENT & SLEEK DECORATIVE CSS
# =============================================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #090d16 100%) !important;
    background-attachment: fixed !important;
}
.element-container, .stMarkdown {
    color: #e6edf3;
}
.alert-box { background-color: #2b1d1d; border-left: 4px solid #f85149; padding: 10px; border-radius: 4px; margin-top: 5px; }
.success-box { background-color: #1a2f23; border-left: 4px solid #2ea043; padding: 10px; border-radius: 4px; margin-top: 5px; }
.stSlider { padding-top: 0px !important; padding-bottom: 0px !important; }
.stSlider [data-baseweb="slider"] { margin-top: -2px; }
.stSlider [data-testid="stSliderTrack"] { background: linear-gradient(90deg, #161a22 0%, #21262d 100%) !important; height: 3px !important; border-radius: 2px !important; }
.stSlider [data-testid="stSliderFilledTrack"] { background: #00FF88 !important; }
.stSlider [data-testid="stSliderThumb"] {
    background-color: #00FF88 !important;
    border: 2px solid #0e1117 !important;
    width: 14px !important; height: 14px !important;
    box-shadow: 0 0 10px rgba(0, 255, 136, 0.7);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stSlider [data-testid="stSliderThumb"]:hover {
    transform: scale(1.25);
    box-shadow: 0 0 16px rgba(0, 255, 136, 0.95);
}
div[data-testid="stHorizontalBlock"] { align-items: center; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["NVDA", "AAPL", "BTC-USD"]

# --- LOAD PERMANENT KNOWLEDGE BASE ---
def load_all_knowledge_files():
    kb_dir = "knowledge_base"
    full_text = ""
    if os.path.exists(kb_dir):
        for root, _, files in os.walk(kb_dir):
            for file in files:
                if file.endswith(".md") or file.endswith(".json"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        full_text += f"\n\n=== KNOWLEDGE SOURCE: {file} ===\n" + f.read()
    return full_text

permanent_library = load_all_knowledge_files()

if st.sidebar.button("🧹 Clear App Cache"):
    st.cache_data.clear()
    st.rerun()

# =============================================================================
# SIDEBAR CONTROL DECK
# =============================================================================
st.sidebar.header("🕹 Terminal Control Deck")
app_mode = st.sidebar.radio("Navigation Mode", ["🔍 Single Asset Terminal", "⚡ Morning Watchlist & Edge Scanner"])

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Personal Watchlist")

new_ticker_input = st.sidebar.text_input("Add Ticker (e.g. TSLA, ETH-USD):").upper().strip()
if st.sidebar.button("➕ Add to Watchlist"):
    if new_ticker_input and new_ticker_input not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_ticker_input)
        st.sidebar.success(f"Added {new_ticker_input}!")
        st.rerun()

st.sidebar.markdown("**Current Saved Setups:**")
for t in list(st.session_state.watchlist):
    col_w1, col_w2 = st.sidebar.columns([3, 1])
    col_w1.write(f"• `{t}`")
    if col_w2.button("❌", key=f"del_{t}"):
        st.session_state.watchlist.remove(t)
        st.rerun()

st.sidebar.markdown("---")

with st.sidebar.expander("📁 Asset & Position Sizing", expanded=True):
    preset_choice = st.selectbox(
        "Preset", 
        ["Select Preset...", "AAPL", "NVDA", "TSLA", "MSFT", "BTC-USD", "ETH-USD", "PEPE-USD", "DOGE-USD"],
        label_visibility="collapsed"
    )
    custom_choice = st.text_input("Custom", placeholder="e.g. MSFT or Solana Contract...", label_visibility="collapsed")

    if custom_choice.strip():
        ticker_input = custom_choice.strip().upper()
    elif preset_choice != "Select Preset...":
        ticker_input = preset_choice
    else:
        ticker_input = "NVDA"

    portfolio_size = st.number_input("Account Equity ($)", value=25000.0, step=1000.0)
    risk_pct = st.number_input("Max Risk Per Trade (%)", min_value=0.1, max_value=25.0, value=1.0, step=0.1)

with st.sidebar.expander("🧠 AI Backend Engine", expanded=False):
    use_cloud = st.checkbox("🚀 Use Cloud API (Production)", value=False)
    cloud_api_key = ""
    if use_cloud:
        cloud_api_key = st.text_input("Cloud API Key (OpenAI)", type="password", value="")

with st.sidebar.expander("📊 Chart & Projection Settings", expanded=False):
    timeframe_choice = st.selectbox("Timeframe / Interval", ["1 Day (Daily Swing)", "1 Hour (Intraday Scalp)"])
    chart_style = st.radio("Chart Style", ["Candlestick", "Line Chart"])
    forecast_horizon = st.slider("Forecast Horizon (Bars)", min_value=2, max_value=20, value=5, step=1)

# =============================================================================
# FORMATTING HELPER
# =============================================================================
def format_price(val):
    if val is None or np.isnan(val): return "$0.00"
    if abs(val) < 0.01: return f"${val:.8f}"
    elif abs(val) < 1.0: return f"${val:.4f}"
    else: return f"${val:,.2f}"

# =============================================================================
# CACHED DATA & STOCK QUANTITATIVE TOOLKIT
# =============================================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_market_data(symbol, timeframe):
    try:
        symbol = symbol.strip()
        search_symbol = symbol.upper()
        is_crypto = "-USD" in search_symbol or search_symbol in ["DOGE", "PEPE", "SHIB", "FLOKI", "BONK", "BTC", "ETH"]
        if is_crypto and not search_symbol.endswith("-USD"):
            search_symbol = f"{search_symbol}-USD"

        stock = yf.Ticker(search_symbol)
        period, interval = ("3mo", "1h") if "1 Hour" in timeframe else ("1y", "1d")

        df = stock.history(period=period, interval=interval)
        
        if df is None or df.empty or len(df) < 2:
            return None, None, {}, False

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        df['SMA_50'] = df['Close'].rolling(window=min(50, len(df)-1)).mean()
        df['SMA_200'] = df['Close'].rolling(window=min(200, len(df)-1)).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
        df['ATR'] = df['TR'].rolling(window=14).mean()

        fund_data = {}
        try:
            info = stock.info
            fund_data = {
                "Market Cap": info.get('marketCap', 'N/A'),
                "Trailing P/E": info.get('trailingPE', 'N/A'),
                "Dividend Yield": info.get('dividendYield', 'N/A'),
                "52W High": info.get('fiftyTwoWeekHigh', 'N/A'),
                "52W Low": info.get('fiftyTwoWeekLow', 'N/A'),
                "Sector": info.get('sector', 'N/A')
            }
        except Exception:
            pass

        news = []
        try:
            news = stock.news
        except Exception:
            news = []

        return df, news, fund_data, is_crypto
    except Exception:
        return None, None, {}, False

# =============================================================================
# UNIFIED LLM ENGINE WRAPPER
# =============================================================================
def call_ai_engine(prompt):
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "") or cloud_api_key
    except Exception:
        api_key = cloud_api_key
    
    if use_cloud and api_key:
        try:
            openai.api_key = api_key
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return None
    else:
        try:
            response = ollama.chat(
                model='llama3.2',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.6, 'num_ctx': 8192, 'num_predict': 2048}
            )
            return response['message']['content'].strip()
        except Exception:
            return None

# =============================================================================
# DYNAMIC AI PREDICTION ENGINE
# =============================================================================
def generate_event_prediction(symbol, current_price, atr, sma_50, rsi, fund_data, is_crypto, news_headlines, horizon_bars):
    asset_type = "Cryptocurrency" if is_crypto else "Equity Stock"
    tech_bias = "BULLISH" if current_price >= sma_50 else "BEARISH"
    kb_snippet = permanent_library[:2500] if permanent_library else "Standard risk and technical rules apply."

    prompt = f"""
You are an elite quantitative portfolio manager analyzing {symbol} ({asset_type}):
- Current Price: {format_price(current_price)}
- 14-period RSI: {rsi:.1f}
- 50-period SMA Baseline: {format_price(sma_50)}
- News Context: {news_headlines}

Guidelines:
{kb_snippet}

Output MUST strictly be valid JSON format:
{{
    "bias": "{tech_bias}",
    "probability": 75,
    "target_multiplier": 1.6,
    "stop_multiplier": 1.0,
    "reasoning": "Detailed institutional structural explanation."
}}
"""
    content = call_ai_engine(prompt)
    if not content:
        return {
            "bias": tech_bias, "probability": 70,
            "target_multiplier": 1.5, "stop_multiplier": 1.0,
            "reasoning": f"Asset is trading relative to baseline {format_price(sma_50)} with RSI {rsi:.1f}."
        }

    try:
        if content.startswith("```json"): content = content[7:]
        if content.endswith("```"): content = content[:-3]
        content = content.strip()
        start_idx, end_idx = content.find('{'), content.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            data = json.loads(content[start_idx:end_idx])
            return data
        else:
            raise ValueError()
    except Exception:
        return {
            "bias": tech_bias, "probability": 70,
            "target_multiplier": 1.5, "stop_multiplier": 1.0,
            "reasoning": f"Asset is trading relative to baseline {format_price(sma_50)} with RSI {rsi:.1f}."
        }

# =============================================================================
# MODE 1: SINGLE ASSET TERMINAL
# =============================================================================
if app_mode == "🔍 Single Asset Terminal":
    st.title("AI Institutional Trading Terminal & Stock Copilot")
    st.caption("Advanced Stock Metrics • RSI & Moving Average Confluence • Predictive Price Cones")

    if ticker_input:
        df, news, fund_data, is_crypto = fetch_market_data(ticker_input, timeframe_choice)
        
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            latest_price = float(latest['Close'])
            latest_atr = float(latest['ATR']) if not np.isnan(latest['ATR']) and float(latest['ATR']) > 0 else latest_price * 0.03
            sma_50 = float(latest['SMA_50']) if not np.isnan(latest['SMA_50']) else latest_price
            current_rsi = float(latest['RSI']) if not np.isnan(latest['RSI']) else 50.0
            
            headlines = [item.get('title', '') if isinstance(item, dict) else str(item) for item in (news[:3] if news else [])]
            headline_text = " | ".join(headlines) if headlines else "No major news."
            
            pred = generate_event_prediction(ticker_input, latest_price, latest_atr, sma_50, current_rsi, fund_data, is_crypto, headline_text, forecast_horizon)
            
            dollar_risk = portfolio_size * (risk_pct / 100.0)
            stop_distance = latest_atr * pred['stop_multiplier']
            target_distance = latest_atr * pred['target_multiplier'] * (1 + (forecast_horizon * 0.08))
            
            if pred['bias'] == "BULLISH":
                target_price = latest_price + target_distance
                stop_price = latest_price - stop_distance
                cone_color, target_color, stop_color = 'rgba(0, 255, 136, 0.1)', '#00FF88', '#FF3366'
            elif pred['bias'] == "BEARISH":
                target_price = latest_price - target_distance
                stop_price = latest_price + stop_distance
                cone_color, target_color, stop_color = 'rgba(255, 51, 102, 0.1)', '#FF3366', '#00FF88'
            else:
                target_price = latest_price + (target_distance * 0.5)
                stop_price = latest_price - stop_distance
                cone_color, target_color, stop_color = 'rgba(255, 204, 0, 0.1)', '#FFCC00', '#FF3366'
                
            share_qty = dollar_risk / stop_distance if stop_distance > 0 else 0
            position_value = share_qty * latest_price

            # Top Metrics Dashboard
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", format_price(latest_price))
            col2.metric("Directional Forecast", f"{pred['bias']}", f"{pred['probability']}% Confidence ({forecast_horizon} Bars)")
            col3.metric("RSI (14-period)", f"{current_rsi:.1f}")
            col4.metric("Position Size", f"{share_qty:,.1f} Units", f"${position_value:,.2f}")
            
            st.info(f"💡 **Copilot Trade Reasoning:** {pred['reasoning']}")
            st.divider()

            # --- MAIN PRICE CHART WITH PREDICTIVE CONES ---
            chart_df = df.copy()
            chart_x = chart_df.index.strftime('%Y-%m-%d').tolist()

            fig_price = go.Figure()
            if chart_style == "Candlestick":
                fig_price.add_trace(go.Candlestick(
                    x=chart_x, open=chart_df['Open'], high=chart_df['High'],
                    low=chart_df['Low'], close=chart_df['Close'], name="Price History",
                    increasing_line_color='#00FF88', decreasing_line_color='#FF3366'
                ))
            else:
                fig_price.add_trace(go.Scatter(x=chart_x, y=chart_df['Close'], mode='lines', line=dict(color='#00FF88', width=2), name="Price Line"))

            fig_price.add_trace(go.Scatter(x=chart_x, y=chart_df['SMA_50'], mode='lines', line=dict(color='#FFA500', width=1.5), name="50 SMA"))

            # Add Predictive Price Cones
            last_date = chart_df.index[-1]
            future_step_delta = pd.Timedelta(hours=1) if "1 Hour" in timeframe_choice else pd.Timedelta(days=1)
            future_datetimes = [last_date + (future_step_delta * i) for i in range(1, forecast_horizon + 1)]
            future_x = [dt.strftime('%Y-%m-%d') for dt in future_datetimes]
            proj_x = [chart_x[-1]] + future_x

            steps = len(future_datetimes)
            target_trend = np.linspace(latest_price, target_price, steps)
            proj_target_y = [latest_price] + list(target_trend + np.random.normal(0, latest_atr * 0.15, size=steps))
            proj_target_y[-1] = target_price

            stop_trend = np.linspace(latest_price, stop_price, steps)
            proj_stop_y = [latest_price] + list(stop_trend + np.random.normal(0, latest_atr * 0.1, size=steps))
            proj_stop_y[-1] = stop_price

            fig_price.add_trace(go.Scatter(x=proj_x, y=proj_target_y, mode='lines+markers', line=dict(color=target_color, width=2, dash='dot'), name=f"Target ({pred['probability']}%)"))
            fig_price.add_trace(go.Scatter(x=proj_x, y=proj_stop_y, mode='lines+markers', line=dict(color=stop_color, width=2, dash='dot'), name="Invalidation"))
            proj_full_x = proj_x + proj_x[::-1]
            proj_full_y = proj_target_y + proj_stop_y[::-1]
            fig_price.add_trace(go.Scatter(
                x=proj_full_x, y=proj_full_y,
                fill='toself', fillcolor=cone_color, line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip", showlegend=False
            ))

            fig_price.update_layout(
                yaxis_title="Price ($)", template="plotly_dark", height=500,
                xaxis=dict(title="", type="category", rangeslider_visible=False, nticks=10),
                margin=dict(l=40, r=40, t=20, b=20)
            )
            st.plotly_chart(fig_price, use_container_width=True)

            # --- RSI SECONDARY SUB-CHART ---
            st.markdown("### Relative Strength Index (RSI 14)")
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=chart_x, y=chart_df['RSI'], mode='lines', line=dict(color='#DA70D6', width=1.8), name="RSI (14)"))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#FF3366", annotation_text="Overbought (70)")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00FF88", annotation_text="Oversold (30)")

            fig_rsi.update_layout(
                yaxis_title="RSI", yaxis=dict(range=[0, 100]), template="plotly_dark", height=220,
                xaxis=dict(title="", type="category", nticks=10), margin=dict(l=40, r=40, t=10, b=10)
            )
            st.plotly_chart(fig_rsi, use_container_width=True)

            # --- RISK ENGINE PARAMETERS ---
            st.subheader("Risk Engine & Order Parameters")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Max Dollar Risk ($)", f"${dollar_risk:,.2f}")
            r2.metric("Stop-Loss Distance", format_price(stop_distance))
            r3.metric("Reward-to-Risk Ratio", f"{pred['target_multiplier']/pred['stop_multiplier']:.1f} : 1")
            r4.metric("Volatility / ATR", format_price(latest_atr))

# =============================================================================
# MODE 2: MORNING WATCHLIST & EDGE SCANNER
# =============================================================================
elif app_mode == "⚡ Morning Watchlist & Edge Scanner":
    st.title("⚡ Morning Portfolio Edge & Risk Scanner")
    st.markdown("Instant batch-scan of your custom watchlist for volume anomalies and risk flags.")

    if st.button("🔄 Run Morning Briefing Batch Scan", type="primary"):
        with st.spinner("Scanning watchlist assets..."):
            results = []
            for t in st.session_state.watchlist:
                try:
                    h, n_list, _, _ = fetch_market_data(t, timeframe_choice)
                    if h is not None and not h.empty:
                        lp = h['Close'].iloc[-1]
                        pc = h['Close'].iloc[-2]
                        pct_chg = ((lp - pc) / pc) * 100
                        
                        cur_v = h['Volume'].iloc[-1]
                        avg_v = h['Volume'][:-1].mean()
                        v_mult = cur_v / avg_v if avg_v > 0 else 1.0
                        
                        headline = n_list[0].get('title', 'No breaking news') if n_list else 'No breaking news'
                        risk_flag = "🚨 Unusual Volume Spike (>1.5x)" if v_mult > 1.5 else "Normal Order Flow"

                        results.append({
                            "Ticker": t, "Price": f"${lp:,.2f}", "Change": f"{pct_chg:+.2f}%",
                            "Volume Multiplier": f"{v_mult:.2f}x", "Status": risk_flag
                        })
                except Exception:
                    results.append({"Ticker": t, "Price": "Error", "Status": "Failed"})

            st.dataframe(pd.DataFrame(results), use_container_width=True)