import json
import re
import ollama

def extract_and_parse_json(raw_text):
    """Robustly extracts JSON from raw LLM output, ignoring chatty text."""
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if not match:
        print(f"\n--- RAW MODEL OUTPUT THAT FAILED ---\n{raw_text}\n--------------------------------------")
        raise ValueError("No valid JSON structure found in model response.")
    return json.loads(match.group(0))

def build_chunked_knowledge_base():
    print("🧠 Starting Bulletproof Chunked Institutional Knowledge Compilation...")
    
    master_kb = {}

    # --- CHUNK 1: UI Rules & First Batch of Patterns ---
    print("\n⏳ [1/4] Generating UI Rules & Core Candlestick Patterns...")
    prompt_chunk1 = """You are a quantitative trading architect. Return a JSON object containing:
1. "ui_and_risk_rules": an array of 3 strict rules for a minimalist trading terminal.
2. "candlestick_library_deep_dive": an object containing deep technical breakdowns for "Bullish_Engulfing", "Bearish_Engulfing", "Hammer", and "Shooting_Star".

For EACH pattern, include:
- "structural_mechanics"
- "volume_and_location_requirements"
- "failure_and_invalidation_rules"

Return ONLY valid JSON. No preamble, no explanation."""

    try:
        res1 = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompt_chunk1}],
            options={'temperature': 0.1, 'num_ctx': 8192}
        )
        master_kb.update(extract_and_parse_json(res1['message']['content']))
        print("✅ Chunk 1 compiled successfully.")
    except Exception as e:
        print(f"❌ Error in Chunk 1: {e}")
        return

    # --- CHUNK 2: Remaining Patterns ---
    print("\n⏳ [2/4] Generating Additional Candlestick Patterns...")
    prompt_chunk2 = """You are a quantitative trading architect. Return a JSON object containing ONE key:
"candlestick_library_deep_dive_part2" with deep technical breakdowns for "Morning_Star", "Three_White_Soldiers", "Bullish_Harami", and "Pinbar_Rejection".

For EACH pattern, include:
- "structural_mechanics"
- "volume_and_location_requirements"
- "failure_and_invalidation_rules"

Return ONLY valid JSON. No conversational text."""

    try:
        res2 = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompt_chunk2}],
            options={'temperature': 0.1, 'num_ctx': 8192}
        )
        chunk2_data = extract_and_parse_json(res2['message']['content'])
        # Merge part 2 into main candlestick library dictionary if desired, or keep as subkey
        master_kb["candlestick_library_deep_dive"].update(chunk2_data.get("candlestick_library_deep_dive_part2", {}))
        print("✅ Chunk 2 compiled successfully.")
    except Exception as e:
        print(f"❌ Error in Chunk 2: {e}")
        return

    # --- CHUNK 3: Asset Class Behavioral Profiles ---
    print("\n⏳ [3/4] Generating Asset Class Behavioral Profiles...")
    prompt_chunk3 = """You are a quantitative trading architect. Return a JSON object containing ONE key:
"asset_class_behavioral_profiles" covering "Traditional_Equities", "Major_Cryptocurrencies", and "High_Volatility_Memecoins".

For EACH asset class, provide:
- "core_drivers"
- "technical_respect"

Return ONLY valid JSON."""

    try:
        res3 = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompt_chunk3}],
            options={'temperature': 0.1, 'num_ctx': 8192}
        )
        master_kb.update(extract_and_parse_json(res3['message']['content']))
        print("✅ Chunk 3 compiled successfully.")
    except Exception as e:
        print(f"❌ Error in Chunk 3: {e}")
        return

    # --- CHUNK 4: Event Mechanics & Math Models ---
    print("\n⏳ [4/4] Generating Event Mechanics & Quantitative Risk Math Models...")
    prompt_chunk4 = """You are a quantitative trading architect. Return a JSON object containing TWO keys:
1. "event_and_product_price_mechanics_deep_dive" covering "product_launch_buy_rumor_sell_news", "earnings_and_macro_surprises", and "memecoin_sentiment_velocity".
2. "quantitative_risk_math_models" covering "position_sizing_formula_breakdown", "risk_reward_ratio_rule", "atr_volatility_buffer", and "event_driven_sizing_modifier".

Return ONLY valid JSON."""

    try:
        res4 = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompt_chunk4}],
            options={'temperature': 0.1, 'num_ctx': 8192}
        )
        master_kb.update(extract_and_parse_json(res4['message']['content']))
        print("✅ Chunk 4 compiled successfully.")
    except Exception as e:
        print(f"❌ Error in Chunk 4: {e}")
        return

    # --- FINAL SAVE ---
    with open("app_knowledge_base.json", "w", encoding="utf-8") as f:
        json.dump(master_kb, f, indent=2)
        
    print("\n🎉 SUCCESS! Full Institutional Knowledge Base compiled and saved to 'app_knowledge_base.json'.")

if __name__ == "__main__":
    build_chunked_knowledge_base()