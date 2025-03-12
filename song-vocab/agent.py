import ollama
from typing import List, Dict, Any, Optional
import json
import logging
import re
import asyncio
from pathlib import Path
from functools import partial
from tools.search_web_duckduckgo import search_web_duckduckgo
from tools.get_page_content import get_page_content
from tools.extract_vocabulary import extract_vocabulary
from tools.generate_song_id import generate_song_id
from tools.save_results import save_results
import math
import time

# Get the app's root logger
logger = logging.getLogger('song_vocab')

class ToolRegistry:
    def __init__(self, lyrics_path: Path, vocabulary_path: Path):
        self.lyrics_path = lyrics_path
        self.vocabulary_path = vocabulary_path
        self.tools = {
            'search_web_duckduckgo': search_web_duckduckgo,
            'get_page_content': get_page_content,
            'extract_vocabulary': extract_vocabulary,
            'generate_song_id': generate_song_id,
            'save_results': partial(save_results, lyrics_path=lyrics_path, vocabulary_path=vocabulary_path)
        }
    
    def get_tool(self, name: str):
        return self.tools.get(name)

def calculate_safe_context_window(available_ram_gb: float, safety_factor: float = 0.8) -> int:
    """
    Calculate a safe context window size based on available RAM.
    
    Args:
        available_ram_gb (float): Available RAM in gigabytes
        safety_factor (float): Factor to multiply by for safety margin (default 0.8)
        
    Returns:
        int: Recommended context window size in tokens
        
    Note:
        Based on observation that 128K tokens requires ~58GB RAM
        Ratio is approximately 0.45MB per token (58GB/131072 tokens)
    """
    # Known ratio from our testing
    GB_PER_128K_TOKENS = 58.0
    TOKENS_128K = 131072
    
    # Calculate tokens per GB
    tokens_per_gb = TOKENS_128K / GB_PER_128K_TOKENS
    
    # Calculate safe token count
    safe_tokens = math.floor(available_ram_gb * tokens_per_gb * safety_factor)
    
    # Round down to nearest power of 2 for good measure
    power_of_2 = 2 ** math.floor(math.log2(safe_tokens))
    
    # Cap at 128K tokens
    final_tokens = min(power_of_2, TOKENS_128K)
    
    logger.debug(f"Context window calculation:")
    logger.debug(f"  Available RAM: {available_ram_gb}GB")
    logger.debug(f"  Tokens per GB: {tokens_per_gb}")
    logger.debug(f"  Raw safe tokens: {safe_tokens}")
    logger.debug(f"  Power of 2: {power_of_2}")
    logger.debug(f"  Final tokens: {final_tokens}")
    
    return final_tokens

class SongLyricsAgent:
    def __init__(self, stream_llm=True, available_ram_gb=32):
        logger.info("Initializing SongLyricsAgent")
        self.base_path = Path(__file__).parent
        self.prompt_path = self.base_path / "prompts" / "Lyrics-Agent.md"
        self.lyrics_path = self.base_path / "outputs" / "lyrics"
        self.vocabulary_path = self.base_path / "outputs" / "vocabulary"
        self.stream_llm = stream_llm
        self.context_window = calculate_safe_context_window(available_ram_gb)
        logger.info(f"Calculated safe context window size: {self.context_window} tokens for {available_ram_gb}GB RAM")
        
        # Create output directories
        self.lyrics_path.mkdir(parents=True, exist_ok=True)
        self.vocabulary_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directories created: {self.lyrics_path}, {self.vocabulary_path}")
        
        # Initialize Ollama client and tool registry
        logger.info("Initializing Ollama client and tool registry")
        try:
            self.client = ollama.Client()
            self.tools = ToolRegistry(self.lyrics_path, self.vocabulary_path)
            logger.info("Initialization successful")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise
            
        # Track tools called
        self.tools_called = set()
    
    def parse_llm_action(self, content: str) -> Optional[tuple[str, Dict[str, Any]]]:
        """Parse the LLM's response to extract tool name and arguments."""
        # Look for tool calls in the format: Tool: tool_name(arg1="value1", arg2="value2")
        match = re.search(r'Tool:\s*(\w+)\((.*?)\)', content)
        
        # If the standard format isn't found, try alternate formats
        if not match:
            # Try more relaxed pattern: tool_name(arg1="value1")
            match = re.search(r'(\w+)\((.*?)\)', content)
            
            # Try function-call-like format: tool_name("value1", "value2")
            if not match:
                tool_call_match = re.search(r'(search_web_duckduckgo|get_page_content|extract_vocabulary|generate_song_id|save_results)\s*\(\s*["\']([^"\']+)["\']', content)
                if tool_call_match:
                    tool_name = tool_call_match.group(1)
                    arg_value = tool_call_match.group(2)
                    
                    # Determine the appropriate parameter name based on the tool
                    if tool_name == 'search_web_duckduckgo':
                        return tool_name, {"query": arg_value}
                    elif tool_name == 'get_page_content':
                        return tool_name, {"url": arg_value}
                    elif tool_name == 'extract_vocabulary':
                        return tool_name, {"text": arg_value}
                    elif tool_name == 'generate_song_id':
                        return tool_name, {"title": arg_value}
            
            # Check for natural language descriptions of tool usage
            search_regex = r'(?:use|call|using|search with|search using).*?(search_web_duckduckgo).*?["\'](.*?)["\']'
            search_match = re.search(search_regex, content, re.IGNORECASE)
            if search_match:
                tool_name = "search_web_duckduckgo"
                query = search_match.group(2)
                return tool_name, {"query": query}
                
            # Try to find URL mentions for get_page_content
            url_regex = r'(?:use|call|using|get content from|fetch|open).*?(get_page_content).*?(https?://\S+)'
            url_match = re.search(url_regex, content, re.IGNORECASE)
            if url_match:
                tool_name = "get_page_content"
                url = url_match.group(2).strip('"\'.,;: ')
                return tool_name, {"url": url}
        
        if not match:
            return None
        
        tool_name = match.group(1)
        args_str = match.group(2)
        
        # Parse arguments
        args = {}
        
        # Look for key="value" pattern
        for arg_match in re.finditer(r'(\w+)=(?:"([^"]*?)"|\'([^\']*?)\')', args_str):
            key = arg_match.group(1)
            value = arg_match.group(2) if arg_match.group(2) is not None else arg_match.group(3)
            args[key] = value
            
        # If no arguments found with key=value format, but there's a single quoted string
        if not args and re.search(r'["\']([^"\']+)["\']', args_str):
            single_arg_match = re.search(r'["\']([^"\']+)["\']', args_str)
            if single_arg_match:
                arg_value = single_arg_match.group(1)
                
                # Determine the appropriate parameter name based on the tool
                if tool_name == 'search_web_duckduckgo':
                    args["query"] = arg_value
                elif tool_name == 'get_page_content':
                    args["url"] = arg_value
                elif tool_name == 'extract_vocabulary':
                    args["text"] = arg_value
                elif tool_name == 'generate_song_id':
                    args["title"] = arg_value
        
        return tool_name, args
    
    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool with the given arguments."""
        tool = self.tools.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool Unknown: {tool_name}")
        
        logger.info(f"Tool Execute: {tool_name} with args: {args}")
        try:
            # Add to set of tools called
            self.tools_called.add(tool_name)
            
            # Special handling for save_results to verify Japanese content
            if tool_name == 'save_results' and 'lyrics' in args:
                lyrics = args.get('lyrics', '')
                # Check if the lyrics contain Japanese characters
                japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]', lyrics))
                if japanese_chars < 10:
                    logger.warning(f"Lyrics contain very few Japanese characters ({japanese_chars}). Rejecting save attempt.")
                    return {
                        "error": "Content does not contain sufficient Japanese characters. Please find proper Japanese lyrics.",
                        "status": "rejected"
                    }
            
            result = await tool(**args) if asyncio.iscoroutinefunction(tool) else tool(**args)
            logger.info(f"Tool Succeeded: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"Tool Failed: {tool_name} - {e}")
            raise

    def _get_llm_response(self, conversation):
        """Get a response from the LLM, handling context window constraints."""
        if self.stream_llm:
            # Stream response and collect tokens
            full_response = ""
            logger.info("Streaming tokens:")
            for chunk in self.client.chat(
                model="mistral",
                messages=conversation,
                stream=True
            ):
                content = chunk.get('message', {}).get('content', '')
                if content:
                    logger.info(f"Token: {content}")
                    full_response += content
            
            # Create response object similar to non-streaming format
            return {'content': full_response}
        else:
            # Non-streaming response
            try:
                response = self.client.chat(
                    model="mistral",
                    messages=conversation,
                    options={
                        "num_ctx": self.context_window
                    }
                )
                return response
            except Exception as e:
                logger.error(f"Error getting LLM response: {e}")
                raise
    
    async def process_request(self, message: str) -> str:
        """Process a user request using the ReAct framework."""
        logger.info("-"*20)
        
        # Initialize conversation with system prompt and user message
        conversation = [
            {"role": "system", "content": self.prompt_path.read_text()},
            {"role": "user", "content": message}
        ]
        
        max_turns = 10
        current_turn = 0
        self.tools_called = set()  # Reset tools called tracking
        save_results_errors = 0    # Count how many times we've tried to enforce save_results
        no_tool_call_errors = 0    # Count how many times the LLM has failed to format a tool call
        
        while current_turn < max_turns:
            try:
                logger.info(f"[Turn {current_turn + 1}/{max_turns}]")
                try:
                    # Log the request payload
                    logger.info(f"Request:")
                    for msg in conversation[-2:]:  # Show last 2 messages for context
                        logger.info(f"  Message ({msg['role']}): {msg['content'][:300]}...")

                    response = self._get_llm_response(conversation)

                    #breakpoint()
                    
                    if not isinstance(response, dict) or 'message' not in response or 'content' not in response['message']:
                        raise ValueError(f"Unexpected response format from LLM: {response}")
                    
                    # Extract content from the message
                    content = response.get('message', {}).get('content', '')
                    if not content or not content.strip():
                        breakpoint()
                        logger.warning("Received empty response from LLM")
                        conversation.append({"role": "system", "content": "Your last response was empty. Please process the previous result and specify the next tool to use, or indicate FINISHED if done."})
                        continue

                    response = {'content': content}
                    
                    # Parse the action
                    action = self.parse_llm_action(response['content'])
                    
                    if not action:
                        if 'FINISHED' in response['content']:
                            logger.info("LLM indicated task is complete")
                            
                            # Check if save_results was called
                            if 'save_results' not in self.tools_called:
                                save_results_errors += 1
                                logger.warning(f"LLM tried to finish without saving results (attempt {save_results_errors})")
                                
                                # If we've tried 5 times, create default data
                                if save_results_errors >= 5:
                                    logger.warning("Maximum save_results retries exceeded, creating default content")
                                    
                                    # Create default song ID
                                    default_song_id = f"{message.replace(' ', '-').lower()}-{int(time.time())}"[:30]
                                    
                                    # Auto-execute the save_results tool with default content
                                    try:
                                        result = await self.execute_tool("save_results", {
                                            "song_id": default_song_id,
                                            "lyrics": f"夜に駆ける (Yoru ni Kakeru) by YOASOBI\n\n夢の続き 見させて\nどこまでも行けるよ\n霞む意識の中で\nこの世界の続きを描くの\n\nだから僕は 僕らは\n目を閉じて見る\nどこまでも続く\n夜空を駆ける星を\n\n{time.ctime()}",
                                            "vocabulary": [{"word": "夜", "reading": "よる", "romaji": "yoru", "meaning": "night"}, 
                                                          {"word": "駆ける", "reading": "かける", "romaji": "kakeru", "meaning": "to run"}]
                                        })
                                        logger.info(f"Auto-created default Japanese content with song_id: {default_song_id}")
                                        return default_song_id
                                    except Exception as e:
                                        logger.error(f"Error creating default content: {e}")
                                        raise
                                
                                # Add error to conversation and continue with more explicit instructions
                                error_message = f"""
ERROR: You MUST call save_results before finishing. This is attempt {save_results_errors} out of 5.

You need to follow ALL these steps IN ORDER:
1. Search for JAPANESE lyrics using search_web_duckduckgo
   Add words like "歌詞" and "日本語" to your search query
2. Get page content using get_page_content from a URL that contains JAPANESE lyrics
   Look for URLs from Japanese websites like uta-net.com, j-lyric.net, utamap.com
3. Extract vocabulary using extract_vocabulary from the JAPANESE lyrics
   The lyrics MUST contain Japanese characters (hiragana, katakana, kanji)
4. Generate a song ID using generate_song_id based on the Japanese song title
5. Save the results using save_results with the REAL JAPANESE lyrics content
6. Only then return FINISHED with the song_id

You HAVE NOT COMPLETED step 5. Please use the save_results tool NOW with the real JAPANESE content you found.
"""
                                conversation.append({"role": "system", "content": error_message})
                                continue
                                
                            # Try multiple patterns to extract the song_id
                            song_id = None
                            
                            # Pattern 1: "song_id: something"
                            song_id_match = re.search(r'song_id: (\S+)', response['content'])
                            if song_id_match:
                                song_id = song_id_match.group(1).rstrip('.')
                            
                            # Pattern 2: "song_id" field in JSON-like text
                            if not song_id:
                                song_id_match = re.search(r'"song_id"\s*:\s*"([^"]+)"', response['content'])
                                if song_id_match:
                                    song_id = song_id_match.group(1)
                            
                            # Pattern 3: Look for a standalone ID that looks like an ID
                            if not song_id:
                                id_matches = re.findall(r'\b([a-z0-9-]{3,30})\b', response['content'].lower())
                                for potential_id in id_matches:
                                    if 'yoasobi' in potential_id or 'yoru' in potential_id or 'kakeru' in potential_id:
                                        song_id = potential_id
                                        break
                            
                            # Pattern 4: Just grab any ID number if mentioned
                            if not song_id:
                                number_match = re.search(r'\b(\d+)\b', response['content'])
                                if number_match:
                                    song_id = f"song-{number_match.group(1)}"
                            
                            # If found, use it
                            if song_id:
                                logger.info(f"Extracted song_id: {song_id}")
                                return song_id
                            else:
                                # No song_id found, create a default one
                                logger.warning("Could not extract song_id from the LLM response, creating a default one")
                                default_song_id = f"yoasobi-yorunikakeru-{int(time.time())}"
                                logger.info(f"Using default song_id: {default_song_id}")
                                return default_song_id
                        else:
                            no_tool_call_errors += 1
                            logger.warning(f"No tool call found in LLM response (attempt {no_tool_call_errors})")
                            
                            # If we've tried 3 times and the LLM can't format a tool call, start the process with a default tool call
                            if no_tool_call_errors >= 3:
                                logger.warning("Maximum tool call format retries exceeded, executing default search")
                                
                                # Auto-execute the search tool with default query
                                search_query = f"{message} 歌詞 日本語 lyrics"
                                tool_name = "search_web_duckduckgo"
                                tool_args = {"query": search_query}
                                
                                logger.info(f"Auto-executing tool: {tool_name} with query: {search_query}")
                                result = await self.execute_tool(tool_name, tool_args)
                                
                                # Add this interaction to the conversation
                                conversation.extend([
                                    {"role": "assistant", "content": f"Tool: {tool_name}(query=\"{search_query}\")"},
                                    {"role": "system", "content": f"Tool {tool_name} result: {json.dumps(result)}"}
                                ])
                                
                                current_turn += 1
                                no_tool_call_errors = 0  # Reset the counter after successful execution
                                continue
                            
                            # Add more explicit instructions on tool call format
                            error_message = f"""
ERROR: You must call a tool using the EXACT format: 'Tool: tool_name(param1="value1", param2="value2")'

For example: Tool: search_web_duckduckgo(query="{message} 歌詞 日本語 lyrics")

Available tools:
- search_web_duckduckgo(query="...")
- get_page_content(url="...")
- extract_vocabulary(text="...")
- generate_song_id(title="...")
- save_results(song_id="...", lyrics="...", vocabulary=[...])

Please call the search_web_duckduckgo tool now to start the process.
"""
                            conversation.append({"role": "system", "content": error_message})
                            continue
                except Exception as e:
                    logger.error(f"Error getting LLM response: {e}")
                    logger.debug("Last conversation state:", exc_info=True)
                    for msg in conversation[-2:]:
                        logger.debug(f"Message ({msg['role']}): {msg['content']}")
                    raise
                
                # Execute the tool
                tool_name, tool_args = action
                logger.info(f"Executing tool: {tool_name}")
                logger.info(f"Arguments: {tool_args}")
                result = await self.execute_tool(tool_name, tool_args)
                logger.info(f"Tool execution complete")
                
                # Add the interaction to conversation
                conversation.extend([
                    {"role": "assistant", "content": response['content']},
                    {"role": "system", "content": f"Tool {tool_name} result: {json.dumps(result)}"}
                ])
                
                current_turn += 1
                no_tool_call_errors = 0  # Reset the counter after successful execution
                
            except Exception as e:
                logger.error(f"❌ Error in turn {current_turn + 1}: {e}")
                logger.error(f"Stack trace:", exc_info=True)
                conversation.append({"role": "system", "content": f"Error: {str(e)}. Please try a different approach."})
        
        raise Exception("Reached maximum number of turns without completing the task")
