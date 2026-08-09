from __future__ import annotations

import sys
import webbrowser
from pathlib import Path
from threading import Timer

from flask import Flask, jsonify, request, send_file, render_template

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import data_service  
app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def dashboard_page():
    return render_template("dashboard.html")


@app.route("/api/scan", methods=["POST"])
def api_scan():
    payload = request.get_json(silent=True) or {}
    browser_keys = payload.get("browsers") or None
    try:
        summary = data_service.run_scan(browser_keys)
        return jsonify({"ok": True, "summary": summary})
    except Exception as exc: 
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/dashboard")
def api_dashboard():
    if not data_service.has_scanned():
        return jsonify({"ok": True, "scanned": False})

    data = data_service.get_dashboard(
        browser=request.args.get("browser"),
        profile=request.args.get("profile"),
        date_from=request.args.get("date_from"),
        date_to=request.args.get("date_to"),
        keyword=request.args.get("keyword"),
        include_duplicates=request.args.get("include_duplicates", "true") == "true",
        top_sites_only=request.args.get("top_sites_only", "false") == "true",
    )
    data["ok"] = True
    data["scanned"] = True
    return jsonify(data)


@app.route("/api/export")
def api_export():
    export_format = request.args.get("format", "json")
    try:
        paths = data_service.export_current(export_format)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


    return send_file(paths[0], as_attachment=True, download_name=paths[0].name)


@app.route("/api/available-browsers")
def api_available_browsers():
    from profiles import detect_installed_browsers

    installed = detect_installed_browsers()
    return jsonify({"ok": True, "browsers": [{"key": b.key, "name": b.display_name} for b in installed]})


def _open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    Timer(1.0, _open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
