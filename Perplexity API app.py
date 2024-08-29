import tkinter as tk
from tkinter import scrolledtext, font
from openai import OpenAI
import threading
import re
from tkinter import ttk

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text, command=None):
        tk.Canvas.__init__(self, parent, borderwidth=0, 
            relief="flat", highlightthickness=0, bg=parent["bg"])
        self.command = command

        if cornerradius > 0.5*width:
            cornerradius = 0.5*width
        if cornerradius > 0.5*height:
            cornerradius = 0.5*height

        rad = 2*cornerradius
        def shape():
            self.create_polygon((padding,height-cornerradius-padding,padding,cornerradius+padding,padding+cornerradius,padding,width-padding-cornerradius,padding,width-padding,cornerradius+padding,width-padding,height-cornerradius-padding,width-padding-cornerradius,height-padding,padding+cornerradius,height-padding), fill=color, outline=color)
            self.create_arc((padding,padding+rad,padding+rad,padding), start=90, extent=90, fill=color, outline=color)
            self.create_arc((width-padding-rad,padding,width-padding,padding+rad), start=0, extent=90, fill=color, outline=color)
            self.create_arc((width-padding,height-rad-padding,width-padding-rad,height-padding), start=270, extent=90, fill=color, outline=color)
            self.create_arc((padding,height-padding-rad,padding+rad,height-padding), start=180, extent=90, fill=color, outline=color)

        shape()
        self.create_text(width/2, height/2, text=text, fill='white', font=('Segoe UI', 10, 'bold'))
        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.command is not None:
            self.command()

class AIChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chat")
        self.root.configure(bg="#2C2F33")
        
        self.api_key = "[INSERT PERPLEXITY AI API KEY HERE]"
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.perplexity.ai")
        
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence assistant. Engage in a helpful, "
                    "detailed, polite conversation with the user. You can use Markdown-like "
                    "formatting: **bold**, *italic*, # Heading 1, ## Heading 2, ### Heading 3."
                ),
            },
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        main_frame = tk.Frame(self.root, bg="#2C2F33", padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        self.chat_history = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=60, height=20)
        self.chat_history.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.chat_history.config(state=tk.DISABLED, font=("Segoe UI", 10), bg="#36393F", fg="#FFFFFF", bd=0, padx=10, pady=10)
        
        self.setup_tags()
        
        input_frame = tk.Frame(main_frame, bg="#2C2F33")
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_box = tk.Text(input_frame, wrap=tk.WORD, width=50, height=3)
        self.input_box.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_box.config(font=("Segoe UI", 10), bg="#40444B", fg="#FFFFFF", insertbackground="#FFFFFF", bd=0, padx=10, pady=10)
        
        send_button = RoundedButton(input_frame, 80, 40, 10, 2, "#7289DA", "Send", self.send_message)
        send_button.grid(row=0, column=1)
        
        self.input_box.bind("<Return>", self.send_message)
        
        self.root.minsize(500, 400)
        
    def setup_tags(self):
        default_font = font.Font(family="Segoe UI", size=10)
        bold_font = font.Font(family="Segoe UI", size=10, weight="bold")
        italic_font = font.Font(family="Segoe UI", size=10, slant="italic")
        h1_font = font.Font(family="Segoe UI", size=16, weight="bold")
        h2_font = font.Font(family="Segoe UI", size=14, weight="bold")
        h3_font = font.Font(family="Segoe UI", size=12, weight="bold")
        
        self.chat_history.tag_configure('bold', font=bold_font)
        self.chat_history.tag_configure('italic', font=italic_font)
        self.chat_history.tag_configure('h1', font=h1_font)
        self.chat_history.tag_configure('h2', font=h2_font)
        self.chat_history.tag_configure('h3', font=h3_font)
        self.chat_history.tag_configure('user_tag', foreground="#7289DA", font=bold_font)
        self.chat_history.tag_configure('ai_tag', foreground="#43B581", font=bold_font)
        
    def process_formatting(self, text):
        lines = text.split('\n')
        for line in lines:
            if line.startswith('# '):
                self.chat_history.insert(tk.END, line[2:], 'h1')
                self.chat_history.insert(tk.END, '\n')
            elif line.startswith('## '):
                self.chat_history.insert(tk.END, line[3:], 'h2')
                self.chat_history.insert(tk.END, '\n')
            elif line.startswith('### '):
                self.chat_history.insert(tk.END, line[4:], 'h3')
                self.chat_history.insert(tk.END, '\n')
            else:
                parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', line)
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        self.chat_history.insert(tk.END, part[2:-2], 'bold')
                    elif part.startswith('*') and part.endswith('*'):
                        self.chat_history.insert(tk.END, part[1:-1], 'italic')
                    else:
                        self.chat_history.insert(tk.END, part)
                self.chat_history.insert(tk.END, '\n')
        
    def get_ai_response(self):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, "AI: ", 'ai_tag')
        self.chat_history.config(state=tk.DISABLED)
        
        try:
            response_stream = self.client.chat.completions.create(
                model="llama-3-sonar-large-32k-online",
                messages=self.messages,
                stream=True,
            )
            
            full_response = ""
            buffer = ""
            for response in response_stream:
                if response.choices[0].delta.content is not None:
                    buffer += response.choices[0].delta.content
                    full_response += response.choices[0].delta.content
                    if buffer.endswith(('\n', ' ')) or len(buffer) > 100:
                        self.chat_history.config(state=tk.NORMAL)
                        self.process_formatting(buffer)
                        self.chat_history.see(tk.END)
                        self.chat_history.config(state=tk.DISABLED)
                        buffer = ""
            
            if buffer:
                self.chat_history.config(state=tk.NORMAL)
                self.process_formatting(buffer)
                self.chat_history.config(state=tk.DISABLED)
            
            # Add AI's response to the messages list
            self.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, f"An error occurred: {str(e)}\n")
            self.chat_history.config(state=tk.DISABLED)
        
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, "\n\n")
        self.chat_history.config(state=tk.DISABLED)
        
    def send_message(self, event=None):
        user_message = self.input_box.get("1.0", tk.END).strip()
        if user_message:
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, "You: ", 'user_tag')
            self.chat_history.insert(tk.END, f"{user_message}\n\n")
            self.chat_history.config(state=tk.DISABLED)
            self.input_box.delete("1.0", tk.END)
            
            self.messages.append({"role": "user", "content": user_message})
            
            threading.Thread(target=self.get_ai_response).start()
        return 'break'

if __name__ == "__main__":
    root = tk.Tk()
    app = AIChatApp(root)
    root.mainloop()
