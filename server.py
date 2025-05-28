import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from app import getDefinitions, getWordDetails

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("dictionary-mcp")

@mcp.tool()
async def get_definitions(word: str) -> str:
    """
    Get definitions for a word using Dictionary API.
    
    Args:
        word: The word to get definitions for
    
    Returns:
        Definitions of the word or error message
    """
    try:
        if not word or not word.strip():
            return "Please provide a valid word."
        
        logger.info(f"Getting definitions for: {word}")
        
        # Run the synchronous function in a thread pool
        loop = asyncio.get_event_loop()
        definitions = await loop.run_in_executor(None, getDefinitions, word.strip())
        
        if not definitions or definitions == "No definitions found.":
            return f"No definitions found for '{word}'."
        
        return f"Definitions for '{word.upper()}':\n\n{definitions}"
        
    except Exception as e:
        error_msg = f"Error getting definitions: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def get_word_details(word: str) -> str:
    """
    Get detailed word information including pronunciation, synonyms, and examples.
    
    Args:
        word: The word to get detailed information for
    
    Returns:
        Detailed word information or error message
    """
    try:
        if not word or not word.strip():
            return "Please provide a valid word."
        
        logger.info(f"Getting detailed info for: {word}")
        
        # Run the synchronous function in a thread pool
        loop = asyncio.get_event_loop()
        details = await loop.run_in_executor(None, getWordDetails, word.strip())
        
        if not details or details == "No word details found.":
            return f"No detailed information found for '{word}'."
        
        return details
        
    except Exception as e:
        error_msg = f"Error getting word details: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
async def search_word(query: str) -> str:
    """
    Search for a word and provide basic information.
    
    Args:
        query: The word or phrase to search for
    
    Returns:
        Search results or suggestions
    """
    try:
        if not query or not query.strip():
            return "Please provide a valid search query."
        
        query = query.strip().lower()
        logger.info(f"Searching for: {query}")
        
        # First try exact match
        loop = asyncio.get_event_loop()
        definitions = await loop.run_in_executor(None, getDefinitions, query)
        
        if definitions and definitions != "No definitions found.":
            return f"Found '{query}':\n\n{definitions}"
        
        # If no exact match, try variations
        variations = [
            query + 's',           # plural
            query + 'ed',          # past tense
            query + 'ing',         # present participle
            query[:-1] if len(query) > 3 else query,  # remove last letter
            query[:-2] if len(query) > 4 else query,  # remove last 2 letters
        ]
        
        found_variations = []
        for variation in variations:
            try:
                var_definitions = await loop.run_in_executor(None, getDefinitions, variation)
                if var_definitions and var_definitions != "No definitions found.":
                    found_variations.append(variation)
                    if len(found_variations) >= 3:  # Limit to 3 suggestions
                        break
            except:
                continue
        
        if found_variations:
            return f"'{query}' not found. Did you mean: {', '.join(found_variations)}?"
        else:
            return f"No results found for '{query}'. Please check the spelling."
        
    except Exception as e:
        error_msg = f"Error during search: {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    try:
        logger.info("Starting Dictionary MCP Server...")
        logger.info("Available tools: get_definitions, get_word_details, search_word")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
