"""
Question extraction page module for the Listening Learning App frontend
"""

import streamlit as st
from Listening_Learning_App.frontend.processors.question_extractor import extract_questions_from_youtube
from Listening_Learning_App.frontend.processors.youtube import extract_youtube_id
from Listening_Learning_App.frontend.utils.session import go_to_home, go_to_video_selection

def render_extract_questions():
    """Render the question extraction page"""
    st.title("Extract Questions from YouTube")
    
    if "youtube_url" not in st.session_state:
        st.session_state["youtube_url"] = ""
        
    if "extracted_content" not in st.session_state:
        st.session_state["extracted_content"] = None
    
    # Form for URL input
    st.write("### Enter a Japanese YouTube URL")
    youtube_url = st.text_input(
        "日本語 YouTube URL (Japanese YouTube URL)", 
        value=st.session_state.get("youtube_url", ""), 
        key="youtube_url_input",
        help="例: https://www.youtube.com/watch?v=2aqVJS6QOoY"
    )
    
    # Extract button
    col1, col2 = st.columns([3, 1])
    with col2:
        extract_btn = st.button("質問を抽出する (Extract Questions)", key="extract_btn", use_container_width=True)
    
    if extract_btn:
        if not youtube_url:
            st.error("YouTubeのURLを入力してください (Please enter a YouTube URL)")
        else:
            st.session_state["youtube_url"] = youtube_url
            with st.spinner("動画から質問を抽出しています... (Extracting questions from video...)"):
                try:
                    result = extract_questions_from_youtube(youtube_url)
                    if result:
                        st.session_state["extracted_content"] = result
                        if result["type"] == "questions":
                            st.success(f"✅ 成功! {len(result['questions'])}個の質問を抽出しました (Successfully extracted {len(result['questions'])} questions)")
                        else:
                            st.success(f"✅ 成功! {len(result['conversations'])}個の会話を抽出しました (Successfully extracted {len(result['conversations'])} conversations)")
                        st.rerun()  # Refresh to display the content
                    else:
                        st.error("この動画から質問を抽出できませんでした。他の動画を試してください。(Could not extract any questions from this video.)")
                except Exception as e:
                    st.error(f"エラー: {str(e)} (Error processing video)")
                    st.info("別の動画を試すか、インターネット接続を確認してください。(Try a different video URL or check your internet connection.)")
    
    # Display the video if we have content
    if st.session_state.get("extracted_content") and st.session_state.get("youtube_url"):
        video_id = extract_youtube_id(st.session_state["youtube_url"])
        if video_id:
            st.video(f"https://www.youtube.com/watch?v={video_id}")
    
    # Display content if we have it
    if st.session_state.get("extracted_content"):
        content = st.session_state["extracted_content"]
        
        if content["type"] == "questions":
            # Display questions
            questions = content["questions"]
            
            st.markdown("## 動画から抽出された質問 (Questions Extracted from Video)")
            
            for i, question in enumerate(questions):
                with st.expander(f"質問 {i+1}", expanded=True):
                    st.subheader(f"{question['question_text']}")
                    
                    # Display English translation if available
                    if question.get("english_translation"):
                        st.info(f"English: {question['english_translation']}")
                    
                    # Display context
                    st.markdown("### 会話の文脈 (Conversation Context)")
                    
                    if question.get("context_before"):
                        st.markdown("**前 (Before):**")
                        st.markdown(f"*{question['context_before']}*")
                    
                    if question.get("context_after"):
                        st.markdown("**後 (After):**")
                        st.markdown(f"*{question['context_after']}*")
                    
                    # Add timestamp link
                    video_id = extract_youtube_id(st.session_state["youtube_url"])
                    if video_id:
                        start_time = int(question["segment_start"])
                        st.markdown(f"[この質問を動画で見る (Watch this question in the video)](https://www.youtube.com/watch?v={video_id}&t={start_time}s)")
        else:
            # Display conversations
            conversations = content["conversations"]
            
            st.markdown("## 動画から抽出された会話 (Conversations Extracted from Video)")
            
            for i, conversation in enumerate(conversations):
                with st.expander(f"会話 {i+1}", expanded=True):
                    st.markdown("### 会話内容 (Conversation)")
                    st.markdown(f"*{conversation['text']}*")
                    
                    # Try to translate if Ollama is available
                    if st.session_state.get("ollama_available", False):
                        if st.button(f"翻訳する (Translate)", key=f"translate_{i}"):
                            try:
                                import requests
                                with st.spinner("翻訳中... (Translating...)"):
                                    response = requests.post(
                                        "http://localhost:11434/api/generate",
                                        json={
                                            "model": st.session_state.get("ollama_model", "mistral"),
                                            "prompt": f"Translate this Japanese text to English: {conversation['text']}",
                                        },
                                        stream=False,
                                        timeout=10
                                    )
                                    if response.status_code == 200:
                                        translation = response.json().get('response', '')
                                        st.markdown("### 英語訳 (English Translation)")
                                        st.markdown(f"*{translation}*")
                            except Exception as e:
                                st.error(f"翻訳エラー: {str(e)} (Translation error)")
                    
                    # Add timestamp link
                    video_id = extract_youtube_id(st.session_state["youtube_url"])
                    if video_id:
                        start_time = int(conversation["start_time"])
                        st.markdown(f"[この会話を動画で見る (Watch this conversation in the video)](https://www.youtube.com/watch?v={video_id}&t={start_time}s)")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ホームに戻る (Return to Home)", use_container_width=True):
            # Clear extraction results
            if "extracted_content" in st.session_state:
                del st.session_state["extracted_content"]
            go_to_home()
    with col2:
        if st.button("別の動画を選ぶ (Select Another Video)", use_container_width=True):
            # Clear extraction results
            if "extracted_content" in st.session_state:
                del st.session_state["extracted_content"]
            go_to_video_selection() 