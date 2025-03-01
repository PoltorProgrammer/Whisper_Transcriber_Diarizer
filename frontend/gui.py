import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import requests

API_URL = "http://127.0.0.1:8000/transcribe/"

class DiarizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Whisper Diarizer Interface")
        self.geometry("500x500")
        self.configure(bg="#f5f5f5")  # Soft light grey background
        self.selected_file = None
        self.transcript_content = None

        # Configure ttk style for a soft modern look
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Frame styling
        style.configure("TFrame", background="#ffffff")  
        
        # Label styling
        style.configure("TLabel",
                        background="#ffffff",
                        foreground="#333333",
                        font=("Helvetica", 12))
        style.configure("Title.TLabel",
                        font=("Helvetica", 18, "bold"),
                        background="#ffffff",
                        foreground="#333333")
        
        # Button styling
        style.configure("TButton",
                        font=("Helvetica", 12),
                        padding=6,
                        background="#A3D2CA",
                        foreground="#ffffff")
        style.map("TButton", background=[("active", "#82c0b0")])
        
        self.create_widgets()

    def create_widgets(self):
        # Main frame with white background
        main_frame = ttk.Frame(self, padding="20 20 20 20", style="TFrame")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title Label
        title_label = ttk.Label(
            main_frame,
            text="Whisper Diarizer",
            style="Title.TLabel",
            anchor="center"
        )
        title_label.pack(pady=10, anchor="center")

        # File Upload Section
        self.upload_label = ttk.Label(main_frame, text="No file selected", wraplength=400)
        self.upload_label.pack(pady=10, anchor="center")

        self.upload_button = ttk.Button(main_frame, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=5, anchor="center")

        # Language Selection
        language_label = ttk.Label(main_frame, text="Select Language:", anchor="center")
        language_label.pack(pady=(20, 5), anchor="center")

        self.language_var = tk.StringVar(value="Detect Automatically")
        language_options = ["Detect Automatically", "English", "Spanish", "French", "German"]
        self.language_menu = ttk.OptionMenu(main_frame, self.language_var, *language_options)
        self.language_menu.pack(pady=(0, 10), anchor="center")

        # Model Size Selection
        model_label = ttk.Label(main_frame, text="Select Model Size:", anchor="center")
        model_label.pack(pady=(20, 5), anchor="center")

        self.model_var = tk.StringVar(value="tiny")
        model_options = ["tiny", "base", "small", "medium", "large", "large-v2"]
        self.model_menu = ttk.OptionMenu(main_frame, self.model_var, *model_options)
        self.model_menu.pack(pady=(0, 10), anchor="center")

        # Process File Button
        self.process_button = ttk.Button(main_frame, text="Process File", command=self.start_processing)
        self.process_button.pack(pady=15, anchor="center")

        # Progress Label
        self.progress_label = ttk.Label(main_frame, text="", anchor="center")
        self.progress_label.pack(pady=10, anchor="center")

        # Download Button (initially disabled)
        self.download_button = ttk.Button(main_frame, text="Download Transcript", command=self.download_file, state=tk.DISABLED)
        self.download_button.pack(pady=10, anchor="center")

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an Audio File",
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac"), ("All Files", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            self.upload_label.config(text=f"Selected: {file_path}")
        else:
            self.upload_label.config(text="No file selected")

    def start_processing(self):
        if not self.selected_file:
            messagebox.showerror("Error", "Please upload an audio file first!")
            return

        self.progress_label.config(text="Uploading file to API...")
        self.process_button.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)

        # Start processing in a separate thread
        threading.Thread(target=self.process_file).start()

    def process_file(self):
        transcript = self.send_audio_to_api(self.selected_file, self.language_var.get(), self.model_var.get())
        self.transcript_content = transcript

        # Update UI on the main thread after processing
        self.after(0, self.on_processing_complete)

    def send_audio_to_api(self, file_path, language, model):
        with open(file_path, "rb") as f:
            files = {"file": f}
            params = {"language": language, "model": model}
            response = requests.post(API_URL, files=files, params=params)
        
        if response.status_code == 200:
            return response.json()["transcript"]
        else:
            return f"Error: {response.text}"

    def on_processing_complete(self):
        self.progress_label.config(text="Processing complete!")
        self.process_button.config(state=tk.NORMAL)
        self.download_button.config(state=tk.NORMAL)

    def download_file(self):
        if not self.transcript_content:
            messagebox.showerror("Error", "No transcript available!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Transcript As"
        )
        if save_path:
            try:
                with open(save_path, "w") as f:
                    f.write(self.transcript_content)
                messagebox.showinfo("Success", f"Transcript saved to {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

if __name__ == "__main__":
    app = DiarizerApp()
    app.mainloop()

