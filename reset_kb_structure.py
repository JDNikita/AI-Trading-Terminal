import os
import shutil

def reset_knowledge_base():
    base_dir = "knowledge_base"
    
    # Define the standardized directory structure
    target_dirs = {
        "microstructure": os.path.join(base_dir, "microstructure"),
        "event_playbooks": os.path.join(base_dir, "event_playbooks"),
        "sentiment_intelligence": os.path.join(base_dir, "sentiment_intelligence"),
        "risk_math": os.path.join(base_dir, "risk_math")
    }

    print("🧹 Cleaning and resetting knowledge base file structure...\n")

    # 1. Create target directories if they don't exist
    for folder_path in target_dirs.values():
        os.makedirs(folder_path, exist_ok=True)

    # 2. Map existing files to their proper home based on keywords in their names
    if os.path.exists(base_dir):
        for root, _, files in os.walk(base_dir):
            for file in files:
                if not file.endswith(".md"):
                    continue
                
                src_path = os.path.join(root, file)
                filename_lower = file.lower()
                
                # Determine destination based on file content/name keywords
                if any(k in filename_lower for k in ["candle", "microstructure", "pattern", "geometry"]):
                    dest_dir = target_dirs["microstructure"]
                elif any(k in filename_lower for k in ["event", "macro", "launch", "news"]):
                    dest_dir = target_dirs["event_playbooks"]
                elif any(k in filename_lower for k in ["sentiment", "review", "app", "reddit"]):
                    dest_dir = target_dirs["sentiment_intelligence"]
                elif any(k in filename_lower for k in ["risk", "formula", "sizing", "atr"]):
                    dest_dir = target_dirs["risk_math"]
                else:
                    dest_dir = target_dirs["microstructure"]

                dest_path = os.path.join(dest_dir, file)
                
                if os.path.abspath(src_path) != os.path.abspath(dest_path):
                    shutil.move(src_path, dest_path)
                    print(f"📦 Moved: {file} ➡️  {os.path.relpath(dest_path, base_dir)}")

    # 3. Clean up residual folders safely (ignoring permission locks)
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item_path not in target_dirs.values():
            try:
                shutil.rmtree(item_path, ignore_errors=True)
            except Exception:
                pass

    print("\n✅ Knowledge Base successfully reset to standard structure:")
    print(" 📂 knowledge_base/")
    print(" ├── 📁 microstructure/")
    print(" ├── 📁 event_playbooks/")
    print(" ├── 📁 sentiment_intelligence/")
    print(" └── 📁 risk_math/")

if __name__ == "__main__":
    reset_knowledge_base()