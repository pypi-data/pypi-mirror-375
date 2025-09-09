# 05.04.2024

import os
import platform
from typing import Dict, List


# External imports
from rich.console import Console
from rich.prompt import Prompt


# Internal utils
from SpotDown.utils.config_json import config_manager



# Variable
console = Console()
CLEAN_CONSOLE = config_manager.get('DEFAULT', 'clean_console')
SHOW_MESSAGE = config_manager.get('DEFAULT', 'show_message')
AUTO_FIRST = config_manager.get('DOWNLOAD', 'auto_first')


class ConsoleUtils:  
    
    def display_spotify_info(self, spotify_info: Dict):
        """
        Display Spotify information
        
        Args:
            spotify_info (Dict): Spotify track data
        """
        console.print("[bold green]Spotify Track Information: [/bold green]")
        console.print(f"[cyan]Title: [red]{spotify_info['title']}[/red]")
        console.print(f"[cyan]Artist: [red]{spotify_info['artist']}[/red]")
        
        if spotify_info.get('album'):
            console.print(f"[cyan]Album: [red]{spotify_info['album']}[/red]")
        if spotify_info.get('year'):
            console.print(f"[cyan]Year: [red]{spotify_info['year']}[/red]")
        if spotify_info.get('duration_formatted'):
            console.print(f"[cyan]Duration: [red]{spotify_info['duration_formatted']}[/red]")
        if spotify_info.get('label'):
            console.print(f"[cyan]Label: [red]{spotify_info['label']}[/red]")

    def display_youtube_results(self, youtube_results: List[Dict]):
        """
        Display YouTube results
        
        Args:
            youtube_results (List[Dict]): List of YouTube videos
        """
        if not youtube_results:
            console.print("[red]No results found")
            return
            
        for i, video in enumerate(youtube_results, 1):
            console.print(f"[green]{i}. {video['title']}[/green], Channel: [cyan]{video['channel']}[/cyan], Duration: [red]{video['duration_formatted']}[/red], Difference: [yellow]{video.get('duration_difference', 'N/A')}s[/yellow]")

    def show_download_menu(self, results_count: int):
        """
        Show download selection menu
        
        Args:
            results_count (int): Number of available results
        """
        console.print("\n[bold cyan]Download selection: [/bold cyan]")
        console.print("[dim]Options:[/dim]")
        console.print(f"• [green]1-{results_count}[/green]: Download the corresponding video")
        console.print("• [yellow]ENTER[/yellow]: Automatically download the first (most similar)")
        console.print("• [red]0[/red]: Exit without downloading")
    
    def get_download_choice(self, max_results: int) -> int:
        """
        Get user choice for download
        
        Args:
            max_results (int): Maximum number of results
            
        Returns:
            int: User choice (0 = exit, 1-n = video)
        """
        if AUTO_FIRST:
            return 1
        
        while True:
            try:
                choice = Prompt.ask(
                    "\n[bold purple]Which video do you want to download?[/bold purple]",
                    default="1"
                ).strip()
                
                if choice == "0":
                    return 0
                
                # Default: first video
                if choice == "" or choice == "1":
                    return 1
                
                # Check for valid number
                choice_num = int(choice)
                if 1 <= choice_num <= max_results:
                    return choice_num
                else:
                    console.print(f"[red]Invalid choice. Enter a number between 1 and {max_results}[/red]")
                    continue
                    
            except ValueError:
                console.print("[red]Enter a valid number[/red]")
                continue
    
    def show_download_info(self, music_folder, filename: str):
        """
        Show download information
        
        Args:
            music_folder: Destination folder
            filename (str): File name
        """
        console.print(f"[blue]File name: {filename}[/blue]")
        console.print(f"[blue]Destination folder: {music_folder}[/blue]")
    
    def show_download_start(self, video_title: str, video_url: str):
        """
        Show download start
        
        Args:
            video_title (str): Video title
            video_url (str): Video URL
        """
        console.print(f"[yellow]\nDownloading: {video_title}[/yellow]")
        console.print(f"[dim]URL: {video_url}[/dim]")
    
    def show_success(self, message: str):
        """Show success message"""
        console.print(f"[green]{message}[/green]")
    
    def show_error(self, message: str):
        """Show error message"""
        console.print(f"[red]{message}[/red]")
    
    def show_warning(self, message: str):
        """Show warning message"""
        console.print(f"[yellow]{message}[/yellow]")
    
    def show_info(self, message: str):
        """Show informational message"""
        console.print(f"[blue]{message}[/blue]")
    
    def get_spotify_url(self) -> str:
        """
        Get Spotify URL from the user
        
        Returns:
            str: Entered Spotify URL
        """
        while True:
            url = Prompt.ask("\n[purple]Enter Spotify URL[/purple][green]").strip()

            if not url:
                console.print("[red]URL cannot be empty. Please enter a Spotify track URL.[/red]")
                continue

            if "/track/" in url or "/playlist/" in url:
                return url
            
            console.print("[red]Invalid format. Please enter a valid Spotify track URL.[/red]")

    def start_message(self):
        """Display a stylized start message in the console."""
        
        msg = r'''                                                                               
                 _____                                                 _   _ ___     
                |  _  |___ ___ ___ _ _ _ ___ ___    _ _    ___ ___ ___| |_|_|  _|_ _ 
                |     |  _|  _| . | | | | .'|  _|  |_'_|  |_ -| . | . |  _| |  _| | |
                |__|__|_| |_| |___|_____|__,|_|    |_,_|  |___|  _|___|_| |_|_| |_  |
                                                              |_|               |___|
        '''

        if CLEAN_CONSOLE:
            os.system("cls" if platform.system() == 'Windows' else "clear")

        if SHOW_MESSAGE:
            console.print(f"[purple]{msg}")
            separator = "_" * (console.width - 2)
            console.print(f"[cyan]{separator}[/cyan]\n")