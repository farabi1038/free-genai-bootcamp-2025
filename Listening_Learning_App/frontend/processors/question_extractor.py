"""
Question extraction module for YouTube videos
"""

import re
import streamlit as st
import requests
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from Listening_Learning_App.frontend.processors.youtube import extract_youtube_id

# Configure logging
logger = logging.getLogger(__name__)

def extract_questions_from_youtube(video_url):
    """
    Extract questions from a YouTube video transcript
    
    Parameters:
        video_url (str): YouTube URL
    
    Returns:
        dict: Dictionary with extracted content (questions or conversations)
    """
    try:
        # Validate the YouTube URL
        video_id = extract_youtube_id(video_url)
        if not video_id:
            st.error("無効なYouTube URLです。有効なURLを入力してください。(Invalid YouTube URL. Please provide a valid URL.)")
            # Show examples of valid URLs
            st.info("有効なURL例 (Valid URL examples):\n- https://www.youtube.com/watch?v=2aqVJS6QOoY\n- https://youtu.be/2aqVJS6QOoY")
            return None
            
        st.info(f"処理中のビデオID: {video_id} (Processing video ID: {video_id})")
        
        # Get transcript using youtube_transcript_api (open source)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'ja-JP'])
            st.success("日本語字幕を正常に取得しました！(Japanese transcript successfully retrieved!)")
        except Exception as e:
            st.error(f"日本語字幕の取得に失敗しました: {str(e)} (Failed to get Japanese transcript)")
            st.info("いずれかの利用可能な字幕を取得しようとしています... (Trying to get any available transcript...)")
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                st.success("字幕を取得しました（非日本語）。(Transcript retrieved (non-Japanese).)")
            except Exception as e2:
                st.error(f"いずれの字幕も取得できませんでした: {str(e2)} (Failed to get any transcript)")
                # Try to get auto-generated transcript as last resort
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en', 'auto'])
                    st.success("自動生成された字幕を取得しました。(Auto-generated transcript retrieved.)")
                except Exception as e3:
                    st.error("このビデオに利用可能な字幕がありません。(No transcript available for this video.)")
                    return None
            
        # Format transcript for processing
        formatted_transcript = []
        for segment in transcript:
            formatted_transcript.append({
                "start": segment["start"],
                "text": segment["text"],
                "duration": segment["duration"]
            })
            
        # Show transcript preview for debugging
        with st.expander("字幕の内容 (Transcript Content)", expanded=False):
            st.write(f"取得した字幕セグメント: {len(formatted_transcript)}個 (Found {len(formatted_transcript)} transcript segments)")
            if len(formatted_transcript) > 0:
                st.write("字幕の内容 (Transcript content):")
                for segment in formatted_transcript:
                    st.write(f"{segment['start']:.1f}s: {segment['text']}")
        
        # Extract ONLY REAL questions from the transcript (questions actually asked in the video)
        actual_questions = []
        
        # Combine all transcript text
        full_text = " ".join([segment["text"] for segment in formatted_transcript])
        st.info(f"字幕内の文字数: {len(full_text)}文字 (Transcript length: {len(full_text)} characters)")
        
        # Japanese question detection patterns
        question_patterns = [
            # Pattern for questions ending with ka (か) and question mark
            r'([^。？！]*[か][？])',
            # Pattern for questions ending with ka (か) and period
            r'([^。？！]*[か][。])',
            # Pattern for questions ending with a question mark
            r'([^。？！]*[？])',
            # Pattern for polite questions
            r'([^。？！]*(?:ですか|ますか|のですか|のでしょうか)[？。]?)',
            # Pattern for questions with interrogatives
            r'([^。？！]*(?:何|なに|どう|なぜ|どこ|誰|だれ|いつ|どんな|どの)[^。？！]*[か][？。]?)'
        ]
        
        # Find all questions in the transcript
        for pattern in question_patterns:
            matches = re.finditer(pattern, full_text)
            for match in matches:
                question_text = match.group(0).strip()
                
                # Skip very short questions or duplicates
                if len(question_text) < 10:
                    continue
                    
                if question_text in [q["question_text"] for q in actual_questions]:
                    continue
                
                # Find which segment this question appears in
                segment_idx = None
                for idx, segment in enumerate(formatted_transcript):
                    if question_text in segment["text"]:
                        segment_idx = idx
                        break
                
                # If we couldn't find the segment, try to find the most relevant one
                if segment_idx is None:
                    for idx, segment in enumerate(formatted_transcript):
                        for word in question_text.split():
                            if len(word) > 2 and word in segment["text"]:
                                segment_idx = idx
                                break
                        if segment_idx is not None:
                            break
                
                # If we still couldn't find a segment, use the first segment
                if segment_idx is None:
                    segment_idx = 0
                
                # Get the segment containing this question
                segment = formatted_transcript[segment_idx]
                
                # Get context (surrounding segments)
                context_before = []
                for i in range(max(0, segment_idx - 2), segment_idx):
                    context_before.append(formatted_transcript[i]["text"])
                    
                context_after = []
                for i in range(segment_idx + 1, min(len(formatted_transcript), segment_idx + 3)):
                    context_after.append(formatted_transcript[i]["text"])
                
                # Add the question
                actual_questions.append({
                    "question_text": question_text,
                    "segment_start": segment["start"],
                    "segment_end": segment["start"] + segment["duration"],
                    "context_before": " ".join(context_before),
                    "context_after": " ".join(context_after)
                })
        
        # Check if we found any questions
        if not actual_questions:
            st.warning("動画から直接質問を見つけることができませんでした。(No direct questions found in the video.)")
            
            # Extract conversation segments as a fallback
            conversations = extract_conversations(formatted_transcript)
            
            # If we have conversations, show them
            if conversations:
                st.success(f"{len(conversations)}個の会話を見つけました。(Found {len(conversations)} conversations.)")
                return {
                    "type": "conversations",
                    "conversations": conversations
                }
            else:
                st.error("この動画から質問や会話を抽出できませんでした。(Could not extract questions or conversations.)")
                return None
                
        # Sort questions by timestamp
        actual_questions.sort(key=lambda q: q["segment_start"])
        
        # If Ollama is available, try to translate the questions
        if st.session_state.get("ollama_available", False):
            for question in actual_questions:
                try:
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": st.session_state.get("ollama_model", "mistral"),
                            "prompt": f"Translate this Japanese text to English: {question['question_text']}",
                        },
                        stream=False,
                        timeout=5
                    )
                    if response.status_code == 200:
                        question["english_translation"] = response.json().get('response', '')
                except:
                    question["english_translation"] = "(Translation unavailable)"
        
        # Return the list of questions
        return {
            "type": "questions",
            "questions": actual_questions
        }
        
    except Exception as e:
        st.error(f"Error extracting questions: {str(e)}")
        return None

def extract_conversations(transcript_segments, min_length=30, max_segments=5):
    """
    Extract complete conversation segments from the transcript
    
    Parameters:
        transcript_segments (list): List of transcript segments
        min_length (int): Minimum length of a conversation in characters
        max_segments (int): Maximum number of conversation segments to extract
    
    Returns:
        list: List of conversation segments
    """
    conversations = []
    
    if not transcript_segments:
        return conversations
    
    # Group transcript segments into conversations
    current_conversation = {
        "start_time": transcript_segments[0]["start"],
        "text": transcript_segments[0]["text"],
        "segments": [transcript_segments[0]]
    }
    
    for i in range(1, len(transcript_segments)):
        current_segment = transcript_segments[i]
        previous_segment = transcript_segments[i-1]
        
        # Check if there's a significant pause between segments (more than 3 seconds)
        time_gap = current_segment["start"] - (previous_segment["start"] + previous_segment["duration"])
        
        if time_gap > 3.0:  # New conversation if gap > 3 seconds
            # Save previous conversation if it's long enough
            if len(current_conversation["text"]) >= min_length:
                conversations.append(current_conversation)
            
            # Start a new conversation
            current_conversation = {
                "start_time": current_segment["start"],
                "text": current_segment["text"],
                "segments": [current_segment]
            }
        else:
            # Continue current conversation
            current_conversation["text"] += " " + current_segment["text"]
            current_conversation["segments"].append(current_segment)
    
    # Add the last conversation if it's long enough
    if len(current_conversation["text"]) >= min_length:
        conversations.append(current_conversation)
    
    # Sort conversations by length (longer ones first) and limit to max_segments
    conversations.sort(key=lambda c: len(c["text"]), reverse=True)
    return conversations[:max_segments] 