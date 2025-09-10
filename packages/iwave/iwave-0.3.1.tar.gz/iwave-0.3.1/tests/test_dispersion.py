import numpy as np
from iwave import dispersion, spectral

def test_dispersion(img_windows_norm):
    """Check shape of dispersion result."""
    kt, ky, kx = spectral.wave_numbers(img_windows_norm.shape, res=0.01, fps=25)
    kt_gw, kt_turb = dispersion.dispersion(ky, kx, velocity=[1, 0], depth=1, vel_indx=1)
    # test if the size of kt_gw is 1 x dim_y x dim_x
    assert kt_gw.shape == (
        (1, img_windows_norm.shape[-2], img_windows_norm.shape[-1])
    )

def test_intensity(img_windows_norm):
    """Check shape of intensity result."""
    kt, ky, kx = spectral.wave_numbers(img_windows_norm.shape, res=0.01, fps=25)
    kt_gw, kt_turb = dispersion.dispersion(ky, kx, velocity=[1, 0], depth=1, vel_indx=1)
    th_spectrum = dispersion.theoretical_spectrum(kt_gw, kt_turb, kt, gauss_width=1, gravity_waves_switch=True, turbulence_switch=True)
    measured_spectrum = spectral._numpy_fourier_transform(img_windows_norm)
    # test if the size of the theoretical spectrum is equal to the size of the spectrum measured with numba
    assert th_spectrum.shape == (
    (int(np.ceil(measured_spectrum.shape[-3] / 2)), measured_spectrum.shape[-2], measured_spectrum.shape[-1])
    )
        
    
def test_downsample(img_windows_norm):
    """Check shape of intensity result."""
    img_single_window = img_windows_norm[0]
    full_spectrum = spectral._numpy_fourier_transform(img_single_window)
    trimmed_spectrum, res, fps, window_dims = dispersion.spectrum_downsample(full_spectrum, res=0.01, fps=25, window_dims=img_single_window.shape, downsample=2)
    downsampled_img = img_single_window[:, ::2, ::2]
    downsampled_spectrum = spectral._numpy_fourier_transform(downsampled_img)
    assert trimmed_spectrum.shape == downsampled_spectrum.shape