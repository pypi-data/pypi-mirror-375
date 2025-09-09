import asyncio

from mcp_allthetools.server import main as entrypoint

def main() -> None:
    print("Hello from mcp-allthetools!")
    asyncio.run(entrypoint())

if __name__ == "__main__":
    main()