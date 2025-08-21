"""Flask API server for QR code based 3D rendering."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, send_file

from qr_perspective import detect_qr_pose

app = Flask(__name__)


@app.route("/render", methods=["POST"])
def render_endpoint():
    if "image" not in request.files:
        return jsonify({"error": "missing image"}), 400

    image_file = request.files["image"]
    model_path = request.form.get("model")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.png"
        image_file.save(input_path)

        pose = detect_qr_pose(str(input_path))
        if pose is None:
            return jsonify({"error": "QR code not detected"}), 400

        output_path = Path(tmpdir) / "output.png"
        cmd = [
            "blender",
            "-b",
            "-P",
            str(Path(__file__).with_name("render_blender.py")),
            "--",
            str(input_path),
            str(output_path),
            json.dumps(pose.matrix),
        ]
        if model_path:
            cmd.append(model_path)

        try:
            subprocess.run(cmd, check=True)
        except Exception as exc:  # pragma: no cover - requires blender
            return jsonify({"error": f"render failed: {exc}"}), 500

        return send_file(output_path, mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
