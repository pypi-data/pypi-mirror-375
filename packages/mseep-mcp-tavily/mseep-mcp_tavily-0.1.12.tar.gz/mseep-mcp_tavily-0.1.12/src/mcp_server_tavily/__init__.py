from .server import serve
from dotenv import load_dotenv


def main():
    """MCP Tavily Server - AI-powered web search functionality for MCP"""
    import argparse
    import asyncio
    import os
    
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="give a model the ability to perform AI-powered web searches using Tavily"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Tavily API key (can also be set via TAVILY_API_KEY environment variable)",
    )

    args = parser.parse_args()
    
    # Check for API key in args first, then environment
    api_key = args.api_key or os.getenv("TAVILY_API_KEY")
    if not api_key:
        parser.error("Tavily API key must be provided either via --api-key or TAVILY_API_KEY environment variable")
    
    asyncio.run(serve(api_key))


if __name__ == "__main__":
    main()