import ollama
import requests

def run_market_scan(search_query):
    print(f"\n🔍 Searching Reddit for: '{search_query}'...\n")
    
    # 1. Fetch public Reddit discussions (No API keys required)
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://www.reddit.com/search.json?q={search_query.replace(' ', '+')}&limit=10&sort=relevance"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        posts_text = ""
        for child in data.get('data', {}).get('children', []):
            post_data = child.get('data', {})
            title = post_data.get('title', '')
            snippet = post_data.get('selftext', '')[:300]
            posts_text += f"- Title: {title}\n  Snippet: {snippet}\n\n"
        
        if not posts_text:
            print("⚠️ No Reddit threads found for that query. Try a different search term.")
            return

        print("🤖 Feeding data to local Llama 3.2 for analysis...\n")
        
        # 2. Build the prompt payload for Ollama
        prompt = f"""You are a startup product strategist. Analyze these recent Reddit posts and user discussions about AI trading tools:

{posts_text}

Provide a concise breakdown using these exact headers:
### ❌ 1. Top User Frustrations & Complaints
- [List 2-3 major things users hate about existing apps]

### 💡 2. High-Demand Feature Requests
- [List 2-3 features users are actively begging for]

### 🚀 3. Winning Edge for Our Local App
- [1 sentence on how our local, zero-subscription, Ollama-powered app solves these exact problems]"""

        # 3. Call local Ollama AI
        res = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.4, 'num_ctx': 8192}
        )
        
        print("====== MARKET INTELLIGENCE REPORT ======\n")
        print(res['message']['content'])
        print("\n========================================")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    # Type whatever topic or competitor you want to investigate here:
    topic = input("Enter a search topic (e.g., 'tradingview ai complaints' or 'ai trading bot features'): ")
    if not topic.strip():
        topic = "AI trading bot complaints features"
    
    run_market_scan(topic)