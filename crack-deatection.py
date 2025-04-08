import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading

#  UI
class CrackDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crack Detection Tool")
        self.root.geometry("1200x700")
        
        # Variables
        self.input_path = ""
        self.output_path = ""
        self.threshold1 = tk.IntVar(value=50)  # Lower threshold for Canny
        self.threshold2 = tk.IntVar(value=150)  # Upper threshold for Canny
        self.min_area = tk.IntVar(value=100)
        self.original_image = None
        self.result_image = None
        self.is_processing = False
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (controls)
        left_panel = ttk.LabelFrame(main_frame, text="Controls")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # File selection
        ttk.Label(left_panel, text="Input Image:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_path_label = ttk.Label(left_panel, text="No file selected", width=25)
        self.input_path_label.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(left_panel, text="Browse...", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(left_panel, text="Output Path:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_path_label = ttk.Label(left_panel, text="No path selected", width=25)
        self.output_path_label.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(left_panel, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Parameters
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=10)
        
        ttk.Label(left_panel, text="Canny Lower Threshold:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        threshold1_slider = ttk.Scale(left_panel, from_=0, to=255, variable=self.threshold1, orient=tk.HORIZONTAL)
        threshold1_slider.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(left_panel, textvariable=self.threshold1).grid(row=3, column=2, padx=5, pady=5)
        
        ttk.Label(left_panel, text="Canny Upper Threshold:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        threshold2_slider = ttk.Scale(left_panel, from_=0, to=255, variable=self.threshold2, orient=tk.HORIZONTAL)
        threshold2_slider.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(left_panel, textvariable=self.threshold2).grid(row=4, column=2, padx=5, pady=5)
        
        ttk.Label(left_panel, text="Minimum Area:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        area_slider = ttk.Scale(left_panel, from_=10, to=1000, variable=self.min_area, orient=tk.HORIZONTAL)
        area_slider.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(left_panel, textvariable=self.min_area).grid(row=5, column=2, padx=5, pady=5)
        
        # Buttons
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).grid(row=6, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=10)
        
        self.detect_button = ttk.Button(left_panel, text="Detect Cracks", command=self.start_detection)
        self.detect_button.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        
        self.save_button = ttk.Button(left_panel, text="Save Result", command=self.save_result, state=tk.DISABLED)
        self.save_button.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Button(left_panel, text="Batch Process", command=self.batch_process).grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(left_panel, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=10, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        # Right panel (image display)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Original image
        original_frame = ttk.LabelFrame(right_panel, text="Original Image")
        original_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.original_canvas = tk.Canvas(original_frame, bg="lightgray")
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Result image
        result_frame = ttk.LabelFrame(right_panel, text="Detected Cracks")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.result_canvas = tk.Canvas(result_frame, bg="lightgray")
        self.result_canvas.pack(fill=tk.BOTH, expand=True)
    
    def browse_input(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.input_path = path
            self.input_path_label.config(text=os.path.basename(path))
            self.load_image(path)
    
    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path = path
            self.output_path_label.config(text=os.path.basename(path))
    
    def load_image(self, path):
        try:
            image = cv2.imread(path)
            if image is None:
                messagebox.showerror("Error", f"Could not read image: {path}")
                return
                
            self.original_image = image
            self.display_image(image, self.original_canvas)
            
            self.result_canvas.delete("all")
            self.save_button.config(state=tk.DISABLED)
            self.status_var.set("Image loaded. Ready to detect cracks.")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading image: {str(e)}")
    
    def display_image(self, cv_image, canvas):
        canvas.delete("all")
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
        
        img_height, img_width = cv_image.shape[:2]
        ratio = min(canvas_width/img_width, canvas_height/img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        resized = cv2.resize(rgb_image, (new_width, new_height))
        pil_image = Image.fromarray(resized)
        tk_image = ImageTk.PhotoImage(image=pil_image)
        
        canvas.image = tk_image
        canvas.create_image(canvas_width//2, canvas_height//2, image=tk_image)

#     detection logic 
    def detect_cracks(self, image_path):
        
        original = cv2.imread(image_path)
        if original is None:
            return None, None
        
        result = original.copy()
        
        # Converting to grayscale
        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        
        # Applying  Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny edge detection
        edges = cv2.Canny(blurred, self.threshold1.get(), self.threshold2.get())
        
        # Dilate to connect edges , basicaly highliting the detected edge 
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Finding contours 
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours based on area
        crack_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > self.min_area.get()]
        
        # Draw contours on result image
        cv2.drawContours(result, crack_contours, -1, (0, 0, 255), 2)
        
        return original, result, len(crack_contours)
    
#   UI   
    def start_detection(self):
        if not self.input_path:
            messagebox.showwarning("Warning", "Please select an input image first.")
            return
        
        if self.is_processing:
            return
            
        self.is_processing = True
        self.detect_button.config(state=tk.DISABLED)
        self.status_var.set("Processing... Please wait.")
        
        threading.Thread(target=self.run_detection).start()
    
    def run_detection(self):
        try:
            _, result, count = self.detect_cracks(self.input_path)
            
            if result is not None:
                self.result_image = result
                self.display_image(result, self.result_canvas)
                self.save_button.config(state=tk.NORMAL)
                self.status_var.set(f"Detection complete. Found {count} crack regions.")
            else:
                self.status_var.set("Error processing image.")
        except Exception as e:
            messagebox.showerror("Error", f"Error during detection: {str(e)}")
            self.status_var.set("Ready")
        finally:
            self.detect_button.config(state=tk.NORMAL)
            self.is_processing = False
    
    def save_result(self):
        if self.result_image is None:
            messagebox.showwarning("Warning", "No result to save.")
            return
            
        filetypes = [("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=filetypes)
        
        if path:
            try:
                cv2.imwrite(path, self.result_image)
                self.status_var.set(f"Result saved to {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving image: {str(e)}")
    
    def batch_process(self):
        if not self.output_path:
            messagebox.showwarning("Warning", "Please select an output directory first.")
            return
            
        input_dir = filedialog.askdirectory(title="Select Directory with Images")
        if not input_dir:
            return
            
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = [f for f in os.listdir(input_dir) if os.path.splitext(f.lower())[1] in image_extensions]
        
        if not image_files:
            messagebox.showinfo("Info", "No image files found in the selected directory.")
            return
            
        if not messagebox.askyesno("Confirm", f"Process {len(image_files)} images?"):
            return
            
        self.is_processing = True
        self.detect_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.status_var.set("Batch processing started...")
        
        threading.Thread(target=self.run_batch_process, args=(input_dir, image_files)).start()
    
    def run_batch_process(self, input_dir, image_files):
        try:
            processed = 0
            total = len(image_files)
            
            for image_file in image_files:
                input_path = os.path.join(input_dir, image_file)
                output_path = os.path.join(self.output_path, f"detected_{image_file}")
                
                self.status_var.set(f"Processing {processed+1}/{total}: {image_file}")
                
                _, result, _ = self.detect_cracks(input_path)
                if result is not None:
                    cv2.imwrite(output_path, result)
                
                processed += 1
                
            self.status_var.set(f"Batch processing complete. Processed {processed}/{total} images.")
            messagebox.showinfo("Complete", f"Batch processing complete. Processed {processed}/{total} images.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during batch processing: {str(e)}")
            self.status_var.set("Batch processing error.")
        finally:
            self.detect_button.config(state=tk.NORMAL)
            self.is_processing = False

def main():
    root = tk.Tk()
    app = CrackDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
