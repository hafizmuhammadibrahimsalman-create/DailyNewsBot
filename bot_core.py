
import argparse, logging, time, sys, json
from pathlib import Path
from datetime import datetime

# UTF-8 Setup
if sys.platform == 'win32': sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))

from news_fetcher import NewsFetcher
from ai_summarizer import GeminiSummarizer
from whatsapp_sender import WhatsAppSender
from config import TOPICS, LOG_FILE
from analytics import Analytics
from video_generator import generate_video

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true', help='No send')
    p.add_argument('--test', action='store_true', help='Test send')
    p.add_argument('--fetch-only', action='store_true', help='Fetch only')
    p.add_argument('--json-output', action='store_true', help='JSON out')
    args = p.parse_args()
    
    start = time.time()
    
    try:
        # TEST MODE
        if args.test:
            WhatsAppSender().send_message("🧪 Test Message")
            Analytics.log_run(time.time()-start, True, 0)
            return 0

        # FETCH
        fetcher = NewsFetcher()
        all_news = fetcher.fetch_all_news()
        count = sum(len(a) for a in all_news.values())
        
        if args.fetch_only:
            print(f"Fetched {count} articles.")
            Analytics.log_run(time.time()-start, True, count)
            return 0

        # SUMMARIZE
        summarizer = GeminiSummarizer()
        filtered = {k: summarizer.filter_relevant_news(v, k) for k, v in all_news.items() if v}
        report = summarizer.create_intelligence_report(filtered)
        
        # VIDEO
        vid_path = ""
        if args.json_output:
            vid_path = generate_video(filtered) # Only generate video if in automation mode for now

        # SEND / OUT
        if args.json_output:
            print(json.dumps({"status": "success", "report": report, "video": str(vid_path), "count": count}))
        elif not args.dry_run:
            WhatsAppSender().send_message(report)
        else:
            print(f"--- REPORT PREVIEW ---\n{report}")
            
        Analytics.log_run(time.time()-start, True, count)
        return 0

    except Exception as e:
        if args.json_output: print(json.dumps({"status": "error", "message": str(e)}))
        else: logger.error(f"Error: {e}")
        Analytics.log_run(time.time()-start, False, 0)
        return 1

if __name__ == "__main__": sys.exit(main())
