import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_script(name, script_path):
    logging.info(f"Running {name} ...")
    result = subprocess.run(["python", script_path], capture_output=True, text=True)

    if result.stdout:
        logging.info(f"{name} Output:\n{result.stdout.strip()}")
    if result.stderr:
        logging.error(f"{name} Errors:\n{result.stderr.strip()}")

def main():
    logging.info("Starting daily news pipeline...")

    run_script("Scraper", "scraper.py")
    run_script("Clustering", "clustering.py")

    logging.info("Pipeline completed. articles_clustered.json is ready!")

if __name__ == "__main__":
    main()
