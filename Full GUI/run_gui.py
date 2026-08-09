import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "gui"))

if __name__ == "__main__":
    try:
        import app as gui_app
    except ImportError:
        print(
            "Flask is required for the GUI. Install it with:\n"
            "    pip install -e \".[gui]\"\n"
            "or:\n"
            "    pip install flask"
        )
        sys.exit(1)

    import webbrowser
    from threading import Timer

    Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    gui_app.app.run(host="127.0.0.1", port=5000, debug=False)
