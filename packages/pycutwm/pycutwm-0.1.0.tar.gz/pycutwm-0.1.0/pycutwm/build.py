import os
import shutil
import subprocess
from pathlib import Path


__all__ = ["compile"]




def _detect_compute_capability(gpu_index: int | None = None) -> str:
"""Return compute capability like '80' (for sm_80). Picks first GPU unless index provided."""
cmd = [
"nvidia-smi",
"--query-gpu=compute_cap",
"--format=csv,noheader",
]
out = subprocess.check_output(cmd, text=True).strip().splitlines()
if not out:
raise RuntimeError("nvidia-smi returned no GPUs; is NVIDIA driver installed?")
line = out[gpu_index or 0].strip().replace(".", "")
if not line.isdigit():
raise RuntimeError(f"Unexpected compute_cap output: {line!r}")
return line




def compile(
sources_dir: str | os.PathLike = "../cuOPO3D",
output_exe: str | os.PathLike = "cuOPO3D",
dispersion: bool = True,
opt_level: int = 3,
gpu_index: int | None = None,
extra_nvcc: list[str] | None = None,
env: dict[str, str] | None = None,
) -> Path:
"""
Compile the CUDA solver with nvcc. Returns path to the executable.


Parameters
----------
sources_dir : path to directory containing cuOPO3D.cu
output_exe : executable name or path to create
dispersion : if True, add -DDISPERSION
opt_level : 0..3 optimization level
gpu_index : pick GPU index for compute capability detection
extra_nvcc : list of extra flags for nvcc
env : environment overrides for subprocess
"""
sources_dir = Path(sources_dir).resolve()
cu_file = sources_dir / "cuOPO3D.cu"
if not cu_file.exists():
raise FileNotFoundError(f"cu file not found: {cu_file}")


sm = _detect_compute_capability(gpu_index)


nvcc = shutil.which("nvcc")
if not nvcc:
raise RuntimeError("nvcc not found in PATH. Install CUDA toolkit or update PATH.")


cflags = [
nvcc,
str(cu_file),
"-O" + str(opt_level),
"-diag-suppress",
"177",
"-gencode=arch=compute_" + sm + ",code=sm_" + sm,
return exe_path