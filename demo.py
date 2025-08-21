"""Simple script to run a demo render using a generated QR code image."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from qr_perspective import detect_qr_pose


def generate_qr_image(path: Path) -> bool:
    """Generate a basic QR code image for the demo."""
    try:
        import qrcode
    except ImportError:
        print('The "qrcode" package is required for this demo.')
        return False
    img = qrcode.make("demo")
    img.save(path)
    return True


def run_demo(output_path: Path) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        input_path = tmpdir_path / "demo_qr.png"
        if not generate_qr_image(input_path):
            return

        pose = detect_qr_pose(str(input_path))
        if pose is None:
            print("QR code not detected in generated image.")
            return

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
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            print("Blender is required to run this demo. Please install Blender and ensure it is in your PATH.")
        except subprocess.CalledProcessError as exc:
            print(f"Rendering failed: {exc}")
        else:
            print(f"Demo render written to {output_path}")


if __name__ == "__main__":
    output = Path("demo_render.png")
    run_demo(output)
