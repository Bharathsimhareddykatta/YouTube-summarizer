import re
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data with better error handling
def ensure_nltk_data():
    """Ensure all required NLTK data is downloaded"""
    required_packages = ['punkt', 'stopwords', 'wordnet', 'punkt_tab']
    
    for package in required_packages:
        try:
            nltk.data.find(f'tokenizers/{package}')
        except LookupError:
            try:
                print(f"Downloading NLTK package: {package}")
                nltk.download(package, quiet=True)
            except Exception as e:
                print(f"Failed to download {package}: {str(e)}")
                return False
    
    # Also try to download punkt_tab specifically
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            print("Downloading NLTK package: punkt_tab")
            nltk.download('punkt_tab', quiet=True)
        except Exception as e:
            print(f"Failed to download punkt_tab: {str(e)}")
    
    return True

# Initialize NLTK data
ensure_nltk_data()

def summarize_text(transcript, max_sentences=10):
    """
    Create a summary using extractive summarization techniques
    """
    try:
        # Ensure NLTK data is available
        if not ensure_nltk_data():
            return "❌ NLTK data not available. Please check your internet connection and try again."
        
        # Clean the transcript
        transcript = re.sub(r'\s+', ' ', transcript).strip()
        
        if not transcript:
            return "❌ Empty transcript provided."
        
        # Split into sentences
        try:
            sentences = sent_tokenize(transcript)
        except Exception as e:
            # Fallback: simple sentence splitting
            sentences = [s.strip() for s in re.split(r'[.!?]+', transcript) if s.strip()]
        
        if len(sentences) == 0:
            return "❌ No valid sentences found in transcript."
        
        if len(sentences) <= max_sentences:
            return transcript
        
        # Tokenize and preprocess words
        try:
            stop_words = set(stopwords.words('english'))
            lemmatizer = WordNetLemmatizer()
        except Exception as e:
            # Fallback: simple word processing
            stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            lemmatizer = None
        
        # Calculate word frequencies
        word_freq = Counter()
        for sentence in sentences:
            try:
                words = word_tokenize(sentence.lower())
            except:
                # Fallback: simple word splitting
                words = re.findall(r'\b\w+\b', sentence.lower())
            
            if lemmatizer:
                words = [lemmatizer.lemmatize(word) for word in words 
                        if word.isalnum() and word not in stop_words and len(word) > 2]
            else:
                words = [word for word in words 
                        if word.isalnum() and word not in stop_words and len(word) > 2]
            
            word_freq.update(words)
        
        if not word_freq:
            return "❌ No meaningful words found for summarization."
        
        # Calculate sentence scores based on word frequency
        sentence_scores = {}
        for sentence in sentences:
            try:
                words = word_tokenize(sentence.lower())
            except:
                words = re.findall(r'\b\w+\b', sentence.lower())
            
            if lemmatizer:
                words = [lemmatizer.lemmatize(word) for word in words 
                        if word.isalnum() and word not in stop_words and len(word) > 2]
            else:
                words = [word for word in words 
                        if word.isalnum() and word not in stop_words and len(word) > 2]
            
            score = sum(word_freq[word] for word in words)
            sentence_scores[sentence] = score
        
        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), 
                              key=lambda x: x[1], reverse=True)[:max_sentences]
        
        # Sort by original order
        top_sentences = sorted(top_sentences, 
                              key=lambda x: sentences.index(x[0]))
        
        # Create summary
        summary = ' '.join([sentence for sentence, score in top_sentences])
        
        if not summary.strip():
            return "❌ Failed to generate summary."
        
        return summary
        
    except Exception as e:
        return f"❌ Summarization error: {str(e)}"

def summarize_with_api(transcript):
    """
    Alternative API-based summarization (requires API key)
    """
    try:
        import requests
        import os
        from dotenv import load_dotenv

        load_dotenv()
        API_KEY = os.getenv("OPENROUTER_API_KEY")
        
        if not API_KEY:
            return "❌ API key not found. Please set OPENROUTER_API_KEY in your .env file"
        
        if not transcript.strip():
            return "❌ Empty transcript provided."
        
        API_URL = "https://openrouter.ai/api/v1/chat/completions"
        
        # Try different models in order of preference
        models = [
            "anthropic/claude-3-5-sonnet-20241022",  # Latest Claude model
            "anthropic/claude-3-sonnet-20240229",    # Alternative Claude model
            "openai/gpt-4o",                         # GPT-4 as fallback
            "openai/gpt-3.5-turbo",                  # GPT-3.5 as last resort
        ]
        
        for model in models:
            try:
                print(f"Trying model: {model}")
                
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }

                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that summarizes YouTube transcripts. Provide a clear, concise summary that captures the main points and key insights from the transcript."},
                        {"role": "user", "content": f"Please summarize this YouTube transcript in a clear and organized way:\n\n{transcript}"}
                    ],
                    "max_tokens": 1000
                }

                response = requests.post(API_URL, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        print(f"✅ Success with model: {model}")
                        return result['choices'][0]['message']['content']
                    else:
                        print(f"❌ Unexpected response format for model: {model}")
                        continue
                elif response.status_code == 404:
                    print(f"❌ Model not found: {model}")
                    continue
                else:
                    print(f"❌ API Error {response.status_code} for model {model}: {response.text}")
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"❌ Timeout for model: {model}")
                continue
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error for model {model}: {str(e)}")
                continue
            except Exception as e:
                print(f"❌ Error with model {model}: {str(e)}")
                continue
        
        return "❌ All API models failed. Please check your API key and try again."
        
    except Exception as e:
        return f"❌ API summarization error: {str(e)}"
