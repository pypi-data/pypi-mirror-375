from .youtube_transcript import YouTubeTranscriptApi
from .transcript_list import TranscriptList
from .fetched_transcript import FetchedTranscript
from .ai_translator import AITranscriptTranslator
from .utils import extract_video_id, extract_video_ids, normalize_url_or_id
from .exceptions import (
    TranscriptRetrievalError,
    VideoUnavailable,
    TranscriptNotFound,
    TranscriptDisabled,
    NoTranscriptFound,
    NotTranslatable,
    TranslationLanguageNotAvailable,
    CookiePathInvalid,
    CookiesInvalid,
    FailedToCreateConsentCookie,
    NoTranscriptAvailable,
    TooManyRequests
)
from .formatters import (
    Formatter,
    PrettyPrintFormatter,
    JSONFormatter,
    TextFormatter,
    SRTFormatter,
    VTTFormatter
)

__version__ = "1.1.0"
__author__ = "U-Transkript Team"
__email__ = "contact@u-transkript.com"
__description__ = "YouTube videolarını otomatik olarak çıkarıp AI ile çeviren güçlü Python kütüphanesi"
__url__ = "https://github.com/U-C4N/u-transkript"

# Ana sınıf ve fonksiyonları dışa aktar
__all__ = [
    # Ana AI çeviri sınıfı
    'AITranscriptTranslator',
    
    # YouTube transcript API sınıfları
    'YouTubeTranscriptApi',
    'TranscriptList',
    'FetchedTranscript',
    
    # Utility functions (NEW in v1.1.0)
    'extract_video_id',
    'extract_video_ids', 
    'normalize_url_or_id',
    
    # Hata sınıfları
    'TranscriptRetrievalError',
    'VideoUnavailable',
    'TranscriptNotFound',
    'TranscriptDisabled',
    'NoTranscriptFound',
    'NotTranslatable',
    'TranslationLanguageNotAvailable',
    'CookiePathInvalid',
    'CookiesInvalid',
    'FailedToCreateConsentCookie',
    'NoTranscriptAvailable',
    'TooManyRequests',
    
    # Formatter sınıfları
    'Formatter',
    'PrettyPrintFormatter',
    'JSONFormatter',
    'TextFormatter',
    'SRTFormatter',
    'VTTFormatter'
]

# Paket bilgileri
__package_info__ = {
    "name": "u-transkript",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "email": __email__,
    "url": __url__,
    "license": "MIT",
    "python_requires": ">=3.7",
    "keywords": [
        "youtube", "transcript", "translation", "ai", "gemini",
        "subtitle", "video", "nlp", "machine-learning", "automation"
    ]
}

def get_version():
    """Paket versiyonunu döndür."""
    return __version__

def get_info():
    """Paket bilgilerini döndür."""
    return __package_info__

# Hızlı başlangıç fonksiyonu
def quick_translate(video_url_or_id: str, api_key: str, target_language: str = "Turkish", output_type: str = "txt"):
    """
    Hızlı çeviri fonksiyonu - v1.1.0'da URL desteği eklendi.
    
    Args:
        video_url_or_id: YouTube video URL veya ID
        api_key: Google Gemini API anahtarı
        target_language: Hedef dil (varsayılan: "Turkish")
        output_type: Çıktı formatı (varsayılan: "txt")
    
    Returns:
        Çevrilmiş transcript
    
    Example:
        # URL ile kullanım (YENİ!)
        result = quick_translate("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "YOUR_API_KEY")
        
        # Video ID ile kullanım (eskisi gibi)
        result = quick_translate("dQw4w9WgXcQ", "YOUR_API_KEY", "Turkish")
    """
    translator = AITranscriptTranslator(api_key)
    return translator.set_lang(target_language).set_type(output_type).translate_transcript(video_url_or_id)

