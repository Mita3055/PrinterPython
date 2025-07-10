#!/usr/bin/env python3

import cv2
import subprocess
import threading
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from datetime import datetime

# — CONFIG —
VIDEO_DEVICES = {
    'video0': {
        'node': '/dev/video0',
        'capture_resolution': (8000, 6000),
        'preview_resolution': (640, 480),
        'focus_value': 120,  # Manual focus start value
        'rotate': True,
        'name': 'Camera_0'
    },
    'video2': {
        'node': '/dev/video2',
        'capture_resolution': (1920, 1080),
        'preview_resolution': (640, 480),
        'focus_value': None, 
        'rotate': False,
        'name': 'Camera_2'
    }
}

# Preview settings
PREVIEW_FOURCC = cv2.VideoWriter_fourcc(*'YUYV')
PREVIEW_FPS = 20

# Focus range
FOCUS_MIN, FOCUS_MAX = 1, 127


def set_camera_focus(device_node: str, focus_value: int = None):
    """Set camera focus - manual if value provided, auto if None"""
    try:
        if focus_value is not None:
            # Manual focus
            subprocess.run([
                "v4l2-ctl", "-d", device_node,
                "--set-ctrl=focus_automatic_continuous=0",
                f"--set-ctrl=focus_absolute={focus_value}"
            ], check=False)
            print(f"[*] {device_node}: Manual focus set to {focus_value}")
        else:
            # Auto focus
            subprocess.run([
                "v4l2-ctl", "-d", device_node,
                "--set-ctrl=focus_automatic_continuous=1"
            ], check=False)
            print(f"[*] {device_node}: Auto focus enabled")
    except Exception as e:
        print(f"[!] Failed to set focus for {device_node}: {e}")


def capture_still_fswebcam(device_config: dict, app_instance=None, save_path=None):
    """Capture high-resolution still using fswebcam"""
    device_node = device_config['node']
    width, height = device_config['capture_resolution']
    camera_name = device_config['name']
    rotate = device_config['rotate']
    device_id = None
    for did, cfg in VIDEO_DEVICES.items():
        if cfg['node'] == device_node:
            device_id = did
            break

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{camera_name}_{timestamp}.jpg"
    if save_path:
        filename = os.path.join(save_path, filename)

    print(f"[*] Capturing from {device_node} ({width}x{height})...")
    if app_instance and device_id in getattr(app_instance, 'streams', {}):
        app_instance.streams[device_id].stop()
        time.sleep(0.5)

    try:
        cmd = [
            "fswebcam",
            "-d", device_node,
            "-r", f"{width}x{height}",
            "--jpeg", "95",
            "--no-banner",
            "--skip", "2",
            "-v",
            filename
        ]
        if rotate:
            cmd.extend(["--rotate", "180"])

        print(f"[*] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and os.path.exists(filename):
            size_mb = os.path.getsize(filename) / (1024*1024)
            print(f"[+] Photo saved: {os.path.abspath(filename)} ({size_mb:.1f} MB)")
            return True, filename
        else:
            print(f"[!] fswebcam failed for {device_node}: {result.stderr}")
            return False, f"fswebcam error: {result.stderr}"
    except subprocess.TimeoutExpired:
        print(f"[!] fswebcam timed out for {device_node}")
        return False, "Capture timed out"
    except Exception as e:
        print(f"[!] fswebcam exception for {device_node}: {e}")
        return False, str(e)
    finally:
        if app_instance and device_id in getattr(app_instance, 'streams', {}):
            time.sleep(0.3)
            new_stream = VideoStream(VIDEO_DEVICES[device_id])
            if new_stream.start():
                app_instance.streams[device_id] = new_stream
                if app_instance.root.winfo_exists():
                    app_instance.root.after(0, lambda: app_instance.status_labels[device_id].config(text="Preview restarted", fg="blue"))


def capture_still_opencv(device_config: dict, app_instance=None, save_path=None):
    """Capture still using OpenCV (alternative)"""
    device_node = device_config['node']
    width, height = device_config['capture_resolution']
    camera_name = device_config['name']
    rotate = device_config['rotate']
    device_id = None
    for did, cfg in VIDEO_DEVICES.items():
        if cfg['node'] == device_node:
            device_id = did
            break
    device_num = int(device_node.split('video')[-1])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{camera_name}_{timestamp}_opencv.jpg"
    if save_path:
        filename = os.path.join(save_path, filename)

    print(f"[*] OpenCV capture from {device_node} ({width}x{height})...")
    if app_instance and device_id in getattr(app_instance, 'streams', {}):
        app_instance.streams[device_id].stop()
        time.sleep(0.5)

    try:
        cap = cv2.VideoCapture(device_num, cv2.CAP_V4L2)
        if not cap.isOpened():
            return False, f"Failed to open {device_node}"
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        time.sleep(1)
        ret, frame = cap.read()
        cap.release()
        if ret and frame is not None:
            if rotate:
                frame = cv2.flip(frame, -1)
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            size_mb = os.path.getsize(filename) / (1024*1024)
            print(f"[+] Photo saved: {os.path.abspath(filename)} ({size_mb:.1f} MB)")
            return True, filename
        else:
            return False, "Failed to capture frame"
    except Exception as e:
        return False, str(e)
    finally:
        if app_instance and device_id in getattr(app_instance, 'streams', {}):
            time.sleep(0.3)
            new_stream = VideoStream(VIDEO_DEVICES[device_id])
            new_stream.start()





class VideoStream:
    def __init__(self, device_config):
        self.node = device_config['node']
        self.w, self.h = device_config['preview_resolution']
        self.rotate = device_config['rotate']
        self.device_num = int(self.node.split('video')[-1])
        self.cap = None
        self.frame = None
        self.running = False

    def start(self):
        try:
            self.cap = cv2.VideoCapture(self.device_num, cv2.CAP_V4L2)
            if not self.cap.isOpened(): return False
            self.cap.set(cv2.CAP_PROP_FOURCC, PREVIEW_FOURCC)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
            self.cap.set(cv2.CAP_PROP_FPS, PREVIEW_FPS)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.running = True
            threading.Thread(target=self._reader, daemon=True).start()
            return True
        except:
            return False

    def _reader(self):
        while self.running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    if self.rotate: frame = cv2.flip(frame, -1)
                    self.frame = frame
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.1)

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

class MultiCameraApp:
    def __init__(self, root):
        self.root = root
        root.title("Multi-Camera Still Capture System")
        root.geometry("1000x800")
        self.streams = {}
        self.active_devices = []
        self.save_folder = os.getcwd()
        self.timelapse_active = {}
        self.timelapse_threads = {}
        self._initialize_cameras()
        self._create_ui()
        self._start_previews()
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_loop()

    def _initialize_cameras(self):
        for did, cfg in VIDEO_DEVICES.items():
            if os.path.exists(cfg['node']) and os.access(cfg['node'], os.R_OK|os.W_OK):
                set_camera_focus(cfg['node'], cfg['focus_value'])
                self.active_devices.append(did)
                self.timelapse_active[did] = False

    def _create_ui(self):
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="Multi-Camera Still Capture System", font=('Arial',16,'bold')).pack()
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=5,fill=tk.X,padx=20)
        tk.Label(folder_frame,text="Save Folder:",font=('Arial',10,'bold')).pack(side=tk.LEFT)
        self.folder_label = tk.Label(folder_frame,text=self.save_folder,bg='white',relief=tk.SUNKEN,anchor='w')
        self.folder_label.pack(side=tk.LEFT,fill=tk.X,expand=True,padx=5)
        tk.Button(folder_frame,text="Browse",command=self.select_save_folder,bg='lightblue').pack(side=tk.RIGHT)
        self.camera_frames,self.video_labels,self.status_labels,self.timelapse_controls = {},{}, {},{}
        for did in self.active_devices:
            self._create_camera_panel(did,VIDEO_DEVICES[did])
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10,fill=tk.X,padx=20)
        self.capture_all_btn = tk.Button(control_frame,text="📸 Capture All Cameras",command=self.capture_all,bg='green',fg='white',font=('Arial',12,'bold'))
        self.capture_all_btn.pack(pady=5)
        self.global_status = tk.Label(control_frame,text="Ready",fg="green")
        self.global_status.pack(pady=5)

    def _create_camera_panel(self, device_id, config):
        frame = tk.LabelFrame(self.root, text=f"{config['name']} ({config['node']})", font=('Arial',10,'bold'))
        frame.pack(pady=5,padx=20,fill=tk.X)
        vf = tk.Frame(frame,bg='black',width=320,height=240); vf.pack(side=tk.LEFT,padx=10,pady=10); vf.pack_propagate(False)
        lbl = tk.Label(vf,text="Starting preview...",bg='black',fg='white'); lbl.pack(expand=True)
        self.video_labels[device_id] = lbl
        cf = tk.Frame(frame); cf.pack(side=tk.LEFT,fill=tk.BOTH,expand=True,padx=10,pady=10)
        info = f"Preview: {config['preview_resolution'][0]}x{config['preview_resolution'][1]}\n"
        info+=f"Capture: {config['capture_resolution'][0]}x{config['capture_resolution'][1]}\n"
        info+=f"Rotation: {'180°' if config['rotate'] else 'None'}"
        tk.Label(cf,text=info,justify=tk.LEFT,font=('Arial',9)).pack(anchor='w')
        # Focus Slider
        sf = tk.Frame(cf); sf.pack(fill=tk.X,pady=5)
        tk.Label(sf,text="Focus:",font=('Arial',8)).pack(anchor='w')
        slider = tk.Scale(sf, from_=FOCUS_MAX, to=FOCUS_MIN, orient=tk.HORIZONTAL, length=200,
                          command=lambda v, n=config['node']: set_camera_focus(n,int(v)))
        init = config['focus_value'] if config['focus_value'] is not None else FOCUS_MAX//2
        slider.set(init); slider.pack(fill=tk.X)
        btn = tk.Button(cf,text=f"📷 Capture {config['name']}",command=lambda d=device_id: self.capture_single(d),bg='blue',fg='white')
        btn.pack(pady=5,fill=tk.X)
        # Time-lapse controls & status
        tlf = tk.LabelFrame(cf,text="Time-lapse",font=('Arial',9,'bold')); tlf.pack(pady=5,fill=tk.X)
        ivf = tk.Frame(tlf); ivf.pack(fill=tk.X,padx=5,pady=2)
        tk.Label(ivf,text="Interval (seconds):",font=('Arial',8)).pack(side=tk.LEFT)
        iv = tk.StringVar(value="30")
        tk.Entry(ivf,textvariable=iv,width=8).pack(side=tk.RIGHT)
        dvf = tk.Frame(tlf); dvf.pack(fill=tk.X,padx=5,pady=2)
        tk.Label(dvf,text="Duration (seconds):",font=('Arial',8)).pack(side=tk.LEFT)
        dv = tk.StringVar(value="600")
        tk.Entry(dvf,textvariable=dv,width=8).pack(side=tk.RIGHT)
        tbtn=tk.Button(tlf,text="🎬 Start Time-lapse",bg='purple',fg='white',font=('Arial',8),command=lambda d=device_id: self.toggle_timelapse(d))
        tbtn.pack(pady=3,fill=tk.X)
        tstat=tk.Label(tlf,text="Ready",fg="green",font=('Arial',8)); tstat.pack()
        self.timelapse_controls[device_id]={'interval_var':iv,'duration_var':dv,'button':tbtn,'status':tstat}
        slbl=tk.Label(cf,text="Initializing...",fg="orange"); slbl.pack(anchor='w'); self.status_labels[device_id]=slbl
        self.camera_frames[device_id]=frame

    def select_save_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_folder,title="Select Save Folder")
        if folder: self.save_folder=folder; self.folder_label.config(text=folder)

    def toggle_timelapse(self, device_id):
        if self.timelapse_active[device_id]: self.stop_timelapse(device_id)
        else: self.start_timelapse(device_id)

    def start_timelapse(self, device_id):
        controls=self.timelapse_controls[device_id]
        try:
            interval=float(controls['interval_var'].get()); duration=float(controls['duration_var'].get())
            if interval<=0 or duration<=0 or interval>duration:
                messagebox.showerror("Error","Invalid interval/duration")
                return
            cfg=VIDEO_DEVICES[device_id]
            ts=datetime.now().strftime("%Y%m%d_%H%M%S")
            folder=os.path.join(self.save_folder,f"timelapse_{cfg['name']}_{ts}"); os.makedirs(folder,exist_ok=True)
            self.timelapse_active[device_id]=True
            controls['button'].config(text="⏹ Stop Time-lapse",bg='red')
            controls['status'].config(text="Starting...",fg="orange")
            t=threading.Thread(target=self._timelapse_worker,args=(device_id,interval,duration,folder),daemon=True)
            t.start(); self.timelapse_threads[device_id]=t
        except ValueError:
            messagebox.showerror("Error","Invalid interval or duration values")

    def stop_timelapse(self, device_id):
        self.timelapse_active[device_id]=False
        c=self.timelapse_controls[device_id]
        c['button'].config(text="🎬 Start Time-lapse",bg='purple')
        c['status'].config(text="Stopped",fg='red')

    def _timelapse_worker(self, device_id,interval,duration,save_folder):
        start=time.time(); count=0
        while self.timelapse_active[device_id] and time.time()-start<duration:
            if self.root.winfo_exists():
                rem=duration-(time.time()-start)
                self.root.after(0,lambda: self.timelapse_controls[device_id]['status'].config(text=f"Photo {count+1} | {rem:.0f}s left",fg="blue"))
            success,fn=capture_still_fswebcam(VIDEO_DEVICES[device_id],self,save_folder)
            if not success: success,fn=capture_still_opencv(VIDEO_DEVICES[device_id],self,save_folder)
            if success: count+=1
            next_t=start+count*interval; sleep=next_t-time.time()
            if sleep>0: time.sleep(sleep)
        if self.timelapse_active[device_id]:
            if self.root.winfo_exists():
                self.root.after(0,lambda: self.timelapse_controls[device_id]['status'].config(text=f"Completed! {count} photos",fg="green"))
                self.root.after(0,lambda: self.timelapse_controls[device_id]['button'].config(text="🎬 Start Time-lapse",bg='purple'))
        self.timelapse_active[device_id]=False

    def _start_previews(self):
        for did in self.active_devices:
            stream=VideoStream(VIDEO_DEVICES[did])
            if stream.start():
                self.streams[did]=stream
                self.status_labels[did].config(text="Preview active",fg="green")
            else:
                self.status_labels[did].config(text="Preview failed",fg="red")

    def capture_single(self, did):
        self.status_labels[did].config(text="Capturing...",fg="orange")
        threading.Thread(target=self._do_single_capture,args=(did,),daemon=True).start()

    def _do_single_capture(self, did):
        success, msg=capture_still_fswebcam(VIDEO_DEVICES[did],self,self.save_folder)
        if not success: success, msg=capture_still_opencv(VIDEO_DEVICES[did],self,self.save_folder)
        if self.root.winfo_exists():
            text=f"✓ Saved: {os.path.basename(msg)}" if success else f"✗ Failed: {msg}"
            color="green" if success else "red"
            self.root.after(0,lambda: self.status_labels[did].config(text=text,fg=color))

    def capture_all(self):
        self.global_status.config(text="Capturing from all cameras...",fg="orange")
        self.capture_all_btn.config(state="disabled")
        threading.Thread(target=self._do_all_captures,daemon=True).start()

    def _do_all_captures(self):
        threads=[]
        for d in self.active_devices:
            t=threading.Thread(target=self._do_single_capture,args=(d,))
            t.start(); threads.append(t)
        for t in threads: t.join()
        if self.root.winfo_exists():
            self.root.after(0,lambda: self.global_status.config(text="All captures completed",fg="green"))
            self.root.after(0,lambda: self.capture_all_btn.config(state="normal"))

    def update_loop(self):
        if not self.root.winfo_exists(): return
        for did,stream in self.streams.items():
            if stream.frame is not None:
                try:
                    img=cv2.cvtColor(stream.frame,cv2.COLOR_BGR2RGB)
                    img=cv2.resize(img,(320,240))
                    imgtk=ImageTk.PhotoImage(Image.fromarray(img))
                    lbl=self.video_labels[did]; lbl.imgtk=imgtk; lbl.configure(image=imgtk)
                except: pass
        self.root.after(50,self.update_loop)

    def on_close(self):
        for d in self.active_devices:
            self.timelapse_active[d]=False
        for s in self.streams.values(): s.stop()
        time.sleep(0.1)
        self.root.destroy()


def check_dependencies():
    ok=True
    try:
        subprocess.run(["fswebcam","--version"],capture_output=True,text=True)
    except FileNotFoundError:
        print("[!] fswebcam not found. Install: sudo apt install fswebcam")
        ok=False
    try:
        subprocess.run(["v4l2-ctl","--version"],capture_output=True,check=True)
    except:
        print("[!] v4l2-ctl not found. Install: sudo apt install v4l-utils")
        ok=False
    return ok

if __name__ == "__main__":
    print("=== Multi-Camera Still Capture System ===")
    for did,cfg in VIDEO_DEVICES.items():
        print(f"  {cfg['name']}: {cfg['node']} Capture: {cfg['capture_resolution'][0]}x{cfg['capture_resolution'][1]} Focus: {'Manual' if cfg['focus_value'] else 'Auto'}")
    if not check_dependencies(): exit(1)
    available=0
    for did,cfg in VIDEO_DEVICES.items():
        if os.path.exists(cfg['node']) and os.access(cfg['node'],os.R_OK|os.W_OK):
            available+=1
        else:
            print(f"[!] Cannot access {cfg['node']}")
    if available==0:
        print("No cameras available!")
        os.system("ls /dev/video* 2>/dev/null || echo 'No video devices found'")
        exit(1)
    root=tk.Tk(); app=MultiCameraApp(root); root.mainloop()
