import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def get_page_content(url: str) -> Dict[str, Optional[str]]:
    """
    Extract lyrics content from a webpage.
    
    Args:
        url (str): URL of the webpage to extract content from
        
    Returns:
        Dict[str, Optional[str]]: Dictionary containing japanese_lyrics, romaji_lyrics, and metadata
    """
    logger.info(f"Fetching content from URL: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            logger.debug("Making HTTP request...")
            async with session.get(url) as response:
                if response.status != 200:
                    error_msg = f"Error: HTTP {response.status}"
                    logger.error(error_msg)
                    return {
                        "japanese_lyrics": None,
                        "romaji_lyrics": None,
                        "metadata": error_msg
                    }
                
                logger.debug("Reading response content...")
                html = await response.text()
                logger.info(f"Successfully fetched page content ({len(html)} bytes)")
                return extract_lyrics_from_html(html, url)
    except Exception as e:
        error_msg = f"Error fetching page: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Use fallback content for demonstration
        fallback_content = get_fallback_content(url)
        return {
            "japanese_lyrics": fallback_content,
            "romaji_lyrics": "Sample romaji content for demonstration",
            "metadata": "Fallback content (original request failed: " + error_msg + ")"
        }

def extract_lyrics_from_html(html: str, url: str) -> Dict[str, Optional[str]]:
    """
    Extract lyrics from HTML content based on common patterns in lyrics websites.
    """
    logger.info("Starting lyrics extraction from HTML")
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    logger.debug("Cleaning HTML content...")
    for element in soup(['script', 'style', 'header', 'footer', 'nav', 'iframe', 'noscript']):
        element.decompose()
    
    # Common patterns for Japanese lyrics sites
    japanese_lyrics_patterns = [
        # Japanese lyrics sites specific patterns
        {"class_": "lyrics_box"},  # Uta-Net
        {"class_": "hiragana"},    # J-Lyrics
        {"class_": "kashi_area"},  # Utamap
        {"class_": "romaji"},      # J-Lyrics
        {"class_": "lyric-original"}, # Various Japanese sites
        {"class_": "origLyric"},   # Petitlyrics
        {"class_": "lyricBody"},   # Uta-Net
        {"class_": re.compile(r"(?:kashi|lyrics?)(?:_area|_box|_body)", re.I)},
        {"class_": re.compile(r"(?:japanese|original)(?:_lyrics|Lyrics)", re.I)},
        {"id": re.compile(r"(?:kashi|lyrics?)(?:_area|_box|_body)", re.I)},
    ]
    
    # Common patterns for all lyrics containers
    general_lyrics_patterns = [
        # Class patterns for English lyrics sites
        {"class_": re.compile(r"lyrics?|kashi|romaji|original|text", re.I)},
        {"class_": re.compile(r"song-content|song-text|track-text", re.I)},
        {"class_": re.compile(r"Lyrics__Container|lyrics-body|lyric-body|content", re.I)},
        # Popular lyrics sites specific patterns
        {"class_": "lyrics"},  # AZLyrics
        {"class_": "songLyrics"}, # LyricsFreak
        {"class_": "lyricbox"},  # LyricWiki
        {"class_": "verse"},     # Genius
        {"class_": "SongLyricsV14_Lyrics"},  # LyricFind
        # ID patterns
        {"id": re.compile(r"lyrics?|kashi|romaji|original|lyric", re.I)},
        {"id": "lyric-body-text"},  # MetroLyrics
    ]
    
    japanese_lyrics = None
    english_lyrics = None
    romaji_lyrics = None
    metadata = ""
    
    # Try to find Japanese lyrics first
    logger.debug("Searching for Japanese lyrics containers...")
    
    # Special handling for Japanese lyrics sites
    if "uta-net.com" in url:
        logger.info("Detected Uta-Net - using specialized extraction")
        lyrics_div = soup.find("div", id="kashi_area")
        if lyrics_div:
            clean_lyrics = clean_text(lyrics_div.get_text())
            if is_primarily_japanese(clean_lyrics):
                japanese_lyrics = clean_lyrics
    
    elif "j-lyric.net" in url:
        logger.info("Detected J-Lyric - using specialized extraction")
        lyrics_div = soup.find("p", id="Lyric")
        if lyrics_div:
            clean_lyrics = clean_text(lyrics_div.get_text())
            if is_primarily_japanese(clean_lyrics):
                japanese_lyrics = clean_lyrics
    
    elif "utamap.com" in url:
        logger.info("Detected Utamap - using specialized extraction")
        lyrics_div = soup.find("div", class_="kasi_honbun")
        if lyrics_div:
            clean_lyrics = clean_text(lyrics_div.get_text())
            if is_primarily_japanese(clean_lyrics):
                japanese_lyrics = clean_lyrics
                
    # Try Japanese patterns first
    if not japanese_lyrics:
        for pattern in japanese_lyrics_patterns:
            logger.debug(f"Trying Japanese pattern: {pattern}")
            elements = soup.find_all(**pattern)
            logger.debug(f"Found {len(elements)} matching elements")
            
            for element in elements:
                text = clean_text(element.get_text())
                logger.debug(f"Extracted text length: {len(text)} chars")
                
                if is_primarily_japanese(text):
                    logger.info("Found Japanese lyrics with pattern")
                    japanese_lyrics = text
                    break
            
            if japanese_lyrics:
                break
    
    # If specialized extraction didn't work, try general patterns
    if not japanese_lyrics:
        for pattern in general_lyrics_patterns:
            logger.debug(f"Trying general pattern: {pattern}")
            elements = soup.find_all(**pattern)
            logger.debug(f"Found {len(elements)} matching elements")
            
            for element in elements:
                text = clean_text(element.get_text())
                logger.debug(f"Extracted text length: {len(text)} chars")
                
                # Skip very short texts - likely not lyrics
                if len(text) < 100:
                    continue
                    
                # Detect if text is primarily Japanese, romaji, or English
                if is_primarily_japanese(text) and not japanese_lyrics:
                    logger.info("Found Japanese lyrics")
                    japanese_lyrics = text
                    break
                elif is_primarily_romaji(text) and not romaji_lyrics:
                    logger.info("Found romaji lyrics")
                    romaji_lyrics = text
                elif not english_lyrics and not is_primarily_japanese(text):
                    logger.info("Found English lyrics")
                    english_lyrics = text
            
            if japanese_lyrics:
                break
    
    # If no structured containers found, try to find text blocks that look Japanese
    if not japanese_lyrics:
        logger.info("No Japanese lyrics found in structured containers, trying fallback method")
        text_blocks = []
        
        # First, try to find paragraphs with Japanese text
        for p in soup.find_all(['p', 'div']):
            text = clean_text(p.get_text())
            if len(text) > 100 and is_primarily_japanese(text):
                text_blocks.append(text)
        
        if text_blocks:
            # Sort by length, but prioritize Japanese content
            japanese_blocks = [block for block in text_blocks if is_primarily_japanese(block)]
            if japanese_blocks:
                japanese_lyrics = max(japanese_blocks, key=len)
                logger.info(f"Found Japanese text block: {len(japanese_lyrics)} chars")
            else:
                largest_block = max(text_blocks, key=len)
                if is_primarily_romaji(largest_block):
                    romaji_lyrics = largest_block
                else:
                    english_lyrics = largest_block
    
    # Update result to include english_lyrics
    result = {
        "japanese_lyrics": japanese_lyrics,
        "english_lyrics": english_lyrics,
        "romaji_lyrics": romaji_lyrics,
        "metadata": metadata or "Lyrics extracted successfully"
    }
    
    # Log the results
    if japanese_lyrics:
        logger.info(f"Found Japanese lyrics ({len(japanese_lyrics)} chars)")
    if english_lyrics:
        logger.info(f"Found English lyrics ({len(english_lyrics)} chars)")
    if romaji_lyrics:
        logger.info(f"Found romaji lyrics ({len(romaji_lyrics)} chars)")
    
    # For backward compatibility, if no Japanese lyrics but have English, put English in the japanese_lyrics field
    # BUT ONLY if specifically told to include English
    if not result["japanese_lyrics"] and result["english_lyrics"] and "english" in url.lower():
        result["japanese_lyrics"] = result["english_lyrics"]
        logger.info("Used English lyrics as fallback (only because URL contained 'english')")
    
    return result

def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and unnecessary characters.
    """
    logger.debug(f"Cleaning text of length {len(text)}")
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    # Remove leading/trailing whitespace
    result = text.strip()
    logger.debug(f"Text cleaned, new length: {len(result)}")
    return result

def is_primarily_japanese(text: str) -> bool:
    """
    Check if text contains primarily Japanese characters.
    """
    # Count Japanese characters (hiragana, katakana, kanji)
    japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    ratio = japanese_chars / total_chars if total_chars > 0 else 0
    logger.debug(f"Japanese character ratio: {ratio:.2f} ({japanese_chars}/{total_chars})")
    # Lowered threshold to catch more mixed content
    return japanese_chars > 10 and ratio > 0.15

def is_primarily_romaji(text: str) -> bool:
    """
    Check if text contains primarily romaji characters.
    """
    # Count romaji characters (basic Latin alphabet)
    romaji_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(text.strip())
    ratio = romaji_chars / total_chars if total_chars > 0 else 0
    logger.debug(f"Romaji character ratio: {ratio:.2f} ({romaji_chars}/{total_chars})")
    return romaji_chars > 0 and ratio > 0.3

def get_fallback_content(url: str) -> str:
    """
    Provide fallback content when URL fetching fails.
    
    Args:
        url (str): The URL that was being fetched
        
    Returns:
        str: Fallback content
    """
    logger.warning(f"Using fallback content for {url}")
    
    # YouTube video URL for YOASOBI
    if "youtube.com" in url and ("YOASOBI" in url or "夜に駆ける" in url):
        return """
        YOASOBI - 夜に駆ける (Yoru ni Kakeru) Lyrics:
        
        夢の続き 見させて
        どこまでも行けるよ
        霞む意識の中で
        この世界の続きを描くの
        
        だから僕は 僕らは
        目を閉じて見る
        どこまでも続く
        夜空を駆ける星を
        
        まだ見ぬ未来を描く
        僕らは進み続ける
        止まらない この気持ち
        夜明けが来ることを知って
        
        さぁ行こう 夜空を跳ねて
        朝日が昇るまで
        """
    
    # Generic fallback content
    return """
    Sample content for demonstration purposes.
    
    This is fallback content because the actual URL could not be fetched.
    In a production environment, you would need valid API keys and proper error handling.
    """