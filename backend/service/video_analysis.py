import os, sys, json, re, tempfile, yt_dlp
from urllib.parse import urlparse
from dotenv import load_dotenv
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
client = GoogleGenAI(
    model="models/gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1,
    max_tokens=4096
)

SUPPORTED_PLATFORMS = {
    'youtube.com': 'YouTube', 'youtu.be': 'YouTube',
    'tiktok.com': 'TikTok', 'instagram.com': 'Instagram',
    'facebook.com': 'Facebook', 'fb.watch': 'Facebook',
    'twitter.com': 'X/Twitter', 'x.com': 'X/Twitter'
}

def detect_platform(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '').replace('m.', '')
        path = parsed.path.lower()
        if 'instagram.com' in domain or '/reels/' in path or '/reel/' in path:
            return 'Instagram'
        return next((name for dom, name in SUPPORTED_PLATFORMS.items() if dom in domain), 'Unknown')
    except:
        return 'Unknown'

def extract_video_info(url):
    platform = detect_platform(url)
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'extract_flat': False, 
        'force_generic_extractor': False,
        'writeinfojson': False,
        'writethumbnail': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'skip_download': True
    }
    if platform in ['Instagram', 'Facebook'] and os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'
    if platform == 'X/Twitter':
        ydl_opts['extractor_args'] = {'twitter': ['api=syndication']}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return ydl.sanitize_info(info)
    except Exception as e:
        print(f"Error extracting video info: {e}")
        return None

def get_captions(url):
    platform = detect_platform(url)
    ydl_opts = {'writesubtitles': True, 'writeautomaticsub': True, 'subtitleslangs': ['en'],
                'skip_download': True, 'quiet': True, 'no_warnings': True}
    if os.path.exists('cookies.txt') and platform in ['Instagram', 'Facebook']:
        ydl_opts['cookiefile'] = 'cookies.txt'
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            if 'en' in subtitles:
                return subtitles['en'][0]['url'], 'manual_captions'
            elif 'en' in automatic_captions:
                return automatic_captions['en'][0]['url'], 'auto_captions'
        return None, None
    except:
        return None, None



def download_captions_text(caption_url):
    try:
        import urllib.request
        with urllib.request.urlopen(caption_url) as response:
            content = response.read().decode('utf-8')
        lines = content.split('\n')
        text_lines = [re.sub(r'<[^>]+>', '', line.strip()) for line in lines
                      if line.strip() and not re.match(r'^(\d+|\d{2}:\d{2}:\d{2})', line.strip())]
        return " ".join(filter(None, text_lines))
    except:
        return None

def extract_activities_with_ai(text, video_title="", video_duration=0, video_metadata=None):
    """Extract structured activity information from video content using AI."""
    try:
        if not text or len(text.strip()) < 10:
            text = f"Video titled '{video_title}' with minimal description"
        duration_context = f"Video duration: {video_duration} seconds" if video_duration else ""

        metadata_context = ""
        if video_metadata:
            tags = video_metadata.get('tags', [])
            categories = video_metadata.get('categories', [])
            if tags:
                metadata_context += f"Tags: {', '.join(tags[:10])}\n"
            if categories:
                metadata_context += f"Categories: {', '.join(categories)}\n"
        prompt = f"""Extract actionable activities from this video content.

Video Title: {video_title}
Description: {text[:4000]}
{duration_context}
{metadata_context}

Extract 1-3 main activities viewers could actually do. Focus on real-world activities.

For each activity provide:
- title: Clear, actionable title
- description: Brief description (max 100 words)
- activity_type: [travel, food, entertainment, sports, education, shopping, outdoor, cultural, business, other]
- location: Specific location or infer from context
- estimated_duration: Realistic time in minutes
- confidence_score: 0.0-1.0

Format as JSON:
{{
  "activities": [
    {{
      "title": "Activity Title",
      "description": "What the person would do",
      "activity_type": "category",
      "location": "Location",
      "estimated_duration": 120,
      "confidence_score": 0.9
    }}
  ],
  "analysis_confidence": "high/medium/low"
}}"""

        full_prompt = "Extract actionable activities from video content. Focus on activities people can actually do.\n\n" + prompt

        response = client.complete(full_prompt)
        result = json.loads(response.text)
        activities = result.get("activities", [])
        for activity in activities:
            activity.setdefault("title", "Unknown Activity")
            activity.setdefault("description", "No description available")
            activity.setdefault("activity_type", "other")
            activity.setdefault("location", "Unknown")
            activity.setdefault("estimated_duration", 60)
            activity.setdefault("confidence_score", 0.5)
        return {
            "activities": activities,
            "analysis_confidence": result.get("analysis_confidence", "medium")
        }
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return {
            "activities": [{
                "title": video_title or "Video Activity",
                "description": text[:200] + "..." if len(text) > 200 else text,
                "activity_type": "other",
                "location": "Unknown",
                "estimated_duration": max(30, video_duration // 60) if video_duration else 60,
                "confidence_score": 0.3
            }],
            "analysis_confidence": "low"
        }


def extract_location_from_metadata(video_info):
    """Extract location information from comprehensive video metadata."""
    location_data = {}

    if 'location' in video_info and video_info['location']:
        location_data['coordinates'] = video_info['location']

    location_fields = ['location', 'filming_location', 'recording_location', 'geo_location']
    for field in location_fields:
        if field in video_info and video_info[field]:
            location_data[field] = video_info[field]

    tags = video_info.get('tags', [])
    if tags:
        location_tags = [tag for tag in tags if any(keyword in tag.lower() for keyword in 
                        ['city', 'country', 'location', 'place', 'travel', 'visit'])]
        if location_tags:
            location_data['location_tags'] = location_tags

    description = video_info.get('description', '')
    if description:

        import re
        location_patterns = [
            r'(?:filmed|shot|recorded|taken)\s+(?:in|at)\s+([A-Z][a-zA-Z\s,]+)',
            r'(?:location|place):\s*([A-Z][a-zA-Z\s,]+)',
            r'@\s*([A-Z][a-zA-Z\s,]+)',
        ]
        for pattern in location_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                location_data['description_locations'] = matches
                break

    if 'uploader_location' in video_info:
        location_data['uploader_location'] = video_info['uploader_location']
    return location_data


async def analyze_video_for_activities(video_url: str, provided_location: str = None):
    """
    Analyze a video URL and extract activity information.
    Args:
        video_url: URL of the video to analyze
        provided_location: Optional location context (ignored, uses metadata)
    Returns:
        Dictionary with video info, activities, and metadata
    """
    platform = detect_platform(video_url)

    video_info = extract_video_info(video_url)
    if not video_info:
        raise Exception(f"Failed to extract video information from {platform}")

    title = video_info.get('title', 'Unknown')
    description = video_info.get('description', '')
    duration = video_info.get('duration', 0)

    location_data = extract_location_from_metadata(video_info)
    detected_location = None
    if location_data:
        if 'coordinates' in location_data:
            detected_location = f"GPS: {location_data['coordinates']}"
        elif 'description_locations' in location_data:
            detected_location = location_data['description_locations'][0]
        elif 'location_tags' in location_data:
            detected_location = location_data['location_tags'][0]
        elif 'uploader_location' in location_data:
            detected_location = location_data['uploader_location']

    activity_analysis = extract_activities_with_ai(
        text=description,
        video_title=title,
        video_duration=duration,
        video_metadata=video_info
    )

    for activity in activity_analysis.get("activities", []):
        if activity.get("location") == "Unknown" and detected_location:
            activity["location"] = detected_location
    return {
        "video_info": {
            "title": title,
            "platform": platform,
            "uploader": video_info.get('uploader', 'Unknown'),
            "duration": duration,
            "description": description,
            "url": video_url,
            "view_count": video_info.get('view_count'),
            "like_count": video_info.get('like_count'),
            "tags": video_info.get('tags', []),
            "detected_location": detected_location
        },
        "activities": activity_analysis.get("activities", []),
        "analysis_metadata": {
            "analysis_confidence": activity_analysis.get("analysis_confidence", "medium")
        }
    }
