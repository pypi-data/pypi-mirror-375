from mcp.server.fastmcp import FastMCP
import uuid
import sys

# Initialize FastMCP server
mcp = FastMCP("uuid_generator")

@mcp.tool()
async def get_uuid() -> str:
    """
    Generate a random UUID and return it as a string.
    
    Returns:
        str: A randomly generated UUID in string format.
    """
    return str(uuid.uuid4())


def generate_uuid_cli():
    """Generate and print a UUID for command-line usage."""
    print(uuid.uuid4())


if __name__ == "__main__":
    # Check for --noserver option
    if "--noserver" in sys.argv:
        generate_uuid_cli()
    else:
        # Initialize and run the server
        mcp.run(transport='stdio')