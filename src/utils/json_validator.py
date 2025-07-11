import json
import re
from typing import Dict, Any, List

class VideoConfigValidator:
    def __init__(self):
        self.required_structure = {
            "version": str,
            "video_info": {
                "filename": str,
                "duration": str
            },
            "time_segments": [
                {
                    "id": int,
                    "name": str,
                    "trigger_time": str,
                    "jump_to_time": str,
                    "enabled": bool
                }
            ],
            "settings": {
                "loop_segments": bool,
                "show_notifications": bool
            }
        }
    
    def validate_time_format(self, time_str: str) -> bool:
        """Checks the time format HH:MM:SS"""        
        pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$'
        return bool(re.match(pattern, time_str))
    
    def validate_structure(self, data: Dict[Any, Any], structure: Dict[Any, Any], path: str = "") -> List[str]:
        """Recursively validates data structure"""
        errors = []
        
        # Check that all required keys are present
        for key, expected_type in structure.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in data:
                errors.append(f"Missing required key: {current_path}")
                continue
            
            value = data[key]
            
            # Check that the value is not empty
            if value is None or (isinstance(value, str) and value.strip() == ""):
                errors.append(f"Empty value for key: {current_path}")
                continue
            
            # Check data type
            if isinstance(expected_type, dict):
                if not isinstance(value, dict):
                    errors.append(f"Invalid type for {current_path}. Expected object, got {type(value).__name__}")
                else:
                    errors.extend(self.validate_structure(value, expected_type, current_path))
            
            elif isinstance(expected_type, list) and len(expected_type) == 1:
                if not isinstance(value, list):
                    errors.append(f"Invalid type for {current_path}. Expected array, got {type(value).__name__}")
                elif len(value) == 0:
                    errors.append(f"Empty array for {current_path}")
                else:
                    for i, item in enumerate(value):
                        item_path = f"{current_path}[{i}]"
                        if not isinstance(item, dict):
                            errors.append(f"Invalid array element type {item_path}. Expected object")
                        else:
                            errors.extend(self.validate_structure(item, expected_type[0], item_path))
            
            else:
                if not isinstance(value, expected_type):
                    errors.append(f"Invalid type for {current_path}. Expected {expected_type.__name__}, got {type(value).__name__}")
        
        # Check that there are no extra keys
        for key in data:
            if key not in structure:
                current_path = f"{path}.{key}" if path else key
                errors.append(f"Unexpected key: {current_path}")
        
        return errors
    
    def validate_business_rules(self, data: Dict[Any, Any]) -> List[str]:
        """Validates business logic"""
        errors = []
        
        # Check time format in video_info
        if "video_info" in data and "duration" in data["video_info"]:
            if not self.validate_time_format(data["video_info"]["duration"]):
                errors.append("Invalid time format for video_info.duration (expected HH:MM:SS)")
        
        # Check time format in segments
        if "time_segments" in data:
            for i, segment in enumerate(data["time_segments"]):
                if "trigger_time" in segment:
                    if not self.validate_time_format(segment["trigger_time"]):
                        errors.append(f"Invalid time format for time_segments[{i}].trigger_time")
                
                if "jump_to_time" in segment:
                    if not self.validate_time_format(segment["jump_to_time"]):
                        errors.append(f"Invalid time format for time_segments[{i}].jump_to_time")
                
                # Check ID uniqueness
                if "id" in segment:
                    segment_ids = [s.get("id") for s in data["time_segments"] if "id" in s]
                    if segment_ids.count(segment["id"]) > 1:
                        errors.append(f"Duplicate segment ID: {segment['id']}")
        
        # Check file extension
        if "video_info" in data and "filename" in data["video_info"]:
            filename = data["video_info"]["filename"]
            valid_extensions = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"]
            if not any(filename.lower().endswith(ext) for ext in valid_extensions):
                errors.append(f"Unsupported file extension: {filename}")
        
        return errors
    
    def validate_json_file(self, file_path: str) -> Dict[str, Any]:
        """Main JSON file validation function"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        
        except FileNotFoundError:
            result["errors"].append(f"File not found: {file_path}")
            return result
        
        except json.JSONDecodeError as e:
            result["errors"].append(f"JSON parsing error: {e}")
            return result
        
        except Exception as e:
            result["errors"].append(f"File reading error: {e}")
            return result
        
        # Validate structure
        structure_errors = self.validate_structure(data, self.required_structure)
        result["errors"].extend(structure_errors)
        
        # Validate business rules (only if structure is correct)
        if not structure_errors:
            business_errors = self.validate_business_rules(data)
            result["errors"].extend(business_errors)
        
        # Determine validity
        result["valid"] = len(result["errors"]) == 0
        
        return result

def main(file_path):
    validator = VideoConfigValidator()
    
    result = validator.validate_json_file(file_path)
    
    print(f"File validation: {file_path}")
    print(f"Result: {'✅ VALID' if result['valid'] else '❌ NOT VALID'}")
    
    if result["errors"]:
        print("\nErrors:")
        for error in result["errors"]:
            print(f"  • {error}")
    
    if result["warnings"]:
        print("\nWarnings:")
        for warning in result["warnings"]:
            print(f"  • {warning}")
    
    if result["valid"]:
        print("\n✅ JSON file is correct and ready to use!")

    return result["valid"]  # Return boolean value