#!/usr/bin/env python3
import hashlib
import os
import subprocess
import sys

from ipykernel.kernelapp import IPKernelApp


def main():
    # Get a unique venv path based on user and session name
    user = os.getenv("JUPYTERHUB_USER", "default")
    session_name = os.getenv("JPY_SESSION_NAME", "default")
    venv_id = hashlib.md5(f"{user}_{session_name}".encode()).hexdigest()

    venv_path = (
        f"{os.environ.get('UV_VENV_DIR', '/tmp/juppyter_uv_kernel/venv')}/{venv_id}"
    )

    # Create virtualenv if it doesn't exist
    # Note that UV_CACHE_DIR is set by the kernel environment in jupyter config
    if not os.path.exists(venv_path):
        subprocess.run(["uv", "venv", venv_path], check=True)
        print(f"Virtualenv created : {venv_path}")
    else:
        print(f"Virtualenv already exists : {venv_path}")

    # change "pip" to be "uv pip"
    pip_wrapper_path = os.path.join(venv_path, "bin", "pip")
    if not os.path.exists(pip_wrapper_path):
        with open(pip_wrapper_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write('exec uv pip "$@"\n')
        os.chmod(pip_wrapper_path, 0o755)

    # make virtualenv available
    os.environ["PATH"] = f"{os.path.join(venv_path, 'bin')}:" + os.environ["PATH"]
    sys.path.insert(
        0,
        f"{venv_path}/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages",
    )

    argv = sys.argv[1:]
    IPKernelApp.launch_instance(argv=argv)


# Start the IPython kernel app
if __name__ == "__main__":
    main()
