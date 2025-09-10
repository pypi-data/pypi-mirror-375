"""
Utility functions for U-Transkript.
"""
import re
from typing import List, Union
from urllib.parse import urlparse, parse_qs


def extract_video_id(url_or_id: str) -> str:
    """
    Extract video ID from various YouTube URL formats or return ID if already extracted.
    
    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/embed/VIDEO_ID
    - https://youtube.com/v/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - VIDEO_ID (direct)
    
    Args:
        url_or_id: YouTube URL or video ID
        
    Returns:
        Video ID (11 characters)
        
    Raises:
        ValueError: If video ID cannot be extracted
    """
    # Strip whitespace
    url_or_id = url_or_id.strip()
    
    # If it's already a video ID (11 characters, alphanumeric + _ -)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # YouTube URL patterns
    patterns = [
        # Standard watch URLs
        r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:www\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
        
        # Short URLs
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        
        # Embed URLs
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'(?:www\.youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        
        # Old format
        r'(?:youtube\.com/v/)([a-zA-Z0-9_-]{11})',
        r'(?:www\.youtube\.com/v/)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    # Try parsing as URL and extract from query parameters
    try:
        parsed = urlparse(url_or_id)
        if 'youtube.com' in parsed.netloc:
            query_params = parse_qs(parsed.query)
            if 'v' in query_params:
                video_id = query_params['v'][0]
                if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    return video_id
    except:
        pass
    
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def extract_video_ids(urls_or_ids: List[str]) -> List[str]:
    """
    Extract video IDs from a list of URLs or IDs.
    
    Args:
        urls_or_ids: List of YouTube URLs or video IDs
        
    Returns:
        List of video IDs
        
    Raises:
        ValueError: If any URL/ID is invalid
    """
    video_ids = []
    errors = []
    
    for i, url_or_id in enumerate(urls_or_ids):
        try:
            video_id = extract_video_id(url_or_id)
            video_ids.append(video_id)
        except ValueError as e:
            errors.append(f"Item {i+1}: {e}")
    
    if errors:
        raise ValueError(f"Failed to extract video IDs:\n" + "\n".join(errors))
    
    return video_ids


def validate_video_id(video_id: str) -> bool:
    """
    Validate if a string is a valid YouTube video ID.
    
    Args:
        video_id: String to validate
        
    Returns:
        True if valid video ID format
    """
    return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))


def is_youtube_url(url: str) -> bool:
    """
    Check if a URL is a YouTube URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if it's a YouTube URL
    """
    try:
        parsed = urlparse(url.strip())
        return any(domain in parsed.netloc.lower() for domain in 
                  ['youtube.com', 'youtu.be', 'm.youtube.com', 'www.youtube.com'])
    except:
        return False


def normalize_url_or_id(url_or_id: Union[str, List[str]]) -> Union[str, List[str]]:
    """
    Normalize URL(s) or ID(s) to video ID(s).
    
    Args:
        url_or_id: Single URL/ID or list of URLs/IDs
        
    Returns:
        Single video ID or list of video IDs
    """
    if isinstance(url_or_id, str):
        return extract_video_id(url_or_id)
    elif isinstance(url_or_id, list):
        return extract_video_ids(url_or_id)
    else:
        raise TypeError("Input must be string or list of strings")