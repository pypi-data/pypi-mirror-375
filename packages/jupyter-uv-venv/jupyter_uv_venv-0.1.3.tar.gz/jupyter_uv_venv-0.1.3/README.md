# Jupyter UV environment Kernel

[![PyPi](https://img.shields.io/badge/pypi-%23ececec.svg?style=for-the-badge&logo=pypi&logoColor=1f73b7)](https://pypi.org/project/jupyter-uv-venv/)

Python Kernel to reduce disk space usage, isolate each notebook environment, and avoid package overwriting. All in one, with [uv](https://github.com/astral-sh/uv)

## TL;DR

Install the package and use the registration module:

```
pip install jupyter-uv-kernel
python -m jupyter_uv_kernel.register
```

Restart Jupyter Hub / Lab and use the new kernel "Python 3 (uv venv)".

You can try the demo container with Podman or Docker:

```bash
podman run \
  --name jupyter-uv \
  -p 8000:8000 \
  registry.gitlab.com/metal3d/jupyter-uv-venv:latest

# add a user, has the demo uses "jupyter hub"
podman exec -it jupyter-uv adduser -m John
podman exec -it jupyter-uv passwd John
```

Then visit <http://localhost:8000> and login with user "John" and the password you set.

## What is it?

This is an experiment for Jupyter Hub and Lab of a Kernel that build **one cirtual env per notebook**. Using the fantastic [uv](https://github.com/astral-sh/uv) python manager, there is no duplication of pacakge.

It avoids overwriting packages in a kernel and duplication of installed packages. You'll gain disk space and speed up large package installation.

**Why?**

From the perspective of Jupyter Lab/Hub, a “kernel” is a Python environment that serves as a repository for installing the necessary packages. It works efficiently but has one major drawback: this repository is statically shared.
To understand the problem, if I create a notebook that runs `!pip install numpy==2.2` and a second one that runs `!pip install numpy==2.3`, one will take precedence over the other and overwrite the package for that kernel.

My idea is as follows:

- A notebook must be isolated.
- It must control its own package versions without impacting others.

A virtual environment per notebook is therefore the first building block of the solution.

This leaves a second issue to address: the duplication of installations, particularly for large packages such as “torch” and “Nvidia” dependencies.

The solution is to have a global repository, something that PDM or UV do very well.

Since PDM is mainly used for project management, UV is more than enough. As a reminder:

> uv installs packages in a cache, then allows you to create a hard link or symbolic link to the packages in the target environment. So, if 100 environments install torch, there's only one installation, and it'll be linked to one environment.

## What the “jupyter-uv-venv” kernel does

1. The kernel create one venv per notebook, and use uv to install packages in this venv.
2. The uv cache is shared between all notebooks, so that all notebooks can install its own version of a package without overwriting others. The uv cache avoid duplication of installations, you drastically reduce the disk space occupation.

When started, this kernel creates a virtual environment unique to this notebook. The “uv venv” command creates the necessary components.
The notebook environment is then forced onto this environment (`PATH` and `sys.path` path) as a `source bin/activate` would do.
The `pip` command is replaced by an alias `uv pip` in order to benefit from the cache.

In the case of this repository, which uses containerization, and in order to store the environment and cache in volumes, the links are symbolic (see the environment variable `UV_LINK_MODE`).

## Installation in your Jupyter Hub / Lab

```bash
pip install jupyter-uv-kernel
python -m jupyter_uv_kernel.register
```

Then restart your Jupyter Hub / Lab server.

**Do not use `jupyter kernelspec install` command for this kernel.** The registration script does everything needed, and is required to be able to specify paths and link mode.

To set up the registration with new values:

```bash
# see help
python -m jupyter_uv_kernel.register --help

# install with custom values
python -m jupyter_uv_kernel.register \
  --uv-cache-dir /path/to/uv_cache \
  --uv-venvs-dir /path/to/venvs \
  --uv-link-mode symlink
```

> Do not use "`hardlink`" mode if your virtual environments and uv cache are not on the same filesystem. For example, if you use Docker / Podman volumes.

If you're using my demo image, the values are already set :

- `UV_CACHE_DIR=/opt/uv_cache`
- `UV_VENVS_DIR=/opt/venvs`
- `UV_LINK_MODE=symlink`

