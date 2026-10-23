import os
import ollama

# Base output directory
BASE_DIR = "knowledge_base"

# Ensure the NEW target directory exists alongside your existing ones
TARGET_DIR = f"{BASE_DIR}/real_world_catalysts"
os.makedirs(TARGET_DIR, exist_ok=True)

def append_to_markdown(filepath, content):
    """Appends generated section content cleanly into a markdown file."""
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content + "\n\n")

def call_llm(prompt):
    """Executes a deep-generation prompt using local Ollama (Llama 3.2) with optimized RAM limits."""
    print("   [⏳] Generating deep knowledge chunk...")
    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}],
        options={
            'temperature': 0.2, # Low temperature for quantitative accuracy
            'num_ctx': 4096,     # Optimized context window to prevent RAM overload
            'num_predict': 1500  # Optimized token length for smooth execution
        }
    )
    return response['message']['content'].strip()

def build_real_world_library():
    print("🚀 Starting Real-World Catalysts & User Feedback Library Generator...\n")

    # =========================================================================
    # MODULE 1: HISTORICAL REAL-WORLD EVENT PLAYBOOKS
    # =========================================================================
    path_m1 = f"{TARGET_DIR}/master_event_playbooks.md"
    # Clear existing file if re-running
    open(path_m1, "w", encoding="utf-8").close()

    print("📄 Building File 1: Master Historical Event Playbooks...")

    p1_1 = """You are an elite quantitative macro strategist. Write an EXHAUSTIVE, textbook-grade section detailing how Real-World Catalysts impact stock prices and market liquidity.
Include deep breakdowns for:
1. Earnings Surprises & Guidance Revisions: Post-Earnings Announcement Drift (PEAD), gap-and-go mechanics, and distribution into retail buying.
2. Federal Reserve & Central Bank Policy: Rate hikes, rate cuts, FOMC press conference volatility spikes, and interest rate swap adjustments.
3. Geopolitical Escalations & Supply Chain Shocks: How oil, defense, and semiconductor stocks react during energy cliffs, trade tariffs, and supply freezes.
4. Regulatory & Product Approvals (FDA/Tech/Semiconductor): Pre-catalyst run-ups, binary outcome risk, and post-news collapse/surge dynamics.
Format in professional Markdown with clear subheadings, mathematical risk modifiers, and quantitative rules."""
    
    append_to_markdown(path_m1, "# Master Real-World Catalysts & Macro Volatility Playbook\n")
    append_to_markdown(path_m1, call_llm(p1_1))

    p1_2 = """You are an elite quantitative portfolio manager. Write an EXHAUSTIVE section on 20-to-80 Minute Intraday Tactical Positioning around Breaking News.
Include:
1. News Velocity & Order Book Microstructure: How algorithmic market makers pull limit orders during breaking news, creating liquidity voids.
2. The 15-Minute News Exhaustion Rule: Identifying panic buying/selling tops/bottoms using 1-minute and 5-minute volume spikes.
3. Short-Term Probability Formulas: How to calculate short-term directional bias percentages (20 to 80 minutes) combining RSI momentum shifts, volume spikes, and headline sentiment.
4. Strict Risk Execution Rules: Why position sizing MUST be cut by 50% during binary news events.
Format in professional Markdown with LaTeX formulas for probability and position sizing."""
    
    append_to_markdown(path_m1, call_llm(p1_2))

    # =========================================================================
    # MODULE 2: REDDIT INSIGHTS & COPILOT FEATURE ARCHITECTURE
    # =========================================================================
    path_m2 = f"{TARGET_DIR}/user_pain_points_and_feature_blueprint.md"
    open(path_m2, "w", encoding="utf-8").close()

    print("📄 Building File 2: User Pain Points & Feature Blueprint...")

    p2_1 = """You are a senior fintech product architect and lead quant engineer. Write an EXHAUSTIVE research report analyzing retail trader complaints from Reddit (r/algotrading, r/Daytrading, r/wallstreetbets) and existing commercial AI trading software (TrendSpider, Trade Ideas, Danelfin).
Include:
1. Top 5 Fatal Flaws of Current AI Trading Software: Black-box signals with no explanations, inability to factor in breaking news, clunky subscription paywalls, repainting indicators, and false alerts during chop.
2. What Retail Traders ACTUALLY Want: Real-time news sentiment integration, plain-English trade reasoning ('Why' a trade is suggested), dynamic risk-to-reward position sizing, and live short-term tactical forecasts.
Format in professional Markdown with detailed bullet points."""
    
    append_to_markdown(path_m2, "# Retail User Pain-Point Intelligence & Copilot Feature Blueprint\n")
    append_to_markdown(path_m2, call_llm(p2_1))

    p2_2 = """You are a fintech product architect. Write an EXHAUSTIVE blueprint defining the UI/UX Layout and Feature Engine for an Institutional-Grade AI Copilot.
Include explicit specifications for:
1. Main Dashboard Layout: Live auto-updating candlestick chart, news ticker dropdown, and sidebar parameter controls.
2. The 20-to-80 Minute Forecast Engine: Probability percentage gauge, confidence score, and catalyst alignment panel.
3. Plain-English Explanation Card: Converting complex technical indicators (50 SMA, 200 SMA, RSI) into simple 2-sentence actionable summaries.
4. Mathematical Risk Calculator: Automatic stop-loss, take-profit, and position sizing calculation based on user dollar risk inputs ($).
Format in professional Markdown with step-by-step UI wireframe breakdowns."""
    
    append_to_markdown(path_m2, call_llm(p2_2))

    print("\n🎉 Real-World Catalysts & User Intelligence Library Successfully Constructed!")
    print(f"Files created in '{TARGET_DIR}/' with deep multi-thousand word textbooks.")

if __name__ == "__main__":
    build_real_world_library()