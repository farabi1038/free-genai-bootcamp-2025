import json
import logging
from typing import Dict, List, Any, Optional
from .llm_client import LLMClient

logger = logging.getLogger(__name__)

class VocabGenerator:
    """Generator for vocabulary words and groups using LLM."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize the vocabulary generator.
        
        Args:
            llm_client: The LLM client to use for generating vocabulary
        """
        self.llm_client = llm_client
        logger.info("Vocabulary generator initialized")
    
    def generate_vocab_words(
        self, 
        language: str = "Japanese", 
        category: str = "Basic Greetings", 
        count: int = 10,
        difficulty: str = "Beginner"
    ) -> List[Dict[str, Any]]:
        """Generate vocabulary words using the LLM.
        
        Args:
            language: The target language for vocabulary
            category: The category/topic for the vocabulary
            count: Number of words to generate
            difficulty: Difficulty level (Beginner, Intermediate, Advanced)
            
        Returns:
            List[Dict[str, Any]]: List of generated vocabulary words
        """
        # Special handling for Japanese to ensure better quality
        if language.lower() == "japanese":
            return self._generate_japanese_vocab(category, count, difficulty)
        
        # Generic handling for other languages
        system_prompt = """You are a language learning expert who creates vocabulary lists for students.
        Generate vocabulary in the exact JSON format requested. Only output valid JSON that matches the requested schema.
        The JSON should be an array of vocabulary items. Each vocabulary item should have the properties specified in the request.
        Do not include any additional explanation or commentary in your output, only the JSON data."""
        
        prompt = f"""Please create a vocabulary list with {count} {language} words for the category "{category}" at {difficulty} level.
        
        For each {language} word, provide the following:
        1. The word in {language}
        2. The pronunciation in romaji (if applicable)
        3. The English translation
        
        Format your response as a JSON array with objects having these exact keys:
        - "japanese" for the {language} word
        - "romaji" for the pronunciation
        - "english" for the English translation
        
        Only include words that are appropriately challenging for {difficulty} level students.
        
        Example output format:
        [
            {{
                "japanese": "こんにちは",
                "romaji": "konnichiwa",
                "english": "hello"
            }}
        ]
        
        Return exactly {count} vocabulary items in the JSON array.
        """
        
        try:
            # Generate response from LLM
            response = self.llm_client.generate_text(prompt, max_tokens=2048, system_prompt=system_prompt)
            
            # Check if we got an error response
            if response.startswith("Error:"):
                logger.error(f"LLM generation failed: {response}")
                
                # Provide fallback data if LLM fails
                return self._generate_fallback_vocab(language, category, count, difficulty)
            
            # Parse JSON response, handling potential formatting issues
            try:
                # Find JSON array in the response (in case there's extra text)
                response = response.strip()
                
                # Check if the response contains proper JSON
                if not ("[" in response and "]" in response):
                    logger.error("Response doesn't contain JSON array markers")
                    return self._generate_fallback_vocab(language, category, count, difficulty)
                
                start_idx = response.find("[")
                end_idx = response.rfind("]") + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    vocab_list = json.loads(json_str)
                    
                    # Validate each item has the required fields
                    valid_vocab = []
                    for item in vocab_list:
                        if all(key in item for key in ["japanese", "romaji", "english"]):
                            valid_vocab.append(item)
                    
                    if valid_vocab:
                        logger.info(f"Successfully generated {len(valid_vocab)} vocabulary items")
                        return valid_vocab
                    else:
                        logger.error("No valid vocabulary items in response")
                        return self._generate_fallback_vocab(language, category, count, difficulty)
                else:
                    logger.error("Failed to find JSON array in LLM response")
                    return self._generate_fallback_vocab(language, category, count, difficulty)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.debug(f"Raw response: {response}")
                return self._generate_fallback_vocab(language, category, count, difficulty)
        
        except Exception as e:
            logger.error(f"Failed to generate vocabulary: {str(e)}")
            return self._generate_fallback_vocab(language, category, count, difficulty)
    
    def _generate_japanese_vocab(self, category: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate Japanese vocabulary with specialized prompting.
        
        Args:
            category: The category/topic for the vocabulary
            count: Number of words to generate
            difficulty: Difficulty level (Beginner, Intermediate, Advanced)
            
        Returns:
            List[Dict[str, Any]]: List of generated Japanese vocabulary words
        """
        system_prompt = """You are a Japanese language expert who creates accurate vocabulary lists for students.
        You have excellent knowledge of Japanese writing (kanji, hiragana, katakana) and romaji transcription.
        Generate vocabulary in the exact JSON format requested with proper Japanese characters and accurate romaji.
        Only output valid JSON that matches the requested schema.
        Do not include any additional explanation or commentary in your output, only the JSON data."""
        
        # Difficulty-specific instructions
        difficulty_guide = {
            "Beginner": "Use mostly hiragana with very simple kanji. Include common everyday words that beginners would learn first.",
            "Intermediate": "Use a mix of hiragana, katakana, and basic to intermediate kanji. Include practical vocabulary for daily conversations.",
            "Advanced": "Use more complex kanji and specialized vocabulary. Include nuanced terms and expressions."
        }.get(difficulty, "Use appropriate Japanese writing based on the difficulty level.")
        
        # Category-specific examples to guide the model
        category_examples = {
            "Basic Greetings": '[{"japanese": "こんにちは", "romaji": "konnichiwa", "english": "hello"}, {"japanese": "さようなら", "romaji": "sayounara", "english": "goodbye"}]',
            "Food": '[{"japanese": "寿司", "romaji": "sushi", "english": "sushi"}, {"japanese": "ラーメン", "romaji": "rāmen", "english": "ramen"}]',
            "Numbers": '[{"japanese": "一", "romaji": "ichi", "english": "one"}, {"japanese": "二", "romaji": "ni", "english": "two"}]',
            "Family": '[{"japanese": "家族", "romaji": "kazoku", "english": "family"}, {"japanese": "両親", "romaji": "ryōshin", "english": "parents"}]'
        }.get(category, "")
        
        prompt = f"""Please create a vocabulary list with {count} Japanese words for the category "{category}" at {difficulty} level.
        
        {difficulty_guide}
        
        For each Japanese word, provide:
        1. The word in Japanese using appropriate kanji, hiragana, and/or katakana
        2. The accurate romaji pronunciation (use macrons for long vowels: ā, ī, ū, ē, ō)
        3. The precise English translation
        
        Format your response as a JSON array with objects having these exact keys:
        - "japanese" for the Japanese word
        - "romaji" for the romaji pronunciation
        - "english" for the English translation
        
        Example output format for this category:
        {category_examples if category_examples else '[{"japanese": "日本語", "romaji": "nihongo", "english": "Japanese language"}]'}
        
        Return exactly {count} vocabulary items in the JSON array.
        """
        
        try:
            # Generate response from LLM with increased tokens for better quality
            response = self.llm_client.generate_text(prompt, max_tokens=3072, system_prompt=system_prompt)
            
            # Check if we got an error response
            if response.startswith("Error:"):
                logger.error(f"LLM generation failed: {response}")
                return self._generate_fallback_vocab("Japanese", category, count, difficulty)
            
            # Parse JSON response, handling potential formatting issues
            try:
                # Find JSON array in the response (in case there's extra text)
                response = response.strip()
                
                # Check if the response contains proper JSON
                if not ("[" in response and "]" in response):
                    logger.error("Response doesn't contain JSON array markers")
                    return self._generate_fallback_vocab("Japanese", category, count, difficulty)
                
                start_idx = response.find("[")
                end_idx = response.rfind("]") + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    vocab_list = json.loads(json_str)
                    
                    # Validate each item has the required fields
                    valid_vocab = []
                    for item in vocab_list:
                        if all(key in item for key in ["japanese", "romaji", "english"]):
                            valid_vocab.append(item)
                    
                    if valid_vocab:
                        logger.info(f"Successfully generated {len(valid_vocab)} Japanese vocabulary items")
                        return valid_vocab
                    else:
                        logger.error("No valid Japanese vocabulary items in response")
                        return self._generate_fallback_vocab("Japanese", category, count, difficulty)
                else:
                    logger.error("Failed to find JSON array in LLM response")
                    return self._generate_fallback_vocab("Japanese", category, count, difficulty)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.debug(f"Raw response: {response}")
                return self._generate_fallback_vocab("Japanese", category, count, difficulty)
        
        except Exception as e:
            logger.error(f"Failed to generate Japanese vocabulary: {str(e)}")
            return self._generate_fallback_vocab("Japanese", category, count, difficulty)
    
    def _generate_fallback_vocab(self, language: str, category: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate fallback vocabulary when LLM fails."""
        logger.info(f"Generating fallback vocabulary for {language} - {category}")
        
        # Dictionary of common words by language and category
        fallbacks = {
            "Japanese": {
                "Basic Greetings": [
                    {"japanese": "こんにちは", "romaji": "konnichiwa", "english": "hello"},
                    {"japanese": "さようなら", "romaji": "sayounara", "english": "goodbye"},
                    {"japanese": "おはよう", "romaji": "ohayou", "english": "good morning"},
                    {"japanese": "こんばんは", "romaji": "konbanwa", "english": "good evening"},
                    {"japanese": "ありがとう", "romaji": "arigatou", "english": "thank you"},
                    {"japanese": "どういたしまして", "romaji": "dou itashimashite", "english": "you're welcome"},
                    {"japanese": "すみません", "romaji": "sumimasen", "english": "excuse me/sorry"},
                    {"japanese": "はじめまして", "romaji": "hajimemashite", "english": "nice to meet you"},
                    {"japanese": "お元気ですか", "romaji": "o-genki desu ka", "english": "how are you?"},
                    {"japanese": "元気です", "romaji": "genki desu", "english": "I'm fine"}
                ],
                "Numbers": [
                    {"japanese": "一", "romaji": "ichi", "english": "one"},
                    {"japanese": "二", "romaji": "ni", "english": "two"},
                    {"japanese": "三", "romaji": "san", "english": "three"},
                    {"japanese": "四", "romaji": "shi/yon", "english": "four"},
                    {"japanese": "五", "romaji": "go", "english": "five"},
                    {"japanese": "六", "romaji": "roku", "english": "six"},
                    {"japanese": "七", "romaji": "shichi/nana", "english": "seven"},
                    {"japanese": "八", "romaji": "hachi", "english": "eight"},
                    {"japanese": "九", "romaji": "kyū/ku", "english": "nine"},
                    {"japanese": "十", "romaji": "jū", "english": "ten"}
                ],
                "Food": [
                    {"japanese": "ご飯", "romaji": "gohan", "english": "rice/meal"},
                    {"japanese": "寿司", "romaji": "sushi", "english": "sushi"},
                    {"japanese": "魚", "romaji": "sakana", "english": "fish"},
                    {"japanese": "肉", "romaji": "niku", "english": "meat"},
                    {"japanese": "野菜", "romaji": "yasai", "english": "vegetables"},
                    {"japanese": "果物", "romaji": "kudamono", "english": "fruit"},
                    {"japanese": "水", "romaji": "mizu", "english": "water"},
                    {"japanese": "お茶", "romaji": "ocha", "english": "tea"},
                    {"japanese": "コーヒー", "romaji": "kōhī", "english": "coffee"},
                    {"japanese": "ビール", "romaji": "bīru", "english": "beer"}
                ],
                "Family": [
                    {"japanese": "家族", "romaji": "kazoku", "english": "family"},
                    {"japanese": "父", "romaji": "chichi", "english": "father"},
                    {"japanese": "母", "romaji": "haha", "english": "mother"},
                    {"japanese": "兄", "romaji": "ani", "english": "older brother"},
                    {"japanese": "姉", "romaji": "ane", "english": "older sister"},
                    {"japanese": "弟", "romaji": "otōto", "english": "younger brother"},
                    {"japanese": "妹", "romaji": "imōto", "english": "younger sister"},
                    {"japanese": "祖父", "romaji": "sofu", "english": "grandfather"},
                    {"japanese": "祖母", "romaji": "sobo", "english": "grandmother"},
                    {"japanese": "子供", "romaji": "kodomo", "english": "child"}
                ]
            },
            "French": {
                "Basic Greetings": [
                    {"japanese": "bonjour", "romaji": "bon-zhoor", "english": "hello"},
                    {"japanese": "au revoir", "romaji": "oh ruh-vwar", "english": "goodbye"},
                    {"japanese": "merci", "romaji": "mehr-see", "english": "thank you"},
                    {"japanese": "s'il vous plaît", "romaji": "seel voo play", "english": "please"},
                    {"japanese": "excusez-moi", "romaji": "ex-koo-zay mwa", "english": "excuse me"}
                ]
            }
        }
        
        # Default fallback for any language
        default_fallback = [
            {"japanese": f"Word {i} in {language}", "romaji": f"pronunciation {i}", "english": f"meaning {i}"} 
            for i in range(1, count+1)
        ]
        
        # Get language-specific fallbacks
        language_fallbacks = fallbacks.get(language, {})
        
        # Get category-specific fallbacks
        category_fallbacks = language_fallbacks.get(category, [])
        
        # If we have fallbacks for this language and category, use them
        if category_fallbacks:
            # Make sure we have enough words
            while len(category_fallbacks) < count:
                # Add generic words if needed
                index = len(category_fallbacks) + 1
                category_fallbacks.append({
                    "japanese": f"{language} word {index}", 
                    "romaji": f"pronunciation {index}", 
                    "english": f"meaning {index}"
                })
            
            # Return only the requested number of words
            return category_fallbacks[:count]
        
        # Otherwise use the default fallback
        return default_fallback[:count]
    
    def generate_vocab_groups(self, count: int = 5, language: str = "Japanese") -> List[Dict[str, str]]:
        """Generate vocabulary group names using the LLM.
        
        Args:
            count: Number of groups to generate
            language: The target language for vocabulary
            
        Returns:
            List[Dict[str, str]]: List of generated vocabulary groups
        """
        system_prompt = """You are a language learning expert who creates vocabulary groups for students.
        Generate vocabulary group names in the exact JSON format requested. Only output valid JSON.
        Do not include any explanation or commentary in your output, only the JSON data."""
        
        prompt = f"""Please create {count} vocabulary group categories for learning {language}.
        
        Create a diverse set of practical, everyday categories that would be useful for language learners.
        Include a mix of categories for beginners, intermediate and advanced learners.
        
        Format your response as a JSON array with objects having exactly this key:
        - "name" for the category name
        
        Example output format:
        [
            {{
                "name": "Basic Greetings"
            }},
            {{
                "name": "Numbers and Counting"
            }}
        ]
        
        Return exactly {count} category items in the JSON array.
        """
        
        try:
            # Generate response from LLM
            response = self.llm_client.generate_text(prompt, max_tokens=1024, system_prompt=system_prompt)
            
            # Check if we got an error response
            if response.startswith("Error:"):
                logger.error(f"LLM generation failed: {response}")
                return self._generate_fallback_groups(count, language)
            
            # Parse JSON response, handling potential formatting issues
            try:
                # Find JSON array in the response (in case there's extra text)
                response = response.strip()
                
                # Check if the response contains proper JSON
                if not ("[" in response and "]" in response):
                    logger.error("Response doesn't contain JSON array markers")
                    return self._generate_fallback_groups(count, language)
                
                start_idx = response.find("[")
                end_idx = response.rfind("]") + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    group_list = json.loads(json_str)
                    
                    # Validate each item has the required fields
                    valid_groups = []
                    for item in group_list:
                        if "name" in item:
                            valid_groups.append(item)
                    
                    if valid_groups:
                        logger.info(f"Successfully generated {len(valid_groups)} vocabulary groups")
                        return valid_groups
                    else:
                        logger.error("No valid vocabulary groups in response")
                        return self._generate_fallback_groups(count, language)
                else:
                    logger.error("Failed to find JSON array in LLM response")
                    return self._generate_fallback_groups(count, language)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.debug(f"Raw response: {response}")
                return self._generate_fallback_groups(count, language)
        
        except Exception as e:
            logger.error(f"Failed to generate vocabulary groups: {str(e)}")
            return self._generate_fallback_groups(count, language)
    
    def _generate_fallback_groups(self, count: int, language: str) -> List[Dict[str, str]]:
        """Generate fallback vocabulary groups when LLM fails."""
        logger.info(f"Generating fallback vocabulary groups for {language}")
        
        # Common vocabulary categories for language learning
        default_groups = [
            {"name": "Basic Greetings and Introductions"},
            {"name": "Numbers and Counting"},
            {"name": "Food and Drink"},
            {"name": "Family Members"},
            {"name": "Colors and Shapes"},
            {"name": "Days, Months, and Seasons"},
            {"name": "Weather and Climate"},
            {"name": "Clothing and Fashion"},
            {"name": "Body Parts and Health"},
            {"name": "Transportation and Travel"},
            {"name": "Home and Furniture"},
            {"name": "School and Education"},
            {"name": "Work and Careers"},
            {"name": "Hobbies and Leisure Activities"},
            {"name": "Nature and Environment"}
        ]
        
        # Return only the requested number of groups
        return default_groups[:count] 