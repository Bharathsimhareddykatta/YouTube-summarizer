import re
import time
import requests
import json

def clean_transcript(transcript):
    """
    Clean transcript by removing HTML tags, timestamps, and formatting elements
    """
    if not transcript:
        return transcript
    
    # Remove HTML tags like <c>, <00:00:27.119>, etc.
    transcript = re.sub(r'<[^>]+>', '', transcript)
    
    # Remove timestamp patterns like <00:00:27.119>
    transcript = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d+>', '', transcript)
    
    # Remove duplicate words/phrases that often occur in VTT
    words = transcript.split()
    cleaned_words = []
    for i, word in enumerate(words):
        # Skip if it's a duplicate of the previous word
        if i > 0 and word.lower() == words[i-1].lower():
            continue
        cleaned_words.append(word)
    
    # Join back and clean up extra whitespace
    cleaned_transcript = ' '.join(cleaned_words)
    cleaned_transcript = re.sub(r'\s+', ' ', cleaned_transcript).strip()
    
    # Remove repetitive phrases (common in VTT transcripts)
    # Split into sentences and remove duplicates
    sentences = re.split(r'[.!?]+', cleaned_transcript)
    unique_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and sentence not in unique_sentences:
            unique_sentences.append(sentence)
    
    # Join sentences back together
    final_transcript = '. '.join(unique_sentences)
    
    # Clean up any remaining artifacts
    final_transcript = re.sub(r'\s+', ' ', final_transcript).strip()
    final_transcript = re.sub(r'\.+', '.', final_transcript)  # Remove multiple dots
    
    return final_transcript

def get_transcript(video_url):
    try:
        # Clean the URL
        video_url = video_url.strip()
        
        # Extract video ID from URL
        video_id = None
        
        # Handle different YouTube URL formats
        if "v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        elif "youtube.com/embed/" in video_url:
            video_id = video_url.split("youtube.com/embed/")[1].split("?")[0]
        else:
            return "❌ Invalid YouTube URL format. Please use a valid YouTube URL."
        
        # Validate video ID format
        if not video_id or len(video_id) != 11:
            return "❌ Invalid video ID extracted from URL."
        
        print(f"Attempting to fetch transcript for video ID: {video_id}")
        
        # Try multiple methods (yt-dlp is most reliable)
        methods = [
            ("yt-dlp Method", get_transcript_ytdlp),
            ("Direct API Method", get_transcript_direct_api),
            ("Web Scraping Method", get_transcript_web_scraping)
        ]
        
        for method_name, method_func in methods:
            try:
                print(f"Trying {method_name}...")
                result = method_func(video_id, video_url)
                if not result.startswith("❌"):
                    print(f"✅ {method_name} successful!")
                    # Clean the transcript before returning
                    cleaned_result = clean_transcript(result)
                    print(f"Cleaned transcript length: {len(cleaned_result)} characters")
                    return cleaned_result
                else:
                    print(f"❌ {method_name} failed: {result}")
            except Exception as e:
                print(f"❌ {method_name} error: {str(e)}")
                continue
        
        return "❌ All transcript methods failed. This video may not have accessible transcripts."
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return f"❌ Unexpected error: {str(e)}"

def get_transcript_ytdlp(video_id, video_url):
    """Use yt-dlp to extract transcript (most reliable method)"""
    try:
        import yt_dlp
        
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'en-US', 'en-GB'],
            'skip_download': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info = ydl.extract_info(video_url, download=False)
            
            # Try to get subtitles
            if 'subtitles' in info:
                for lang_code, subtitles in info['subtitles'].items():
                    if lang_code in ['en', 'en-US', 'en-GB']:
                        for sub in subtitles:
                            if sub.get('ext') == 'vtt':
                                # Download and parse VTT
                                subtitle_url = sub['url']
                                response = requests.get(subtitle_url, timeout=10)
                                if response.status_code == 200:
                                    return parse_vtt_content(response.text)
            
            # Try automatic subtitles
            if 'automatic_captions' in info:
                for lang_code, captions in info['automatic_captions'].items():
                    if lang_code in ['en', 'en-US', 'en-GB']:
                        for cap in captions:
                            if cap.get('ext') == 'vtt':
                                subtitle_url = cap['url']
                                response = requests.get(subtitle_url, timeout=10)
                                if response.status_code == 200:
                                    return parse_vtt_content(response.text)
        
        return "❌ No subtitles found with yt-dlp."
        
    except ImportError:
        return "❌ yt-dlp not installed. Please install with: pip install yt-dlp"
    except Exception as e:
        return f"❌ yt-dlp error: {str(e)}"

def parse_vtt_content(vtt_content):
    """Parse VTT subtitle content and extract text"""
    try:
        lines = vtt_content.split('\n')
        transcript_parts = []
        
        for line in lines:
            line = line.strip()
            # Skip timestamp lines and empty lines
            if (line and 
                not line.startswith('WEBVTT') and 
                not line.startswith('-->') and 
                not re.match(r'^\d+:\d+:\d+', line) and
                not line.isdigit()):
                
                # Clean the line of HTML tags and timestamps
                cleaned_line = clean_transcript(line)
                if cleaned_line:
                    transcript_parts.append(cleaned_line)
        
        if transcript_parts:
            full_transcript = " ".join(transcript_parts)
            return full_transcript
        else:
            return "❌ No transcript content found in VTT."
            
    except Exception as e:
        return f"❌ VTT parsing error: {str(e)}"

def get_transcript_direct_api(video_id, video_url):
    """Direct API method using YouTube's internal API"""
    try:
        # Try multiple language codes
        languages = ['en', 'en-US', 'en-GB', 'auto']
        
        for lang in languages:
            try:
                url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang={lang}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200 and response.text.strip():
                    # Parse the XML response manually
                    import xml.etree.ElementTree as ET
                    try:
                        root = ET.fromstring(response.text)
                        transcript_parts = []
                        for text in root.findall('.//text'):
                            if text.text:
                                transcript_parts.append(text.text.strip())
                        
                        if transcript_parts:
                            full_transcript = " ".join(transcript_parts)
                            return full_transcript
                    except ET.ParseError:
                        continue
            except:
                continue
        
        return "❌ Direct API method failed."
        
    except Exception as e:
        return f"❌ Direct API error: {str(e)}"

def get_transcript_web_scraping(video_id, video_url):
    """Web scraping method to extract transcript from video page"""
    try:
        # Get the video page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(video_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Look for transcript data in the page
            content = response.text
            
            # Try to find transcript data in various formats
            patterns = [
                r'"captions":\s*\{[^}]*"playerCaptionsTracklistRenderer":\s*\{[^}]*\}',
                r'"transcript":\s*\{[^}]*\}',
                r'"captions":\s*\{[^}]*\}',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    # Try to extract transcript from the JSON-like data
                    try:
                        # Look for actual transcript text in the page
                        transcript_pattern = r'"text":\s*"([^"]*)"'
                        transcript_matches = re.findall(transcript_pattern, content)
                        
                        if transcript_matches:
                            # Filter out very short or non-transcript text
                            valid_transcripts = [t for t in transcript_matches if len(t) > 10 and not t.startswith('http')]
                            if valid_transcripts:
                                return " ".join(valid_transcripts[:50])  # Limit to first 50 entries
                    except:
                        continue
        
        return "❌ Web scraping method failed."
        
    except Exception as e:
        return f"❌ Web scraping error: {str(e)}"

def test_video_accessibility(video_id):
    """
    Test if the video is accessible before trying to get transcript
    """
    try:
        # Try to access video info
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False
