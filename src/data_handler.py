"""
Data Handler Module
Handles loading exercise data from local files or web sources.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import requests
import streamlit as st


def load_data_from_file(file_path: str) -> Dict[str, Any]:
    """
    Load exercise data from a local JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing exercises and configuration
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_data_from_url(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Load exercise data from a web URL (JSON format).
    
    Args:
        url: URL to fetch the JSON data from
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing exercises and configuration, or None if failed
    """
    try:
        response = requests.get(url, timeout=timeout, verify=True)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error loading data from URL: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"Timeout error loading data from URL: {e}")
        return None
    except requests.RequestException as e:
        print(f"Error loading data from URL: {e}")
        return None


def load_exercises_data(source: Optional[str] = None) -> Dict[str, Any]:
    """
    Load exercise data from file or web source.
    Falls back to local file if web source fails.
    
    Args:
        source: Either a file path or URL. If None, uses default local file.
        
    Returns:
        Dictionary containing exercises and configuration
    """
    # Default local file path
    default_file = Path(__file__).parent.parent / "data" / "exercises.json"
    
    # If source is provided
    if source:
        # Check if it's a URL
        if source.startswith("http://") or source.startswith("https://"):
            data = load_data_from_url(source)
            if data:
                return data
            # Fallback to local file if URL fails
            st.warning(f"Failed to load from URL. Using local file instead.")
        
        # Assume it's a file path
        elif os.path.exists(source):
            return load_data_from_file(source)
        else:
            st.warning(f"File not found: {source}. Using default file instead.")
    
    # Load from default local file
    if default_file.exists():
        return load_data_from_file(str(default_file))
    else:
        raise FileNotFoundError(
            f"Default exercise data file not found at {default_file}. "
            "Please ensure the data/exercises.json file exists."
        )


def get_exercises_dict(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Extract exercises dictionary from loaded data.
    
    Args:
        data: Loaded data dictionary
        
    Returns:
        Dictionary of exercises
    """
    return data.get("exercises", {})


def get_goal_set_rep(data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    Extract goal set/rep configuration from loaded data.
    
    Args:
        data: Loaded data dictionary
        
    Returns:
        Dictionary mapping goals to level-based set/rep schemes
    """
    return data.get("goal_set_rep", {})


def get_equipment_options(data: Dict[str, Any]) -> list:
    """
    Extract equipment options from loaded data.
    
    Args:
        data: Loaded data dictionary
        
    Returns:
        List of equipment option dictionaries
    """
    return data.get("equipment_options", [])

