from canvasapi import Canvas
from google import genai
import json
import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

script_dir = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(script_dir, 'config.json')




canvas = None
client = None
courses = None
REQUIRED_KEYS = ["GEMINI_KEY", "CANVAS_TOKEN", "CANVAS_URL"]




def ai_generate_text(text):
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=text
    )
    return response.text


def course_ai_task():
    whole_list = ""
    print("Generating")
    for course in courses:
        if hasattr(course, "name"):
            whole_list += str(course)
            whole_list += course.show_front_page().body

    
    
    
    print(ai_generate_text(f"I am going to give you a piece of HTML code. ONLY respond with the assignments and/or things you must do for the class that week. make sure you give EVERY assignment. Format it like this \n1. Class name | Assignment | Due date \nIf there is no due date, replace it with (No due date specified){whole_list}"))

def data_validity_check():
    try:
        tokens_initialize()
        print(f"Loading.. {canvas.get_current_user()}")
    except:
        messagebox.showerror("Invalid Data", "Please double check to make sure you inputted the right stuff.")
        return False
    else:
        return True

def tokens_initialize():
    with open(config_path, "r") as f:
        config = json.load(f)
    global canvas, client, courses
    AI_KEY = config["GEMINI_KEY"]
    CANVAS_TOKEN = config["CANVAS_TOKEN"]
    CANVAS_URL = config["CANVAS_URL"]
    canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)
    client = genai.Client(api_key=AI_KEY)
    courses = canvas.get_courses()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Configuration Manager")
        self.geometry("500x450") 
        ctk.set_appearance_mode("dark")
        
        self.entries = {}
        self.check_and_load()

    def check_and_load(self):
        data = self.load_data()
        if data and all(key in data for key in REQUIRED_KEYS) and data_validity_check():
            tokens_initialize()
            self.show_welcome_page(data)
        else:
            if os.path.exists(config_path):
                os.remove(config_path)
            self.show_setup_page()

    def load_data(self):
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                try:
                    return json.load(f)
                except:
                    return None
        return None

    def save_data(self):
        new_data = {key: self.entries[key].get() for key in REQUIRED_KEYS}
        with open(config_path, "w") as f:
            json.dump(new_data, f, indent=4)
        
        self.setup_frame.destroy()
        self.check_and_load()

    def show_setup_page(self):
        self.setup_frame = ctk.CTkFrame(self)
        self.setup_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(self.setup_frame, text="Missing Configuration", font=("Arial", 20, "bold")).pack(pady=10)

        for key in REQUIRED_KEYS:
            ctk.CTkLabel(self.setup_frame, text=f"Enter {key}:").pack(pady=(10, 0))
            entry = ctk.CTkEntry(self.setup_frame, width=300, placeholder_text=f"Paste {key} here...")
            entry.pack(pady=5)
            self.entries[key] = entry

        ctk.CTkButton(self.setup_frame, text="Save Config", command=self.save_data).pack(pady=20)

    def show_welcome_page(self, data):
        self.welcome_frame = ctk.CTkFrame(self)
        self.welcome_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(self.welcome_frame, text="System Ready", font=("Arial", 10, "bold"), text_color="#2FA572").pack(pady=10)
        
        for key in REQUIRED_KEYS:
            ctk.CTkLabel(self.welcome_frame, text=f"{key}: LOADED", font=("Arial", 12)).pack()


        self.extra_btn = ctk.CTkButton(
            self.welcome_frame, 
            text="Open Blank Window", 
            fg_color="gray25", 
            hover_color="gray35",
            command=self.open_extra_window
        )
        self.extra_btn.pack(side="bottom", pady=20)

    def open_extra_window(self):

  
        extra_window = ctk.CTkToplevel(self)
        extra_window.title("Empty Window")
        extra_window.geometry("300x200")
        
        extra_window.after(100, lambda: extra_window.focus()) 
        

        ctk.CTkLabel(extra_window, text="This is a separate window\nYou can close me!").pack(expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()

