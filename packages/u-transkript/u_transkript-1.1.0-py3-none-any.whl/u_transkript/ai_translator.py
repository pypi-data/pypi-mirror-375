import json
import requests
from typing import List, Dict, Optional, Union, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from .youtube_transcript import YouTubeTranscriptApi
from .formatters import get_formatter, JSONFormatter, TextFormatter
from .utils import extract_video_id, extract_video_ids, normalize_url_or_id


class AITranscriptTranslator:
    """
    AI-powered transcript translator using Google Gemini API.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the AI translator.
        
        Args:
            api_key: Google Gemini API key
            model: Gemini model to use (default: gemini-2.0-flash-exp)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
    def set_model(self, model_name: str) -> 'AITranscriptTranslator':
        """
        Set the Gemini model to use.
        
        Args:
            model_name: Name of the Gemini model
            
        Returns:
            Self for method chaining
        """
        self.model = model_name
        return self
        
    def set_api(self, api_key: str) -> 'AITranscriptTranslator':
        """
        Set the API key.
        
        Args:
            api_key: Google Gemini API key
            
        Returns:
            Self for method chaining
        """
        self.api_key = api_key
        return self
        
    def set_lang(self, target_language: str) -> 'AITranscriptTranslator':
        """
        Set the target language for translation.
        
        Args:
            target_language: Target language (e.g., 'Turkish', 'English', 'Spanish')
            
        Returns:
            Self for method chaining
        """
        self.target_language = target_language
        return self
        
    def set_type(self, output_type: str) -> 'AITranscriptTranslator':
        """
        Set the output format type.
        
        Args:
            output_type: Output format ('txt', 'json', 'xml')
            
        Returns:
            Self for method chaining
        """
        self.output_type = output_type.lower()
        return self
        
    def translate_transcript(
        self, 
        video_url_or_id: str, 
        target_language: Optional[str] = None,
        output_type: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Extract and translate YouTube transcript using AI.
        
        Args:
            video_url_or_id: YouTube video URL or video ID
            target_language: Target language for translation
            output_type: Output format ('txt', 'json', 'xml')
            custom_prompt: Custom prompt for AI translation
            
        Returns:
            Translated transcript in specified format
        """
        # Extract video ID from URL or use as-is if already an ID
        video_id = extract_video_id(video_url_or_id)
        
        # Use instance variables if parameters not provided
        target_lang = target_language or getattr(self, 'target_language', 'English')
        output_fmt = output_type or getattr(self, 'output_type', 'txt')
        
        # Extract transcript
        try:
            raw_transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Gelen verinin liste olup olmadığını ve sözlük içerip içermediğini kontrol et
            if not isinstance(raw_transcript_data, list) or \
               not all(isinstance(item, dict) and 'text' in item for item in raw_transcript_data):
                error_message = f"Unexpected transcript data format. Expected List[Dict[str, any]], got: {type(raw_transcript_data)}"
                if isinstance(raw_transcript_data, list) and raw_transcript_data:
                    error_message += f" First item type: {type(raw_transcript_data[0])}"
                raise Exception(error_message)
            transcript = raw_transcript_data
        except Exception as e:
            # Hata mesajına video_id'yi ekleyerek daha anlaşılır hale getirelim
            raise Exception(f"Failed to extract or validate transcript for video_id '{video_id}' (from: {video_url_or_id}): {str(e)}")
            
        # Store current video ID for output formatting
        self._current_video_id = video_id
            
        # Combine transcript text
        full_text = " ".join([entry['text'] for entry in transcript])
        
        # Translate using Gemini AI
        translated_text = self._translate_with_gemini(
            full_text, 
            target_lang, 
            custom_prompt
        )
        
        # Format output
        return self._format_output(translated_text, transcript, output_fmt)
        
    def _translate_with_gemini(
        self, 
        text: str, 
        target_language: str,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Translate text using Google Gemini API.
        
        Args:
            text: Text to translate
            target_language: Target language
            custom_prompt: Custom prompt for translation
            
        Returns:
            Translated text
        """
        if custom_prompt:
            prompt = custom_prompt.format(text=text, language=target_language)
        else:
            prompt = f"""
            Please translate the following text to {target_language}. 
            Maintain the natural flow and context of the content.
            Only return the translated text without any additional comments or explanations.
            
            Text to translate:
            {text}
            """
        
        url = f"{self.base_url}/{self.model}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        params = {
            'key': self.api_key
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                if 'content' in result['candidates'][0]:
                    if 'parts' in result['candidates'][0]['content']:
                        return result['candidates'][0]['content']['parts'][0]['text'].strip()
            
            raise Exception("Invalid response format from Gemini API")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
            
    def _format_output(
        self, 
        translated_text: str, 
        original_transcript: List[Dict],
        output_type: str
    ) -> str:
        """
        Format the translated text according to specified output type.
        
        Args:
            translated_text: Translated text
            original_transcript: Original transcript with timestamps
            output_type: Output format type
            
        Returns:
            Formatted output
        """
        if output_type == 'txt':
            return translated_text
            
        elif output_type == 'json':
            # Create a structured JSON with translation
            result = {
                "video_id": getattr(self, '_current_video_id', 'unknown'),
                "target_language": getattr(self, 'target_language', 'unknown'),
                "original_transcript": original_transcript,
                "translated_text": translated_text,
                "translation_metadata": {
                    "model": self.model,
                    "timestamp": self._get_current_timestamp()
                }
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        elif output_type == 'xml':
            # Create XML format
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<transcript>
    <metadata>
        <video_id>{getattr(self, '_current_video_id', 'unknown')}</video_id>
        <target_language>{getattr(self, 'target_language', 'unknown')}</target_language>
        <model>{self.model}</model>
        <timestamp>{self._get_current_timestamp()}</timestamp>
    </metadata>
    <original_transcript>
"""
            for entry in original_transcript:
                xml_content += f"""        <entry start="{entry['start']}" duration="{entry['duration']}">
            <text>{self._escape_xml(entry['text'])}</text>
        </entry>
"""
            xml_content += """    </original_transcript>
    <translated_text>
        <![CDATA[{translated_text}]]>
    </translated_text>
</transcript>""".format(translated_text=translated_text)
            
            return xml_content
            
        else:
            raise ValueError(f"Unsupported output type: {output_type}")
            
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))

    def batch_translate(
        self,
        video_urls_or_ids: List[str],
        target_language: Optional[str] = None,
        output_type: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        skip_errors: bool = True,
        save_intermediate: bool = False,
        output_dir: str = "./translations"
    ) -> Dict[str, Union[str, Exception]]:
        """
        Batch translate multiple YouTube videos sequentially.
        
        Args:
            video_urls_or_ids: List of YouTube URLs or video IDs
            target_language: Target language for translation
            output_type: Output format ('txt', 'json', 'xml')
            custom_prompt: Custom prompt for AI translation
            progress_callback: Callback function (completed, total, current_video)
            skip_errors: Continue processing if a video fails
            save_intermediate: Save each translation to a separate file
            output_dir: Directory to save intermediate files
            
        Returns:
            Dictionary mapping video IDs to results (translated text or Exception)
        """
        import os
        
        # Normalize URLs to IDs
        try:
            video_ids = extract_video_ids(video_urls_or_ids)
        except ValueError as e:
            if not skip_errors:
                raise e
            # Extract as many as possible
            video_ids = []
            for url_or_id in video_urls_or_ids:
                try:
                    video_ids.append(extract_video_id(url_or_id))
                except:
                    if progress_callback:
                        progress_callback(len(video_ids), len(video_urls_or_ids), f"INVALID: {url_or_id}")
        
        results = {}
        total = len(video_ids)
        
        # Create output directory if saving intermediate files
        if save_intermediate:
            os.makedirs(output_dir, exist_ok=True)
        
        for i, video_id in enumerate(video_ids):
            try:
                # Progress callback
                if progress_callback:
                    progress_callback(i, total, video_id)
                
                # Translate
                result = self.translate_transcript(
                    video_id,
                    target_language=target_language,
                    output_type=output_type,
                    custom_prompt=custom_prompt
                )
                
                results[video_id] = result
                
                # Save intermediate file
                if save_intermediate:
                    ext = output_type or getattr(self, 'output_type', 'txt')
                    filename = f"{video_id}.{ext}"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(result)
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                results[video_id] = e
                if not skip_errors:
                    break
        
        # Final progress callback
        if progress_callback:
            progress_callback(total, total, "COMPLETED")
        
        return results
    
    def batch_translate_concurrent(
        self,
        video_urls_or_ids: List[str],
        target_language: Optional[str] = None,
        output_type: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        max_workers: int = 3,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        skip_errors: bool = True,
        save_intermediate: bool = False,
        output_dir: str = "./translations"
    ) -> Dict[str, Union[str, Exception]]:
        """
        Batch translate multiple YouTube videos concurrently.
        
        Args:
            video_urls_or_ids: List of YouTube URLs or video IDs
            target_language: Target language for translation
            output_type: Output format ('txt', 'json', 'xml')
            custom_prompt: Custom prompt for AI translation
            max_workers: Maximum number of concurrent workers
            progress_callback: Callback function (completed, total, current_video)
            skip_errors: Continue processing if a video fails
            save_intermediate: Save each translation to a separate file
            output_dir: Directory to save intermediate files
            
        Returns:
            Dictionary mapping video IDs to results (translated text or Exception)
        """
        import os
        
        # Normalize URLs to IDs
        try:
            video_ids = extract_video_ids(video_urls_or_ids)
        except ValueError as e:
            if not skip_errors:
                raise e
            video_ids = []
            for url_or_id in video_urls_or_ids:
                try:
                    video_ids.append(extract_video_id(url_or_id))
                except:
                    pass
        
        results = {}
        total = len(video_ids)
        completed = 0
        
        # Create output directory if saving intermediate files
        if save_intermediate:
            os.makedirs(output_dir, exist_ok=True)
        
        def translate_single(video_id: str) -> tuple:
            """Helper function for concurrent translation."""
            try:
                result = self.translate_transcript(
                    video_id,
                    target_language=target_language,
                    output_type=output_type,
                    custom_prompt=custom_prompt
                )
                return video_id, result, None
            except Exception as e:
                return video_id, None, e
        
        # Execute concurrent translations
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_video = {
                executor.submit(translate_single, video_id): video_id 
                for video_id in video_ids
            }
            
            # Process completed tasks
            for future in as_completed(future_to_video):
                video_id, result, error = future.result()
                completed += 1
                
                if error:
                    results[video_id] = error
                    if not skip_errors:
                        # Cancel remaining tasks
                        for f in future_to_video:
                            f.cancel()
                        break
                else:
                    results[video_id] = result
                    
                    # Save intermediate file
                    if save_intermediate:
                        ext = output_type or getattr(self, 'output_type', 'txt')
                        filename = f"{video_id}.{ext}"
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(result)
                
                # Progress callback
                if progress_callback:
                    status = "ERROR" if error else "SUCCESS"
                    progress_callback(completed, total, f"{video_id} ({status})")
        
        return results

 