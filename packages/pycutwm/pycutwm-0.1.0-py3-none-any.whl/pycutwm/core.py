import os
import shutil
import json
import subprocess
import time
import glob
import re
import sys 

from .utils import load_config, save_config


def write_grid_on_file(json_path='config.json', cuh_path='headers/SetGrid.cuh'):
    with open(json_path, 'r') as f:
        config = json.load(f)
    # take values from file
    grid = config["grid"]["grid_points"]
    kernel = config["grid"]["kernel_dim"]

    NX = grid["NX"]
    NY = grid["NY"]
    NZ = grid["NZ"]
    NT = grid["NT"]
    BLKT = kernel["BLKT"]
    BLKX = kernel["BLKX"]
    BLKY = kernel["BLKY"]

    # set global variables
    content = (
        "#ifndef _SETGRIDCUH\n"
        "#define _SETGRIDCUH\n\n"
        f"const uint32_t NX = {NX};\n"
        f"const uint32_t NY = {NY};\n"
        f"const uint32_t NZ = {NZ};\n"
        f"#ifdef DISPERSION\n"
        f"const uint32_t NT = {NT};\n"
        f"#else\n"
        f"const uint32_t NT = 1;\n"
        f"#endif\n"
        f"const uint32_t BLKT = {BLKT};\n"
        f"const uint32_t BLKX = {BLKX};\n"
        f"const uint32_t BLKY = {BLKY};\n"
        f"const uint32_t SIZE = NX*NY*NT;\n"
        "\n\n#endif // _SETGRIDCUH\n"
    )

    # write the file
    with open(cuh_path, 'w') as f:
        f.write(content)
    print(f"File {cuh_path} filled with the corresponding grid values.")


def compile_cutwm(dispersion=False, twm_process="shg", compiler="nvcc", opt=3):
    """
    Compile the executable file cuTWM with flags.
    """
    import subprocess

    print("*-----------------------------------------------------------------*") 
    write_grid_on_file(json_path='config.json', cuh_path='headers/SetGrid.cuh')

    # Detect automatically compute capability
    compute_cap = subprocess.check_output(
        "nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -1 | tr -d '.'",
        shell=True
    ).decode().strip()

    flags = [
        compiler, "cuTWM.cu", "-w",
        f"-O{opt}",
        f"-gencode=arch=compute_{compute_cap},code=sm_{compute_cap}",
        f"-gencode=arch=compute_{compute_cap},code=compute_{compute_cap}", # f"-diag-suppress 177",
        "-lcufftw", "-lcufft", "-o", "cuTWM"
    ]

    if dispersion:
        flags.insert(2, "-DDISPERSION")

    if twm_process == "shg":
        flags.insert(3, "-DSHG")
    elif twm_process == "opg":
        flags.insert(3, "-DOPG")
    else:   
        raise RuntimeError("Compilation failed: invalid twm_process")

    print("*-----------------------------------------------------------------*")
    print("Compiling with:", " ".join(flags))
    result = subprocess.run(flags)
    if result.returncode != 0:
        raise RuntimeError("Compilation failed")
    print("Compilation succeeded.")



# ---------------- Logging: captura en tiempo real stdout/stderr de un comando ----------------
def run_and_tee(cmd, log_path, cwd=None, env=None):
    """
    Ejecuta `cmd` capturando TODO lo que imprime a terminal y guardándolo en `log_path`,
    mientras también lo muestra en pantalla en tiempo real.
    """
    log_dir = os.path.dirname(log_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    with open(log_path, "a", encoding="utf-8", buffering=1) as lf:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=cwd,
            env=env
        )
        # Leer línea a línea y volcar a consola y archivo
        for line in proc.stdout:
            sys.stdout.write(line)
            lf.write(line)
        returncode = proc.wait()

    return returncode


def run_cutwm(config_path="config.json", exe_path="./cuTWM", log_path=None, cwd=None, env=None):
    """
    Run the main file with config.json.

    Si `log_path` es None, se genera automáticamente junto al config:
        <misma_carpeta>/<misma_base>.log
    """
    # Derivar log por defecto junto al JSON
    if log_path is None:
        cfg_abs = os.path.abspath(config_path)
        base, _ = os.path.splitext(cfg_abs)
        log_path = base + ".log"

    cmd = [exe_path, config_path]
    print("Running:", " ".join(cmd))
    rc = run_and_tee(cmd, log_path=log_path, cwd=cwd, env=env)
    if rc != 0:
        raise RuntimeError(f"Simulation failed (exit code {rc}). Log: {log_path}")
    print(f"\n\nSimulation finished. Log saved to: {log_path}\n\n")


def move_dat_files(dest_folder):
    """
    Move all .dat file from current dir to dest_folder.
    """
    # Create folder if does not exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Sweep files in the current folder
    for file in os.listdir("."):
        if file.endswith(".dat"):
            src = os.path.join(".", file)
            dst = os.path.join(dest_folder, file)
            shutil.move(src, dst)
            print(f"Moved: {file} -> {dest_folder}")


# ---------- Helpers ----------
def _format_value(v, decimals=1) -> str:
    """
    Formatea el valor para nombres. Para floats, fija el número de decimales.
    Ej: 1   -> "1"
        1.0 -> "1.0" (si decimals=1)
        5.25 -> "5.3" (si decimals=1)
    """
    if isinstance(v, float):
        return f"{v:.{decimals}f}"
    return str(v)

def _sanitize_value_str(s: str) -> str:
    """
    Permite letras, números, punto, guion, guion_bajo, + y =.
    NO reemplaza el punto.
    """
    return re.sub(r"[^A-Za-z0-9.\-+=_]", "_", s)

def _value_str(val, decimals=1) -> str:
    """Formatea y sanitiza en un solo paso."""
    return f"{val:.{decimals}f}"


# ---------- Sweep ----------
def run_cutwm_sweep(config_path, param_path, values,
                    exe_path="./cuTWM",
                    out_dir_base="./results/sweep",
                    keep_config=True,
                    source_dir=".",              # de dónde recoger .dat si el exe no respeta output_directory
                    patterns=("*.dat",),         # qué patrones mover post-corrida
                    mtime_tolerance_s=1.0,       # tolerancia por resolución de timestamps
                    value_decimals=1             # decimales para el valor en nombres
                    ):
    """
    Barre un único parámetro y deja la salida de cada corrida en:
        <out_dir_base>/simulation_<leaf>_<valor>/

    - Si el ejecutable respeta cfg['simulation']['output_directory'], los .dat
      aparecerán directamente dentro de esa carpeta.
    - Si NO lo respeta y escribe en otra parte (p. ej. CWD), se intentará mover
      los .dat recién creados/modificados desde `source_dir`.

    Además, genera un .log con el MISMO nombre que el JSON temporal de la corrida,
    guardándolo en la misma carpeta (out_dir).
    """
    cfg = load_config(config_path)

    keys = param_path.split("/")
    leaf = keys[-1]

    os.makedirs(out_dir_base, exist_ok=True)

    for v in values:
        # 1) aplicar el valor en la config (nota: si tu ejecutable modifica el JSON en memoria,
        #    considera recargar cfg cada iteración con load_config(config_path))
        ptr = cfg
        for k in keys[:-1]:
            ptr = ptr[k]
        ptr[leaf] = v

        # 2) construir nombre y carpeta (con punto en floats)
        val_str = _value_str(v, decimals=value_decimals)
        folder_name = f"simulation_{leaf}_{val_str}"
        out_dir = os.path.join(out_dir_base, folder_name)
        os.makedirs(out_dir, exist_ok=True)

        # 3) actualizar metadatos de simulación
        base_name = cfg.get('simulation', {}).get('name', 'sim')
        sim_name = f"{base_name}_{leaf}_{val_str}"
        cfg['simulation']['name'] = sim_name
        cfg['simulation']['output_directory'] = out_dir

        # 4) guardar config dentro de la carpeta de salida
        temp_config = os.path.join(out_dir, f"config_{leaf}_{val_str}.json")
        save_config(cfg, temp_config)

        # 5) ejecutar, registrando también un log con el MISMO nombre base que el JSON
        #    (p.ej., config_pump_power_W_1.0.json -> config_pump_power_W_1.0.log)
        log_path = os.path.splitext(temp_config)[0] + ".log"
        t0 = time.time()
        run_cutwm(config_path=temp_config, exe_path=exe_path, log_path=log_path)

        # 6) si no hay .dat en out_dir, mover los recién generados desde source_dir
        has_dat_in_out = any(fn.lower().endswith(".dat") for fn in os.listdir(out_dir))
        if not has_dat_in_out:
            for pat in patterns:
                for f in glob.glob(os.path.join(source_dir, pat)):
                    try:
                        # mover archivos nuevos/modificados desde el inicio de la corrida
                        if os.path.getmtime(f) >= (t0 - mtime_tolerance_s):
                            dst = os.path.join(out_dir, os.path.basename(f))
                            if os.path.exists(dst):
                                base, ext = os.path.splitext(dst)
                                dst = f"{base}__{leaf}_{val_str}{ext}"
                            shutil.move(f, dst)
                    except FileNotFoundError:
                        pass

        # 7) limpieza opcional del config
        if not keep_config:
            try:
                os.remove(temp_config)
            except OSError:
                pass
