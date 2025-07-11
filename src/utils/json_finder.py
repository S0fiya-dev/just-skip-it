import os
from src.utils.json_validator import main as validate_main

def find_json_file(video_path):
    """
    Searches for a JSON file with the same name as the video file
    """
    directory = os.path.dirname(video_path)
    filename_without_ext = os.path.splitext(os.path.basename(video_path))[0]
    json_path = os.path.join(directory, f"{filename_without_ext}.json")
    
    return json_path if os.path.exists(json_path) else None

def check_video_file(video_path):
    """
    Checks for the existence of a JSON file for the specified video file
    """
    # Check if the video file exists
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return
    
    # Search for the JSON file
    json_path = find_json_file(video_path)
    
    if json_path:
        print(f"JSON file found: {json_path}")
        # Pass the JSON file path to the validation function and return the result
        return validate_main(json_path)
    else:
        print("File with json extension not found")
        return False