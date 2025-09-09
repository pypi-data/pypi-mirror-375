# 05.04.2024

import re
import json
import difflib
import logging
from urllib.parse import quote_plus
from typing import Dict, List, Optional


# External imports
import httpx
from rich.console import Console


# Internal utils
from SpotDown.utils.headers import get_userAgent
from SpotDown.helpers.string import contains_emoji
from SpotDown.utils.config_json import config_manager


# Variable
console = Console()
search_limit = config_manager.get_int("SEARCH", "limit")
exclude_emoji = config_manager.get_bool("SEARCH", "exclude_emoji")



class YouTubeExtractor:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def search_videos(self, query: str) -> List[Dict]:
        """
        Search for videos on YouTube
        
        Args:
            query (str): Search query
            
        Returns:
            List[Dict]: List of found videos
        """
        try:
            logging.info(f"Starting YouTube search for query: {query}")
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            console.print(f"\n[bold blue]Searching on YouTube:[/bold blue] {query}")

            with httpx.Client(timeout=10) as client:
                response = client.get(search_url, headers={"User-Agent": get_userAgent()})
                html = response.text

            results = self._extract_youtube_videos(html, search_limit)
            logging.info(f"Found {len(results)} results for query: {query}")
            return results

        except Exception as e:
            logging.error(f"YouTube search error: {e}")
            print(f"YouTube search error: {e}")
            return []

    def sort_by_duration_similarity(self, youtube_results: List[Dict], target_duration: int):
        """
        Sort results by duration closest to the target
        
        Args:
            youtube_results (List[Dict]): List of YouTube videos
            target_duration (int): Target duration in seconds
        """
        logging.info(f"Sorting {len(youtube_results)} results by duration similarity to {target_duration}s")
        for result in youtube_results:
            if result.get('duration_seconds') is not None:
                result['duration_difference'] = abs(result['duration_seconds'] - target_duration)

            else:
                result['duration_difference'] = float('inf')
        
        youtube_results.sort(key=lambda x: x['duration_difference'])

    def sort_by_affinity_and_duration(self, youtube_results: List[Dict], spotify_info: Dict):
        """
        Sort results by artist match priority, then duration, then title affinity.
        Prioritizes exact artist matches in channel name over duration similarity.
        """
        logging.info(f"Sorting {len(youtube_results)} results by artist affinity and duration")
        target_duration = spotify_info.get('duration_seconds')
        target_title = spotify_info.get('title', '').lower()

        # Split artists and clean them
        target_artists = [a.strip().lower() for a in spotify_info.get('artist', '').split(',')]
        logging.info(f"Target artists: {target_artists}")

        for result in youtube_results:
            # Duration difference
            if result.get('duration_seconds') is not None and target_duration is not None:
                result['duration_difference'] = abs(result['duration_seconds'] - target_duration)
            else:
                result['duration_difference'] = float('inf')

            yt_title = result.get('title', '').lower()
            yt_channel = result.get('channel', '').lower()

            # Title matching
            result['exact_title_match'] = yt_title == target_title
            result['title_affinity'] = difflib.SequenceMatcher(None, yt_title, target_title).ratio()

            # Artist/Channel matching - check each artist
            channel_exact_matches = []
            channel_affinities = []
            for artist in target_artists:

                # Exact match
                exact_match = yt_channel == artist
                channel_exact_matches.append(exact_match)

                # Check if artist is contained in channel
                contains_artist = artist in yt_channel
                channel_exact_matches.append(contains_artist)

                # Similarity ratio
                similarity = difflib.SequenceMatcher(None, yt_channel, artist).ratio()
                channel_affinities.append(similarity)

            # Best matches
            result['exact_channel_match'] = any(channel_exact_matches)
            result['channel_affinity'] = max(channel_affinities) if channel_affinities else 0.0

        # Sorting: 
        # 1. Exact channel match first (most important)
        # 2. Then duration difference
        # 3. Then channel affinity
        # 4. Then title matching
        youtube_results.sort(
            key=lambda x: (
                not x['exact_channel_match'],        # False first (exact matches)
                x['duration_difference'],            # Lower difference first  
                -x['channel_affinity'],              # Higher affinity first
                not x['exact_title_match'],          # False first (exact titles)
                -x['title_affinity']                 # Higher title affinity first
            )
        )

    def _extract_youtube_videos(self, html: str, limit: int) -> List[Dict]:
        """Extract videos from YouTube HTML"""
        try:
            yt_match = re.search(r'var ytInitialData = ({.+?});', html, re.DOTALL)

            if not yt_match:
                logging.warning("ytInitialData not found in HTML")
                return []

            yt_data = json.loads(yt_match.group(1))
            results = []

            # Navigate the data structure
            contents = (yt_data.get('contents', {})
                       .get('twoColumnSearchResultsRenderer', {})
                       .get('primaryContents', {})
                       .get('sectionListRenderer', {})
                       .get('contents', []))

            for section in contents:
                items = section.get('itemSectionRenderer', {}).get('contents', [])

                for item in items:
                    if 'videoRenderer' in item:
                        video_info = self._parse_video_renderer(item['videoRenderer'])

                        # Exclude results with emoji in title or channel
                        if video_info:
                            if exclude_emoji:
                                title = video_info.get('title', '')
                                channel = video_info.get('channel', '')
                                if contains_emoji(title) or contains_emoji(channel):
                                    continue

                            results.append(video_info)
                            
                        if len(results) >= search_limit:
                            break
                
                if len(results) >= search_limit:
                    break

            logging.info(f"Extracted {len(results)} video(s) from HTML")
            return results

        except Exception as e:
            logging.error(f"Video extraction error: {e}")
            print(f"Video extraction error: {e}")
            return []

    def _parse_video_renderer(self, video_data: Dict) -> Optional[Dict]:
        """Complete parsing of a video renderer"""
        try:
            video_id = video_data.get('videoId')
            if not video_id:
                logging.warning("videoId not found in video_data")
                return None

            # Title
            title = self._extract_text(video_data.get('title', {}))
            if not title:
                return None

            # Channel
            channel = self._extract_text(video_data.get('ownerText', {}))
            
            # Duration
            duration_seconds = self._extract_video_duration(video_data)
            duration_formatted = self._format_seconds(duration_seconds) if duration_seconds else None
            
            # Views
            views = self._extract_text(video_data.get('viewCountText', {}))
            
            # Thumbnail
            thumbnails = video_data.get('thumbnail', {}).get('thumbnails', [])
            thumbnail = thumbnails[-1].get('url') if thumbnails else None
            
            # Published date
            published = self._extract_text(video_data.get('publishedTimeText', {}))

            logging.info(f"Parsed video: {title} (ID: {video_id})")
            return {
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'title': title,
                'channel': channel or 'Unknown channel',
                'duration_seconds': duration_seconds,
                'duration_formatted': duration_formatted or 'N/A',
                'views': views or 'N/A',
                'published': published or 'N/A',
                'thumbnail': thumbnail
            }

        except Exception as e:
            logging.error(f"Video parsing error: {e}")
            print(f"Video parsing error: {e}")
            return None

    def _extract_text(self, text_obj: Dict) -> str:
        """Extract text from YouTube objects"""
        if isinstance(text_obj, str):
            return text_obj
        
        if isinstance(text_obj, dict):
            if 'runs' in text_obj and text_obj['runs']:
                return ''.join(run.get('text', '') for run in text_obj['runs'])
            
            return text_obj.get('simpleText', '')
        
        return ''

    def _extract_video_duration(self, video_data: Dict) -> Optional[int]:
        """Extract video duration in seconds"""

        # First attempt: direct lengthText
        length_text = video_data.get('lengthText', {})
        duration_str = self._extract_text(length_text)
        
        if duration_str:
            return self._parse_duration_string(duration_str)
        
        # Second attempt: search in thumbnailOverlays
        overlays = video_data.get('thumbnailOverlays', [])
        for overlay in overlays:
            if 'thumbnailOverlayTimeStatusRenderer' in overlay:
                time_status = overlay['thumbnailOverlayTimeStatusRenderer']
                duration_text = self._extract_text(time_status.get('text', {}))

                if duration_text:
                    return self._parse_duration_string(duration_text)
        
        return None

    def _parse_duration_string(self, duration_str: str) -> Optional[int]:
        """Convert duration string (e.g., '3:45') to seconds"""
        try:
            duration_str = re.sub(r'[^\d:]', '', duration_str)
            parts = duration_str.split(':')
            
            if len(parts) == 2:
                minutes, seconds = int(parts[0]), int(parts[1])
                return minutes * 60 + seconds
            
            elif len(parts) == 3:
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            
        except (ValueError, IndexError):
            pass
        
        return None

    def _format_seconds(self, seconds: int) -> str:
        """Format seconds into mm:ss or hh:mm:ss"""
        if seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}:{secs:02d}"
        
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"