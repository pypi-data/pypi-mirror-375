# main.py (in root)
from mcpserver.server import mcp
import traceback

def main():
    try:
        mcp.run()
    except Exception as e:
        print(f"Error running server: {str(e)}")
        traceback.print_exc()