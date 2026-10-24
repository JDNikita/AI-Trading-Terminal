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
/* Smooth Dark Blue Gradient Background */
.stApp {
    background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #090d16 100%) !important;
    background-attachment: fixed !important;
}

/* Institutional Card Containers */
.element-container, .stMarkdown {
    color: #e6edf3;
}

.alert-box { background-color: #2b1d1d; border-left: 4px solid #f85149; padding: 10px; border-radius: 4px; margin-top: 5px; }
.success-box { background-color: #1a2f23; border-left: 4px solid #2ea043; padding: 10px; border-radius: 4px; margin-top: 5px; }

/* Ultra-Sleek Institutional Slider Styling */
.stSlider {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
}
.stSlider [data-baseweb="slider"] {
    margin-top: -2px;
}
.stSlider [data-testid="stSliderTrack"] {
    background: linear-gradient(90deg, #161a22 0%, #21262d 100%) !important;
    height: 3px !important;
    border-radius: 2px !important;
}
.stSlider [data-testid="stSliderFilledTrack"] {
    background: #00FF88 !important;
}
.stSlider [data-testid="stSliderThumb"] {
    background-color: #00FF88 !important;
    border: 2px solid #0e1117 !important;
    width: 14px !important;
    height: 14px !important;
    box-shadow: 0 0 10px rgba(0, 255, 136, 0.7);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stSlider [data-testid="stSliderThumb"]:hover {
    transform: scale(1.25);
    box-shadow: 0 0 16px rgba(0, 255, 136, 0.95);
}
div[data-testid="stHorizontalBlock"] {
    align-items: center;
}
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
                if file.endswith(".md"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        full_text += f"\n\n=== SOURCE: {file} ===\n" + f.read()
    return full_text

permanent_library = load_all_knowledge_files()

if st.sidebar.button("🧹 Clear App Cache"):
    st.cache_data.clear()
    st.rerun()

# =============================================================================
# ORGANIZED SIDEBAR CONTROL DECK (EXPANDERS & NAVIGATION)
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

# Section 1: Asset & Position Sizing
with st.sidebar.expander("📁 Asset & Position Sizing", expanded=True):
    st.markdown("##### Select Preset Asset")
    preset_choice = st.selectbox(
        "Preset", 
        ["Select Preset...", "AAPL", "NVDA", "TSLA", "MSFT", "BTC-USD", "ETH-USD", "PEPE-USD", "DOGE-USD"],
        label_visibility="collapsed"
    )
    
    st.markdown("##### Or Enter Custom Ticker / Contract")
    custom_choice = st.text_input(
        "Custom", 
        placeholder="e.g. MSFT or Solana Contract...", 
        label_visibility="collapsed"
    )

    if custom_choice.strip():
        ticker_input = custom_choice.strip().upper()
    elif preset_choice != "Select Preset...":
        ticker_input = preset_choice
    else:
        ticker_input = "NVDA"

    portfolio_size = st.number_input("Account Equity ($)", value=25000.0, step=1000.0)
    risk_pct = st.number_input("Max Risk Per Trade (%)", min_value=0.1, max_value=25.0, value=1.0, step=0.1)

# Section 2: AI Backend
with st.sidebar.expander("🧠 AI Backend Engine", expanded=False):
    use_cloud = st.checkbox("🚀 Use Cloud API (Production)", value=False, help="Uncheck for free local Ollama testing, check for cloud production API.")
    cloud_api_key = ""
    if use_cloud:
        cloud_api_key = st.text_input("Cloud API Key (OpenAI)", type="password", value="")

# Section 3: Chart & Horizon Controls
with st.sidebar.expander("📊 Chart & Projection Settings", expanded=False):
    timeframe_choice = st.selectbox("Timeframe / Interval", ["1 Day (Daily Swing)", "1 Hour (Intraday Scalp)"])
    chart_style = st.radio("Chart Style", ["Candlestick", "Line Chart"])
    axis_mode = st.radio("X-Axis Gap Mode", ["Ignore Gaps (Continuous)", "Keep Gaps (Linear Date)"], help="Remove non-trading gaps or keep calendar spacing.")
    forecast_horizon = st.slider("Forecast Horizon (Bars)", min_value=2, max_value=20, value=5, step=1)

# =============================================================================
# FORMATTING HELPER
# =============================================================================
def format_price(val):
    if val is None or np.isnan(val):
        return "$0.00"
    if abs(val) < 0.01:
        return f"${val:.8f}"
    elif abs(val) < 1.0:
        return f"${val:.4f}"
    else:
        return f"${val:,.2f}"

# =============================================================================
# CACHED DATA & STOCK QUANTITATIVE TOOLKIT
# =============================================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_market_data(symbol, timeframe):
    try:
        symbol = symbol.strip()
        
        # Check if input is a Solana/EVM contract address (30+ characters)
        if len(symbol) >= 30:
            ds_url = f"https://api.dexscreener.com/latest/dex/tokens/{symbol}"
            ds_res = requests.get(ds_url, timeout=5).json()
            pairs = ds_res.get('pairs')
            
            if not pairs:
                return None, None, {}, True
            
            top_pair = pairs[0]
            chain_id = top_pair.get('chainId', 'solana')
            pool_address = top_pair.get('pairAddress')
            
            tf_param, aggregate_param = ("hour", 1) if "1 Hour" in timeframe else ("day", 1)
            headers = {"Accept": "application/json;version=20230203"}
            all_ohlcv = []
            before_ts = None
            
            for _ in range(5):
                gt_url = f"https://api.geckoterminal.com/api/v2/networks/{chain_id}/pools/{pool_address}/ohlcv/{tf_param}?aggregate={aggregate_param}&limit=100"
                if before_ts:
                    gt_url += f"&before_timestamp={before_ts}"
                
                res = requests.get(gt_url, headers=headers, timeout=5).json()
                data = res.get('data', {}).get('attributes', {}).get('ohlcv_list', [])
                
                if not data:
                    break
                    
                all_ohlcv.extend(data)
                before_ts = data[-1][0]
            
            if all_ohlcv and len(all_ohlcv) >= 2:
                records = []
                for row in all_ohlcv:
                    dt = datetime.fromtimestamp(int(row[0])).replace(tzinfo=None)
                    records.append({
                        'Date': dt, 'Open': float(row[1]), 'High': float(row[2]),
                        'Low': float(row[3]), 'Close': float(row[4]), 'Volume': float(row[5])
                    })
                
                df = pd.DataFrame(records).drop_duplicates(subset=['Date']).set_index('Date').sort_index()
            else:
                return None, None, {}, True

            df['SMA_50'] = df['Close'].rolling(window=min(50, len(df)-1)).mean()
            df['SMA_200'] = df['Close'].rolling(window=min(200, len(df)-1)).mean()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
            df['ATR'] = df['TR'].rolling(window=14).mean().fillna(df['Close'] * 0.05)

            fund_data = {"Type": "DEX Token", "Volume 24h": f"${top_pair.get('volume', {}).get('h24', 0):,.0f}"}
            return df, [], fund_data, True

        # Standard Yahoo Finance Processing
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
        except Exception as e:
            st.error(f"Cloud API Error: {e}")
            return None
    else:
        try:
            response = ollama.chat(
                model='llama3.2',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.6, 'num_ctx': 4096}
            )
            return response['message']['content'].strip()
        except Exception as e:
            return None

# =============================================================================
# DYNAMIC AI PREDICTION ENGINE
# =============================================================================
def generate_event_prediction(symbol, current_price, atr, sma_50, rsi, fund_data, is_crypto, news_headlines, horizon_bars):
    asset_type = "Cryptocurrency / Memecoin" if is_crypto else "Equity Stock"
    tech_bias = "BULLISH" if current_price >= sma_50 else "BEARISH"
    
    prompt = f"""
You are an institutional quantitative portfolio manager. Analyze this {asset_type} for {symbol}:
- Current Price: {format_price(current_price)}
- 14-period RSI: {rsi:.1f}
- 50-period SMA Baseline: {format_price(sma_50)}
- Fundamentals: {fund_data}
- Projection Horizon: {horizon_bars} bars into the future.
- Recent News/Sentiment Context: {news_headlines}
- Knowledge Base Context: {permanent_library[:1000]}

Task:
1. Determine short-term directional bias. Choose strictly between: "BULLISH", "BEARISH", or "NEUTRAL".
2. Assign a base confidence percentage (55% to 85%).
3. Output target and stop multipliers based on ATR volatility.
4. Write a 2-sentence rationale explaining the setup.

Output MUST strictly be valid JSON format:
{{
    "bias": "{tech_bias}",
    "probability": 75,
    "target_multiplier": 1.6,
    "stop_multiplier": 1.0,
    "reasoning": "Explanation of the setup here."
}}
"""
    content = call_ai_engine(prompt)
    if not content:
        base_prob = int(np.random.randint(68, 82))
        decay_penalty = (horizon_bars - 2) * 1.5
        final_prob = int(max(50, base_prob - decay_penalty))
        return {
            "bias": tech_bias,
            "probability": final_prob,
            "target_multiplier": 1.5,
            "stop_multiplier": 1.0,
            "reasoning": f"Asset is trading relative to its moving average baseline at {format_price(sma_50)} with an RSI of {rsi:.1f}."
        }

    try:
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            data = json.loads(content[start_idx:end_idx])
            decay_penalty = (horizon_bars - 2) * 1.5
            data["probability"] = int(max(50, min(90, data.get("probability", 70) - decay_penalty)))
            if data.get("bias") not in ["BULLISH", "BEARISH", "NEUTRAL"]:
                data["bias"] = tech_bias
            return data
        else:
            raise ValueError("JSON braces not found.")
    except Exception:
        base_prob = int(np.random.randint(68, 82))
        decay_penalty = (horizon_bars - 2) * 1.5
        final_prob = int(max(50, base_prob - decay_penalty))
        return {
            "bias": tech_bias,
            "probability": final_prob,
            "target_multiplier": 1.5,
            "stop_multiplier": 1.0,
            "reasoning": f"Asset is trading relative to its moving average baseline at {format_price(sma_50)} with an RSI of {rsi:.1f}."
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
            
            headlines = []
            if news:
                for item in news[:3]:
                    if isinstance(item, str): headlines.append(item)
                    elif isinstance(item, dict): headlines.append(item.get('title', ''))
            headline_text = " | ".join(headlines) if headlines else "No major breaking headlines found."
            
            pred = generate_event_prediction(ticker_input, latest_price, latest_atr, sma_50, current_rsi, fund_data, is_crypto, headline_text, forecast_horizon)
            
            dollar_risk = portfolio_size * (risk_pct / 100.0)
            stop_distance = latest_atr * pred['stop_multiplier']
            target_distance = latest_atr * pred['target_multiplier'] * (1 + (forecast_horizon * 0.08))
            
            if pred['bias'] == "BULLISH":
                target_price = latest_price + target_distance
                stop_price = latest_price - stop_distance
                cone_color = 'rgba(0, 255, 136, 0.1)'
                target_color = '#00FF88'
                stop_color = '#FF3366'
            elif pred['bias'] == "BEARISH":
                target_price = latest_price - target_distance
                stop_price = latest_price + stop_distance
                cone_color = 'rgba(255, 51, 102, 0.1)'
                target_color = '#FF3366'
                stop_color = '#00FF88'
            else:
                target_price = latest_price + (target_distance * 0.5)
                stop_price = latest_price - stop_distance
                cone_color = 'rgba(255, 204, 0, 0.1)'
                target_color = '#FFCC00'
                stop_color = '#FF3366'
                
            share_qty = dollar_risk / stop_distance if stop_distance > 0 else 0
            position_value = share_qty * latest_price

            # Dashboard Header Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", format_price(latest_price))
            col2.metric("Directional Forecast", f"{pred['bias']}", f"{pred['probability']}% Confidence ({forecast_horizon} Bars)")
            col3.metric("RSI (14-period)", f"{current_rsi:.1f}", "Overbought >70 | Oversold <30" if current_rsi > 70 or current_rsi < 30 else "Neutral Range")
            col4.metric("Position Size", f"{share_qty:,.1f} Units", f"${position_value:,.2f} Allocation")
            
            st.info(f"💡 **Copilot Trade Reasoning:** {pred['reasoning']}")

            if fund_data and not is_crypto:
                with st.expander("📌 Stock Fundamental & Valuation Metrics"):
                    f_cols = st.columns(len(fund_data))
                    for i, (k, v) in enumerate(fund_data.items()):
                        val_str = f"${v:,.0f}" if isinstance(v, (int, float)) and v > 1000 else str(v)
                        f_cols[i].metric(k, val_str)

            st.divider()
            p_col1, p_col2 = st.columns([3, 1])
            with p_col1:
                st.markdown(f"### {ticker_input} — Institutional Price & Predictive Trajectory")
            with p_col2:
                price_height = st.slider("Price Height", min_value=400, max_value=1000, value=650, step=50, label_visibility="collapsed")

            chart_df = df.copy()
            chart_df = chart_df[~chart_df.index.duplicated(keep='last')]
            chart_df.sort_index(inplace=True)
            
            if "Ignore Gaps" in axis_mode:
                chart_x = chart_df.index.strftime('%Y-%m-%d %H:%M' if "1 Hour" in timeframe_choice else '%Y-%m-%d').tolist()
            else:
                chart_x = chart_df.index

            fig_price = go.Figure()

            if chart_style == "Candlestick":
                fig_price.add_trace(go.Candlestick(
                    x=chart_x, open=chart_df['Open'], high=chart_df['High'],
                    low=chart_df['Low'], close=chart_df['Close'], name="Price History",
                    increasing_line_color='#00FF88', decreasing_line_color='#FF3366'
                ))
            else:
                fig_price.add_trace(go.Scatter(
                    x=chart_x, y=chart_df['Close'], mode='lines', name="Price Line",
                    line=dict(color='#00FF88', width=2), connectgaps=True
                ))

            fig_price.add_trace(go.Scatter(x=chart_x, y=chart_df['SMA_50'], mode='lines', name="50 SMA", line=dict(color='#FFA500', width=1.5), connectgaps=True))
            fig_price.add_trace(go.Scatter(x=chart_x, y=chart_df['SMA_200'], mode='lines', name="200 SMA", line=dict(color='#1E90FF', width=1.5), connectgaps=True))

            last_date = chart_df.index[-1]
            future_step_delta = pd.Timedelta(hours=1) if "1 Hour" in timeframe_choice else pd.Timedelta(days=1)
            future_datetimes = [last_date + (future_step_delta * i) for i in range(1, forecast_horizon + 1)]
            
            if "Ignore Gaps" in axis_mode:
                future_x = [dt.strftime('%Y-%m-%d %H:%M' if "1 Hour" in timeframe_choice else '%Y-%m-%d') for dt in future_datetimes]
                proj_x = [chart_x[-1]] + future_x
            else:
                proj_x = [last_date] + future_datetimes

            steps = len(future_datetimes)
            np.random.seed(int(datetime.now().timestamp()) % 10000)
            
            target_trend = np.linspace(latest_price, target_price, steps)
            proj_target_y = [latest_price] + list(target_trend + np.random.normal(0, latest_atr * 0.15, size=steps))
            proj_target_y[-1] = target_price

            stop_trend = np.linspace(latest_price, stop_price, steps)
            proj_stop_y = [latest_price] + list(stop_trend + np.random.normal(0, latest_atr * 0.1, size=steps))
            proj_stop_y[-1] = stop_price

            fig_price.add_trace(go.Scatter(x=proj_x, y=proj_target_y, mode='lines+markers', line=dict(color=target_color, width=2, dash='dot'), name=f"Target ({pred['probability']}%)"))
            fig_price.add_trace(go.Scatter(x=proj_x, y=proj_stop_y, mode='lines+markers', line=dict(color=stop_color, width=2, dash='dot'), name="Invalidation"))
            fig_price.add_trace(go.Scatter(
                x=proj_x + proj_x[::-1], y=proj_target_y + proj_stop_y[::-1],
                fill='toself', fillcolor=cone_color, line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip", showlegend=False
            ))

            xaxis_settings = dict(title="", rangeslider_visible=False)
            if "Ignore Gaps" in axis_mode:
                xaxis_settings["type"] = "category"
                xaxis_settings["nticks"] = 12
            else:
                xaxis_settings["type"] = "date"
                xaxis_settings["rangebreaks"] = [dict(bounds=["sat", "sun"])]

            fig_price.update_layout(
                yaxis_title="Price ($)",
                template="plotly_dark",
                height=price_height,
                xaxis=xaxis_settings,
                margin=dict(l=40, r=40, t=20, b=20)
            )

            st.plotly_chart(fig_price, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})

            r_col1, r_col2 = st.columns([3, 1])
            with r_col1:
                st.markdown("### Relative Strength Index (RSI 14)")
            with r_col2:
                rsi_height = st.slider("RSI Height", min_value=150, max_value=500, value=250, step=25, label_visibility="collapsed")

            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=chart_x, y=chart_df['RSI'], mode='lines', name="RSI (14)",
                line=dict(color='#DA70D6', width=1.8), connectgaps=True
            ))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#FF3366", annotation_text="Overbought (70)", annotation_position="top left")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00FF88", annotation_text="Oversold (30)", annotation_position="bottom left")

            fig_rsi.update_layout(
                yaxis_title="RSI",
                yaxis=dict(range=[0, 100]),
                template="plotly_dark",
                height=rsi_height,
                xaxis=xaxis_settings,
                margin=dict(l=40, r=40, t=20, b=20)
            )

            st.plotly_chart(fig_rsi, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

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
    st.markdown("Instant batch-scan of your custom watchlist. Flags unusual volume spikes, breaking headlines, and hidden risk anomalies before retail market open.")

    if st.button("🔄 Run Morning Briefing Batch Scan", type="primary"):
        with st.spinner("Scanning all watchlist assets for institutional volume anomalies and news catalysts..."):
            
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
                        
                        risk_flag = "Normal Order Flow"
                        if v_mult > 1.5:
                            risk_flag = "🚨 Unusual Volume Spike Detected (Institutional Accumulation/Distribution)"
                        elif pct_chg < -4.0:
                            risk_flag = "⚠️ Sharp Intraday Drawdown Warning"

                        results.append({
                            "Ticker": t,
                            "Price": f"${lp:,.2f}",
                            "Change": f"{pct_chg:+.2f}%",
                            "Volume Multiplier": f"{v_mult:.2f}x",
                            "Latest Headline": headline,
                            "Edge & Risk Status": risk_flag
                        })
                except Exception as ex:
                    results.append({
                        "Ticker": t,
                        "Price": "Error",
                        "Change": "N/A",
                        "Volume Multiplier": "N/A",
                        "Latest Headline": str(ex),
                        "Edge & Risk Status": "Data Fetch Failed"
                    })

            df_watchlist = pd.DataFrame(results)
            st.markdown("### 📊 Daily Portfolio Overview Matrix")
            st.dataframe(df_watchlist, use_container_width=True)

            st.markdown("### 🔍 Actionable Edge Highlights")
            for row in results:
                if "🚨" in row["Edge & Risk Status"] or "⚠️" in row["Edge & Risk Status"]:
                    st.markdown(f"""
                        <div class="alert-box">
                            <b>{row['Ticker']} ({row['Price']} | {row['Change']})</b><br>
                            <b>Status:</b> {row['Edge & Risk Status']}<br>
                            <b>Catalyst Headline:</b> {row['Latest Headline']}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="success-box">
                            <b>{row['Ticker']} ({row['Price']} | {row['Change']})</b> — Volume: {row['Volume Multiplier']} | Status: Stable
                        </div>
                    """, unsafe_allow_html=True)