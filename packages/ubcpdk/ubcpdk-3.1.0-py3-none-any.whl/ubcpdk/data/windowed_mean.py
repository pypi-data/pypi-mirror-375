import numpy as np
import scipy.signal as sig


def windowed_mean(data: np.array, n: int = 60) -> np.array:
    """Returns the smoothen data using a window averaging of a 1d array.

    Args:
        data: data array.
        n: points per window.
    """
    dims = len(data.shape)
    s = sig.convolve(data, np.ones((2 * n + 1,) * dims), mode="same")
    d = sig.convolve(np.ones_like(data), np.ones((2 * n + 1,) * dims), mode="same")
    return s / d


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    from ubcpdk.config import PATH
    from ubcpdk.data.read_mat import read_mat

    wavelength, power = read_mat(PATH.ring_te_r3_g100)
    power_envelope = windowed_mean(power, 60)
    plt.plot(wavelength, power, label="power")
    plt.plot(wavelength, power_envelope, label="envelope")
    plt.legend()
    plt.show()
