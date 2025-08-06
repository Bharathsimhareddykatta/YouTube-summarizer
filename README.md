# YouTube Script Summarizer

A powerful Streamlit application that extracts transcripts from YouTube videos and creates intelligent AI-powered summaries using Claude AI.

## Features

- 🎬 **YouTube Transcript Extraction**: Automatically fetch transcripts from YouTube videos using yt-dlp
- 🤖 **AI-Powered Summarization**: Uses Claude AI via OpenRouter for intelligent, contextual summaries
- 💾 **Export Options**: Download summaries as PDF or DOCX files
- 🎨 **Modern UI**: Clean, responsive interface with progress indicators
- 🔧 **Smart Transcript Cleaning**: Automatically removes HTML tags, timestamps, and duplicates
- 📊 **Dual View**: See both raw and cleaned transcript versions

## Live Demo

🚀 **Deployed on Streamlit Cloud**: [Your App URL Here]

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd yt_summarizer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key**:
   - Get your API key from [OpenRouter](https://openrouter.ai/keys)
   - Create a `.env` file in the project root:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Usage

1. **Run the application**:
   ```bash
   streamlit run app.py
   ```

2. **Choose your input method**:
   - **YouTube URL**: Paste a YouTube video URL to automatically fetch the transcript
   - **Paste Transcript**: Manually paste your transcript text

3. **Generate AI Summary**:
   - Click "Generate AI Summary" to create an intelligent summary using Claude AI
   - Download as PDF or DOCX for offline use

## Deployment

### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set environment variables:
     - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - Deploy!

### Option 2: Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set OPENROUTER_API_KEY=your_api_key_here
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

### Option 3: Railway

1. **Connect to Railway**:
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub repository

2. **Set environment variables**:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key

3. **Deploy automatically**!

## How It Works

### Transcript Extraction
- Uses yt-dlp for reliable YouTube transcript extraction
- Supports multiple URL formats (youtube.com, youtu.be, embed URLs)
- Handles various subtitle formats and languages
- Provides clear error messages for unavailable transcripts

### AI Summarization
- Uses OpenRouter API with Claude-3-5-Sonnet model
- Provides intelligent, contextual summaries
- Handles long transcripts efficiently
- Multiple model fallbacks for reliability

### Transcript Cleaning
- Removes HTML tags and timestamps
- Eliminates duplicate words and phrases
- Cleans up formatting artifacts
- Prepares clean text for optimal summarization

## File Structure

```
yt_summarizer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku deployment
├── setup.sh              # Streamlit Cloud setup
├── runtime.txt           # Python version
├── README.md             # This file
├── utils/
│   ├── youtube_utils.py  # YouTube transcript extraction
│   └── summarizer.py     # AI summarization logic
└── .env                  # API keys (create this file)
```

## Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)

## Troubleshooting

### Common Issues

1. **"API key not found" error**:
   - Make sure OPENROUTER_API_KEY is set in your environment variables
   - Check your deployment platform's environment variable settings

2. **"No transcript available" error**:
   - The video might not have captions/transcripts enabled
   - Try a different video with available subtitles

3. **API summarization fails**:
   - Check your OpenRouter account has sufficient credits
   - Verify your API key is correct
   - Ensure stable internet connection

### Dependencies

The application requires:
- `streamlit`: Web application framework
- `yt-dlp`: YouTube transcript extraction
- `requests`: HTTP requests for API calls
- `python-dotenv`: Environment variable management
- `fpdf`: PDF generation
- `python-docx`: DOCX file creation

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application!

## License

This project is open source and available under the MIT License. 