import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from pathlib import Path

class BIOSRepairTool:
    def __init__(self, root):
        self.root = root
        self.root.title("BIOS Repair Tool - ideapad/thinkbook")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variable untuk menyimpan file path
        self.file_path = tk.StringVar()
        self.extract_method = tk.StringVar(value="auto")
        self.use_padding = tk.BooleanVar(value=False)
        self.move_dmi = tk.BooleanVar(value=False)
        self.detect_dmi = tk.BooleanVar(value=False)
        self.timeout_value = tk.StringVar(value="15")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ===== FILE SELECTION SECTION =====
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(file_frame, text="EXE").pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="EXE", command=self.select_exe_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(file_frame, text="BIN").pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="BIN", command=self.select_bin_file).pack(side=tk.LEFT, padx=5)
        
        file_display = ttk.Entry(file_frame, textvariable=self.file_path, state='readonly', width=50)
        file_display.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # ===== REPAIR OPTIONS SECTION =====
        repair_frame = ttk.LabelFrame(main_frame, text="Repair Options", padding="10")
        repair_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Radio buttons untuk extract method
        ttk.Radiobutton(repair_frame, text="HnO Extract", variable=self.extract_method, 
                       value="hno").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(repair_frame, text="Z6 Extract", variable=self.extract_method, 
                       value="z6").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(repair_frame, text="Temp Extract", variable=self.extract_method, 
                       value="temp").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(repair_frame, text="Auto Process", variable=self.extract_method, 
                       value="auto").pack(anchor=tk.W, pady=5)
        
        # Padding options
        padding_frame = ttk.Frame(repair_frame)
        padding_frame.pack(anchor=tk.W, pady=10)
        
        ttk.Checkbutton(padding_frame, text="Use Padding", variable=self.use_padding).pack(side=tk.LEFT)
        ttk.Label(padding_frame, text="TimeOut in sec").pack(side=tk.LEFT, padx=10)
        ttk.Spinbox(padding_frame, from_=1, to=300, textvariable=self.timeout_value, 
                   width=5).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(repair_frame)
        button_frame.pack(anchor=tk.W, pady=10)
        
        ttk.Button(button_frame, text="Repair Original File", 
                  command=self.repair_original).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Extract Only", 
                  command=self.extract_only).pack(side=tk.LEFT, padx=5)
        
        # ===== DMI SECTION =====
        dmi_frame = ttk.LabelFrame(main_frame, text="DMI", padding="10")
        dmi_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Checkbutton(dmi_frame, text="Detect DMI", variable=self.detect_dmi).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(dmi_frame, text="Move DMI to Repaired File", variable=self.move_dmi).pack(anchor=tk.W, pady=5)
        
        ttk.Label(dmi_frame, text="Recared File").pack(anchor=tk.W, pady=10)
        ttk.Button(dmi_frame, text="Go", command=self.process_dmi).pack(anchor=tk.W, pady=5)
        
        # ===== PROGRESS SECTION =====
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        self.log_text = tk.Text(progress_frame, height=8, width=80, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(progress_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscroll=scrollbar.set)
        
        # ===== PREVIEW SECTION =====
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.grid(row=0, column=2, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        
        self.preview_canvas = tk.Canvas(preview_frame, bg='#000080', width=300, height=400)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
    def select_exe_file(self):
        file = filedialog.askopenfilename(filetypes=[("EXE files", "*.exe"), ("All files", "*.*")])
        if file:
            self.file_path.set(file)
            self.log("Selected EXE file: " + os.path.basename(file))
    
    def select_bin_file(self):
        file = filedialog.askopenfilename(filetypes=[("BIN files", "*.bin"), ("All files", "*.*")])
        if file:
            self.file_path.set(file)
            self.log("Selected BIN file: " + os.path.basename(file))
    
    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def repair_original(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a file first!")
            return
        
        thread = threading.Thread(target=self._repair_process)
        thread.daemon = True
        thread.start()
    
    def extract_only(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a file first!")
            return
        
        thread = threading.Thread(target=self._extract_process)
        thread.daemon = True
        thread.start()
    
    def process_dmi(self):
        if not self.detect_dmi.get() and not self.move_dmi.get():
            messagebox.showwarning("Warning", "Please select at least one option!")
            return
        
        thread = threading.Thread(target=self._dmi_process)
        thread.daemon = True
        thread.start()
    
    def _repair_process(self):
        self.progress_bar.start()
        self.log(f"Starting repair process...")
        self.log(f"Method: {self.extract_method.get()}")
        self.log(f"Use Padding: {self.use_padding.get()}")
        self.log(f"Timeout: {self.timeout_value.get()} seconds")
        
        try:
            # Simulate repair process
            import time
            time.sleep(2)
            self.log("✓ File extracted successfully")
            time.sleep(1)
            self.log("✓ Repair process completed")
            time.sleep(0.5)
            self.log("✓ Repaired file saved")
            
            messagebox.showinfo("Success", "Repair process completed successfully!")
        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Repair process failed: {str(e)}")
        finally:
            self.progress_bar.stop()
    
    def _extract_process(self):
        self.progress_bar.start()
        self.log(f"Starting extract process...")
        self.log(f"Method: {self.extract_method.get()}")
        
        try:
            import time
            time.sleep(2)
            self.log("✓ File extracted successfully")
            
            messagebox.showinfo("Success", "Extract process completed successfully!")
        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Extract process failed: {str(e)}")
        finally:
            self.progress_bar.stop()
    
    def _dmi_process(self):
        self.progress_bar.start()
        self.log(f"Starting DMI process...")
        
        if self.detect_dmi.get():
            self.log("Detecting DMI data...")
        
        if self.move_dmi.get():
            self.log("Moving DMI to repaired file...")
        
        try:
            import time
            time.sleep(2)
            self.log("✓ DMI process completed")
            
            messagebox.showinfo("Success", "DMI process completed successfully!")
        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"DMI process failed: {str(e)}")
        finally:
            self.progress_bar.stop()


def main():
    root = tk.Tk()
    app = BIOSRepairTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
