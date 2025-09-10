import subprocess
import threading
import logging
import sys


class redirect_all_output_to_file:
    def __init__(self, log_file="anvil_app_output.log", redirect_print=True):
        self.log_file = log_file
        self.redirect_print = redirect_print

        self.logger = logging.getLogger("LiveSubprocessLogger")
        self.logger.setLevel(logging.DEBUG)

        self.file_handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)

        self._original_call = subprocess.call
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

    def __enter__(self):
        if self.redirect_print:
            self._patch_streams()
        self._patch_subprocess_call()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._restore()

    def _patch_streams(self):
        class StreamToLogger:
            def __init__(self, logger, level):
                self.logger = logger
                self.level = level
                self.buffer = ""

            def write(self, message):
                self.buffer += message
                while "\n" in self.buffer:
                    line, self.buffer = self.buffer.split("\n", 1)
                    self.logger.log(self.level, line)

            def flush(self):
                if self.buffer:
                    self.logger.log(self.level, self.buffer)
                    self.buffer = ""

            def isatty(self):
                return False

            def fileno(self):
                return 1  # stdout

            def close(self):
                pass

        sys.stdout = StreamToLogger(self.logger, logging.INFO)
        sys.stderr = StreamToLogger(self.logger, logging.ERROR)

    def _patch_subprocess_call(self):
        def async_logged_call(*args, **kwargs):
            self._run_subprocess_live(*args, **kwargs)
            return 0  # non-blocking return

        subprocess.call = async_logged_call

    def _run_subprocess_live(self, *args, **kwargs):
        try:
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            kwargs['bufsize'] = 1  # line-buffered
            kwargs['text'] = True  # decode output as text

            cmd = args[0] if args else kwargs.get("args")
            self.logger.debug(f"[Subprocess Start] Command: {cmd}")

            process = subprocess.Popen(*args, **kwargs)

            # Live-stream stdout and stderr
            self.stdthread = threading.Thread(target=self._stream_output, args=(process.stdout, self.logger.info, "STDOUT"), daemon=True)
            self.stdthread.start()
            self.stdthread2 =threading.Thread(target=self._stream_output, args=(process.stderr, self.logger.error, "STDERR"), daemon=True)
            self.stdthread2.start()

            process.wait()
            self.logger.debug(f"[Subprocess End] Return code: {process.returncode}")

        except Exception as e:
            self.logger.exception(f"Subprocess live logging failed: {e}")

    def _stream_output(self, stream, log_fn, label):
        try:
            for line in iter(stream.readline, ''):
                if line:
                    log_fn(f"[{label}] {line.strip()}")
        finally:
            stream.close()

    def _restore(self):

        subprocess.call = self._original_call
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        self.logger.removeHandler(self.file_handler)
        self.file_handler.close()
