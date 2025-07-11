import tkinter as tk
from tkinter import messagebox
import tkinterdnd2 as tkdnd
import os
import threading
from src.utils.json_finder import check_video_file
from src.vlc.launcher import main as vlc_main

class VideoDropWindow:
    def __init__(self):
        # Create main window with DnD support
        self.root = tkdnd.TkinterDnD.Tk()
        self.current_video_path = None  # Store path to current video file
        self.setup_window()
        self.setup_drop_area()
        
    def setup_window(self):
        """Main window setup"""
        self.root.title("Just Skip It!")
        self.root.geometry("500x300")
        self.root.resizable(True, True)
        
        # Add window icon - for Windows use iconbitmap
        try:
            # Path to icon file
            icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        
            # For Windows we need to use .ico file, but we can temporarily convert png to ico
            from PIL import Image, ImageTk
            import tempfile
        
            # Create temporary .ico file
            temp_ico = tempfile.NamedTemporaryFile(suffix='.ico', delete=False)
            temp_ico.close()
        
            # Convert png to ico
            img = Image.open(icon_path)
            img.save(temp_ico.name)
        
            # Set icon for window
            self.root.iconbitmap(temp_ico.name)
        
            # Schedule deletion of temporary file when window is closed
            def cleanup_temp_ico():
                try:
                    os.unlink(temp_ico.name)
                except:
                    pass
                self.root.quit()
            
            self.root.protocol("WM_DELETE_WINDOW", cleanup_temp_ico)
        except Exception as e:
            print(f"Error when setting icon: {e}")
        
    def setup_drop_area(self):
        """Create area for file drag and drop"""
        # Create frame for drop area
        self.drop_frame = tk.Frame(
            self.root, 
            bg="lightgray", 
            relief="ridge", 
            bd=2
        )
        self.drop_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add hint text
        self.label = tk.Label(
            self.drop_frame,
            text="Drop video file here",
            bg="lightgray",
            fg="darkblue",
            font=("Arial", 12),
            justify="center"
        )
        self.label.pack(expand=True)
        
        # Setup drag-and-drop
        self.drop_frame.drop_target_register(tkdnd.DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_frame.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.drop_frame.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        
        # Area for displaying file information
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.info_label = tk.Label(
            self.info_frame,
            text="",
            wraplength=480,
            justify="left",
            font=("Arial", 10)
        )
        self.info_label.pack()
        
    def on_drag_enter(self, event):
        """Handle entering the drop zone"""
        self.drop_frame.config(bg="lightblue")
        self.label.config(bg="lightblue", text="Release file here")
        
    def on_drag_leave(self, event):
        """Handle leaving the drop zone"""
        self.drop_frame.config(bg="lightgray")
        self.label.config(
            bg="lightgray", 
            text="Drop video file here"
        )
        
    def on_drop(self, event):
        """Handle file drop"""
        # Get file path
        file_path = event.data.strip('{}')  # Remove curly braces if present

        # Check if it's a video file
        if self.is_video_file(file_path):
            self.process_video_file(file_path)
        else:
            messagebox.showerror(
                "Error", 
                "This is not a video file or format is not supported!"
            )
        
        # Return to normal appearance
        self.on_drag_leave(event)
        
    def is_video_file(self, file_path):
        """Check if the file is a video file"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in video_extensions
        
    def process_video_file(self, file_path):
        """Process video file - extract path and name"""
        # Save file path
        self.current_video_path = os.path.abspath(file_path)
        
        # Get full path
        full_path = os.path.abspath(file_path)
        
        # Get file name
        file_name = os.path.basename(file_path)
        
        # Get directory
        directory = os.path.dirname(full_path)
        
        # Get file size
        try:
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
        except:
            size_mb = 0
        
        # Display information
        info_text = f"""Video file successfully added!

File name: {file_name}
Full path: {full_path}
Directory: {directory}
Size: {size_mb:.2f} MB

Checking JSON file..."""
        
        self.info_label.config(text=info_text, fg="darkblue")
        self.root.update()  # Update interface to show message

        # Check for JSON file
        json_check_result = check_video_file(self.current_video_path)
        
        if json_check_result:
            # JSON file found and valid
            final_info_text = f"""Video file successfully added!

File name: {file_name}
Full path: {full_path}
Directory: {directory}
Size: {size_mb:.2f} MB

✓ JSON file found and valid"""
            
            self.info_label.config(text=final_info_text, fg="darkgreen")
            
            # Show confirm button only if JSON file is valid
            self.show_confirm_button()
        else:
            # JSON file not found or invalid
            final_info_text = f"""Video file added, but there are issues:

File name: {file_name}
Full path: {full_path}
Directory: {directory}
Size: {size_mb:.2f} MB

✗ JSON file not found or invalid"""
            
            self.info_label.config(text=final_info_text, fg="red")
        
        # Print to console for convenience
        print("=" * 50)
        print("VIDEO FILE INFORMATION:")
        print(f"File name: {file_name}")
        print(f"Full path: {full_path}")
        print(f"Directory: {directory}")
        print(f"Size: {size_mb:.2f} MB")
        print(f"JSON file valid: {json_check_result}")
        print("=" * 50)
    
    def show_confirm_button(self):
        """Show confirmation button"""
        # Create frame for button if it doesn't exist yet
        if not hasattr(self, 'button_frame'):
            self.button_frame = tk.Frame(self.root)
            self.button_frame.pack(pady=10)
            
            self.ok_button = tk.Button(
                self.button_frame,
                text="Launch VLC",
                command=self.on_confirm,
                bg="green",
                fg="white",
                font=("Arial", 12, "bold"),
                padx=20,
                pady=5
            )
            self.ok_button.pack()
        else:
            # If frame already exists, just show it
            self.button_frame.pack(pady=10)
            
    def on_confirm(self):
        """Handle confirmation button click"""
        if self.current_video_path:
            try:
                # Hide button
                self.button_frame.pack_forget()
    
                # Update interface
                self.info_label.config(text="Launching VLC player...", fg="blue")
                self.root.update()
    
                # Launch VLC in a separate thread or process
                import threading
    
                def run_vlc():
                    # Call main function from launcher
                    vlc_main(self.current_video_path)
    
                # Launch in a separate thread
                self.vlc_thread = threading.Thread(target=run_vlc)
                self.vlc_thread.daemon = False  # Thread will continue after main application closes
                self.vlc_thread.start()
    
                # Close main window
                self.root.destroy()
        
                # Create a new window with stop button
                self.create_stop_window()
    
            except Exception as e:
                messagebox.showerror("Error", f"Launch error: {str(e)}")
                self.info_label.config(text="Launch error", fg="red")
                self.show_confirm_button()  # Show button again

    def create_stop_window(self):
        """Create window with stop button"""
        stop_window = tk.Tk()
        stop_window.title("Just Skip It!")
        stop_window.geometry("300x150")
        stop_window.resizable(True, True)

        # Add window icon - for Windows use iconbitmap
        try:
            # Path to icon file
            icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        
            # For Windows we need to use .ico file, but we can temporarily convert png to ico
            from PIL import Image, ImageTk
            import tempfile
        
            # Create temporary .ico file
            temp_ico = tempfile.NamedTemporaryFile(suffix='.ico', delete=False)
            temp_ico.close()
        
            # Convert png to ico
            img = Image.open(icon_path)
            img.save(temp_ico.name)
        
            # Set icon for window
            stop_window.iconbitmap(temp_ico.name)
        
            # Schedule deletion of temporary file after window is closed
            def cleanup_temp_ico():
                try:
                    os.unlink(temp_ico.name)
                except:
                    pass
                stop_window.destroy()
        
            # Redefine stop function to clean up temporary file
            def stop_application():
                cleanup_temp_ico()
                import os, sys
                os._exit(0)
            
            stop_window.protocol("WM_DELETE_WINDOW", cleanup_temp_ico)
        except Exception as e:
            print(f"Error when setting icon: {e}")
        
        # Position window in the bottom right corner of the screen
        screen_width = stop_window.winfo_screenwidth()
        screen_height = stop_window.winfo_screenheight()
        x = screen_width - 320
        y = screen_height - 200
        stop_window.geometry(f"+{x}+{y}")
    
        # Add explanatory text
        info_label = tk.Label(
            stop_window,
            text="Program is running in background.\nTo stop it, press the button below.",
            wraplength=280,
            justify="center",
            font=("Arial", 10)
        )
        info_label.pack(pady=(20, 15))
    
        # Add button to stop the program
        stop_button = tk.Button(
            stop_window,
            text="Stop Program",
            command=stop_application,
            bg="red",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=5
        )
        stop_button.pack()
    
        stop_window.mainloop()
            
    def run(self):
        """Run the application"""
        self.root.mainloop()

