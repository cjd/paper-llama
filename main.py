import argparse
import sys
import threading
from src.paperless_client import PaperlessClient
from src.llm_client import OllamaClient
from src.utils import logger, get_user_prompt
from src.processor import process_single_document, run_auto_mode
from src.webhook import run_webhook_mode


def run():
    parser = argparse.ArgumentParser(description="PaperLlama")
    parser.add_argument("--mode", choices=["auto", "manual", "webhook"], default="auto", help="Execution mode")
    parser.add_argument("--doc-id", type=int, help="Document ID for manual mode")
    parser.add_argument("--dry-run", action="store_true", help="Log changes without applying them to Paperless")
    
    args = parser.parse_args()

    try:
        p_client = PaperlessClient()
        o_client = OllamaClient()
    except Exception as e:
        logger.critical(f"Initialization failed: {e}")
        sys.exit(1)



    if args.mode == "manual":
        if not args.doc_id:
            logger.error("Manual mode requires --doc-id")
            sys.exit(1)
        p_client.refresh_metadata()
        prompt = get_user_prompt(p_client)
        process_single_document(args.doc_id, prompt, p_client, o_client, args.dry_run)
        
    elif args.mode == "auto":
        run_auto_mode(p_client, o_client, args.dry_run)
        
    elif args.mode == "webhook":
        # Start auto mode in a background thread
        logger.info("Starting auto mode in background...")
        polling_thread = threading.Thread(
            target=run_auto_mode, 
            args=(p_client, o_client, args.dry_run),
            daemon=True
        )
        polling_thread.start()
        
        # Start webhook mode (blocking)
        run_webhook_mode(p_client, o_client, args.dry_run)

if __name__ == "__main__":
    run()
