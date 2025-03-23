import subprocess

def run_script(name, script_path):
    print(f"🚀 Running {name} ...")
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"⚠️ Errors while running {name}:\n{result.stderr}")

def main():
    print("🧠 Starting daily news pipeline...")

    # Step 1: Scrape fresh articles
    run_script("Scraper", "scraper.py")

    # Step 2: Cluster news articles
    run_script("Clustering", "clustering.py")

    print("✅ Pipeline completed. articles_clustered.json is ready!")

if __name__ == "__main__":
    main()
