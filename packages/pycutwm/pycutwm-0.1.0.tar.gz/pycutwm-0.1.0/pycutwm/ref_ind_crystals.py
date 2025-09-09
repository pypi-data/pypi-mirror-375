import numpy as np

def n_mgoppln(wavelength, temperature):
    """
    Sellmeier equation for MgO:PPLN.
    Parameters:
        wavelength: Wavelength in microns
        temperature: Temperature in Celsius
    Returns:
        Refractive index
    """
    f = (temperature - 24.5) * (temperature + 570.82)
    a1 = 5.756
    a2 = 0.0983
    a3 = 0.2020
    a4 = 189.32
    a5 = 12.52
    a6 = 1.32e-2
    b1 = 2.860e-6
    b2 = 4.700e-8
    b3 = 6.113e-8
    b4 = 1.516e-4

    G1 = a1 + b1 * f
    G2 = a2 + b2 * f
    G3 = a3 + b3 * f
    G4 = a4 + b4 * f

    L2 = wavelength ** 2
    n2 = G1 + G2 / (L2 - G3 ** 2) + G4 / (L2 - a5 ** 2) - a6 * L2
    return np.sqrt(n2)

def n_ppln(wavelength, temperature):
    """
    Sellmeier equation for PPLN (from Gayer et al.).
    Parameters:
        wavelength: Wavelength in microns
        temperature: Temperature in Celsius
    Returns:
        Refractive index
    """
    f = (temperature - 24.5) * (temperature + 570.82)
    a1 = 5.35583
    a2 = 0.100473
    a3 = 0.20692
    a4 = 100.0
    a5 = 11.34927
    a6 = 1.5334e-2
    b1 = 4.629e-6
    b2 = 1.1685e-7
    b3 = 3.9046e-8
    b4 = 1.6762e-4

    G1 = a1 + b1 * f
    G2 = a2 + b2 * f
    G3 = a3 + b3 * f
    G4 = a4 + b4 * f

    L2 = wavelength ** 2
    n2 = G1 + G2 / (L2 - G3 ** 2) + G4 / (L2 - a5 ** 2) - a6 * L2
    return np.sqrt(n2)

def n_mgospplt(wavelength, temperature):
    """
    Sellmeier equation for MgO:SPP-LT (from Gayer et al.).
    Parameters:
        wavelength: Wavelength in microns
        temperature: Temperature in Celsius
    Returns:
        Refractive index
    """
    f = (temperature - 24.5) * (temperature + 570.82)
    a1 = 5.113
    a2 = 0.0996
    a3 = 0.2102
    a4 = 189.69
    a5 = 12.48
    a6 = 1.32e-2
    b1 = 2.767e-6
    b2 = 3.728e-8
    b3 = 5.290e-8
    b4 = 1.275e-4

    G1 = a1 + b1 * f
    G2 = a2 + b2 * f
    G3 = a3 + b3 * f
    G4 = a4 + b4 * f

    L2 = wavelength ** 2
    n2 = G1 + G2 / (L2 - G3 ** 2) + G4 / (L2 - a5 ** 2) - a6 * L2
    return np.sqrt(n2)

def n_zgp(wavelength, pol):
    """
    Sellmeier equation for ZnGeP2 (ZGP).
    Parameters:
        wavelength: Wavelength in microns
        pol: 'o' (ordinary) or 'e' (extraordinary) polarization
    Returns:
        Refractive index
    """
    L2 = wavelength ** 2
    if pol == 'o':
        A = 8.0409
        B = 1.68625
        CC = 0.40824
        D = 1.2880
        E = 611.05
    elif pol == 'e':
        A = 8.0929
        B = 1.8649
        CC = 0.41468
        D = 0.84052
        E = 452.05
    else:
        raise ValueError("Polarization must be 'o' or 'e'")

    n2 = A + (B * L2) / (L2 - CC) + (D * L2) / (L2 - E)
    return np.sqrt(n2)
