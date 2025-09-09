import numpy as np
import matplotlib.pyplot as plt
import os
import json
import imageio
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def plot_signal_intensity(real_file, imag_file):
    real = np.loadtxt(real_file)
    imag = np.loadtxt(imag_file)
    intensity = real**2 + imag**2
    plt.plot(intensity)
    plt.xlabel("Grid point / Time")
    plt.ylabel("Intensity |E|²")
    plt.title("Signal Field Intensity")
    plt.show()


def plot_XY_profile(real_path, imag_path,
                    Lx_um=1000.0, Ly_um=1000.0,
                    save_fig=True, out_png="fig_name.png"):
    """
    Read two .dat (real e imaginary parts) as 2D-matrices (NY, NX),
    compute |A|^2 and plot x-y in micron scale.
    """
    real = np.loadtxt(real_path)
    imag = np.loadtxt(imag_path)

    if real.shape != imag.shape:
        raise ValueError(f"Shape mismatch: real {real.shape} vs imag {imag.shape}")

    NY, NX = real.shape
    
    A2 = real**2 + imag**2

    dx_um = Lx_um / (NX - 1) if NX > 1 else float("nan")
    dy_um = Ly_um / (NY - 1) if NY > 1 else float("nan")

    plt.figure(figsize=(7, 6))
    extent = [0, Lx_um, 0, Ly_um]
    im = plt.imshow(A2, origin="lower", extent=extent, aspect="equal")
    plt.xlabel("x (μm)")
    plt.ylabel("y (μm)")
    plt.title(f"|ψ|²   NX={NX}, NY={NY},   dx={dx_um:.3g} μm, dy={dy_um:.3g} μm")
    plt.colorbar(im, label="Intensity (arb. units)")
    plt.tight_layout()
    if save_fig:
        plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.show()
    return {"NX": NX, "NY": NY, "dx_um": dx_um, "dy_um": dy_um, "out_png": out_png}


def plot_fields_from_slices(
    files_folder,
    config_json_path,
    n_dict,        # {'pump': n_p, 'signal': n_s, 'idler': n_i}
    cmap='inferno',
    image_dir="intensity_cut_YZ/",
    image_name="intensity_profile",
    image_extension=".png"
):
    """
    Visualiza la propagación de los campos habilitados en config.json

    Args:
        files_folder (str): Carpeta con archivos .dat
        config_json_path (str): Ruta al archivo config.json
        n_dict (dict): {'pump': n_p, 'signal': n_s, 'idler': n_i}
        aspect_ratio (float): Relación de aspecto para cada panel
        cmap (str): Colormap
    """

    # --- Leer config.json ---
    with open(config_json_path, "r") as f:
        cfg = json.load(f)
    save_mode = cfg.get("save_mode", {})
    grid_points = cfg.get("grid", {}).get("grid_points", {})
    NX = int(grid_points.get("NX", 32))
    NY = int(grid_points.get("NY", 32))
    NZ = int(grid_points.get("NZ", 1))

    # --- Qué campos graficar ---
    field_list = [field for field in ('pump', 'signal', 'idler') if save_mode.get(f"save_{field}", False)]
    if not field_list:
        print("No hay campos seleccionados para graficar según config.json.")
        return

    # --- Leer archivos de cada campo ---
    E_fields = {}
    for field in field_list:
        E_cmplx = np.zeros((NZ, NY, NX), dtype=np.complex128)
        for z in range(NZ):
            for part in ('r', 'i'):
                fname = os.path.join(files_folder, f"{field}_output_XY_z_slice_{z}_{part}.dat")
                if not os.path.isfile(fname):
                    raise FileNotFoundError(f"No se encontró {fname}")
                data = np.loadtxt(fname)
                if part == 'r':
                    E_cmplx[z] = data
                else:
                    E_cmplx[z] += 1j * data
        E_fields[field] = E_cmplx

    # --- Graficar ---
    x_idx = NX // 2
    y = np.arange(NY)
    z_pos = np.arange(NZ)

    fig, axes = plt.subplots(len(field_list), 1, figsize=(5, 5), constrained_layout=True)

    if len(field_list) == 1:
        axes = [axes]

    for i, field in enumerate(field_list):
        n = n_dict[field]
        E = E_fields[field]
                # Physical constants in user units:
        C0 = 299792458 * 1e6 / 1e12        # Speed of light in vacuum [μm/ps]
        EPS0 = 8.8541878128e-12 * 1e12 / 1e6 # Vacuum permittivity [W·ps/V²·μm]
        intensity_Wum2 = C0*EPS0*n*np.abs(E[:, :, x_idx])**2 / 2.0
        intensity_Wcm2 = intensity_Wum2 * 1e8
        ax = axes[i]
        im = ax.imshow(
            intensity_Wcm2.T,
            origin='lower',
            aspect='auto',         # <-- esto centra SIEMPRE
            extent=[0, NZ-1, 0, NY-1],
            cmap=cmap
        )
        ax.set_title(f"{field.capitalize()} field")
        ax.set_xlabel('z-slice')
        ax.set_ylabel('y')
        cb = fig.colorbar(im, ax=ax, fraction=0.045)
        cb.set_label("Intensity (W/cm²)")
    plt.suptitle("Propagación de los campos (corte en x=NX/2)")

    # Ensure output directory exists
    output_image_dir = os.path.dirname(image_dir)
    if output_image_dir and not os.path.exists(image_dir):
        os.makedirs(image_dir)
    fig.savefig(image_dir+image_name+image_extension, dpi=150, bbox_inches='tight')
    plt.show()
    return


def make_field_propagation_gif(
    files_folder,
    config_json_path,
    n_dict,           # {'pump': n_p, 'signal': n_s, 'idler': n_i}
    gif_path,
    cmap='inferno',
    fps=10,
    vmin=None,
    vmax=None
):
    """
    Generates a GIF showing the progression of field intensity (x-y plane) at each slice along the crystal
    for each field enabled in config.json. Each frame is a horizontal row of 2D intensity maps (one per field).

    Args:
        files_folder (str): Path to the folder containing the .dat files.
        config_json_path (str): Path to config.json.
        n_dict (dict): Refractive indices for each field. Example: {'pump': 2.23, 'signal': 2.21, 'idler': 2.19}
        gif_path (str): Output path for the GIF file (should end with .gif).
        cmap (str): Colormap to use for intensity images.
        fps (int): Frames per second for the GIF animation.
        vmin, vmax (float or None): Set fixed min/max for color scale. If None, scale automatically for each field.
    """

    # --- Load config.json ---
    with open(config_json_path, "r") as f:
        cfg = json.load(f)

    save_mode = cfg.get("save_mode", {})
    grid_points = cfg.get("grid", {}).get("grid_points", {})
    NX = int(grid_points.get("NX", 32))
    NY = int(grid_points.get("NY", 32))
    NZ = int(grid_points.get("NZ", 1))
    crystal = cfg.get("crystal", {})
    Lcr = float(crystal.get("dimensions", {}).get("Lcr", 10000.0))  # in micrometers

    # --- Which fields to plot? ---
    field_list = [field for field in ('pump', 'signal', 'idler') if save_mode.get(f"save_{field}", False)]
    if not field_list:
        print("No fields selected for plotting in config.json.")
        return

    dz = Lcr / (NZ - 1) if NZ > 1 else 0

    # --- Precompute color limits for all fields over all slices (for consistent colorbar) ---
    if vmin is None or vmax is None:
        all_intensities = {field: [] for field in field_list}
        for z in range(NZ):
            for field in field_list:
                fname_real = os.path.join(files_folder, f"{field}_output_XY_z_slice_{z}_r.dat")
                fname_imag = os.path.join(files_folder, f"{field}_output_XY_z_slice_{z}_i.dat")
                real = np.loadtxt(fname_real)
                imag = np.loadtxt(fname_imag)
                E = real + 1j * imag
                # Physical constants in user units:
                C0 = 299792458 * 1e6 / 1e12        # Speed of light in vacuum [μm/ps]
                EPS0 = 8.8541878128e-12 * 1e12 / 1e6 # Vacuum permittivity [W·ps/V²·μm]
                intensity_Wum2 = C0*EPS0*n_dict[field]*np.abs(E)**2 / 2.0  # (NY, NX)
                intensity_Wcm2 = intensity_Wum2 * 1e8
                all_intensities[field].append(intensity_Wcm2)
        # Flatten and find global min/max for all fields
        flat_all = np.concatenate([np.ravel(arr) for field in field_list for arr in all_intensities[field]])
        vmin = float(np.nanmin(flat_all))
        vmax = float(np.nanmax(flat_all))

    # --- Ensure output directory exists ---
    output_dir = os.path.dirname(gif_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- Create and save frames ---
    images = []
    for z in range(NZ):
        # Create figure and attach Agg canvas
        fig = Figure(figsize=(6*len(field_list), 5), constrained_layout=True)
        FigureCanvas(fig)
        axes = fig.subplots(1, len(field_list))
        if len(field_list) == 1:
            axes = [axes]

        for i, field in enumerate(field_list):
            fname_real = os.path.join(files_folder, f"{field}_output_XY_z_slice_{z}_r.dat")
            fname_imag = os.path.join(files_folder, f"{field}_output_XY_z_slice_{z}_i.dat")
            real = np.loadtxt(fname_real)
            imag = np.loadtxt(fname_imag)
            E = real + 1j * imag
            # Physical constants in user units:
            C0 = 299792458 * 1e6 / 1e12        # Speed of light in vacuum [μm/ps]
            EPS0 = 8.8541878128e-12 * 1e12 / 1e6 # Vacuum permittivity [W·ps/V²·μm]
            intensity_Wum2 = C0*EPS0*n_dict[field]*np.abs(E)**2 / 2.0  # shape (NY, NX)
            intensity_Wcm2 = intensity_Wum2 * 1e8

            ax = axes[i]
            im = ax.imshow(
                intensity_Wcm2,
                origin='lower',
                aspect='auto',
                extent=[0, NX-1, 0, NY-1],
                cmap=cmap,
                vmin=vmin,
                vmax=vmax
            )
            ax.set_title(f"{field.capitalize()} field")
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            cb = fig.colorbar(im, ax=ax, fraction=0.045)
            cb.set_label("Intensity (W/cm²)")

        z_um = z * dz
        fig.suptitle(f"z = {z_um:.1f} μm")

        # Draw and convert figure to numpy RGB array
        fig.canvas.draw()
        image = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        images.append(image)
        plt.close('all')
    
    # --- Save GIF ---
    # Ensure output directory exists
    output_dir = os.path.dirname(gif_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    imageio.mimsave(gif_path, images, fps=fps)
    print(f"GIF saved to {gif_path}")