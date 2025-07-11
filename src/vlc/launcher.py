import subprocess
import socket
import time
import os
import configparser

def load_config():
    """Loads configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.ini')
    
    if not os.path.exists(config_path):
        print(f"Error: Configuration file {config_path} not found")
        return None
    
    try:
        config.read(config_path, encoding='utf-8')
        
        # Extract settings
        vlc_path = config.get('VLC', 'executable_path')
        rc_host = config.get('VLC', 'rc_host')
        rc_port = config.getint('VLC', 'rc_port')
        rc_password = config.get('VLC', 'rc_password', fallback='')
        check_interval = config.getfloat('TIMEOUTS', 'rc_check_interval')
        timeout_seconds = config.getint('TIMEOUTS', 'rc_connection_timeout')
        
        return {
            'vlc_path': vlc_path,
            'rc_host': rc_host,
            'rc_port': rc_port,
            'rc_password': rc_password,
            'check_interval': check_interval,
            'timeout_seconds': timeout_seconds
        }
        
    except Exception as e:
        print(f"Error reading configuration: {e}")
        return None

def start_vlc(vlc_path, video_path):
    """Launches VLC with the video file"""
    try:
        # Check if files exist
        if not os.path.exists(vlc_path):
            print(f"Error: VLC not found at path {vlc_path}")
            return None
        
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at path {video_path}")
            return None
        
        # Command to launch VLC with video file
        cmd = [vlc_path, video_path]
        
        print("Launching VLC...")
        process = subprocess.Popen(cmd)
        return process
    
    except Exception as e:
        print(f"Error launching VLC: {e}")
        return None

def test_rc_connection(host, port, timeout, password=''):
    """Tests connection to the RC interface"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        
        if result == 0:
            # If password is specified, send it first
            if password:
                sock.send(f"{password}\n".encode())
                # Get response after entering password
                response = sock.recv(1024)
                
            # Send test command
            sock.send(b"help\n")
            response = sock.recv(1024)
            sock.close()
            return len(response) > 0
        else:
            sock.close()
            return False
            
    except Exception:
        return False


def main(video_path):
    """Main function"""
    print("Starting script...")

    # Load configuration
    config = load_config()
    if config is None:
        return
    
    print(f"Configuration loaded:")
    print(f"  VLC: {config['vlc_path']}")
    print(f"  Video: {video_path}")
    print(f"  RC: {config['rc_host']}:{config['rc_port']}")
    print(f"  Check interval: {config['check_interval']} sec")
    print(f"  Timeout: {config['timeout_seconds']} sec")
    
    # Launch VLC
    vlc_process = start_vlc(config['vlc_path'], video_path)
    if vlc_process is None:
        print("Failed to launch VLC")
        return
    
    print("VLC launched, checking RC interface availability...")

    # Calculate number of attempts
    max_attempts = int(config['timeout_seconds'] / config['check_interval'])
    
    # Wait and check RC interface
    for attempt in range(max_attempts):
        elapsed_time = attempt * config['check_interval']
        print(f"Attempt {attempt + 1}/{max_attempts} (elapsed {elapsed_time:.1f} sec)...")
        
        if test_rc_connection(config['rc_host'], config['rc_port'], 1, config.get('rc_password', '')):
            print("RC interface available!")

            # Get path to JSON file from video path
            json_file_path = video_path.rsplit(".", 1)[0] + ".json"
            
            from src.vlc.controller import main as skip_controller_main
            
            print("Starting skip controller...")
            skip_controller_main(json_file_path)
            return
        
        time.sleep(config['check_interval'])
    
    # If connection couldn't be established within the timeout period
    print(f"Timeout: RC interface not available for {config['timeout_seconds']} seconds")
    print("Terminating script")
