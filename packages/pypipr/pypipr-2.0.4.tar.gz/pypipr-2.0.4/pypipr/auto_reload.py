from time import sleep
from subprocess import run

from .get_filemtime import get_filemtime
from .print_colorize import print_colorize


def auto_reload(filename):
    """
    Menjalankan file python secara berulang.
    Dengan tujuan untuk melihat perubahan secara langsung.
    Pastikan kode aman untuk dijalankan.
    Jalankan kode ini di terminal console.

    ```py
    auto_reload("file_name.py")
    ```

    or run in terminal

    ```
    pypipr auto_reload
    ```
    """
    mtime = get_filemtime(filename)
    last_mtime = 0

    try:
        print_colorize("Start")
        while True:
            last_mtime = mtime
            run(f"python {filename}")
            while mtime == last_mtime:
                sleep(1)
                mtime = get_filemtime(filename)
            print_colorize("Reload")
    except KeyboardInterrupt:
        print_colorize("Stop")
