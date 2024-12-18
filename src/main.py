import uvicorn
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument('-a', '--address', type=str, help='IP address to bind to', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int, help='Port number to bind to', default=8000)
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development', default=False)

    parser.add_argument('-l', '--log_level', type=str, choices=['debug', 'info', 'warning', 'error'], help='Logging level', default='info')

    return parser.parse_args()

def main():
    args = get_args()
    uvicorn.run(
        "app:app", 
        host=args.address, 
        port=args.port, 
        reload=args.reload, 
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()