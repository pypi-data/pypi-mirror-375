import sys
import os
import runpy
import logging

logger = logging.getLogger(__name__)
"this code is for embededing inside aviyal desktop ,because jar server will call it in runtime to run python code"

def main():
    """
    this code is used for mimicing python.exe comandline
    this is used inside anvil desktop app that built with pyinstaller.
    because pyinsataller creates an exe from python file but it will not generate a python.exe file for runtime usage.
    so to run comandline in embedded python.exe we have only two ways. either embedded a python.exe and all files like
    venv inside pyinstaller as datafodler
      or
    create a proxy that  mmimics python.exe. and pass all comandline arguments it received to pythons internal modules.
    i choosed mimicing exe because it is better. we can reuse pyinstaller  generated exe.
    if no comandline arguments passed then it will behave as normal. and arguments are passed while starting then
    it will behave like python.exe. it will run script that provided as argument

    """

    argv = sys.argv
    if len(argv) >= 3 and argv[1] == '-c':
        # Simulate `python -c "code"`
        code = argv[2]
        exec(code, {'__name__': '__main__'})
    elif len(argv) >= 3 and argv[1] == '-m':
        # Simulate `python -m module`
        runpy.run_module(argv[2], run_name="__main__", alter_sys=True)

    elif len(argv) >= 3 and argv[1] == '-um':
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)
        # Simulate `python -m module`
        runpy.run_module(argv[2], run_name="__main__", alter_sys=True)

    elif len(argv) >= 2 and argv[1].endswith('.py') and os.path.exists(argv[1]):
        # Simulate `python script.py`
        runpy.run_path(argv[1], run_name='__main__')
    else:
        # Default entry point
        logger.info("no comandline arguments provided")

if __name__ == '__main__':
    main()
