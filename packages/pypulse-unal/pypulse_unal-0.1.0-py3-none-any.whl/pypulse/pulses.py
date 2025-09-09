import jax.numpy as jnp
from jax import jit

# Definition of curve Shapes
@jit
def gaussian_curve(
    f: jnp.ndarray,
    f_0: float,
    gamma_0: float
) -> jnp.ndarray:
    """
    Gaussian pulse defined in frequency space.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        gamma_0 (float): Pulse bandwidth. This bandwidth is defined equal to the FWHM
            of the square of the electric field in the frequency domain (power profile).

    Returns:
        jnp.ndarray: Evaluated electric field in frequency domain.
    """
    return jnp.exp(-0.5*((f-f_0)/gamma_0)**2)

@jit
def lorentzian_curve(
    f: jnp.ndarray,
    f_0: float,
    gamma_0: float
) -> jnp.ndarray:
    """
    Lorentzian pulse defined in frequency space.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        gamma_0 (float): Pulse bandwidth. This bandwidth is defined equal to the FWHM
            of the square of the electric field in the frequency domain (power profile)..

    Returns:
        jnp.ndarray: Evaluated electric field in frequency domain.
    """
    return 1/(1+((f-f_0)/gamma_0)**2)

@jit
def psquare_curve(
    f: jnp.ndarray,
    f_0: float,
    gamma_0: float,
    smoothness: float = 0.005
) -> jnp.ndarray:
    """
    Smoothed square pulse defined in frequency space.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        gamma_0 (float): Pulse bandwidth. This bandwidth is defined equal to the FWHM
            of the square of the electric field in the frequency domain (power profile).

    Returns:
        jnp.ndarray: evaluated electric field in frequency domain.
    """
    left_edge = 1/(1+jnp.exp(-(f-(f_0-gamma_0))/(gamma_0*smoothness)))
    right_edge = 1/(1+jnp.exp((f-(f_0+gamma_0))/(gamma_0*smoothness)))
    return left_edge*right_edge

@jit
def sech_curve(
    f: jnp.ndarray,
    f_0: float,
    gamma_0: float
) -> jnp.ndarray:
    """
    Sech pulse defined in frequency space.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        gamma_0 (float): Pulse bandwidth. This bandwidth is defined equal to the FWHM
            of the square of the electric field in the frequency domain (power profile).

    Returns:
        jnp.ndarray: Evaluated electric field in frequency domain.
    """
    return 1/jnp.cosh((f-f_0)/gamma_0)

@jit
def sech2_curve(
    f: jnp.ndarray,
    f_0: float,
    gamma_0: float
) -> jnp.ndarray:
    """
    Sech^2 pulse defined in frequency space.

    Args:
        f (jnp.ndarray): Frequencies array [PHz].
        f_0 (float): Pulse center frequency [PHz].
        gamma_0 (float): Pulse bandwidth. This bandwidth is defined equal to the FWHM
            of the square of the electric field in the frequency domain (power profile).

    Returns:
        jnp.ndarray: Evaluated electric field in frequency domain.
    """
    return 1/jnp.cosh((f-f_0)/gamma_0)**2


#For selecting curve type
gaussian = 0
lorentzian = 1
square = 2
sech = 3
sech2 = 4

curve_shapes = [gaussian_curve, 
                lorentzian_curve, 
                psquare_curve, 
                sech_curve,
                sech2_curve]

fmwh_const = [2*jnp.sqrt(jnp.log(2)),                                  #gaussian 
              2*jnp.sqrt(jnp.sqrt(2)-1),                               #lorentzian
              2,                                                       #square
              2*jnp.log(jnp.sqrt(2)+1),                                #sech
              2*jnp.log(jnp.power(2, .25)+jnp.sqrt(jnp.sqrt(2)-1))]    #sech2
