import subprocess
import os
import platform

CREATE_NO_WINDOW = 0x08000000

class SubprocessCallPatcher:
    def __init__(self, extra_creationflags=0):
        self.original_call = subprocess.call
        self.extra_creationflags = extra_creationflags or CREATE_NO_WINDOW
        self.is_windows = platform.system() == "Windows"
        self._is_patched = False

    def _patched_call(self, *args, **kwargs):
        if self.is_windows:
            current_flags = kwargs.get("creationflags", 0)
            kwargs["creationflags"] = current_flags | self.extra_creationflags
            print(f"[SubprocessCallPatcher] Patched creationflags: {kwargs['creationflags']}")
        return self.original_call(*args, **kwargs)

    def patch(self):
        if not self._is_patched:
            subprocess.call = self._patched_call
            self._is_patched = True
            print("[SubprocessCallPatcher] subprocess.call has been patched.")

    def unpatch(self):
        if self._is_patched:
            subprocess.call = self.original_call
            self._is_patched = False
            print("[SubprocessCallPatcher] subprocess.call has been restored.")

    def __enter__(self):
        self.patch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unpatch()
