import numpy as np
import scipy as sp
from scipy.stats import norm

phi = norm.cdf


def positive_normal_mgf(t: float, mu: float, sigma2: float) -> float:
    sigma = np.sqrt(sigma2)
    return (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2))) * (phi((mu / sigma) - sigma * t) / phi(mu / sigma))


def positive_normal_mgf_derivative(t: float, mu: float, sigma2: float) -> float:
    sigma = np.sqrt(sigma2)
    intermediate_value_1 = (
        -mu
        * (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2)))
        * (phi((mu / sigma) - sigma * t) / phi(mu / sigma))
    )
    intermediate_value_2 = (
        sigma2
        * t
        * (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2)))
        * (phi((mu / sigma) - sigma * t) / phi(mu / sigma))
    )
    intermediate_value_3 = (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2))) * (
        -sigma * np.exp(-(((mu / sigma) - sigma * t) ** 2) / 2) / (phi(mu / sigma) * np.sqrt(2 * np.pi))
    )
    return intermediate_value_1 + intermediate_value_2 + intermediate_value_3


def positive_normal_mgf_derivative2(t: float, mu: float, sigma2: float) -> float:
    sigma = np.sqrt(sigma2)
    intermediate_value_1 = (
        mu**2
        * (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2)))
        * (phi((mu / sigma) - sigma * t) / phi(mu / sigma))
    )
    intermediate_value_2 = (
        -mu
        * sigma2
        * t
        * (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2)))
        * (phi((mu / sigma) - sigma * t) / phi(mu / sigma))
    )
    intermediate_value_3 = (
        -mu
        * (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2)))
        * (-sigma * np.exp(-(((mu / sigma) - sigma * t) ** 2) / 2))
        / (phi(mu / sigma) * np.sqrt(2 * np.pi))
    )
    intermediate_value_4 = (
        sigma2
        * (sigma2 * t**2 + 1)
        * (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2)))
        * (phi((mu / sigma) - sigma * t) / phi(mu / sigma))
    )
    intermediate_value_5 = (
        sigma2
        * t
        * (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2)))
        * (-sigma * np.exp(-(((mu / sigma) - sigma * t) ** 2) / 2))
        / (phi(mu / sigma) * np.sqrt(2 * np.pi))
    )
    intermediate_value_6 = (
        (np.exp(-mu * t) * np.exp((1 / 2) * (sigma2) * (t**2)))
        * (-sigma * np.exp(-(((mu / sigma) - sigma * t) ** 2) / 2) / (phi(mu / sigma) * np.sqrt(2 * np.pi)))
        * (mu - sigma2 * t)
    )
    return (
        intermediate_value_1
        + 2 * intermediate_value_2
        + 2 * intermediate_value_3
        + intermediate_value_4
        + 2 * intermediate_value_5
        + intermediate_value_6
    )


def exponential_mgf(t: float, lam: float) -> float:
    return lam / (lam + t)


def exponential_mgf_derivative(t: float, lam: float) -> float:
    return lam / ((lam + t) ** 2)


def exponential_mgf_derivative2(t: float, lam: float) -> float:
    return -2 * lam / ((lam + t) ** 3)


def uniform_mgf(t: float, start: float, stop: float) -> float:
    return 1 if np.isclose(t, 0) else (np.exp(-1 * t * stop) - np.exp(-1 * t * start)) / (-1 * t * (stop - start))


def uniform_mgf_derivative(t: float, start: float, stop: float) -> float:
    return (
        (start + stop) / 2
        if np.isclose(t, 0)
        else (np.exp(-1 * t * start) * (start * t + 1) - np.exp(-1 * t * stop) * (stop * t + 1))
        / ((t**2) * (stop - start))
    )


def uniform_mgf_derivative2(t: float, start: float, stop: float) -> float:
    return (
        (start**2 + start * stop + stop**2)
        if np.isclose(t, 0)
        else (
            np.exp(-1 * t * start) * ((start**2) * (t**2) + 2 * start * t + 2)
            - np.exp(-1 * t * stop) * ((stop**2) * (t**2) + 2 * stop * t + 2)
        )
        / ((t**3) * (stop - start))
    )


def poisson_mgf(t: float, lam: float) -> float:
    return np.exp(lam * (np.exp(-1 * t) - 1))


def poisson_mgf_derivative(t: float, lam: float) -> float:
    return -1 * lam * np.exp(lam * (np.exp(-1 * t) - 1) - t)


def poisson_mgf_derivative2(t: float, lam: float) -> float:
    return (lam + np.exp(t)) * lam * np.exp(lam * (np.exp(-1 * t) - 1) - 2 * t)


def absolute_cauchy_mgf(t: float, sigma2: float) -> float:
    sigma = np.sqrt(sigma2)
    sin_integral, cos_integal = sp.special.sici(t * sigma)
    return (
        1
        if np.isclose(t, 0)
        else (1 / np.pi) * (2 * cos_integal * np.sin(t * sigma) + np.cos(t * sigma) * (np.pi - 2 * sin_integral))
    )


def absolute_cauchy_mgf_derivative(t: float, sigma2: float) -> float:
    sigma = np.sqrt(sigma2)
    sin_integral, cos_integal = sp.special.sici(t * sigma)
    return (sigma / np.pi) * (2 * np.cos(t * sigma) * cos_integal - np.sin(t * sigma) * (np.pi - 2 * sin_integral))


def absolute_cauchy_mgf_derivative2(t: float, sigma2: float) -> float:
    sigma = np.sqrt(sigma2)
    sin_integral, cos_integal = sp.special.sici(t * sigma)
    return (sigma / (t * np.pi)) * (
        2 - 2 * t * sigma * cos_integal * np.sin(t * sigma) - t * sigma * np.cos(t * sigma) * (np.pi - 2 * sin_integral)
    )
