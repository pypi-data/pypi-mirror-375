import jax.numpy as jnp
from jax import grad
from . import pulses
from . import aux_functions
from scipy.optimize import curve_fit

# Construction of the full NARP pulse in frequency domain

def frequency_field(
    f: jnp.ndarray,
    f_0: float,
    pulse_fwhm: float,
    pulse_area: float,
    pulse_type: int
) -> jnp.ndarray:
    """
    Pure pulse in the frequency domain.

    Args:
        f (jnp.ndarray): Frequencies array.
        f_0 (float): Pulse center frequency.
        pulse_fwhm (float): Pulse bandwidth (power profile).
        pulse_area (float): Pulse area.
        pulse_type (int): shape of the pulse in frequancy domain

    Return:
        jnp.ndarray: Evaluated pulse in the frequency domain.
    """
    return pulse_area*pulses.curve_shapes[pulse_type](f, f_0, pulse_fwhm/pulses.fmwh_const[pulse_type])

# Set chirp

def set_chirp(
    f: jnp.ndarray,
    f_field: jnp.ndarray,
    f_0: float,
    chirp_alpha: float,
    chrip_power: int = 1
) -> jnp.ndarray:
    """
    Set chirp to a pulse.

    Args:
        f (jnp.ndarray): Frequencies array.
        f_field (jnp.ndarray): Frequancy field array.
        f_0 (float): Chirp center frequency.
        chirp_alpha (float): alpha parameter of the chirp.
        chirp_power (int): Power of the instantaneous frequancy as a function of time.

    Return:
        jnp.ndarray: Chirped pulse in the frequency domain.
    """
    if chrip_power == 0:
        return f_field*jnp.exp(1j*chirp_alpha)
    else:
        return f_field*jnp.exp(1j*chirp_alpha*((2*jnp.pi*(f-f_0))**(chrip_power+1))/jnp.max(jnp.array([chrip_power+1, 1])))

# Set notch

def set_notch(
    f: jnp.ndarray,
    f_field: jnp.ndarray,
    f_0: float,
    notch_fwhm: float,
    notch_type: int = pulses.gaussian
) -> jnp.ndarray:
    """
    Set notch filter to a pulse.

    Args:
        f (jnp.ndarray): Frecuencies array.
        f_field (jnp.ndarray): Frequency field array.
        f_0 (float): notch center frequency.
        notch_fwhm (float): notch bandwidth.
        notch_type (int): notch shape

    Return:
        jnp.ndarray: Filtered pulse in frequency domain
    """
    return f_field*(1 - pulses.curve_shapes[notch_type](f, f_0, notch_fwhm/pulses.fmwh_const[notch_type]))

#Get the pulse in the temporal domain
def time_field(
    f: jnp.ndarray,
    f_field: jnp.ndarray,
    t: jnp.ndarray,
    t_0: float = 0
) -> jnp.ndarray:
    """
    Get the pulse in the temporal domain.
    Args:
        f (jnp.ndarray): Frequencies array.
        f_field (jnp.ndarray): Frequency field array.
        t (jnp.ndarray): Time array.
        t_0 (float): Center of the pulse.

        Return: 
            jnp.ndarray: Pulse in the temporal domain.
    """
    return aux_functions.vectorized_inverse_fourier(f, f_field, t-t_0)


#Set temporal limits for the time representation of the pulse

def set_time_limits(
    f: jnp.ndarray,
    f_field: jnp.ndarray,
    step: float,
    t_0: float = 0,
    eps: float = 1e-5,
    max_steps: int = 10_000,
    negative: bool = False
) -> float:
    """
    Function to set the correct time limits independent of pulse characteristics.

    Args:
        f: frequency domain.
        f_field: Pulse in frequency domain
        step (float): Size of the steps.
        t_0 (float): Center of the interval to search for the limit.
        eps (float): Minimum value of the function to set the limit.
        max_steps (float): Maximun number of iterations to find the limit.
    Return:
        float: Limit to evaluate the function and obtain the epsilon value.
    """
    func = lambda t: aux_functions.scalar_inverse_fourier(f, f_field, t)  

    return aux_functions.set_limits(func, step, t_0, eps, max_steps, negative)


#Set limits for the frequency representation of the pulse

def set_frequency_limits(
    f_0: float,
    pulse_fwhm: float,
    pulse_type: int,
    step: float,
    eps: float = 1e-5,
    max_steps: int = 10_000,
    negative: bool = False
) -> float:
    """
    Function to set the correct limits of a function.

    Args:
        f_0 (float): Center of the interval to search for the limit.
        pulse_fwhm (float): pulse width.
        pulse_type (int): Shape of the pulse in frequency.
        step (float): Size of the steps.
        eps (float): Minimum value of the function to set the limit.
        max_steps (float): Maximun number of iterations to find the limit.
    Return:
        float: Limit to evaluate the function and obtain the epsilon value.
    """

    func = lambda f: pulses.curve_shapes[pulse_type](f, f_0, pulse_fwhm/pulses.fmwh_const[pulse_type])

    return aux_functions.set_limits(func, step, f_0, eps, max_steps, negative)

#Get instantaneous frequency

def get_inst_frequency(
        f: jnp.ndarray,
        f_field: jnp.ndarray,
        t: jnp.ndarray,
        t_0: float):
    
    return aux_functions.aux_instantaneous_frequency(f, f_field, t-t_0)

#Calculate the wigner function of a pulse

def wigner_function(
    t_plot: jnp.ndarray,
    f_plot: jnp.ndarray,
    f_field: jnp.ndarray,
) -> jnp.ndarray:
    """
    Calculate the Wigner function using a vectorized approach.
    
    The Wigner function is defined as:
        W(t, f) = ∫ dt' E(t + t'/2) * conj(E(t - t'/2)) * exp(i * 2*pi * f * t')
    
    Args:
        t (jnp.ndarray): Time grid for both evaluation and integration.
        f (jnp.ndarray): Frequency grid (in Hz).
        f_field (jnp.ndarray): Frequency field.
        width (float): integration width.
    
    Returns:
        jnp.ndarray: Wigner function array with shape (len(t), len(f)).
    """
    return aux_functions.compute_wigner(t_plot, f_plot, f_plot, f_field)

def ftcf(
    t_plot: jnp.ndarray,
    f_plot: jnp.ndarray,
    f_field: jnp.ndarray
    ) -> jnp.ndarray:
    """
    Calculate frequency-time correlation function (FTCF) using a vectorized approach.
    Args:
        t_plot (jnp.ndarray): Time grid for both evaluation and integration.
        f_plot (jnp.ndarray): Frequency grid (in Hz).
        f_field (jnp.ndarray): Frequency field.
    Returns:
        jnp.ndarray: Frequency-time correlation function array with shape (len(t), len(f)).
    """
    return aux_functions.compute_wigner(t_plot, f_plot, f_plot, f_field)