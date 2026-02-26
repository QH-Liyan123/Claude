"""
Voice Input Tool - Background mode
Hold CapsLock to speak, release to auto-type text.
Say "关闭语音" or "stop voice" to exit.

Created by Leon Li(李岩) - 20260226
"""

import ctypes
import os
import queue
import threading
import time
import tkinter as tk

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from pynput import keyboard
from pynput.keyboard import Controller as KbController, Key

# Configuration
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(_SCRIPT_DIR, "voice_input.log")
PID_FILE = os.path.join(_SCRIPT_DIR, "voice_input.pid")

# Model configuration - downloads from HuggingFace on first run
# Options: "tiny", "base", "small", "medium", "large-v3"
MODEL_SIZE = os.environ.get("VOICE_MODEL_SIZE", "small")

SAMPLE_RATE = 16000
HOLD_THRESHOLD = 0.25  # seconds to hold CapsLock before recording starts
MIN_RECORDING_TIME = 0.5  # minimum recording duration in seconds


def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            ts = time.strftime("%H:%M:%S")
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


def cleanup_pid():
    try:
        os.remove(PID_FILE)
    except Exception:
        pass


def shutdown(reason=""):
    log(f"Shutting down. {reason}")
    cleanup_pid()
    os._exit(0)


def drain_queue(q):
    """Remove all pending items from a queue."""
    while not q.empty():
        try:
            q.get_nowait()
        except Exception:
            break


def is_capslock_key(key):
    """Check whether the key is CapsLock."""
    return key == Key.caps_lock


class RecordingIndicator:
    """Small floating window that shows recording status."""

    def __init__(self):
        self.root = None
        self.label = None
        self.visible = False
        self._lock = threading.Lock()

        # Start tkinter in its own thread
        self._thread = threading.Thread(target=self._run_tk, daemon=True)
        self._thread.start()

        # Wait for initialization
        time.sleep(0.2)

    def _run_tk(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Start hidden

        # Configure window
        self.root.overrideredirect(True)  # No title bar
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.9)  # Slightly transparent

        # Create label
        self.label = tk.Label(
            self.root,
            text="🎤 Recording...",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#e74c3c",  # Red background
            padx=20,
            pady=10
        )
        self.label.pack()

        # Position at top-center of screen
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        window_width = self.label.winfo_reqwidth() + 40
        x = (screen_width - window_width) // 2
        y = 50  # Near top of screen
        self.root.geometry(f"+{x}+{y}")

        # Run event loop
        self.root.mainloop()

    def show(self):
        with self._lock:
            if not self.visible and self.root:
                self.root.after(0, self._do_show)
                self.visible = True

    def hide(self):
        with self._lock:
            if self.visible and self.root:
                self.root.after(0, self._do_hide)
                self.visible = False

    def update_text(self, text):
        if self.root and self.label:
            self.root.after(0, lambda: self.label.config(text=text))

    def _do_show(self):
        self.label.config(text="🎤 Recording...", bg="#e74c3c")
        self.root.deiconify()

    def _do_hide(self):
        self.root.withdraw()


audio_queue = queue.Queue()
kb_controller = KbController()
shutdown_event = threading.Event()
indicator = None  # Will be initialized in main()

# Thread-safe state
state_lock = threading.Lock()
capslock_pressed = False
capslock_press_time = 0.0
is_recording = False
recording_start_time = 0.0


def audio_callback(indata, frames, time_info, status):
    with state_lock:
        recording = is_recording
    if recording:
        audio_queue.put(bytes(indata))


def _configure_ctypes():
    """Set up ctypes function signatures for 64-bit compatibility (once)."""
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p


_configure_ctypes()

_CF_UNICODETEXT = 13
_GMEM_MOVEABLE = 0x0002


def type_text(text):
    """Type text using Windows clipboard API + Ctrl+V."""
    if not text:
        return

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Open clipboard with retry
    for _ in range(5):
        if user32.OpenClipboard(0):
            break
        time.sleep(0.05)
    else:
        log("Failed to open clipboard")
        return

    try:
        user32.EmptyClipboard()

        # Encode text as UTF-16
        text_bytes = (text + '\0').encode('utf-16-le')
        h_mem = kernel32.GlobalAlloc(_GMEM_MOVEABLE, len(text_bytes))
        if not h_mem:
            log(f"GlobalAlloc failed: {ctypes.get_last_error()}")
            return

        p_mem = kernel32.GlobalLock(h_mem)
        if not p_mem:
            log(f"GlobalLock failed: {ctypes.get_last_error()}")
            kernel32.GlobalFree(h_mem)
            return

        ctypes.memmove(p_mem, text_bytes, len(text_bytes))
        kernel32.GlobalUnlock(h_mem)

        result = user32.SetClipboardData(_CF_UNICODETEXT, h_mem)
        if not result:
            log(f"SetClipboardData failed: {ctypes.get_last_error()}")
            kernel32.GlobalFree(h_mem)
            return
    finally:
        user32.CloseClipboard()

    # Small delay then paste
    time.sleep(0.05)
    kb_controller.press(Key.ctrl)
    kb_controller.press('v')
    kb_controller.release('v')
    kb_controller.release(Key.ctrl)
    time.sleep(0.05)
    log(f"Typed: {text[:20]}...")


def on_key_press(key):
    global capslock_pressed, capslock_press_time

    if is_capslock_key(key):
        with state_lock:
            if not capslock_pressed:
                capslock_pressed = True
                capslock_press_time = time.time()


def _cancel_recording():
    """Stop recording and discard buffered audio."""
    global is_recording
    is_recording = False
    drain_queue(audio_queue)


def on_key_release(key):
    global capslock_pressed, is_recording, recording_start_time

    if not is_capslock_key(key):
        # Non-CapsLock key released while CapsLock held = keyboard shortcut, cancel recording
        with state_lock:
            if capslock_pressed and is_recording:
                _cancel_recording()
                if indicator:
                    indicator.hide()
        return

    # CapsLock key released
    with state_lock:
        capslock_pressed = False

        if not is_recording:
            return

        rec_duration = time.time() - recording_start_time
        is_recording = False

    if rec_duration >= MIN_RECORDING_TIME:
        log(f"Recording stopped ({rec_duration:.2f}s)")
        if indicator:
            indicator.update_text("⏳ Processing...")
        audio_queue.put(None)
    else:
        log(f"Recording too short ({rec_duration:.2f}s)")
        drain_queue(audio_queue)
        if indicator:
            indicator.hide()


def capslock_hold_watcher():
    """Watch for CapsLock held > threshold to start recording."""
    global is_recording, recording_start_time

    while not shutdown_event.is_set():
        should_start = False

        with state_lock:
            if capslock_pressed and not is_recording:
                if (time.time() - capslock_press_time) >= HOLD_THRESHOLD:
                    is_recording = True
                    recording_start_time = time.time()
                    should_start = True
                    drain_queue(audio_queue)

        if should_start:
            log("Recording started")
            if indicator:
                indicator.show()

        time.sleep(0.03)


# Stop phrases - say any of these to exit
STOP_PHRASES = {"关闭语音", "停止语音", "退出语音", "停止录音", "关闭录音", "stop voice", "exit voice"}


def recognize_worker(model):
    """Process audio chunks from the queue and run speech recognition."""
    buffer = bytearray()

    while not shutdown_event.is_set():
        try:
            data = audio_queue.get(timeout=1)
        except queue.Empty:
            continue

        # Accumulate audio data until we receive the end-of-segment sentinel (None)
        if data is not None:
            buffer.extend(data)
            continue

        text = ""
        if buffer:
            # Convert int16 bytes to float32 numpy array (Whisper expects float32 in [-1, 1])
            audio_array = np.frombuffer(bytes(buffer), dtype=np.int16).astype(np.float32) / 32768.0
            segments, _ = model.transcribe(
                audio_array, language="zh", beam_size=5,
                initial_prompt="以下是普通话的句子，包含标点符号。"
            )
            text = "".join(seg.text for seg in segments).strip()

        if indicator:
            indicator.hide()

        if not text:
            log("No speech detected")
        else:
            # Strip punctuation for stop phrase check
            clean = text.rstrip("。，、！？.,!? ").lower()
            if clean in STOP_PHRASES:
                log("Stop phrase detected")
                shutdown("Stop phrase")
            else:
                log(f"Recognized: {text}")
                time.sleep(0.05)
                type_text(text)

        buffer.clear()


def main():
    global indicator

    write_pid()
    log("=" * 40)
    log(f"Voice Input started (PID: {os.getpid()})")
    log("=" * 40)

    log("Creating indicator window...")
    indicator = RecordingIndicator()
    log("Indicator ready")

    log(f"Loading Whisper model '{MODEL_SIZE}' (will download on first run)...")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    log("Model loaded")

    # Start background threads
    threading.Thread(target=recognize_worker, args=(model,), daemon=True).start()
    threading.Thread(target=capslock_hold_watcher, daemon=True).start()
    keyboard.Listener(on_press=on_key_press, on_release=on_key_release).start()

    log("Ready - Hold CapsLock to speak")

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=4000, dtype="int16",
                           channels=1, callback=audio_callback):
        try:
            while not shutdown_event.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    shutdown("Normal exit")


if __name__ == "__main__":
    main()
