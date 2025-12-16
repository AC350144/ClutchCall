import pyperclip
from threading import Thread, Lock
import time

class ClipboardManager:
    def __init__(self):
        self.last_copied = None
        self.running = True
        self.monitor_thread = Thread(target=self._monitor_clipboard)
        self.monitor_thread.daemon = True
        self.db = None
        self.lock = Lock()

    def _monitor_clipboard(self):
        while self.running:
            try:
                with self.lock:
                    current_content = pyperclip.paste().strip()
                    if not current_content:
                        continue
                    if current_content != self.last_copied:
                        print("current: ", current_content)
                        print("last: ", self.last_copied)
                        self.last_copied = current_content
                        
                        if self.db:
                            print("Adding to DB.")
                            self.db.add_entry(current_content)
            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
            time.sleep(1)

    def get_clipboard_content(self):
        """Get current clipboard content"""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Error accessing clipboard: {str(e)}")
            return None

    def set_clipboard_content(self, content: str):
        try:
            with self.lock:
                pyperclip.copy(content)
                self.last_copied = content.strip()
            return True
        except Exception as e:
            print(f"Error setting clipboard: {e}")
            return False

    def start_monitoring(self, db):
        """Start clipboard monitoring"""
        self.db = db
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop clipboard monitoring"""
        self.running = False

if __name__ == "__main__":
    # Simple test of clipboard manager
    cm = ClipboardManager()
    print("ClipboardManager initialized successfully")