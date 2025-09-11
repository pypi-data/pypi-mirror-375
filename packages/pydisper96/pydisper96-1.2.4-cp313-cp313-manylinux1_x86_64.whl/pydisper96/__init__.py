from pydisper96_ import py_disp96_modfile

def py_disp96_modfile_ur(modfile : str, n : int, fS : int, fU : int,
                         fM : int, ic : float, f1 : float, h : float,
                         si_vp_vs_rho:bool,
                         t: list, use_c_impl:bool):
    """
    Computes the group velocities of Rayleigh waves.

    Args:
        modfile: filepath of the model (whose the lines must respect this
        spec.: depth (km), vp (km/s), vs (km/s), rho (g/cm³), qs).
        n: number of frequencies (must be len(t)).
        fS: 1 to enable spherical correction, 0 otherwise.
        fU: 0 to choose the following system unit: km for depths, km/s for vs
        and vp, g/cm³ for rho. Other system unit isn't documented.
        fM: mode number, fundamental = 1 then 2, 3, 4, 5...
        ic: phase velocity search increment.
        f1: reserved parameter (always set to zero).
        h: frequency step for derivation.
        si_vp_vs_rho: must be set to True if vp, vs and rho respect the SI units
        (rho in kg/m^3, vp and vs in m/s). if False the units are assumed to be
        in g/cm^3 for rho, in km/s for vp and vs.
        t: the list of frequency inverses (period) according to compute the
        velocities.

    Returns:
        The velocities as a list of length == len(t).

    """
    return py_disp96_modfile(modfile, n, fS, fU, fM, ic, f1, h, si_vp_vs_rho, t, 0, 0, use_c_impl)

def py_disp96_modfile_ul(modfile : str, n : int, fS : int, fU : int,
                         fM : int, ic : float, f1 : float, h : float,
                         si_vp_vs_rho:bool,
                         t: list, use_c_impl:bool):
    """
    Computes the group velocities of Love waves.

    Args:
        modfile: filepath of the model (whose the lines must respect this
        spec.: depth (km), vp (km/s), vs (km/s), rho (g/cm³), qs).
        n: number of frequencies (must be len(t)).
        fS: 1 to enable spherical correction, 0 otherwise.
        fU: 0 to choose the following system unit: km for depths, km/s for vs
        and vp, g/cm³ for rho. Other system unit isn't documented.
        fM: mode number, fundamental = 1 then 2, 3, 4, 5...
        ic: phase velocity search increment.
        f1: reserved parameter (always set to zero).
        si_vp_vs_rho: must be set to True if vp, vs and rho respect the SI units
        (rho in kg/m^3, vp and vs in m/s). if False the units are assumed to be
        in g/cm^3 for rho, in km/s for vp and vs.
        h: frequency step for derivation.
        t: the list of frequency inverses (period) according to compute the
        velocities.

    Returns:
        The velocities as a list of length == len(t).

    """
    return py_disp96_modfile(modfile, n, fS, fU, fM, ic, f1, h, si_vp_vs_rho, t, 1, 0, use_c_impl)

def py_disp96_modfile_cr(modfile : str, n : int, fS : int, fU : int,
                         fM : int, ic : float, f1 : float, h : float,
                         si_vp_vs_rho:bool,
                         t: list, use_c_impl:bool):
    """
    Computes the phase velocities of Rayleigh waves.

    Args:
        modfile: filepath of the model (whose the lines must respect this
        spec.: depth (km), vp (km/s), vs (km/s), rho (g/cm³), qs).
        n: number of frequencies (must be len(t)).
        fS: 1 to enable spherical correction, 0 otherwise.
        fU: 0 to choose the following system unit: km for depths, km/s for vs
        and vp, g/cm³ for rho. Other system unit isn't documented.
        fM: mode number, fundamental = 1 then 2, 3, 4, 5...
        ic: phase velocity search increment.
        f1: reserved parameter (always set to zero).
        h: frequency step for derivation.
        si_vp_vs_rho: must be set to True if vp, vs and rho respect the SI units
        (rho in kg/m^3, vp and vs in m/s). if False the units are assumed to be
        in g/cm^3 for rho, in km/s for vp and vs.
        t: the list of frequency inverses (period) according to compute the
        velocities.

    Returns:
        The velocities as a list of length == len(t).

    """
    return py_disp96_modfile(modfile, n, fS, fU, fM, ic, f1, h, si_vp_vs_rho,
                             t, 0, 1, use_c_impl)

def py_disp96_modfile_cl(modfile : str, n : int, fS : int, fU : int,
                         fM : int, ic : float, f1 : float, h : float,
                         si_vp_vs_rho:bool,
                         t: list, use_c_impl:bool):
    """
    Computes the phase velocities of Love waves.

    Args:
        modfile: filepath of the model (whose the lines must respect this
        spec.: depth (km), vp (km/s), vs (km/s), rho (g/cm³), qs).
        n: number of frequencies (must be len(t)).
        fS: 1 to enable spherical correction, 0 otherwise.
        fU: 0 to choose the following system unit: km for depths, km/s for vs
        and vp, g/cm³ for rho. Other system unit isn't documented.
        fM: mode number, fundamental = 1 then 2, 3, 4, 5...
        ic: phase velocity search increment.
        f1: reserved parameter (always set to zero).
        h: frequency step for derivation.
        si_vp_vs_rho: must be set to True if vp, vs and rho respect the SI units
        (rho in kg/m^3, vp and vs in m/s). if False the units are assumed to be
        in g/cm^3 for rho, in km/s for vp and vs.
        t: the list of frequency inverses (period) according to compute the
        velocities.

    Returns:
        The velocities as a list of length == len(t).

    """
    return py_disp96_modfile(modfile, n, fS, fU, fM, ic, f1, h, si_vp_vs_rho, t, 1, 1, use_c_impl)
