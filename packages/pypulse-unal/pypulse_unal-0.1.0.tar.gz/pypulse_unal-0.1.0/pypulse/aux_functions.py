import jax.numpy as jnp
from jax import vmap, jit, lax
from functools import partial
from _collections_abc import Callable

# Inverse Fourier for time pulse generation

@partial(jit) 
def scalar_inverse_fourier(
    f: jnp.ndarray,
    f_field: jnp.ndarray,
    t: float,
) -> float:
    """
    NARP pulse for an scalar time.

    Args:
        f (jnp.ndarray): Frequencies array.
        f_field (float): Pulse in frequency domain.
        t (float): Point in time to evaluate the field.

    Return:
        float: Evaluated pulse pulse in the time domain.
    """

    df = jnp.gradient(f)
    integrand = f_field*jnp.exp(-1j*2*jnp.pi*f*t)
    return jnp.sum(integrand*df)

vectorized_inverse_fourier = vmap(
    scalar_inverse_fourier, 
    in_axes=(None, None, 0)
)

#Instantaneous frequency
@partial(jit)
def scalar_instantaneous_frequency(
    f: jnp.ndarray,
    f_field: jnp.ndarray,
    t: float,
) -> float:
    """
    Instantaneous frequency of a pulse.

    Args:
        f (jnp.ndarray): Frequencies array.
        f_field (float): Pulse in frequency domain.
        t (float): Point in time to evaluate the field.

    Return:
        float: Instantaneous frequency of the pulse.
    """

    E =  scalar_inverse_fourier(f, f_field, t)
    grad_E = scalar_inverse_fourier(f, -2j*jnp.pi*f*f_field, t)
    
    return -jnp.imag(grad_E/E) / (2*jnp.pi)  # Instantaneous frequency in Hz

aux_instantaneous_frequency = vmap(
    scalar_instantaneous_frequency,
    in_axes=(None, None, 0)
)

#Set limits for a function

def set_limits(
    func: Callable,
    step: float,
    f_0: float,
    eps: float = 1e-5,
    max_steps = 10_000,
    negative: bool = False,
) -> float:
    """
    Function to set the correct limits of a function.

    Args:
        func (Callable): function.
        step (float): Size of the steps.
        f_0 (float): Center of the interval to search for the limit.
        eps (float): Minimum value of the function to set the limit.
        max_steps (float): Maximun number of iterations to find the limit.
    Return:
        float: Limit to evaluate the function and obtain the epsilon value.
    """

    field_0 = jnp.abs(func(f_0))
    sgn = -1 if negative else 1

    for n in range(max_steps):
        if jnp.abs(func(f_0+sgn*n*step))/field_0 < eps:
            return n*step
        
    print('Maximun number of iterations reached')
    return max_steps*step

#Calculate wigner fuction of a pulse


def compute_wigner(
    t_plot: jnp.ndarray,
    f_plot: jnp.ndarray,
    f_arr: jnp.ndarray,
    f_field: jnp.ndarray,
) -> jnp.ndarray:
    """
    Compute the Wigner function on the grid defined by t_plot and f_plot using an
    optimized integration loop to reduce memory usage.

    Args:
        t_plot (jnp.ndarray): Time array used for field evaluation.
        f_plot (jnp.ndarray): Frequency array for the Wigner function.
        f_arr (jnp.ndarray): Frequency array for the inverse Fourier transform.
        f_field (jnp.ndarray): Field in the frequency domain.
    
    Returns:
        jnp.ndarray: 2D array of the Wigner function with shape (len(t_plot), len(f_plot)).
    """

    # For each t and f, compute the integrated value via a for-loop over tau.
    def wigner_at(t, f):
        # Choose integration width so that the shifted time arguments lie in t_plot.
        width = 2 * jnp.maximum(jnp.abs(t - t_plot[0]), jnp.abs(t_plot[-1] - t))
        # Use the same resolution as t_plot for integration.
        N_tau = t_plot.size
        tau = jnp.linspace(-width, width, num=N_tau)
        dtau = tau[1] - tau[0]

        def body_fun(i, acc):
            # For each tau[i], evaluate the field at shifted times.
            tau_i = tau[i]
            t_plus = t + tau_i / 2
            t_minus = t - tau_i / 2
            # time_field expects an array, so wrap scalar in jnp.array and extract output.
            E_plus = vectorized_inverse_fourier(f_arr, f_field, jnp.array([t_plus]))[0]
            E_minus = vectorized_inverse_fourier(f_arr, f_field, jnp.array([t_minus]))[0]
            integrand = E_plus * jnp.conjugate(E_minus) * jnp.exp(2j * jnp.pi * tau_i * f)
            return acc + integrand

        integral = lax.fori_loop(0, N_tau, body_fun, 0.0)
        return integral * dtau

    # Vectorize over frequency first, then over time.
    wigner_over_f = vmap(wigner_at, in_axes=(None, 0))
    wigner_over_t = vmap(wigner_over_f, in_axes=(0, None))
    return wigner_over_t(t_plot, f_plot)


def compute_ftcf(
    t_plot: jnp.ndarray,
    f_plot: jnp.ndarray,
    f_arr: jnp.ndarray,
    f_field: jnp.ndarray,
) -> jnp.ndarray:
    """
    Compute the ft - correlation function on the grid defined by t_plot and f_plot using an
    optimized integration loop to reduce memory usage.

    Args:
        t_plot (jnp.ndarray): Time array used for field evaluation.
        f_plot (jnp.ndarray): Frequency array for the Wigner function.
        f_arr (jnp.ndarray): Frequency array for the inverse Fourier transform.
        f_field (jnp.ndarray): Field in the frequency domain.
    
    Returns:
        jnp.ndarray: 2D array of the Wigner function with shape (len(t_plot), len(f_plot)).
    """

    # For each t and f, compute the integrated value via a for-loop over tau.
    def ftcf_at(t, f):
        # Choose integration width so that the shifted time arguments lie in t_plot.
        width = 2 * jnp.maximum(jnp.abs(t - t_plot[0]), jnp.abs(t_plot[-1] - t))
        # Use the same resolution as t_plot for integration.
        N_tau = t_plot.size
        tau = jnp.linspace(0, width, num=N_tau)
        dtau = tau[1] - tau[0]

        def body_fun(i, acc):
            # For each tau[i], evaluate the field at shifted times.
            tau_i = tau[i]
            t_plus = t + tau_i
            t_minus = t
            # time_field expects an array, so wrap scalar in jnp.array and extract output.
            E_plus = vectorized_inverse_fourier(f_arr, f_field, jnp.array([t_plus]))[0]
            E_minus = vectorized_inverse_fourier(f_arr, f_field, jnp.array([t_minus]))[0]
            integrand = E_plus * jnp.conjugate(E_minus) * jnp.exp(2j * jnp.pi * tau_i * f)
            return acc + integrand

        integral = lax.fori_loop(0, N_tau, body_fun, 0.0)
        return integral * dtau

    # Vectorize over frequency first, then over time.
    ftcf_over_f = vmap(ftcf_at, in_axes=(None, 0))
    ftcf_over_t = vmap(ftcf_over_f, in_axes=(0, None))
    return ftcf_over_t(t_plot, f_plot)

#factor
def factor(x, a): return a*x