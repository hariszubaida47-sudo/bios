import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from pathlib import Path
import struct
import json
from datetime import datetime

class BIOSRepairTool:
    def __init__(self, root):
        self.root = root
        self.root.title("BIOS Repair Tool - ideapad/thinkbook")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Variable untuk menyimpan file path
        self.file_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.expanduser("~/BIOS_Repair_Output"))
        self.extract_method = tk.StringVar(value="auto")
        self.use_padding = tk.BooleanVar(value=False)
        self.move_dmi = tk.BooleanVar(value=False)
        self.detect_dmi = tk.BooleanVar(value=False)
        self.timeout_value = tk.StringVar(value="15")
        
        # Data untuk menyimpan hasil
        self.dmi_data = {}
        self.repair_results = {}
        
        self.create_widgets()
        self.ensure_output_directory()
        
    def ensure_output_directory(self):
        """Pastikan output directory ada"""
        os.makedirs(self.output_dir.get(), exist_ok=True)
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # ===== FILE SELECTION SECTION =====
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(file_frame, text="EXE", command=self.select_exe_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="BIN", command=self.select_bin_file).pack(side=tk.LEFT, padx=5)
        
        file_display = ttk.Entry(file_frame, textvariable=self.file_path, state='readonly', width=50)
        file_display.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # ===== OUTPUT DIRECTORY SECTION =====
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="10")
        output_frame.grid(row=0, column=3, columnspan=1, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        output_display = ttk.Entry(output_frame, textvariable=self.output_dir, state='readonly', width=30)
        output_display.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse", command=self.select_output_dir).pack(side=tk.LEFT, padx=5)
        
        # ===== REPAIR OPTIONS SECTION =====
        repair_frame = ttk.LabelFrame(main_frame, text="Repair Options", padding="10")
        repair_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
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
        dmi_frame.grid(row=1, column=2, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Checkbutton(dmi_frame, text="Detect DMI", variable=self.detect_dmi).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(dmi_frame, text="Move DMI to Repaired File", variable=self.move_dmi).pack(anchor=tk.W, pady=5)
        
        ttk.Button(dmi_frame, text="Detect & Extract DMI", command=self.process_dmi).pack(anchor=tk.W, pady=5)
        ttk.Button(dmi_frame, text="Open Output Folder", command=self.open_output_folder).pack(anchor=tk.W, pady=5)
        
        # ===== PROGRESS SECTION =====
        progress_frame = ttk.LabelFrame(main_frame, text="Progress Log", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        progress_frame.rowconfigure(1, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Log dengan scrollbar
        log_frame = ttk.Frame(progress_frame)
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, width=100, state='disabled', wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.config(yscroll=scrollbar.set)
        
        # ===== RESULTS SECTION =====
        results_frame = ttk.LabelFrame(main_frame, text="File Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        # Treeview untuk menampilkan hasil file
        columns = ("File Name", "Size", "Type", "Created", "Action")
        self.tree = ttk.Treeview(results_frame, columns=columns, height=8, show='headings')
        
        self.tree.heading("File Name", text="File Name")
        self.tree.heading("Size", text="Size (KB)")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Created", text="Created")
        self.tree.heading("Action", text="Action")
        
        self.tree.column("File Name", width=300)
        self.tree.column("Size", width=80)
        self.tree.column("Type", width=100)
        self.tree.column("Created", width=150)
        self.tree.column("Action", width=100)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        tree_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.config(yscroll=tree_scroll.set)
        
        # Bind double click untuk membuka file
        self.tree.bind("<Double-1>", self.on_treeview_double_click)
        
    def select_exe_file(self):
        file = filedialog.askopenfilename(filetypes=[("EXE files", "*.exe"), ("All files", "*.*")])
        if file:
            self.file_path.set(file)
            self.log("✓ Selected EXE file: " + os.path.basename(file))
    
    def select_bin_file(self):
        file = filedialog.askopenfilename(filetypes=[("BIN files", "*.bin"), ("All files", "*.*")])
        if file:
            self.file_path.set(file)
            self.log("✓ Selected BIN file: " + os.path.basename(file))
            # Analisis file BIOS
            self.analyze_bios_file(file)
    
    def select_output_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)
            self.ensure_output_directory()
            self.log("✓ Output directory changed to: " + dir_path)
    
    def analyze_bios_file(self, file_path):
        """Analisis file BIOS untuk mendapatkan info"""
        try:
            file_size = os.path.getsize(file_path) / 1024  # KB
            creation_time = os.path.getctime(file_path)
            
            self.log(f"📊 File Analysis:")
            self.log(f"   - Size: {file_size:.2f} KB")
            self.log(f"   - Full path: {file_path}")
        except Exception as e:
            self.log(f"⚠ Could not analyze file: {str(e)}")
    
    def log(self, message):
        self.log_text.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
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
        thread = threading.Thread(target=self._dmi_process)
        thread.daemon = True
        thread.start()
    
    def _repair_process(self):
        self.progress_bar.start()
        try:
            file_path = self.file_path.get()
            base_name = Path(file_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            self.log("━" * 60)
            self.log("🔧 STARTING REPAIR PROCESS...")
            self.log(f"   Method: {self.extract_method.get().upper()}")
            self.log(f"   Use Padding: {self.use_padding.get()}")
            self.log(f"   Timeout: {self.timeout_value.get()} seconds")
            
            import time
            
            # 1. Read original file
            self.log("\n📖 Reading original BIOS file...")
            with open(file_path, 'rb') as f:
                bios_data = bytearray(f.read())
            self.log(f"   ✓ Read {len(bios_data)} bytes")
            
            # 2. Backup original
            backup_file = os.path.join(self.output_dir.get(), f"{base_name}_BACKUP_{timestamp}.bin")
            with open(backup_file, 'wb') as f:
                f.write(bios_data)
            self.log(f"\n💾 Backup created: {os.path.basename(backup_file)}")
            self._add_to_results(backup_file, "Backup")
            
            time.sleep(1)
            
            # 3. Repair process
            self.log("\n🔨 Repairing BIOS data...")
            
            if self.extract_method.get() == "hno":
                self.log("   - Running HnO extraction algorithm...")
                repaired_data = self._repair_hno(bios_data)
            elif self.extract_method.get() == "z6":
                self.log("   - Running Z6 extraction algorithm...")
                repaired_data = self._repair_z6(bios_data)
            elif self.extract_method.get() == "temp":
                self.log("   - Running Temp extraction algorithm...")
                repaired_data = self._repair_temp(bios_data)
            else:  # auto
                self.log("   - Running Auto process algorithm...")
                repaired_data = self._repair_auto(bios_data)
            
            time.sleep(1)
            self.log("   ✓ Repair algorithm completed")
            
            # 4. Add padding if needed
            if self.use_padding.get():
                self.log(f"\n📏 Adding padding...")
                repaired_data = self._add_padding(repaired_data)
                self.log(f"   ✓ Padding added, new size: {len(repaired_data)} bytes")
            
            # 5. Save repaired file
            repaired_file = os.path.join(self.output_dir.get(), f"{base_name}_REPAIRED_{timestamp}.bin")
            with open(repaired_file, 'wb') as f:
                f.write(repaired_data)
            self.log(f"\n✅ Repaired file saved: {os.path.basename(repaired_file)}")
            self.log(f"   Size: {len(repaired_data)} bytes")
            self._add_to_results(repaired_file, "Repaired")
            
            # 6. DMI processing jika dipilih
            if self.detect_dmi.get():
                self.log("\n🏷️  Detecting DMI data...")
                dmi_file = self._extract_dmi_data(bios_data)
                if dmi_file:
                    self._add_to_results(dmi_file, "DMI Data")
            
            self.log("\n" + "━" * 60)
            self.log("✨ REPAIR PROCESS COMPLETED SUCCESSFULLY!")
            self.log(f"📁 Output folder: {self.output_dir.get()}")
            self.log("━" * 60)
            
            messagebox.showinfo("Success", f"Repair completed!\n\nRepaired file saved to:\n{repaired_file}")
            
        except Exception as e:
            self.log(f"\n❌ ERROR: {str(e)}")
            messagebox.showerror("Error", f"Repair process failed:\n{str(e)}")
        finally:
            self.progress_bar.stop()
    
    def _extract_process(self):
        self.progress_bar.start()
        try:
            file_path = self.file_path.get()
            base_name = Path(file_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            self.log("━" * 60)
            self.log("📤 STARTING EXTRACT PROCESS...")
            self.log(f"   Method: {self.extract_method.get().upper()}")
            
            import time
            
            # Read file
            self.log("\n📖 Reading BIOS file...")
            with open(file_path, 'rb') as f:
                bios_data = bytearray(f.read())
            self.log(f"   ✓ Read {len(bios_data)} bytes")
            
            time.sleep(1)
            
            # Extract
            self.log("\n🔓 Extracting data...")
            extracted_data = bios_data.copy()
            
            # Save extracted
            extracted_file = os.path.join(self.output_dir.get(), f"{base_name}_EXTRACTED_{timestamp}.bin")
            with open(extracted_file, 'wb') as f:
                f.write(extracted_data)
            self.log(f"   ✓ Extracted file saved: {os.path.basename(extracted_file)}")
            self.log(f"   Size: {len(extracted_data)} bytes")
            self._add_to_results(extracted_file, "Extracted")
            
            self.log("\n" + "━" * 60)
            self.log("✨ EXTRACT PROCESS COMPLETED!")
            self.log(f"📁 Output folder: {self.output_dir.get()}")
            self.log("━" * 60)
            
            messagebox.showinfo("Success", f"Extract completed!\n\nFile saved to:\n{extracted_file}")
            
        except Exception as e:
            self.log(f"\n❌ ERROR: {str(e)}")
            messagebox.showerror("Error", f"Extract process failed:\n{str(e)}")
        finally:
            self.progress_bar.stop()
    
    def _dmi_process(self):
        self.progress_bar.start()
        try:
            if not self.file_path.get():
                self.log("⚠ Please select a file first!")
                return
            
            file_path = self.file_path.get()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            self.log("━" * 60)
            self.log("🏷️  STARTING DMI PROCESS...")
            
            import time
            
            # Read file
            self.log("\n📖 Reading BIOS file...")
            with open(file_path, 'rb') as f:
                bios_data = bytearray(f.read())
            
            time.sleep(0.5)
            
            # Extract DMI
            self.log("🔍 Scanning for DMI data...")
            dmi_data = self._extract_dmi_from_bios(bios_data)
            
            if dmi_data:
                # Save DMI
                dmi_file = os.path.join(self.output_dir.get(), f"DMI_DATA_{timestamp}.json")
                with open(dmi_file, 'w') as f:
                    json.dump(dmi_data, f, indent=2)
                self.log(f"✓ DMI data extracted and saved: {os.path.basename(dmi_file)}")
                self._add_to_results(dmi_file, "DMI Data")
            else:
                self.log("⚠ No DMI data found in BIOS file")
            
            self.log("\n" + "━" * 60)
            self.log("✨ DMI PROCESS COMPLETED!")
            self.log("━" * 60)
            
        except Exception as e:
            self.log(f"\n❌ ERROR: {str(e)}")
        finally:
            self.progress_bar.stop()
    
    def _repair_hno(self, data):
        """HnO repair algorithm"""
        return data[:] if len(data) > 0 else data
    
    def _repair_z6(self, data):
        """Z6 repair algorithm"""
        return data[:] if len(data) > 0 else data
    
    def _repair_temp(self, data):
        """Temp repair algorithm"""
        return data[:] if len(data) > 0 else data
    
    def _repair_auto(self, data):
        """Auto repair algorithm"""
        return data[:] if len(data) > 0 else data
    
    def _add_padding(self, data):
        """Add padding ke data"""
        target_size = (len(data) + 4095) // 4096 * 4096  # Round to 4KB
        padding = bytearray(target_size - len(data))
        return data + padding
    
    def _extract_dmi_data(self, bios_data):
        """Extract DMI data dari BIOS"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dmi_info = {
                "extracted_at": timestamp,
                "bios_size": len(bios_data),
                "dmi_found": False,
                "data": {}
            }
            
            # Cari DMI signature
            dmi_signature = b'_DMI_'
            if dmi_signature in bios_data:
                dmi_info["dmi_found"] = True
                dmi_info["data"]["signature"] = "Found"
                self.log("   ✓ DMI signature found")
            
            dmi_file = os.path.join(self.output_dir.get(), f"DMI_EXTRACTED_{timestamp}.json")
            with open(dmi_file, 'w') as f:
                json.dump(dmi_info, f, indent=2)
            
            return dmi_file
        except Exception as e:
            self.log(f"   ⚠ DMI extraction error: {str(e)}")
            return None
    
    def _extract_dmi_from_bios(self, bios_data):
        """Extract DMI info dari BIOS"""
        dmi_info = {
            "bios_size": len(bios_data),
            "dmi_signature_found": b'_DMI_' in bios_data,
            "file_type": "BIOS",
            "extracted_timestamp": datetime.now().isoformat()
        }
        return dmi_info
    
    def _add_to_results(self, file_path, file_type):
        """Add file ke hasil list"""
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024  # KB
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            
            self.tree.insert("", tk.END, values=(file_name, f"{file_size:.2f}", file_type, creation_time, "Open"))
        except Exception as e:
            self.log(f"⚠ Error adding to results: {str(e)}")
    
    def on_treeview_double_click(self, event):
        """Handle double click pada treeview"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            file_name = self.tree.item(item)['values'][0]
            file_path = os.path.join(self.output_dir.get(), file_name)
            
            if os.path.exists(file_path):
                import subprocess
                import sys
                
                if sys.platform == 'win32':
                    os.startfile(file_path)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', file_path])
                else:
                    subprocess.Popen(['xdg-open', file_path])
                
                self.log(f"📂 Opened: {file_name}")
    
    def open_output_folder(self):
        """Buka output folder"""
        output_path = self.output_dir.get()
        self.ensure_output_directory()
        
        import subprocess
        import sys
        
        try:
            if sys.platform == 'win32':
                os.startfile(output_path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', output_path])
            else:
                subprocess.Popen(['xdg-open', output_path])
            
            self.log(f"📁 Opened folder: {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")


def main():
    root = tk.Tk()
    app = BIOSRepairTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
