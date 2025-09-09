# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import os
import glob
from typing import Any, Dict, Optional, Tuple
import numpy as np

# Physical constants in user units:
C0 = 299792458 * 1e6 / 1e12        # Speed of light in vacuum [μm/ps]
EPS0 = 8.8541878128e-12 * 1e12 / 1e6 # Vacuum permittivity [W·ps/V²·μm]

# Output field file names
FIELD_FILES = {
    "p": ("pump_output_XY_r.dat",   "pump_output_XY_i.dat"),
    "s": ("signal_output_XY_r.dat", "signal_output_XY_i.dat"),
    "i": ("idler_output_XY_r.dat",  "idler_output_XY_i.dat"),
}

# -------------------------
# JSON utilities
# -------------------------
def read_from_json(json_path: str, key: str, default: Any = None) -> Any:
    """
    Reads a value from a JSON file using a dotted key (supports nested keys like 'a.b.c').
    If the key does not exist and default is given, returns default. Otherwise raises KeyError.
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    if "." not in key:
        if key in data:
            return data[key]
        if default is not None:
            return default
        raise KeyError(f"Key '{key}' not found in {json_path}")

    cur = data
    parts = key.split(".")
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            if default is not None:
                return default
            raise KeyError(f"Key '{key}' not found in {json_path}")
    return cur

def _auto_find_config_json(folder: str) -> str:
    """
    Automatically finds the unique config_*.json file in the folder.
    """
    candidates = sorted(glob.glob(os.path.join(folder, "config_*.json")))
    if len(candidates) == 0:
        raise FileNotFoundError(f"No config_*.json found in {folder}")
    if len(candidates) > 1:
        raise RuntimeError(f"Multiple config_*.json files found in {folder}: {candidates}")
    return candidates[0]


def _grid_from_json(json_path: str) -> Tuple[int, int, float, float]:
    """
    Reads NX, NY, LX(μm), LY(μm) from the JSON file.
    Returns: NX, NY, dx (μm), dy (μm).
    """
    NX = int(read_from_json(json_path, "grid.grid_points.NX"))
    NY = int(read_from_json(json_path, "grid.grid_points.NY"))
    LX_um = float(read_from_json(json_path, "crystal.dimensions.LX"))
    LY_um = float(read_from_json(json_path, "crystal.dimensions.LY"))
    dx = LX_um / (NX-1)     # grid spacing in μm
    dy = LY_um / (NY-1)     # grid spacing in μm
    return NX, NY, dx, dy

# -------------------------
# Field loading
# -------------------------
def _load_complex_matrix(real_path: str, imag_path: str, shape: Tuple[int, int]) -> np.ndarray:
    """
    Loads real/imaginary matrices (plain text), reshapes to (NY, NX), and returns a complex array.
    Tries C order first; if it fails, tries Fortran order.
    """
    Er = np.loadtxt(real_path, dtype=np.float64)
    Ei = np.loadtxt(imag_path, dtype=np.float64)
    if Er.size != Ei.size:
        raise ValueError(f"Size mismatch between {os.path.basename(real_path)} and {os.path.basename(imag_path)}")
    NY, NX = shape
    try:
        Er = Er.reshape(NY, NX, order="C")
        Ei = Ei.reshape(NY, NX, order="C")
    except ValueError:
        Er = Er.reshape(NY, NX, order="F")
        Ei = Ei.reshape(NY, NX, order="F")
    return Er + 1j * Ei


def _maybe_load_field(folder: str, key: str, NX: int, NY: int) -> Optional[np.ndarray]:
    """
    Loads a complex field (pump, signal, or idler) from files if both real and imaginary parts exist.
    Returns None if either file is missing.
    """
    r_name, i_name = FIELD_FILES[key]
    r_path = os.path.join(folder, r_name)
    i_path = os.path.join(folder, i_name)
    if not (os.path.isfile(r_path) and os.path.isfile(i_path)):
        return None
    return _load_complex_matrix(r_path, i_path, shape=(NY, NX))

# -------------------------
# Optical power calculation
# -------------------------
def _intensity(E: np.ndarray, n: float, field_scale: float = 1.0) -> np.ndarray:
    """
    Computes the intensity: I = 0.5 * n * eps0 * c * |E|^2 [W/μm²]
    E should be in V/μm if field_scale=1.0, or scale accordingly.
    """
    E_vpm = E * field_scale
    return 0.5 * n * EPS0 * C0 * np.abs(E_vpm)**2


def _power(I: np.ndarray, dx: float, dy: float) -> float:
    """
    Integrates intensity over the (x, y) plane to obtain the total power in [W].
    dx and dy must be given in μm.
    """
    return float(I.sum() * dx * dy)


def compute_powers_from_folder(
    folder: str,
    n_p: float,
    n_s: float,
    n_i: float,
    json_path: Optional[str] = None,
    field_scale: float = 1.0
) -> Dict[str, float]:
    """
    Computes the output power for all present fields (pump, signal, idler) in the specified folder.

    Args:
      folder: Path to the simulation results folder.
      n_p, n_s, n_i: Refractive indices for pump, signal, idler.
      json_path: Path to the simulation config JSON. If None, it is auto-detected in the folder.
      field_scale: Multiply the electric field by this factor to convert it to V/μm. 
                   Use 1.0 if already in V/μm. Use 1e6 if in V/m.

    Returns:
      Dictionary with powers in W for present fields: e.g., {"p": ..., "s": ..., "i": ...}
    """
    if json_path is None:
        json_path = _auto_find_config_json(folder)

    NX, NY, dx, dy = _grid_from_json(json_path)

    out: Dict[str, float] = {}
    # Pump
    Ep = _maybe_load_field(folder, "p", NX, NY)
    if Ep is not None:
        Ip = _intensity(Ep, n=n_p, field_scale=field_scale)
        out["p"] = _power(Ip, dx, dy)

    # Signal
    Es = _maybe_load_field(folder, "s", NX, NY)
    if Es is not None:
        Is = _intensity(Es, n=n_s, field_scale=field_scale)
        out["s"] = _power(Is, dx, dy)

    # Idler
    Ei = _maybe_load_field(folder, "i", NX, NY)
    if Ei is not None:
        Ii = _intensity(Ei, n=n_i, field_scale=field_scale)
        out["i"] = _power(Ii, dx, dy)

    return out

