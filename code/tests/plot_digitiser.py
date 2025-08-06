import os
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import numpy as np
import csv
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DigitiserGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Plot Digitiser")
        self.img = None
        self.x_scale = None
        self.y_scale = None
        self.x_points = []
        self.y_points = []
        self.curves = []
        self.current_curve = []
        self.triple_click_count = 0

        # Layout frames
        self.left_frame = tk.Frame(master)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame = tk.Frame(master)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.left_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Controls
        self.load_btn = tk.Button(self.right_frame, text="Load Image", command=self.load_image)
        self.load_btn.pack(pady=5)
        self.x_btn = tk.Button(self.right_frame, text="Set X Scale", command=self.set_x_scale, state=tk.DISABLED)
        self.x_btn.pack(pady=5)
        self.y_btn = tk.Button(self.right_frame, text="Set Y Scale", command=self.set_y_scale, state=tk.DISABLED)
        self.y_btn.pack(pady=5)
        self.curve_btn = tk.Button(self.right_frame, text="Digitise Curve", command=self.digitise_curve, state=tk.DISABLED)
        self.curve_btn.pack(pady=5)
        self.export_btn = tk.Button(self.right_frame, text="Export CSV", command=self.export_csv, state=tk.DISABLED)
        self.export_btn.pack(pady=5)
        self.crop_btn = tk.Button(self.right_frame, text="Crop Image", command=self.crop_image, state=tk.DISABLED)
        self.crop_btn.pack(pady=5)
        self.plot_btn = tk.Button(self.right_frame, text="Plot Curves", command=self.plot, state=tk.NORMAL)
        self.plot_btn.pack(pady=5)
        self.save_btn = tk.Button(self.right_frame, text="Save Session", command=self.save_session)
        self.save_btn.pack(pady=5)
        self.load_btn_session = tk.Button(self.right_frame, text="Load Session", command=self.load_session)
        self.load_btn_session.pack(pady=5)

        self.status = tk.Label(self.right_frame, text="Load an image to start.")
        self.status.pack(pady=10)

        self.cid = None

    def load_image(self):
        img_path = filedialog.askopenfilename(title="Select image file")
        if not img_path:
            return
        self.img = mpimg.imread(img_path)
        self.ax.clear()
        self.ax.imshow(self.img)
        self.ax.set_title("Select two points on X axis")
        self.canvas.draw()
        # Reset session data
        self.x_points = []
        self.y_points = []
        self.curves = []
        self.current_curve = []
        self.x_scale = None
        self.y_scale = None
        
        self.x_btn.config(state=tk.NORMAL)
        self.y_btn.config(state=tk.DISABLED)
        self.curve_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        self.crop_btn.config(state=tk.NORMAL)
        self.plot_btn.config(state=tk.NORMAL)
        
        self.status.config(text="Click 'Set X Scale' and select two points on X axis.")

    def set_x_scale(self):
        self.status.config(text="Select two points on X axis.")
        self.x_points = []
        self.disconnect()
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click_x)

    def on_click_x(self, event):
        if event.inaxes != self.ax:
            return
        self.x_points.append((event.xdata, event.ydata))
        self.ax.plot(event.xdata, event.ydata, 'ro')
        self.canvas.draw()
        if len(self.x_points) == 2:
            self.disconnect()
            scale = simpledialog.askfloat("X Scale", "Enter X axis scale difference between selected points:")
            if scale is None:
                return
            self.x_scale = scale / (self.x_points[1][0] - self.x_points[0][0])
            self.status.config(text="Click 'Set Y Scale' and select two points on Y axis.")
            self.y_btn.config(state=tk.NORMAL)

    def set_y_scale(self):
        self.status.config(text="Select two points on Y axis.")
        self.y_points = []
        self.disconnect()
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click_y)

    def on_click_y(self, event):
        if event.inaxes != self.ax:
            return
        self.y_points.append((event.xdata, event.ydata))
        self.ax.plot(event.xdata, event.ydata, 'go')
        self.canvas.draw()
        if len(self.y_points) == 2:
            self.disconnect()
            scale = simpledialog.askfloat("Y Scale", "Enter Y axis scale difference between selected points:")
            if scale is None:
                return
            self.y_scale = scale / (self.y_points[1][1] - self.y_points[0][1])
            self.status.config(text="Click 'Digitise Curve' to start curve selection.")
            self.curve_btn.config(state=tk.NORMAL)

    def digitise_curve(self):
        self.status.config(text="Select curve points (single click). Double click to finish curve.")
        self.current_curve = []
        self.disconnect()
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_curve_click)

    def on_curve_click(self, event):
        if event.inaxes != self.ax:
            return
        if event.dblclick:
            self.disconnect()
            self.curves.append(self.current_curve)
            self.status.config(text="Curve finished. You can export CSV or digitise another curve.")
            self.export_btn.config(state=tk.NORMAL)
            self.curve_btn.config(state=tk.NORMAL)
        else:
            self.current_curve.append((event.xdata, event.ydata))
            self.ax.plot(event.xdata, event.ydata, 'bx')
            self.canvas.draw()

    def export_csv(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", title="Save CSV")
        if not save_path:
            return
        with open(save_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['x', 'y'])
            for curve in self.curves:
                for x, y in curve:
                    x_real = (x - self.x_points[0][0]) * self.x_scale
                    y_real = (y - self.y_points[0][1]) * self.y_scale
                    writer.writerow([x_real, y_real])
        
        # print path to console
        print(f"CSV saved to {save_path}")

    def crop_image(self):
        if self.img is None:
            messagebox.showerror("Error", "No image loaded.")
            return
        
        self.status.config(text="Click and drag to select crop area.")
        self.disconnect()
        
        # Variables to track the rectangle
        self.crop_rect = None
        self.crop_start_x = None
        self.crop_start_y = None
        
        def on_press(event):
            if event.inaxes != self.ax:
                return
            self.crop_start_x = event.xdata
            self.crop_start_y = event.ydata
        
        def on_motion(event):
            if self.crop_start_x is None:
                return
            if event.inaxes != self.ax:
                return
            
            if self.crop_rect:
                self.crop_rect.remove()
            width = event.xdata - self.crop_start_x
            height = event.ydata - self.crop_start_y
            self.crop_rect = plt.Rectangle((self.crop_start_x, self.crop_start_y), width, height,
                                            linewidth=1, edgecolor='r', facecolor='none')
            self.ax.add_patch(self.crop_rect)
            self.canvas.draw_idle()
        
        def on_release(event):
            if self.crop_start_x is None or event.inaxes != self.ax:
                return
            
            # Get the final coordinates
            x1 = min(self.crop_start_x, event.xdata)
            y1 = min(self.crop_start_y, event.ydata)
            x2 = max(self.crop_start_x, event.xdata)
            y2 = max(self.crop_start_y, event.ydata)
            
            # Convert to integer pixel coordinates
            x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
            
            # Make sure coordinates are within image bounds
            height, width = self.img.shape[:2]
            x1 = max(0, min(width - 1, x1))
            y1 = max(0, min(height - 1, y1))
            x2 = max(0, min(width, x2))
            y2 = max(0, min(height, y2))
            
            # Crop the image
            cropped_img = self.img[y1:y2, x1:x2]
            self.img = cropped_img
            
            # Update display
            self.ax.clear()
            self.ax.imshow(self.img)
            self.canvas.draw()
            self.status.config(text="Image cropped. You can set scales or digitise curves again.")
            
            # Reset scale data as it's no longer valid
            self.x_scale = None
            self.y_scale = None
            self.x_points = []
            self.y_points = []
            
            # Disconnect the crop event handlers
            self.canvas.mpl_disconnect(self.crop_cid_press)
            self.canvas.mpl_disconnect(self.crop_cid_motion)
            self.canvas.mpl_disconnect(self.crop_cid_release)
        
        # Connect the event handlers
        self.crop_cid_press = self.canvas.mpl_connect('button_press_event', on_press)
        self.crop_cid_motion = self.canvas.mpl_connect('motion_notify_event', on_motion)
        self.crop_cid_release = self.canvas.mpl_connect('button_release_event', on_release)
    
    def plot(self):
        
        # add a new curve plotted from all stored curves
        if not self.curves:
            messagebox.showerror("Error", "No curves to plot.")
            return
        
        self.ax.clear()
        for curve in self.curves:
            x_data = [x for x, y in curve]
            y_data = [y for x, y in curve]
            self.ax.plot(x_data, y_data, 'bx-')
        self.ax.set_title("Digitised Curves")
    
    def save_session(self):
        
        # create next in line session starting with digitizer.session
        save_path = filedialog.asksaveasfilename(
            title="Select save location",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        with open(save_path, 'w') as f:
            f.write(f"x_scale: {self.x_scale}\n")
            f.write(f"y_scale: {self.y_scale}\n")
            f.write("x_points:\n")
            for x, y in self.x_points:
                f.write(f"{x},{y}\n")
            f.write("y_points:\n")
            for x, y in self.y_points:
                f.write(f"{x},{y}\n")
            f.write("curves:\n")
            for curve in self.curves:
                for x, y in curve:
                    f.write(f"{x},{y}\n")
        
        print(f"Session saved to {save_path}")
    
    def load_session(self):
        session_path = filedialog.askopenfilename(title="Select session file", filetypes=[("Session files", "*.txt")])
        if not session_path:
            return
        
        with open(session_path, 'r') as f:
            lines = f.readlines()
        
        self.x_scale = None
        self.y_scale = None
        self.x_points = []
        self.y_points = []
        self.curves = []
        
        for line in lines:
            if line.startswith("x_scale:"):
                self.x_scale = float(line.split(":")[1].strip())
            elif line.startswith("y_scale:"):
                self.y_scale = float(line.split(":")[1].strip())
            elif line.startswith("x_points:"):
                continue
            elif line.startswith("y_points:"):
                continue
            elif line.startswith("curves:"):
                continue
            else:
                x, y = map(float, line.strip().split(','))
                if len(self.x_points) < 2:
                    self.x_points.append((x, y))
                elif len(self.y_points) < 2:
                    self.y_points.append((x, y))
                else:
                    self.curves.append([(x, y)])
        
        # Update the GUI state
        if self.img is not None:
            self.ax.clear()
            self.ax.imshow(self.img)
            self.canvas.draw()
        
        if self.x_scale is not None and self.y_scale is not None:
            self.status.config(text="Session loaded. You can digitise curves or export CSV.")
            self.export_btn.config(state=tk.NORMAL)
    
    def disconnect(self):
        if self.cid is not None:
            self.canvas.mpl_disconnect(self.cid)
            self.cid = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitiserGUI(root)
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
