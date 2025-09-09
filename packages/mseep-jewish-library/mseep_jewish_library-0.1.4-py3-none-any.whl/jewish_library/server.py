from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import asyncio
import os
import logging
import sys
import json
from .tantivy_search_agent import TantivySearchAgent

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('jewish_library.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('jewish_library')

# Initialize TantivySearchAgent with the index path
current_dir = os.path.dirname(os.path.abspath(__file__))
index_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "index")
try:
    search_agent = TantivySearchAgent(index_path)
    logger.info("Search agent initialized")
except Exception as e:
    logger.error(f"Failed to initialize search agent: {e}")
    raise


server = Server("jewish_library")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    logger.debug("Handling list_tools request")
    return [
        types.Tool(
            name="full_text_search",
            description="Full text searching in the jewish library",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": """
Instructions for generating a query:

1. Boolean Operators:

   - AND: term1 AND term2 (both required)
   - OR: term1 OR term2 (either term)
   - Multiple words default to OR operation (cloud network = cloud OR network)
   - AND takes precedence over OR
   - Example: Shabath AND (walk OR go)

2. Field-specific Terms:
   - Field-specific terms: field:term
   - Example: text:אדם AND reference:בראשית
   - available fields: text, reference, topics
   - text contains the text of the document
   - reference contains the citation of the document, e.g. בראשית, פרק א
   - topics contains the topics of the document. available topics includes: תנך, הלכה, מדרש, etc.

3. Required/Excluded Terms:
   - Required (+): +term (must contain)
   - Excluded (-): -term (must not contain)
   - Example: +security cloud -deprecated
   - Equivalent to: security AND cloud AND NOT deprecated

4. Phrase Search:
   - Use quotes: "exact phrase"
   - Both single/double quotes work
   - Escape quotes with \\"
   - Slop operator: "term1 term2"~N 
   - Example: "cloud security"~2 
   - the above will find "cloud framework and security "
   - Prefix matching: "start of phrase"*

5. Wildcards:
   - ? for single character
   - * for any number of characters
   - Example: sec?rity cloud*

6. Special Features:
   - All docs: * 
   - Boost terms: term^2.0 (positive numbers only)
   - Example: security^2.0 cloud
   - the above will boost security by 2.0
   
Query Examples:
1. Basic: +שבת +חולה +אסור
2. Field-specific: text:סיני AND topics:תנך
3. Phrase with slop: "security framework"~2
4. Complex: +reference:בראשית +text:"הבל"^2.0 +(דמי OR דמים) -הבלים
6. Mixed: (text:"רבנו משה"^2.0 OR reference:"משנה תורה") AND topics:הלכה) AND text:"תורה המלך"~3 AND NOT topics:מדרש

Tips:
- Group complex expressions with parentheses
- Use quotes for exact phrases
- Add + for required terms, - for excluded terms
- Boost important terms with ^N
- use field-specific terms for better results. 
- the corpus to search in is an ancient Hebrew corpus: Tora and Talmud. so Try to use ancient Hebrew terms and or Talmudic expressions and prevent modern words that are not common in talmudic texts
"""
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "The maximum number of results to return (default: 25)",
                        "default": 25,
                    },
                },
                "required": ["query"],
            },
        ),
   
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can search the Jewish library and return formatted results.
    """
    logger.debug(f"Handling call_tool request for {name} with arguments {arguments}")
    
    try:
        if not arguments:
            raise ValueError("Missing arguments")
    
        if name == "full_text_search":
            try:
                query = arguments.get("query")
                if not query:
                    raise ValueError("Missing query parameter")                
                num_results = arguments.get("num_results", 25)
                if not isinstance(num_results, int) or num_results <= 0:
                    raise ValueError("Invalid num_results parameter")
                
                logger.info(f"Searching with query: {query}")
                
                # Now do the actual search
                logger.debug(f"Executing search with query: {query}")
                results = await search_agent.search(query, num_results = num_results)
                logger.debug(f"Search completed: {len(results)} results")
                
                if not results or len(results) == 0:
                    logger.info("No results found")
                    return [types.TextContent(
                        type="text",
                        text="No results found"
                    )]
                
                formatted_results = []
                for result in results:
                    text = result.get('text', 'N/A')
                    reference = result.get('reference', 'N/A')
                    formatted_results.append(f"Reference: {reference}\nText: {text}\n")
                
                logger.info(f"Found {len(formatted_results)} results")
                response_text = "\n\n".join(formatted_results)
                logger.debug(f"Response text: {response_text}")
                
                return [
                    types.TextContent(
                        type="text",
                        text=response_text
                    )
                ]
            except Exception as err:
                logger.error(f"Search error: {err}", exc_info=True)
                return [types.TextContent(
                        type="text",
                        text=f"Error: {str(err)}"
                    )]
        
    
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
    
async def main():
    try:
        logger.info("Starting Jewish Library MCP server...")
            
        # Run the server using stdin/stdout streams
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jewish_library",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
