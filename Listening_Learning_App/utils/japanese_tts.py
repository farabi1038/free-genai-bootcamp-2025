import os
import json
import tempfile
import logging
import subprocess
from pathlib import Path
import pyttsx3
from gtts import gTTS
import random
import re
import uuid
import gc
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
AUDIO_DIR = Path(__file__).parent.parent / "data" / "audio"
AUDIO_DIR.mkdir(exist_ok=True, parents=True)

# Define voice types
VOICE_TYPES = {
    "MALE": "male",
    "FEMALE": "female",
    "ANNOUNCER": "announcer"
}

# Available engines
ENGINE_PYTTSX3 = "pyttsx3"  # Local, offline
ENGINE_GTTS = "gtts"  # Online, better quality

class JapaneseTTS:
    """Class for Japanese text-to-speech with multiple speaker support"""
    
    def __init__(self, primary_engine=ENGINE_GTTS, fallback_engine=ENGINE_PYTTSX3):
        """Initialize the TTS engine"""
        self.primary_engine = primary_engine
        self.fallback_engine = fallback_engine
        
        # Check if pyttsx3 is working
        try:
            engine = pyttsx3.init()
            engine.getProperty('voices')
            self._pyttsx3_available = True
        except Exception as e:
            logger.warning(f"pyttsx3 initialization failed: {str(e)}")
            logger.warning("If you're on Linux, try installing espeak: 'sudo apt-get install espeak'")
            self._pyttsx3_available = False
            # If pyttsx3 is not available and was set as primary, switch to gTTS
            if self.primary_engine == ENGINE_PYTTSX3:
                logger.info("Switching primary engine to gTTS due to pyttsx3 initialization failure")
                self.primary_engine = ENGINE_GTTS
                
        self.available_voices = self._get_available_voices()
        
    def _get_available_voices(self):
        """Get available voices categorized by gender"""
        voices = {
            "male": [],
            "female": [],
            "announcer": []
        }
        
        # For pyttsx3 (local engine)
        try:
            if self._pyttsx3_available:
                engine = pyttsx3.init()
                pyttsx3_voices = engine.getProperty('voices')
                
                for voice in pyttsx3_voices:
                    try:
                        # Handle potential encoding issues with voice properties
                        languages = []
                        if hasattr(voice, 'languages') and voice.languages:
                            try:
                                if isinstance(voice.languages[0], bytes):
                                    lang = voice.languages[0].decode('utf-8', errors='ignore').lower()
                                else:
                                    lang = str(voice.languages[0]).lower()
                                languages.append(lang)
                            except (UnicodeDecodeError, IndexError, AttributeError):
                                languages = []
                        
                        voice_name = str(voice.name).lower() if hasattr(voice, 'name') else ""
                        
                        # Determine if this is a Japanese voice
                        is_japanese = ("japanese" in voice_name or 
                                       "ja" in voice_name or 
                                       any("ja" in lang for lang in languages))
                        
                        if is_japanese:
                            if "female" in voice_name or "f" in getattr(voice, 'id', "").lower():
                                voices["female"].append({"id": voice.id, "name": voice.name, "engine": ENGINE_PYTTSX3})
                            else:
                                voices["male"].append({"id": voice.id, "name": voice.name, "engine": ENGINE_PYTTSX3})
                    except Exception as e:
                        logger.warning(f"Error processing voice {voice}: {str(e)}")
                        continue
                
                # If we have at least one male voice, designate it as announcer
                if voices["male"]:
                    voices["announcer"].append(voices["male"][0])
                    
                logger.info(f"Found {len(voices['male'])} male and {len(voices['female'])} female pyttsx3 voices")
        except Exception as e:
            logger.warning(f"Error getting pyttsx3 voices: {str(e)}")
        
        # For gTTS, we don't have different voices but can specify language
        voices["male"].append({"id": "gtts_ja_male", "name": "gTTS Japanese Male", "engine": ENGINE_GTTS})
        voices["female"].append({"id": "gtts_ja_female", "name": "gTTS Japanese Female", "engine": ENGINE_GTTS})
        voices["announcer"].append({"id": "gtts_ja_announcer", "name": "gTTS Japanese Announcer", "engine": ENGINE_GTTS})
        
        return voices
    
    def get_voice_for_role(self, role):
        """Get an appropriate voice for the given role"""
        role = role.upper()
        
        if role == "ANNOUNCER" and self.available_voices["announcer"]:
            return random.choice(self.available_voices["announcer"])
        elif "FEMALE" in role and self.available_voices["female"]:
            return random.choice(self.available_voices["female"])
        elif "MALE" in role and self.available_voices["male"]:
            return random.choice(self.available_voices["male"])
        else:
            # Default to any available voice
            all_voices = (
                self.available_voices["male"] + 
                self.available_voices["female"] + 
                self.available_voices["announcer"]
            )
            return random.choice(all_voices) if all_voices else None
    
    def text_to_speech(self, text, output_path=None, voice_info=None):
        """Convert text to speech using the specified engine and voice"""
        if not text:
            raise ValueError("Text cannot be empty")
        
        # Default to a temporary file if no output path is provided
        if not output_path:
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            output_path = temp_file.name
            temp_file.close()
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # If no voice provided, pick one randomly
        if not voice_info:
            all_voices = (
                self.available_voices["male"] + 
                self.available_voices["female"] + 
                self.available_voices["announcer"]
            )
            voice_info = random.choice(all_voices) if all_voices else None
        
        # Determine which engine to use based on voice_info
        engine = self.primary_engine
        if voice_info and "engine" in voice_info:
            engine = voice_info["engine"]
            
        # If pyttsx3 was selected but isn't available, switch to gTTS
        if engine == ENGINE_PYTTSX3 and not self._pyttsx3_available:
            logger.info("Switching from pyttsx3 to gTTS because pyttsx3 is not available")
            engine = ENGINE_GTTS
        
        try:
            if engine == ENGINE_PYTTSX3:
                self._pyttsx3_tts(text, output_path, voice_info)
            elif engine == ENGINE_GTTS:
                self._gtts_tts(text, output_path)
            else:
                raise ValueError(f"Unknown engine: {engine}")
            
            logger.info(f"Generated speech at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error with {engine}: {str(e)}")
            
            # Try fallback engine if primary failed
            if engine != self.fallback_engine:
                logger.info(f"Trying fallback engine: {self.fallback_engine}")
                
                # If fallback is pyttsx3 but it's not available, use gTTS instead
                if self.fallback_engine == ENGINE_PYTTSX3 and not self._pyttsx3_available:
                    logger.info("Fallback engine pyttsx3 not available, using gTTS instead")
                    engine = ENGINE_GTTS
                    self._gtts_tts(text, output_path)
                    return output_path
                else:
                    return self.text_to_speech(text, output_path, None)
            else:
                raise
    
    def _pyttsx3_tts(self, text, output_path, voice_info):
        """Generate speech using pyttsx3 (works offline)"""
        engine = pyttsx3.init()
        
        # Set voice if specified and available
        if voice_info and "id" in voice_info:
            engine.setProperty('voice', voice_info["id"])
        
        # Set rate and volume
        engine.setProperty('rate', 170)  # Slightly slower for Japanese
        engine.setProperty('volume', 1.0)
        
        # Save to file
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    
    def _gtts_tts(self, text, output_path):
        """Generate speech using gTTS (requires internet)"""
        # Create gTTS object
        tts = gTTS(text=text, lang='ja', slow=False)
        
        # Save to file
        tts.save(output_path)

    def generate_conversation_audio(self, conversation, output_dir=None, output_filename=None):
        """
        Generate audio for a conversation with multiple speakers
        
        Args:
            conversation: List of dictionaries with 'role' and 'text' keys
            output_dir: Directory to save audio files
            output_filename: Name for the final combined audio file
            
        Returns:
            str: Path to the combined audio file
        """
        if not conversation:
            raise ValueError("Conversation cannot be empty")
        
        # Set default output directory
        if not output_dir:
            output_dir = AUDIO_DIR
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True, parents=True)
        
        # Set default output filename
        if not output_filename:
            output_filename = f"conversation_{int(random.random() * 10000)}.mp3"
        
        output_path = output_dir / output_filename
        combined_output_path = str(output_path)
        
        # Generate individual audio files for each speaker
        audio_segments = []
        
        for i, segment in enumerate(conversation):
            role = segment.get('role', 'UNKNOWN')
            text = segment.get('text', '').strip()
            
            if not text:
                continue
            
            # Get appropriate voice for this role
            voice = self.get_voice_for_role(role)
            
            # Generate audio for this segment
            segment_filename = f"segment_{i}_{role.lower()}.mp3"
            segment_path = output_dir / segment_filename
            
            try:
                self.text_to_speech(text, str(segment_path), voice)
                audio_segments.append(str(segment_path))
            except Exception as e:
                logger.error(f"Error generating audio for segment {i}: {str(e)}")
                continue
        
        # Combine all audio segments using FFmpeg
        if audio_segments:
            try:
                self._combine_audio_files(audio_segments, combined_output_path)
                logger.info(f"Combined audio saved to {combined_output_path}")
                
                # Clean up individual segments
                for segment_path in audio_segments:
                    try:
                        os.remove(segment_path)
                    except:
                        pass
                
                return combined_output_path
            except Exception as e:
                logger.error(f"Error combining audio segments: {str(e)}")
                # If combining failed, return the first segment
                return audio_segments[0] if audio_segments else None
        
        return None
    
    def _combine_audio_files(self, input_files, output_file):
        """Combine multiple audio files into a single file using pydub"""
        try:
            # Import pydub inside function to avoid global import issues
            from pydub import AudioSegment
            
            # Initialize with empty audio
            combined = AudioSegment.silent(duration=500)  # Start with 500ms silence
            
            # Add each file
            for file_path in input_files:
                try:
                    # Skip files that don't exist
                    if not os.path.exists(file_path):
                        logger.warning(f"Audio file does not exist: {file_path}")
                        continue
                        
                    # Load this segment
                    segment = AudioSegment.from_file(file_path)
                    
                    # Ensure reasonable volume
                    if segment.dBFS < -30:  # If too quiet
                        segment = segment + min(10, -30 - segment.dBFS)  # Boost by up to 10dB
                    
                    # Add to combined audio
                    combined += segment
                    
                except Exception as e:
                    logger.warning(f"Error adding audio file {file_path}: {str(e)}")
                    # Continue with other files
                    continue
            
            # Add final silence
            combined += AudioSegment.silent(duration=1000)  # End with 1 second silence
            
            # Export the combined file
            combined.export(output_file, format="mp3")
            return True
            
        except Exception as e:
            logger.error(f"Error combining audio files: {str(e)}")
            
            # Fallback: Try using ffmpeg if pydub fails
            try:
                import subprocess
                
                # Create a text file listing all input files
                list_file = output_file + ".list"
                with open(list_file, 'w') as f:
                    for file_path in input_files:
                        if os.path.exists(file_path):
                            f.write(f"file '{os.path.abspath(file_path)}'\n")
                
                # Combine using ffmpeg
                subprocess.run([
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", list_file, "-c", "copy", output_file
                ], check=True, capture_output=True)
                
                # Remove the temporary list file
                os.remove(list_file)
                return True
                
            except Exception as sub_e:
                logger.error(f"Fallback ffmpeg also failed: {str(sub_e)}")
                
                # Last resort: Just copy the first file
                if input_files:
                    try:
                        shutil.copy(input_files[0], output_file)
                        return True
                    except:
                        pass
                        
                return False
    
    def parse_jlpt_script(self, script_text):
        """
        Parse a JLPT-style listening script into a conversation format
        
        Args:
            script_text: Text of the JLPT script
            
        Returns:
            list: List of dictionaries with 'role' and 'text' keys
        """
        # Regular expressions to match different parts of the script
        announcer_pattern = r'\[?ANNOUNCER\]?\s*[:：]?\s*(.+)'
        speaker_pattern = r'\[?(MALE|FEMALE|MAN|WOMAN|BOY|GIRL|SPEAKER\s*\d*)\]?\s*[:：]?\s*(.+)'
        
        lines = script_text.strip().split('\n')
        conversation = []
        
        current_role = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is an announcer line
            announcer_match = re.match(announcer_pattern, line, re.IGNORECASE)
            if announcer_match:
                # If we were building up text for a previous role, add it
                if current_role and current_text:
                    conversation.append({
                        'role': current_role,
                        'text': ' '.join(current_text)
                    })
                
                current_role = "ANNOUNCER"
                current_text = [announcer_match.group(1).strip()]
                continue
            
            # Check if this is a speaker line
            speaker_match = re.match(speaker_pattern, line, re.IGNORECASE)
            if speaker_match:
                # If we were building up text for a previous role, add it
                if current_role and current_text:
                    conversation.append({
                        'role': current_role,
                        'text': ' '.join(current_text)
                    })
                
                current_role = speaker_match.group(1).upper()
                current_text = [speaker_match.group(2).strip()]
                continue
            
            # If it's not a new speaker, add to current text
            if current_role and current_text:
                current_text.append(line)
            else:
                # Default to announcer if no role is specified yet
                current_role = "ANNOUNCER"
                current_text = [line]
        
        # Add the last segment
        if current_role and current_text:
            conversation.append({
                'role': current_role,
                'text': ' '.join(current_text)
            })
        
        return conversation
    
    def generate_jlpt_audio(self, script, output_dir, output_filename=None):
        """Generate audio for a JLPT listening exercise script - simplified version"""
        try:
            # Create safe output path
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True, parents=True)
            
            if output_filename:
                output_path = output_dir / output_filename
            else:
                output_path = output_dir / f"exercise_{uuid.uuid4()}.mp3"
            
            # Force garbage collection before processing
            gc.collect()
            
            # Instead of parsing the script into segments, just generate one file for the entire script
            # This is much simpler and more reliable
            try:
                # Use gTTS for the entire script
                from gtts import gTTS
                
                # Clean up the script to make it more suitable for TTS
                clean_script = script.replace('[ANNOUNCER]:', '')
                clean_script = clean_script.replace('[ANNOUNCER]', '')
                clean_script = clean_script.replace('[MALE]:', '')
                clean_script = clean_script.replace('[MALE]', '')
                clean_script = clean_script.replace('[FEMALE]:', '')
                clean_script = clean_script.replace('[FEMALE]', '')
                
                # Generate and save the audio
                tts = gTTS(text=clean_script, lang='ja', slow=False)
                tts.save(str(output_path))
                
                logger.info(f"Generated speech at {output_path}")
                return str(output_path)
                
            except Exception as e:
                logger.error(f"Error generating speech: {str(e)}")
                return None
            
        except Exception as e:
            logger.error(f"Error in generate_jlpt_audio: {str(e)}")
            return None


# For testing
if __name__ == "__main__":
    tts = JapaneseTTS()
    
    # Test a simple conversation
    conversation = [
        {"role": "ANNOUNCER", "text": "では、問題１を始めます。"},
        {"role": "FEMALE", "text": "すみません、この電車は大阪に行きますか？"},
        {"role": "MALE", "text": "いいえ、大阪に行く電車は隣のホームです。"},
        {"role": "ANNOUNCER", "text": "女の人は何を尋ねましたか？"}
    ]
    
    output_path = tts.generate_conversation_audio(conversation)
    print(f"Conversation audio generated at: {output_path}")
    
    # Test JLPT script parsing
    script = """
    [ANNOUNCER]: 問題１を始めます。
    
    [FEMALE]: すみません、この電車は大阪に行きますか？
    
    [MALE]: いいえ、大阪に行く電車は隣のホームです。
    
    [ANNOUNCER]: 女の人は何を尋ねましたか？
    
    １．大阪に行く電車はどこですか？
    ２．この電車は隣のホームに行きますか？
    ３．電車は何時に出発しますか？
    ４．大阪行きの電車はありますか？
    """
    
    conversation = tts.parse_jlpt_script(script)
    print(f"Parsed conversation: {json.dumps(conversation, ensure_ascii=False, indent=2)}")
    
    output_path = tts.generate_jlpt_audio(script)
    print(f"JLPT audio generated at: {output_path}") 