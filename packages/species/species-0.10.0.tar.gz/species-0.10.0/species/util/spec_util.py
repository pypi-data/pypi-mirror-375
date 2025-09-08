"""
Utility functions for manipulating spectra.
"""

import warnings

from math import ceil
from typing import Tuple, Union

import numpy as np

from scipy.ndimage import gaussian_filter
from typeguard import typechecked


@typechecked
def create_wavelengths(
    wavel_range: Tuple[Union[float, np.float32], Union[float, np.float32]],
    wavel_sampling: float,
) -> np.ndarray:
    """
    Function for creating logarithmically-spaced wavelengths,
    so with a constant :math:`\\lambda/\\Delta\\lambda`.

    Parameters
    ----------
    wavel_range : tuple(float, float)
        Wavelength range (:math:`\\mu\\mathrm{m}`). Tuple with the
        minimum and maximum wavelength.
    wavel_sampling : float
        Wavelength sampling :math:`\\lambda/\\Delta\\lambda`.

    Returns
    -------
    np.ndarray
        Array with the wavelengths (:math:`\\mu\\mathrm{m}`). Since
        the wavelength boundaries are fixed, the output sampling
        is slightly different from the value provided as
        argument of ``wavel_sampling``.
    """

    n_test = 100

    wavel_test = np.logspace(np.log10(wavel_range[0]), np.log10(wavel_range[1]), n_test)
    sampling_test = 0.5 * (wavel_test[1:] + wavel_test[:-1]) / np.diff(wavel_test)

    # math.ceil returns int, but np.ceil returns float
    wavel_array = np.logspace(
        np.log10(wavel_range[0]),
        np.log10(wavel_range[1]),
        ceil(n_test * wavel_sampling / np.mean(sampling_test)) + 1,
    )

    # Check wavelength sampling, lambda/D_lambda, of the created array
    # res_out = np.mean(0.5*(wavel_array[1:]+wavel_array[:-1])/np.diff(wavel_array))

    return wavel_array


@typechecked
def smooth_spectrum(
    wavelength: np.ndarray,
    flux: np.ndarray,
    spec_res: float,
    kernel_size: int = 11,
    force_smooth: bool = False,
) -> np.ndarray:
    """
    Function for smoothing a spectrum with a Gaussian kernel to a
    fixed spectral resolution. The kernel size is set to 5 times the
    FWHM of the Gaussian. The FWHM of the Gaussian is equal to the
    ratio of the wavelength and the spectral resolution. If the
    kernel does not fit within the available wavelength grid (i.e.
    at the edge of the array) then the flux values are set to NaN.

    Parameters
    ----------
    wavelength : np.ndarray
        Wavelength points (um). Should be sampled with constant
        logarithmic steps (i.e. fixed :math:`\\lambda/\\Delta\\lambda`)
        or sampled with a uniform linear spacing. The latter
        implementation is slow so the first is preferred.
    flux : np.ndarray
        Flux (W m-2 um-1).
    spec_res : float
        Spectral resolution.
    kernel_size : int
        Kernel size (odd integer). Only used when the wavelengths
        are linearly sampled. Not used by the function.
    force_smooth : bool
        Force the smoothing for logarithmically spaced wavelengths.

    Returns
    -------
    np.ndarray
        Smoothed spectrum (W m-2 um-1).
    """

    def _gaussian(kernel_size, sigma):
        pos = range(-(kernel_size - 1) // 2, (kernel_size - 1) // 2 + 1)
        kernel = [
            np.exp(-float(x) ** 2 / (2.0 * sigma**2)) / (sigma * np.sqrt(2.0 * np.pi))
            for x in pos
        ]

        return np.asarray(kernel / sum(kernel))

    spacing = np.mean(2.0 * np.diff(wavelength) / (wavelength[1:] + wavelength[:-1]))
    spacing_std = np.std(2.0 * np.diff(wavelength) / (wavelength[1:] + wavelength[:-1]))

    if spacing_std / spacing < 1e-2 or force_smooth:
        # delta_lambda of resolution element is
        # FWHM of the LSF's standard deviation
        sigma_lsf = 1.0 / spec_res / (2.0 * np.sqrt(2.0 * np.log(2.0)))

        # Calculate the sigma to be used with the Gaussian filter
        # in units of the input wavelength bins
        sigma_filter = sigma_lsf / spacing

        flux_smooth = gaussian_filter(flux, sigma=sigma_filter, mode="nearest")

    else:
        flux_smooth = np.zeros(flux.shape)  # (W m-2 um-1)

        spacing = np.mean(np.diff(wavelength))  # (um)
        spacing_std = np.std(np.diff(wavelength))  # (um)

        if spacing_std / spacing > 1e-2:
            warnings.warn(
                "The wavelength spacing is not uniform "
                f"(lambda/d_lambda = {spacing} +/- {spacing_std}). "
                "The smoothing with the Gaussian kernel requires "
                "either the spectral resolution or the wavelength "
                "spacing to be uniformly sampled. This warning "
                "should not have occurred with any of the model "
                "grids provided by species. Please open an issue "
                "on the Github page if help is needed."
            )

        for i, item in enumerate(wavelength):
            fwhm = item / spec_res  # (um)
            sigma = fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))  # (um)

            # Kernel size 5 times the width of the LSF
            kernel_size = int(5.0 * sigma / spacing)

            if kernel_size % 2 == 0:
                kernel_size += 1

            gaussian = _gaussian(kernel_size, sigma / spacing)

            try:
                flux_smooth[i] = np.sum(
                    gaussian
                    * flux[i - (kernel_size - 1) // 2 : i + (kernel_size - 1) // 2 + 1]
                )

            except ValueError:
                flux_smooth[i] = np.nan

    return flux_smooth
