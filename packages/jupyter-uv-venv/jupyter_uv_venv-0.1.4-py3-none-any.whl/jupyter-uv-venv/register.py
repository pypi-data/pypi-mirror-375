import json
import sys
from pathlib import Path


def get_kernel_spec(uv_cache_dir: str, uv_venv_dir: str, uv_link_mode: str):
    """Return kernel.json spec with configured environment."""
    return {
        "argv": ["python", "-m", f"{__package__}.kernel", "-f", "{connection_file}"],
        "display_name": "Python 3 (UV Venv)",
        "language": "python",
        "metadata": {},
        "env": {
            "UV_CACHE_DIR": uv_cache_dir,
            "UV_VENV_DIR": uv_venv_dir,
            "UV_LINK_MODE": uv_link_mode,
        },
    }


def register_kernel(uv_cache_dir: str, uv_venv_dir: str, uv_link_mode: str):
    """Register the kernel in Jupyter"""
    kernel_spec = get_kernel_spec(
        uv_cache_dir,
        uv_venv_dir,
        uv_link_mode,
    )

    # Path to kernel directory
    kernel_dir = Path(f"{sys.prefix}/share/jupyter/kernels/{__package__}")
    kernel_dir.mkdir(parents=True, exist_ok=True)

    # install kernel.json and logo
    with open(kernel_dir / "kernel.json", "w") as f:
        json.dump(kernel_spec, f, indent=2)
    logo_src = Path(__file__).parent / "logo-64x64.png"
    with (
        open(kernel_dir / "logo-64x64.png", "wb") as f_out,
        open(logo_src, "rb") as f_in,
    ):
        f_out.write(f_in.read())

    print(f"Kernel installed in {kernel_dir}")


if __name__ == "__main__":
    import optparse

    opt_parser = optparse.OptionParser()
    opt_parser.add_option(
        "-c",
        "--cache-dir",
        dest="uv_cache_dir",
        help="Set UV_CACHE_DIR (default: %default)",
        default="/tmp/jupyter_uv_kernel/uv_cache",
    )
    opt_parser.add_option(
        "-d",
        "--venv-dir",
        dest="uv_venv_dir",
        help="Set UV_VENV_DIR (default: %default)",
        default="/tmp/jupyter_uv_kernel/venvs",
    )
    opt_parser.add_option(
        "-m",
        "--link-mode",
        dest="uv_link_mode",
        help="Set UV_LINK_MODE (default: %default)",
        default="hardlink",
    )
    options, args = opt_parser.parse_args()

    register_kernel(
        uv_cache_dir=options.uv_cache_dir,
        uv_venv_dir=options.uv_venv_dir,
        uv_link_mode=options.uv_link_mode,
    )
