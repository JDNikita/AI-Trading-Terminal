import os
import ollama

# Base output directory
BASE_DIR = "knowledge_base"

# Ensure target directories exist
os.makedirs(f"{BASE_DIR}/microstructure", exist_ok=True)
os.makedirs(f"{BASE_DIR}/event_playbooks", exist_ok=True)
os.makedirs(f"{BASE_DIR}/sentiment_intelligence", exist_ok=True)

def append_to_markdown(filepath, content):
    """Appends generated section content cleanly into a markdown file."""
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content + "\n\n")

def call_llm(prompt):
    """Executes a deep-generation prompt using local Ollama (Llama 3.2)."""
    print("   [⏳] Generating deep content chunk...")
    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}],
        options={
            'temperature': 0.2, # Low temperature for quantitative accuracy
            'num_ctx': 8192,
            'num_predict': 4096
        }
    )
    return response['message']['content'].strip()

def build_full_library():
    print("🚀 Starting Automated Master Library Generator...\n")

    # =========================================================================
    # MODULE 1: CANDLESTICK MICROSTRUCTURE & PRICE PATH PREDICTIONS
    # =========================================================================
    path_m1 = f"{BASE_DIR}/microstructure/master_microstructure.md"
    # Clear existing file if re-running
    open(path_m1, "w", encoding="utf-8").close()

    print("📄 Building Module 1: Master Microstructure...")

    p1_1 = """You are an elite quantitative trading architect. Write an EXHAUSTIVE, textbook-grade section (1,000+ words) on Bullish Engulfing and Bearish Engulfing patterns.
Include:
1. Exact geometric definitions (Open, High, Low, Close relationships).
2. Order Book Microstructure: Detail liquidity sweeps, stop-hunts, and limit order absorption.
3. Volume Profile: Exact rules requiring >1.5x 20-period moving average volume to eliminate fakeouts.
4. Predicted Price Path: Spatial trajectory, invalidation levels (stop-loss in ATR terms), and Fibonacci pullback targets (38.2%, 50%, 61.8%).
Format in professional Markdown with LaTeX formulas for risk math."""
    
    append_to_markdown(path_m1, "# Master Candlestick Microstructure & Price Path Manual\n")
    append_to_markdown(path_m1, call_llm(p1_1))

    p1_2 = """You are an elite quantitative trading architect. Write an EXHAUSTIVE section (1,000+ words) covering Rejection Wicks (Hammers, Shooting Stars, Pinbars) and Plain-English Buy/Sell Execution Rules.
Include:
1. Wicks representing 2.5x to 3x body height as structural stop-hunts.
2. Plain-English WHEN TO BUY: Confluence requirements (minimum 2 technical confirmations), 1:2 R:R limits, and candle-close execution criteria.
3. Plain-English WHEN TO SELL: Exit triggers, trailing stop-losses using ATR multipliers (1.5x equities, 2.5x crypto/memecoins), and hard stop execution rules.
Format in professional Markdown."""
    
    append_to_markdown(path_m1, call_llm(p1_2))

    # =========================================================================
    # MODULE 2: EVENT-DRIVEN & NEWS MECHANICS
    # =========================================================================
    path_m2 = f"{BASE_DIR}/event_playbooks/master_event_mechanics.md"
    open(path_m2, "w", encoding="utf-8").close()

    print("📄 Building Module 2: Event Playbooks...")

    p2_1 = """You are an elite quantitative portfolio manager. Write an EXHAUSTIVE section (1,000+ words) detailing 'Buy the Rumor, Sell the News' event mechanics and Product Launch price action.
Include:
1. Phase 1: Pre-announcement accumulation (T-21 to T-7 days) and volatility compression.
2. Phase 2: Announcement day exhaustion (T-0), distribution into retail buying, intraday reversals, and long upper wick formation when expectations are merely met.
3. Phase 3: Post-release retracement math (50% to 61.8% retracements).
Format in professional Markdown."""
    
    append_to_markdown(path_m2, "# Real-Life Event Mechanics & Volatility Playbooks\n")
    append_to_markdown(path_m2, call_llm(p2_1))

    p2_2 = """You are an elite quantitative portfolio manager. Write an EXHAUSTIVE section (1,000+ words) covering Macroeconomic Surprises (CPI, FOMC) and High-Volatility Memecoin Sentiment Velocity.
Include:
1. Liquidity voids during macro news releases and the 3-day institutional follow-through rule.
2. Memecoin exponential attention feedback loops and social media volume velocity.
3. The Overbought Anomaly (why RSI > 80 mean-reversion fails in parabolic regimes) and order book collapse mechanics during liquidity cliffs.
Format in professional Markdown."""
    
    append_to_markdown(path_m2, call_llm(p2_2))

    # =========================================================================
    # MODULE 3: AI TRADING APP REVIEWS & PERFECT APP BLUEPRINT
    # =========================================================================
    path_m3 = f"{BASE_DIR}/sentiment_intelligence/master_app_review_analysis.md"
    open(path_m3, "w", encoding="utf-8").close()

    print("📄 Building Module 3: Sentiment & App Review Analysis...")

    p3_1 = """You are a senior product architect and quant strategist. Write an EXHAUSTIVE review analysis (1,000+ words) scanning top AI trading apps (Trade Ideas/Holly AI, TrendSpider, Danelfin, Prospero.ai, RockFlow) and community feedback (r/algotrading, r/Daytrading).
Include:
1. Detailed Pros and Cons of each app.
2. Analysis of core user complaints: high subscription fees ($90-$300/mo), outdated/clunky UIs, black-box signals without risk math, and false alerts during chop.
3. User praises: real-time scanning, automated pattern detection, plain-English explanations.
Format in professional Markdown."""
    
    append_to_markdown(path_m3, "# Top AI Trading Apps: Review Analysis & Blueprint\n")
    append_to_markdown(path_m3, call_llm(p3_1))

    p3_2 = """You are a senior product architect. Write an EXHAUSTIVE blueprint (1,000+ words) defining the 'Perfect, Simple AI Trading Copilot' based on real user desires.
Include detailed specifications for:
1. Plain-English Signal Justifications ('Why' the trade exists).
2. Exact Mathematical Position Sizing based on user equity ($) and risk limits.
3. Dynamic Risk-to-Reward Calculator (minimum 1:2 R:R).
4. Dynamic Event Risk Warnings (automated position reduction near CPI/news).
5. Clean Candlestick Visualization requirements.
Format in professional Markdown."""
    
    append_to_markdown(path_m3, call_llm(p3_2))

    print("\n🎉 Master Library Successfully Constructed!")
    print(f"Files created in '{BASE_DIR}/' with multi-thousand word textbook depth.")

if __name__ == "__main__":
    build_full_library()