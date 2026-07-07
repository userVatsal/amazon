import time
import schedule
from main import run
import config

# Default to running every 6 hours if not specified
RUN_INTERVAL_HOURS = getattr(config, 'RUN_INTERVAL_HOURS', 6)

def job():
    print(f"\n--- Starting Scheduled Sourcing Run at {time.ctime()} ---")
    try:
        run()
    except Exception as e:
        print(f"Error during scheduled run: {e}")
    print(f"--- Scheduled Run Complete. Next run in {RUN_INTERVAL_HOURS} hours. ---\n")

def start():
    print(f"Sourcing Agent Scheduler started. Running every {RUN_INTERVAL_HOURS} hours.")
    # Run immediately on start
    job()

    schedule.every(RUN_INTERVAL_HOURS).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start()
