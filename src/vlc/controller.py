import json
import socket
import time
from src.vlc.launcher import load_config, test_rc_connection

class VLCSkipController:
    def __init__(self, json_file_path, config_data=None):
        self.json_file_path = json_file_path
        
        # Load configuration
        if config_data is None:
            config_data = load_config()
            if config_data is None:
                raise Exception("Failed to load configuration")
        
        self.vlc_host = config_data['rc_host']
        self.vlc_port = config_data['rc_port']
        self.rc_password = config_data.get('rc_password', '')
        self.check_interval = config_data['check_interval']
        self.timeout_seconds = config_data['timeout_seconds']
        
        self.running = False
        self.segments = []
        self.load_segments_config()
        self.last_time = None
        
        self.is_seeking = False
        self.seek_target_time = -1
        
    def load_segments_config(self):
        """Loads segment configuration from JSON file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.segments = [seg for seg in config['time_segments'] if seg['enabled']]
                print(f"Loaded {len(self.segments)} active segments")
        except Exception as e:
            print(f"Error loading segment configuration: {e}")
    
    def time_to_seconds(self, time_str):
        """Converts time in HH:MM:SS format to seconds"""
        parts = time_str.split(':')
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    
    def send_vlc_command(self, command):
        """Sends command to VLC through RC interface"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            sock.connect((self.vlc_host, self.vlc_port))
            
            # If password is specified, send it first
            if self.rc_password:
                sock.send(f"{self.rc_password}\n".encode())
                # Get response after password input
                sock.recv(1024)
            
            sock.send(f"{command}\n".encode())
            response = sock.recv(1024).decode().strip()
            sock.close()
            return response
        except Exception as e:
            print(f"Error connecting to VLC: {e}")
            return None
    
    def get_current_time(self):
        """Gets current playback time in seconds"""
        response = self.send_vlc_command("get_time")
        if response and response.isdigit():
            return int(response)
        return None
    
    def seek_to_time(self, seconds):
        """Seeks video to specified time in seconds and sets seeking flag"""
        self.is_seeking = True
        self.seek_target_time = seconds
        self.send_vlc_command(f"seek {seconds}")
        print(f"Seeking to {seconds} seconds, waiting for completion...")
    
    def check_vlc_pause(self):
        """Simple function to check if VLC is paused"""
        try:
            # Connect to VLC
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.vlc_host, self.vlc_port))

            # If password is specified, send it first
            if self.rc_password:
                sock.send(f"{self.rc_password}\n".encode())
                # Get response after password input
                sock.recv(1024)
            
            # Get current time
            sock.send(b"get_time\n")
            response = sock.recv(1024).decode().strip()
            sock.close()
        
            if response.isdigit():
                current_time = int(response)
            
                if hasattr(self, 'last_time') and self.last_time is not None:
                    if current_time == self.last_time:
                        return True  # Video is paused
            
                self.last_time = current_time
                return False  # Video is playing
            
        except Exception as e:
            print(f"Error checking pause status: {e}")
            return False
    
    def check_segments(self):
        """Checks if video needs to be skipped"""
        # Check if video is paused
        if self.check_vlc_pause():
            return  # If paused, don't skip
        current_time = self.get_current_time()
        if current_time is None:
            return

        if self.is_seeking:
            if current_time >= (self.seek_target_time + 2):
                print(f"Seek to {self.seek_target_time}s complete. Resuming monitoring.")
                self.is_seeking = False
                self.seek_target_time = -1
            return

        for segment in self.segments:
            trigger_seconds = self.time_to_seconds(segment['trigger_time'])
            jump_seconds = self.time_to_seconds(segment['jump_to_time'])
    
            # Check if we are in the range between trigger_time and jump_to_time
            if trigger_seconds <= current_time < jump_seconds:
                print(f"Segment activated: {segment['name']}")
                self.seek_to_time(jump_seconds)
                break
    
    def start_monitoring(self):
        """Starts monitoring playback time"""
        self.running = True
        print("Starting VLC monitoring...")
        print("Press Ctrl+C to stop")

        failed_attempts = 0  # Failed attempts counter
        max_attempts = int(self.timeout_seconds / self.check_interval)  # Maximum attempts
        try:
            while self.running:
                # Check connection to RC interface
                if not test_rc_connection(self.vlc_host, self.vlc_port, 0.1, self.rc_password):
                    failed_attempts += 1
                
                    if failed_attempts == 1:
                        print(f"RC interface unavailable ({self.vlc_host}:{self.vlc_port}), waiting...")
                
                    # Check if maximum attempts exceeded
                    if failed_attempts >= max_attempts:
                        print(f"Failed to connect to VLC RC interface after {failed_attempts} attempts ({self.timeout_seconds} seconds)")
                        print("Shutting down...")
                        self.running = False
                        return False
                
                    time.sleep(self.check_interval)
                    continue
            
                # If connection is successful, reset attempt counter
                if failed_attempts > 0:
                    print("Connection to VLC RC interface restored!")
                    failed_attempts = 0
            
                self.check_segments()
                time.sleep(0.1)  # Check every 0.1 seconds
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            self.running = False
    
        return True
    
    def stop_monitoring(self):
        """Stops monitoring"""
        self.running = False

def main(json_file_path):
    try:
        # Create controller
        controller = VLCSkipController(json_file_path)
        
        # Start monitoring
        if not controller.start_monitoring():
            print("Monitoring was not started")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True