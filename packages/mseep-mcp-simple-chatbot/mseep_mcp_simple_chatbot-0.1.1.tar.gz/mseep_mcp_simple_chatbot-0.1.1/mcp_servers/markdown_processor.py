import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Create a Simple MCP Server
mcp = FastMCP("Markdown Reader and Writer Tool")


@mcp.tool()
def read_markdown_file(directory_path: str) -> str:
    """Read markdown files from a directory.

    Args:
        directory_path: The directory path where the markdown files are located.

    Returns:
        The content of the markdown file as a string, or an error message
        if the file doesn't exist.
    """
    # Construct the file paths
    file_paths = list(Path(directory_path).glob("*.md"))

    # Check if the files exist
    if not file_paths:
        return f"Error: No markdown files found in {directory_path}."

    # Read and return the file contents
    try:
        markdown_contents = []
        for file_path in file_paths:
            with open(file_path, "r", encoding="utf-8") as f:
                markdown_contents.append(f.read())

        return "\n\n".join(markdown_contents)
    except Exception as e:
        return f"Read markdown files error: {str(e)}"


@mcp.tool()
def write_markdown_file(directory_path: str, filename: str, content: str) -> str:
    """Write content to a markdown file in a specified directory,
    without overwriting existing files.

    Args:
        directory_path: The directory path where the markdown file will be written.
        filename: The name of the markdown file to create
            (if it doesn't end with .md, it will be added automatically).
        content: The markdown content to write to the file.

    Returns:
        A description of the operation result.
    """
    # Ensure the filename ends with .md
    if not filename.endswith(".md"):
        filename += ".md"

    # Construct the full file path
    file_path = Path(directory_path) / filename

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Check if the file already exists
    if file_path.exists():
        return (
            f"Error: File {file_path} already exists, "
            "operation canceled to prevent accidental overwrite."
        )

    # Write the file content
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: Markdown file saved to {file_path}"
    except Exception as e:
        return f"Write file error: {str(e)}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()
