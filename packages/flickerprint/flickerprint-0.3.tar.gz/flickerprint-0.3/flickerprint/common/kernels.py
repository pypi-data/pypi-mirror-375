#!/usr/bin/env python
from scipy.ndimage import filters
from dataclasses import dataclass
import numpy as np

""" Kernels used for estimating the gradient of the image. """


@dataclass
class Kernels:
    """ Implemenation of two seperable kernels that represent a gradient estimations. """

    xx: np.ndarray
    xy: np.ndarray
    yx: np.ndarray
    yy: np.ndarray
    label: str

    def gradient_x(self, image):
        """ Apply the x kernels to get the gradient in the x direction. """
        return apply_seperable_kernel(image, self.xx, self.xy)

    def gradient_y(self, image):
        """ Apply the y kernels to get the gradient in the x direction. """
        return apply_seperable_kernel(image, self.yx, self.yy)


def apply_seperable_kernel(image, v_1, v_2):
    """ Apply a separable kernel G to an image where K = v_2 * v_1.

    Namely, v_1 is applied to the image first. """
    output = np.zeros_like(image)
    filter_kwargs = dict(mode="reflect", cval=0, origin=0)

    filters.correlate1d(image, v_1, 1, output, **filter_kwargs)
    filters.correlate1d(output, v_2, 0, output, **filter_kwargs)
    return output

fourth_order = Kernels(
    np.array([1, -8, 0, 8, -1]) / 12.0,
    [1],
    [1],
    np.array([1, -8, 0, 8, -1]) / 12.0,
    "Central fourth order",
)
