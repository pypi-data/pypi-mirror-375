import json
import argparse
import webbrowser
from .server import Backend,Config

def main():
    parser = argparse.ArgumentParser(
        description="Temporary Email Generator (Flask-based)",
        epilog="Example: python main.py --host 0.0.0.0 --port 8080 --no-browser"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port number (default: 5000)")
    parser.add_argument("--no-browser", action="store_true", help="Disable auto-opening the browser")
    parser.add_argument("--config", action="store_true", help="Edit configuration file (config.json)")

    args = parser.parse_args()

    if args.config:
        print("Current configuration:")
        print(json.dumps(Config.CONFIG, indent=4))
        key_list = input("Enter new API keys (space separated) or leave empty to keep: ").strip()
        if key_list:
            Config.CONFIG["rapid_api_keys"] += [k.strip() for k in key_list.split(" ")]
            Config.CONFIG["rapid_api_keys"] = list(set(Config.CONFIG["rapid_api_keys"]))
    
        new_host = input(f"API Host [{Config.CONFIG['api_host']}]: ").strip()
        if new_host:
            Config.CONFIG["api_host"] = new_host
    
        new_base = input(f"API Base URL [{Config.CONFIG['api_base_url']}]: ").strip()
        if new_base:
            Config.CONFIG["api_base_url"] = new_base
            
        Config.save_config()
        print("Configuration updated!")
        return

    if not args.no_browser:
        webbrowser.open(f"http://{args.host}:{args.port}/")
    Backend().run(debug=False, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
