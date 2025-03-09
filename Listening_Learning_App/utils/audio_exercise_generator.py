import os
import json
import logging
import time
import uuid
from pathlib import Path
import random
import gc
import re
import traceback
from datetime import datetime

from .ollama_integration import OllamaClient
from .japanese_tts import JapaneseTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths
DATA_DIR = Path(__file__).parent.parent / "data"
EXERCISES_DIR = DATA_DIR / "exercises"
AUDIO_DIR = DATA_DIR / "audio"

# Ensure directories exist
EXERCISES_DIR.mkdir(exist_ok=True, parents=True)
AUDIO_DIR.mkdir(exist_ok=True, parents=True)

class AudioExerciseGenerator:
    """Generator for JLPT-style listening exercises with audio"""
    
    def __init__(self, ollama_model="llama3.2:1b", jlpt_level="N4"):
        """Initialize the generator"""
        self.ollama_client = OllamaClient(model=ollama_model)
        self.tts = JapaneseTTS()
        self.jlpt_level = jlpt_level
        
        # Clean up old exercises to save space
        self._cleanup_old_exercises()
    
    def _cleanup_old_exercises(self, max_exercises=20):
        """Clean up old exercises to save disk space"""
        try:
            # Get all exercise files
            exercise_files = list(EXERCISES_DIR.glob("exercise_*.json"))
            
            # If we have more than max_exercises, delete the oldest ones
            if len(exercise_files) > max_exercises:
                # Sort by modification time (oldest first)
                exercise_files.sort(key=lambda f: f.stat().st_mtime)
                
                # Delete the oldest ones, keeping only max_exercises
                for file_to_delete in exercise_files[:-max_exercises]:
                    try:
                        # Check if there's an associated audio file
                        exercise_id = file_to_delete.stem.replace("exercise_", "")
                        audio_file = AUDIO_DIR / f"exercise_{exercise_id}.mp3"
                        
                        # Delete the audio file if it exists
                        if audio_file.exists():
                            audio_file.unlink()
                            
                        # Delete the exercise file
                        file_to_delete.unlink()
                        logger.info(f"Cleaned up old exercise: {file_to_delete.name}")
                    except Exception as e:
                        logger.warning(f"Error deleting old exercise file {file_to_delete}: {str(e)}")
                        
            # Clean up any orphaned audio files
            audio_files = list(AUDIO_DIR.glob("*.mp3"))
            for audio_file in audio_files:
                # Get the corresponding exercise ID
                if audio_file.stem.startswith("exercise_"):
                    exercise_id = audio_file.stem.replace("exercise_", "")
                    exercise_file = EXERCISES_DIR / f"exercise_{exercise_id}.json"
                    
                    # If the exercise file doesn't exist, delete the audio file
                    if not exercise_file.exists():
                        try:
                            audio_file.unlink()
                            logger.info(f"Cleaned up orphaned audio file: {audio_file.name}")
                        except Exception as e:
                            logger.warning(f"Error deleting orphaned audio file {audio_file}: {str(e)}")
        except Exception as e:
            logger.warning(f"Error during exercise cleanup: {str(e)}")
    
    async def generate_listening_exercise(self, topic=None, num_questions=1, with_audio=True, jlpt_level=None):
        """
        Generate a JLPT-style listening exercise
        """
        # Use the provided JLPT level if any, otherwise use the default one
        if jlpt_level:
            self.jlpt_level = jlpt_level
        
        # Log the configuration
        logger.info(f"Generating listening exercise with JLPT level: {self.jlpt_level}")
        logger.info(f"Topic: {topic if topic else 'General'}")
        logger.info(f"Number of questions requested: {num_questions}")
        
        try:
            # Generate the script first
            logger.info("Generating conversation script...")
            script = await self._generate_conversation(topic)
            
            # Generate the audio if requested
            if with_audio:
                logger.info("Generating TTS audio...")
                try:
                    audio_path = await self._generate_audio(script)
                except Exception as e:
                    logger.error(f"Error generating audio: {str(e)}")
                    audio_path = None
            else:
                audio_path = None
            
            # Generate questions based on the script
            logger.info("Generating questions...")
            
            # FIXED: Ensure we respect the number of questions requested
            # Hard code to the exact number requested by the user
            questions = await self._generate_questions(script, num_questions=num_questions)
            
            # FIXED: Ensure we have valid questions with valid options
            # Validate each question has a proper question text and options
            valid_questions = []
            for q in questions:
                # Skip questions with placeholder text or problematic formatting
                if "問題" in q.get('question', '') or "．" in q.get('question', ''):
                    continue
                    
                # Ensure question has proper options
                if 'options' in q and len(q['options']) >= 2:
                    # Ensure options aren't just numbers or placeholders
                    valid_options = []
                    for opt in q['options']:
                        if not opt.startswith(('１．', '２．', '３．', '４．')) and "．" not in opt:
                            valid_options.append(opt)
                    
                    # Only use the question if we have valid options
                    if len(valid_options) >= 2:
                        q['options'] = valid_options
                        valid_questions.append(q)
            
            # If we don't have enough valid questions, generate default ones
            if len(valid_questions) < num_questions:
                logger.warning(f"Only found {len(valid_questions)} valid questions, adding defaults to meet the requested {num_questions}")
                
                # Create default questions based on the script topic
                topic_phrase = topic if topic else "この会話"
                
                default_questions = [
                    {
                        "question": f"この会話は何についてですか？ (What is this conversation about?)",
                        "options": [
                            f"{topic_phrase}について (About {topic_phrase})",
                            "食べ物について (About food)",
                            "天気について (About weather)",
                            "旅行について (About travel)"
                        ],
                        "correct_answer": 0  # First option is correct
                    },
                    {
                        "question": "話している人は何人ですか？ (How many people are talking?)",
                        "options": [
                            "1人 (1 person)", 
                            "2人 (2 people)", 
                            "3人 (3 people)", 
                            "4人以上 (4 or more people)"
                        ],
                        "correct_answer": 1  # Assuming 2 people
                    },
                    {
                        "question": "会話の雰囲気はどうですか？ (What is the atmosphere of the conversation?)",
                        "options": [
                            "フォーマル (Formal)",
                            "カジュアル (Casual)",
                            "緊張している (Tense)",
                            "嬉しい (Happy)"
                        ],
                        "correct_answer": 1  # Casual is most likely
                    }
                ]
                
                # Add default questions as needed
                while len(valid_questions) < num_questions and default_questions:
                    valid_questions.append(default_questions.pop(0))
            
            # Limit to the exact number requested
            valid_questions = valid_questions[:num_questions]
            
            # Create and save the exercise
            exercise_id = str(uuid.uuid4())
            exercise = {
                "id": exercise_id,
                "jlpt_level": self.jlpt_level,
                "topic": topic,
                "script": script,
                "main_audio": audio_path,
                "questions": valid_questions,
                "num_questions": len(valid_questions),
                "has_audio": audio_path is not None,
                "timestamp": datetime.now().isoformat(),
                "display_level": f"JLPT {self.jlpt_level}"
            }
            
            # Save the exercise
            exercise_path = os.path.join(EXERCISES_DIR, f"exercise_{exercise_id}.json")
            with open(exercise_path, 'w', encoding='utf-8') as f:
                json.dump(exercise, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exercise saved to {exercise_path}")
            
            return exercise
            
        except Exception as e:
            logger.error(f"Error generating listening exercise: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return a basic fallback exercise in case of errors
            return self._create_fallback_exercise(topic)
    
    async def generate_from_transcript(self, transcript, num_questions=3, with_audio=True):
        """
        Generate a listening exercise based on an existing transcript
        
        Args:
            transcript: Transcript text or segments
            num_questions: Number of questions to generate
            with_audio: Whether to generate audio files
            
        Returns:
            dict: The generated exercise with metadata
        """
        exercise_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        # Prepare the prompt
        system_prompt = """
        You are a Japanese language educator creating listening comprehension exercises based on authentic content.
        Your task is to create JLPT-style questions based on the provided transcript.
        
        Format your response as a complete script with:
        1. Clear speaker labels [ANNOUNCER], [MALE] or [FEMALE] for speakers
        2. Questions asked by the announcer
        3. Multiple-choice options (4 choices per question)
        """
        
        # Convert transcript to text if it's in segments format
        transcript_text = ""
        if isinstance(transcript, list):
            for segment in transcript:
                if isinstance(segment, dict) and "text" in segment:
                    transcript_text += segment["text"] + "\n"
                else:
                    transcript_text += str(segment) + "\n"
        else:
            transcript_text = transcript
        
        prompt = f"""
        Here is a Japanese transcript:
        
        {transcript_text}
        
        Based on this content, create a JLPT-style listening comprehension exercise with {num_questions} questions.
        
        For each question:
        1. Select a specific part of the transcript
        2. Format it as a dialogue with [MALE]/[FEMALE] speaker labels
        3. Add an [ANNOUNCER] who asks a comprehension question
        4. Provide four multiple-choice options (numbered １、２、３、４)
        
        Make sure the questions test understanding of the content, not just vocabulary.
        
        Return ONLY the complete exercise script in plain text format.
        """
        
        # Generate the script
        logger.info(f"Generating listening exercise based on transcript with {num_questions} questions")
        script = await self.ollama_client.generate(prompt, system_prompt, temperature=0.7)
        
        # Record the exercise data
        exercise_data = {
            "id": exercise_id,
            "timestamp": timestamp,
            "jlpt_level": self.jlpt_level,
            "based_on_transcript": True,
            "num_questions": num_questions,
            "script": script,
            "audio_paths": []
        }
        
        # Generate audio if requested
        if with_audio:
            logger.info("Generating audio for the exercise")
            audio_path = self.tts.generate_jlpt_audio(
                script,
                output_dir=AUDIO_DIR,
                output_filename=f"exercise_{exercise_id}.mp3"
            )
            
            if audio_path:
                exercise_data["audio_paths"] = [audio_path]
                exercise_data["main_audio"] = audio_path
        
        # Save the exercise data
        output_path = EXERCISES_DIR / f"exercise_{exercise_id}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(exercise_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exercise saved to {output_path}")
        return exercise_data
    
    def list_stored_exercises(self, max_count=10):
        """List stored exercises"""
        exercises = []
        
        for file_path in EXERCISES_DIR.glob("exercise_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    exercise = json.load(f)
                    
                    # Check if audio actually exists
                    has_audio = False
                    if exercise.get("main_audio") and os.path.exists(exercise.get("main_audio")):
                        has_audio = True
                    elif exercise.get("audio_paths"):
                        for audio_path in exercise.get("audio_paths", []):
                            if audio_path and os.path.exists(audio_path):
                                has_audio = True
                                break
                    
                    exercises.append({
                        "id": exercise.get("id", "unknown"),
                        "timestamp": exercise.get("timestamp", 0),
                        "jlpt_level": exercise.get("jlpt_level", "unknown"),
                        "topic": exercise.get("topic", ""),
                        "num_questions": exercise.get("num_questions", 0),
                        "has_audio": has_audio,
                        "file_path": str(file_path)
                    })
            except Exception as e:
                logger.error(f"Error loading exercise from {file_path}: {str(e)}")
        
        # Sort by timestamp (newest first)
        exercises.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return exercises[:max_count]
    
    def get_exercise_by_id(self, exercise_id):
        """Get a stored exercise by ID"""
        exercise_path = EXERCISES_DIR / f"exercise_{exercise_id}.json"
        
        if not exercise_path.exists():
            logger.error(f"Exercise not found: {exercise_id}")
            return None
        
        try:
            with open(exercise_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading exercise {exercise_id}: {str(e)}")
            return None

    async def _generate_conversation(self, topic=None):
        """Generate a conversation script based on the topic and JLPT level"""
        # Use a minimal system prompt to save tokens
        system_prompt = "You are a Japanese language teacher creating JLPT-style listening exercises."
        
        topic_text = f" about {topic}" if topic else ""
        jlpt_level_text = f"JLPT {self.jlpt_level}" if self.jlpt_level else "N4"
        
        # Use a simpler prompt structure that focuses on natural dialogue
        prompt = f"""Create a natural Japanese conversation for {jlpt_level_text} listening practice{topic_text}.

Format the conversation like this:
[MALE/FEMALE]: (Japanese dialogue)
[MALE/FEMALE]: (Japanese response)

Important guidelines:
1. Use vocabulary and grammar appropriate for {jlpt_level_text}
2. Make it a natural conversation between 2-3 people
3. Include 8-12 exchanges total
4. DO NOT include any questions or answer options in the script
5. DO NOT include any announcer text or problem statements

Make it sound natural and conversational, not like a test.
"""
        
        try:
            # Generate the script
            script = await self.ollama_client.generate(prompt, system_prompt, temperature=0.7, max_tokens=1024)
            
            # Check if script is too short or has errors
            if len(script.strip()) < 50:
                logger.warning(f"Generated script seems too short: {script}")
                # Create a simple fallback script
                script = "[MALE]: こんにちは、お元気ですか？\n[FEMALE]: はい、元気です。あなたは？\n[MALE]: 私も元気です。今日は天気がいいですね。\n[FEMALE]: そうですね。散歩に行きませんか？\n[MALE]: いいですね。何時に行きましょうか？\n[FEMALE]: 3時はどうですか？\n[MALE]: はい、3時に会いましょう。"
            
            # Clean up the script for consistency
            script = script.replace('\r\n', '\n').strip()
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating conversation: {str(e)}")
            # Return a simple default script
            return "[MALE]: こんにちは、お元気ですか？\n[FEMALE]: はい、元気です。あなたは？\n[MALE]: 私も元気です。今日は天気がいいですね。\n[FEMALE]: そうですね。散歩に行きませんか？"
    
    async def _generate_questions(self, script, num_questions=1):
        """Generate questions based on the script"""
        system_prompt = "You are a Japanese language teacher creating questions for JLPT listening tests."
        
        # Focus the prompt on generating proper questions
        prompt = f"""Based on this Japanese conversation, create exactly {num_questions} listening comprehension questions with multiple-choice answers:

{script}

Format each question as JSON like this:
```json
[
  {{
    "question": "Japanese question text (English translation)",
    "options": [
      "Option 1 (with translation)",
      "Option 2 (with translation)",
      "Option 3 (with translation)",
      "Option 4 (with translation)"
    ],
    "correct_answer": 0
  }}
]
```

IMPORTANT GUIDELINES:
1. The "correct_answer" is the INDEX (0-3) of the correct option
2. Always include 4 options per question
3. Always include both Japanese AND English translations
4. Questions should test comprehension of what was said in the conversation
5. Do not use placeholders or question numbers in the question text
6. Do not use "１．", "２．" etc. at the start of options

Return ONLY the JSON array, nothing else.
```json
"""
        
        try:
            # Generate the questions
            response = await self.ollama_client.generate(prompt, system_prompt, temperature=0.7, max_tokens=1024)
            
            # Extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Try to extract JSON without markdown code blocks
                json_str = response.strip()
                # Remove any text before or after the JSON array
                if json_str.find('[') > -1 and json_str.rfind(']') > -1:
                    json_str = json_str[json_str.find('['):json_str.rfind(']')+1]
            
            # Parse the JSON
            questions = json.loads(json_str)
            
            # Ensure each question has the required fields
            for q in questions:
                if 'options' not in q or not q['options']:
                    q['options'] = ["はい (Yes)", "いいえ (No)"]
                if 'correct_answer' not in q:
                    q['correct_answer'] = 0
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            # Return a simple default question
            return [{
                "question": "この会話は何についてですか？ (What is this conversation about?)",
                "options": ["挨拶について (About greetings)", 
                           "趣味について (About hobbies)", 
                           "仕事について (About work)", 
                           "天気について (About the weather)"],
                "correct_answer": 0
            }]
    
    async def _generate_audio(self, script):
        """Generate audio for the script"""
        try:
            # Generate the audio file
            audio_path = self.tts.generate_jlpt_audio(
                script,
                output_dir=AUDIO_DIR,
                output_filename=f"exercise_{str(uuid.uuid4())}.mp3"
            )
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            
            # Try fallback with gTTS
            try:
                from gtts import gTTS
                
                # Simplify the script for TTS by removing speaker indicators
                simple_script = re.sub(r'\[(MALE|FEMALE|MAN|WOMAN|男性|女性)\]:', '', script)
                simple_script = simple_script.replace('\n', ' ').strip()
                
                # If script is too long, take just the first part
                if len(simple_script) > 500:
                    simple_script = simple_script[:500] + "..."
                
                # Generate a unique filename
                audio_path = os.path.join(AUDIO_DIR, f"exercise_{str(uuid.uuid4())}.mp3")
                
                # Create and save the audio file
                tts = gTTS(text=simple_script, lang='ja', slow=False)
                tts.save(audio_path)
                
                return audio_path
                
            except Exception as fallback_e:
                logger.error(f"Fallback audio generation also failed: {str(fallback_e)}")
                return None
    
    def _create_fallback_exercise(self, topic=None):
        """Create a fallback exercise when generation fails"""
        exercise_id = str(uuid.uuid4())
        
        # Create a simple script
        script = "[MALE]: こんにちは、お元気ですか？\n[FEMALE]: はい、元気です。あなたは？\n[MALE]: 私も元気です。今日は天気がいいですね。\n[FEMALE]: そうですね。散歩に行きませんか？"
        
        # Create a default question
        questions = [{
            "question": "男の人は何と言いましたか？ (What did the man say?)",
            "options": [
                "お元気ですか？ (How are you?)",
                "さようなら (Goodbye)",
                "お名前は？ (What is your name?)", 
                "ありがとう (Thank you)"
            ],
            "correct_answer": 0
        }]
        
        # Try to generate audio for the fallback exercise
        try:
            from gtts import gTTS
            
            # Use a simple script for TTS
            simple_script = "これは日本語のリスニング練習です。男の人は「お元気ですか」と言いました。"
            audio_path = os.path.join(AUDIO_DIR, f"exercise_{exercise_id}.mp3")
            
            # Generate the audio file
            tts = gTTS(text=simple_script, lang='ja', slow=False)
            tts.save(audio_path)
            
        except Exception:
            audio_path = None
        
        # Create the exercise
        exercise = {
            "id": exercise_id,
            "jlpt_level": self.jlpt_level,
            "topic": topic,
            "script": script,
            "main_audio": audio_path,
            "questions": questions,
            "num_questions": len(questions),
            "has_audio": audio_path is not None,
            "timestamp": datetime.now().isoformat(),
            "display_level": f"JLPT {self.jlpt_level}",
            "fallback": True
        }
        
        # Save the exercise
        exercise_path = os.path.join(EXERCISES_DIR, f"exercise_{exercise_id}.json")
        with open(exercise_path, 'w', encoding='utf-8') as f:
            json.dump(exercise, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Fallback exercise saved to {exercise_path}")
        
        return exercise

# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        generator = AudioExerciseGenerator()
        
        # Test generating a new exercise
        exercise = await generator.generate_listening_exercise(topic="restaurant", num_questions=2)
        print(f"Generated exercise: {exercise['id']}")
        print(f"Script: {exercise['script']}")
        
        # List stored exercises
        exercises = generator.list_stored_exercises()
        print(f"Stored exercises: {len(exercises)}")
        for ex in exercises:
            print(f"- {ex['id']} ({ex['jlpt_level']}): {ex['topic']} with {ex['num_questions']} questions")
    
    asyncio.run(test()) 