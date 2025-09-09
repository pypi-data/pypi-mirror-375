# PyPulse

Una librería de Python para la construcción, análisis y visualización de pulsos, utilizando JAX para cálculos de alto rendimiento y GPU.
Instalación

Puedes instalar la librería directamente desde el repositorio de Git:

pip install git+[https://gitlab.com/jsierraj/pypulse.git](https://gitlab.com/jsierraj/pypulse.git)

## Uso

La librería pypulse ofrece una variedad de funciones para trabajar con pulsos en los dominios de la frecuencia y el tiempo, incluyendo:

    Generación de diferentes formas de pulso (Gaussiano, Lorentziano, etc.).

    Adición de chirp y filtros de muesca.

    Conversión entre los dominios de la frecuencia y el tiempo.

    Cálculo de la función de Wigner y la función de correlación tiempo-frecuencia (FTCF).

Aquí tienes un ejemplo básico de uso:

```python
import pypulse
import jax.numpy as jnp
import matplotlib.pyplot as plt
```

## Define parámetros del pulso

```python
f_0 = 0.1
pulse_fwhm = 0.0441
pulse_area = 100 * jnp.pi
pulse_type = pypulse.pulses.sech
```

## Construir el pulso en el dominio de la frecuencia

```python
f_lim = pypulse.set_frequency_limits(f_0, pulse_fwhm, pulse_type, pulse_fwhm / 10)
f = jnp.linspace(-f_lim, f_lim, 500) + f_0
frequency_pulse = pypulse.frequency_field(f, f_0, pulse_fwhm, pulse_area, pulse_type)
```

## Aplicar chirp
```python
chirp_power = 1
chirp_rate = 0.1 / pulse_fwhm**2
chirped_frequency_pulse = pypulse.set_chirp(f, frequency_pulse, f_0, chirp_rate, chirp_power)
```

## Aplicar Notch Filter
```python
notch_frequency = f_0
notch_width = pulse_fwhm / 10
notch_type = pypulse.pulses.gaussian
notched_frequency_pulse = pypulse.notch_filter(f, frequency_pulse, notch_frequency, notch_width, notch_type)
```

## Convertir al dominio del tiempo
```python
t_lim = pypulse.set_time_limits(f, frequency_pulse, 0.1 / pulse_fwhm)
t = jnp.linspace(-t_lim, t_lim, 500)
temporal_pulse = pypulse.time_field(f, frequency_pulse, t)
```

## Visualizar el pulso
```python
plt.plot(t, jnp.abs(temporal_pulse)**2, label='Intensidad Temporal')
plt.plot(f, jnp.abs(frequency_pulse)**2, label='Espectro de Intensidad')
plt.xlabel('Eje')
plt.ylabel('Intensidad')
plt.legend()
plt.show()
```

## Contribución

Si deseas contribuir a este proyecto, por favor, sigue las siguientes pautas:


## Licencia

