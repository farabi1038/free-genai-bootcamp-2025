"""
Synthetic question generation functions for when natural questions can't be extracted.
"""

import streamlit as st
import re
import requests

def generate_synthetic_questions(video_id):
    """Generate synthetic questions when no transcript is available"""
    try:
        # Try to get video title at least
        
        # Safe import of BeautifulSoup
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # If BeautifulSoup is not available, we'll just use a default title
            class DummySoup:
                def __init__(self, *args, **kwargs):
                    pass
                def find(self, *args, **kwargs):
                    return None
            BeautifulSoup = DummySoup
        
        # Use a default title in case we can't fetch the real one
        title = "Japanese Video"
        
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            response = requests.get(url, timeout=5)  # Add timeout to prevent hanging
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title_tag = soup.find('title')
                if title_tag and hasattr(title_tag, 'text'):  # Check if title_tag has text attribute
                    title = title_tag.text.replace(' - YouTube', '')
        except Exception as e:
            st.warning(f"Could not fetch video title: {str(e)}")
        
        # Create standard Japanese learning questions
        questions = []
        standard_questions = [
            {
                "question_text": "この動画は何について話していますか？",
                "english_translation": "(Translation: What is this video talking about?)",
                "options": [
                    "日本語の勉強について (About studying Japanese)",
                    "日本の文化について (About Japanese culture)",
                    "日常会話について (About daily conversation)"
                ]
            },
            {
                "question_text": "この動画の難易度はどのくらいですか？",
                "english_translation": "(Translation: How difficult is this video?)",
                "options": [
                    "初級レベル (Beginner level)",
                    "中級レベル (Intermediate level)",
                    "上級レベル (Advanced level)"
                ]
            },
            {
                "question_text": "この動画から新しい単語をいくつ学びましたか？",
                "english_translation": "(Translation: How many new words did you learn from this video?)",
                "options": [
                    "0-5つ (0-5 words)",
                    "6-10つ (6-10 words)",
                    "10つ以上 (More than 10 words)"
                ]
            },
            {
                "question_text": "この動画の内容は理解できましたか？",
                "english_translation": "(Translation: Could you understand the content of this video?)",
                "options": [
                    "はい、よく理解できました (Yes, I understood well)",
                    "だいたい理解できました (I mostly understood)",
                    "あまり理解できませんでした (I didn't understand much)"
                ]
            }
        ]
        
        # Add timestamps spread throughout
        timestamps = [10, 30, 60, 90]
        
        # Create questions with different timestamps
        for i, q in enumerate(standard_questions[:4]):
            questions.append({
                "question_text": q["question_text"],
                "english_translation": q["english_translation"],
                "segment_start": timestamps[i],
                "segment_end": timestamps[i] + 5,
                "options": q["options"],
                "correct_answer": q["options"][0],  # Default to first option
                "context_before": f"「{title}」に関する質問です。",
                "context_after": "動画を見て、最も適切な答えを選んでください。",
                "question_type": "synthetic"
            })
        
        return questions
        
    except Exception as e:
        st.error(f"Error generating synthetic questions: {str(e)}")
        # Return at least one question as absolute fallback
        return [{
            "question_text": "この動画の内容を理解できましたか？",
            "english_translation": "(Translation: Could you understand the content of this video?)",
            "segment_start": 30,
            "segment_end": 35,
            "options": [
                "はい (Yes)", 
                "いいえ (No)", 
                "わかりません (Not sure)"
            ],
            "correct_answer": "はい (Yes)",
            "context_before": "動画の内容に関する質問です。",
            "context_after": "自分の理解度を確認してください。",
            "question_type": "synthetic"
        }] 