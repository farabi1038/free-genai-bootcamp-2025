from duckduckgo_search import DDGS
from typing import List, Dict
import logging
import asyncio

# Configure logging
logger = logging.getLogger('song_vocab')

async def search_web_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web for Japanese song lyrics using DuckDuckGo Search.
    
    Args:
        query (str): Search query for the song lyrics
        max_results (int): Maximum number of search results to return
        
    Returns:
        List[Dict[str, str]]: List of search results with title and url
    """
    logger.info(f"Starting DuckDuckGo search for: {query}")
    
    # Add Japanese-specific keywords to improve results
    japanese_keywords = ["歌詞", "lyrics", "日本語", "カタカナ", "ひらがな", "J-Lyric", "uta-net", "utamap", "utaten"]
    
    # Check if query already contains Japanese characters
    has_japanese = any(0x3040 <= ord(c) <= 0x30ff or 0x4e00 <= ord(c) <= 0x9fff for c in query)
    
    if not has_japanese:
        # For non-Japanese queries, add translation hint
        enhanced_query = f"{query} japanese 日本語 歌詞 lyrics site:uta-net.com OR site:j-lyric.net OR site:utamap.com OR site:utaten.com"
    else:
        # For queries with Japanese characters, preserve them but add site targeting
        enhanced_query = f"{query} 歌詞 site:uta-net.com OR site:j-lyric.net OR site:utamap.com OR site:utaten.com"
    
    logger.info(f"Enhanced query: {enhanced_query}")
    
    try:
        # Run the search in a thread to avoid blocking
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            search_results = await loop.run_in_executor(
                None, 
                lambda: _perform_search(enhanced_query, max_results)
            )
        except Exception as e:
            logger.error(f"Search execution error: {str(e)}")
            # Return empty result instead of fallback
            return []
        
        logger.info(f"Found {len(search_results)} results from DuckDuckGo")
        return search_results
        
    except Exception as e:
        logger.error(f"Error during DuckDuckGo search: {str(e)}", exc_info=True)
        return []

def _perform_search(query: str, max_results: int) -> List[Dict[str, str]]:
    """Helper function to perform the actual search in a separate thread."""
    try:
        search_results = []
        
        # Create DDGS instance
        with DDGS() as ddgs:
            # Perform the search with region set to Japan
            results = ddgs.text(
                query, 
                region="jp",
                safesearch="off", 
                timelimit="y",  # results from last year
                max_results=max_results
            )
            
            # Process results
            for r in results:
                result = {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                }
                search_results.append(result)
                logger.debug(f"Found result: {result['title']} ({result['url']})")
                
        return search_results
        
    except Exception as e:
        logger.error(f"Error in _perform_search: {str(e)}", exc_info=True)
        return []

def get_fallback_results(query: str) -> List[Dict[str, str]]:
    """
    Provide fallback results when the search API fails.
    
    Args:
        query (str): The original search query
        
    Returns:
        List[Dict[str, str]]: List of hardcoded search results
    """
    logger.warning("Using fallback search results due to API failure")
    
    # Check if the query is about YOASOBI's 夜に駆ける
    if "YOASOBI" in query and "夜に駆ける" in query:
        return [
            {
                "title": "YOASOBI「夜に駆ける」Official Music Video - YouTube",
                "url": "https://www.youtube.com/watch?v=x8VYWazR5mE",
                "snippet": "YOASOBI 1st EP「THE BOOK」."
            },
            {
                "title": "夜に駆ける (Yoru ni Kakeru) - YOASOBI Lyrics & Translation",
                "url": "https://vgmsite.com/soundtracks/demo/pgdhjsfu/01%20-%20Untitled.mp3",
                "snippet": "Japanese lyrics for 夜に駆ける by YOASOBI with English translation."
            }
        ]
    
    # Generic fallback for other queries
    return [
        {
            "title": f"Search results for {query}",
            "url": "https://example.com/search",
            "snippet": "Fallback search result due to API limitations."
        }
    ] 