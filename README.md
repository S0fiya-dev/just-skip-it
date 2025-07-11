# Just Skip It!

**Just Skip It!** is a tool designed to automatically skip specific segments of videos played with the VLC media player. It’s perfect for skipping any unwanted content while watching your videos.

---

## Features

* Drag and Drop interface for easy video selection
* Automatic detection and validation of configuration files
* Automatic skipping of predefined video segments
* Customizable skip settings via JSON configuration files

---

## Requirements

* OS: Windows(?)
* Python version 3.6 or higher
* VLC Media Player
* Required Python packages:

  * `tkinterdnd2`
  * `pillow`

---

## Installation

1. Clone or download the repository
2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```
3. Configure the `config.ini` file to include the path to your installed VLC

---

## Configuration

### VLC setup (`config.ini`)

Edit the `config.ini` file to specify the VLC path and remote control interface settings:

```ini
[VLC]
executable_path = C:\apps\VLC\vlc.exe
rc_host = localhost
rc_port = 4212
rc_password =

[TIMEOUTS]
rc_check_interval = 1
rc_connection_timeout = 60
```

Parameter explanations:

* `executable_path`: Full path to the VLC executable
* `rc_host`: Host for the VLC remote control interface
* `rc_port`: Port for the VLC remote control interface (default is 4212)
* `rc_password`: Password for the VLC remote control interface (leave blank if none)
* `rc_check_interval`: How often the utility checks the VLC status (in seconds)
* `rc_connection_timeout`: Maximum time to wait for a connection to VLC (in seconds)

---

### Video skip configuration (JSON files)

For each video you want to use with **Just Skip It!**, create a JSON configuration file with the same name as the video file but with a `.json` extension.
**Important:** The JSON file must be located in the same folder as the video file.

Example:

* Video: `/videos/movie.mp4`
* JSON: `/videos/movie.json`

The JSON structure should look like this:

```json
{
  "version": "1.0",
  "video_info": {
    "filename": "video_name.mp4",
    "duration": "01:30:45"
  },
  "time_segments": [
    {
      "id": 1,
      "name": "Skip intro",
      "trigger_time": "00:01:30",
      "jump_to_time": "00:03:45",
      "enabled": true
    },
    {
      "id": 2,
      "name": "Skip credits",
      "trigger_time": "01:28:00",
      "jump_to_time": "01:29:50",
      "enabled": true
    }
  ],
  "settings": {
    "loop_segments": false,
    "show_notifications": true
  }
}
```

JSON structure explanation:

* `version`: Configuration format version
* `video_info`: Basic information about the video
  * `filename`: Name of the video file
  * `duration`: Total duration of the video in HH\:MM\:SS format
* `time_segments`: Array of segments to skip
  * `id`: Unique segment ID
  * `name`: Description of the segment (e.g., “Skip intro”)
  * `trigger_time`: Time to activate the skip (HH\:MM\:SS)
  * `jump_to_time`: Time to jump to (HH\:MM\:SS)
  * `enabled`: Whether to skip this segment (true/false)
* `settings`: Additional settings
  * `loop_segments`: Defines whether skips should repeat (not fully implemented yet)
  * `show_notifications`: Show notifications while skipping (not fully implemented yet)

---

### VLC setup

Make sure the RC (Remote Control) interface is enabled in VLC:

1. In VLC, go to **Tools > Preferences**
2. At the bottom, select **Show settings: All**
3. Navigate to **Interface > Main interfaces**
4. Check **Remote control interface**
5. Go to **Interface > Main interfaces > RC**
6. Configure the host and port (default: localhost:4212)

---

## Usage

1. Run the utility:

   ```bash
   python main.py
   ```
2. Drag and drop a video file into the utility window
3. If a valid configuration file is found, click “Start VLC”
4. The video will launch in VLC with automatic segment skipping
5. A small control window will appear, allowing you to stop the utility

---

## How it works

1. When you drag and drop a video, the utility looks for a matching JSON file in the same folder
2. If found, the utility validates the file
3. After launching VLC, the utility connects to VLC’s remote control interface
4. It monitors the playback time and automatically skips the defined segments
5. When playback reaches a trigger time, it jumps to the specified skip time

---

## Troubleshooting

* Make sure VLC is installed correctly and the path in `config.ini` is correct
* Ensure the VLC remote control interface is enabled in VLC’s settings
* Verify that your JSON configuration files are valid and follow the expected format
* Make sure the video and JSON filenames match (except for the extension)
* Ensure the JSON file is in the same folder as the video file

---

## License

This project is provided “as is” with no warranties.

[Читать на русском](README_rus.md)