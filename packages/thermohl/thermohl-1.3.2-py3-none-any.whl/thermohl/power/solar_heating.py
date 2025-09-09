# SPDX-FileCopyrightText: 2025 RTE (https://www.rte-france.com)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

from typing import List, Optional, Any

import numpy as np

from thermohl import floatArrayLike, intArrayLike, sun
from thermohl.power.power_term import PowerTerm


class _SRad:
    """Solar radiation calculator."""

    def __init__(self, clean: List[float], indus: List[float]):
        """Initialize the solar radiation calculator.

        Args:
            clean (list[float]): Coefficients for the polynomial function to compute atmospheric turbidity in clean air conditions.
            indus (list[float]): Coefficients for the polynomial function to compute atmospheric turbidity in industrial (polluted) air conditions.
        """
        self.clean = clean
        self.indus = indus

    def catm(
        self, x: floatArrayLike, trb: Optional[floatArrayLike] = 0.0
    ) -> floatArrayLike:
        """Compute coefficient for atmosphere turbidity.
        This method calculates the atmospheric turbidity coefficient using a polynomial
        function of the solar altitude. The coefficients of the polynomial are a weighted
        average of the clean air and industrial air coefficients, with the weights
        determined by the turbidity factor.

        Args:
            x (float | numpy.ndarray): Solar altitude in degrees.
            trb (float | numpy.ndarray): Atmospheric turbidity factor (0 for clean air, 1 for industrial air).

        Returns:
            float | numpy.ndarray: Coefficient for atmospheric turbidity.
        """
        omt = 1.0 - trb
        A = omt * self.clean[6] + trb * self.indus[6]
        B = omt * self.clean[5] + trb * self.indus[5]
        C = omt * self.clean[4] + trb * self.indus[4]
        D = omt * self.clean[3] + trb * self.indus[3]
        E = omt * self.clean[2] + trb * self.indus[2]
        F = omt * self.clean[1] + trb * self.indus[1]
        G = omt * self.clean[0] + trb * self.indus[0]
        return A * x**6 + B * x**5 + C * x**4 + D * x**3 + E * x**2 + F * x**1 + G

    def __call__(
        self,
        lat: floatArrayLike,
        alt: floatArrayLike,
        azm: floatArrayLike,
        trb: floatArrayLike,
        month: intArrayLike,
        day: intArrayLike,
        hour: floatArrayLike,
    ) -> floatArrayLike:
        """Compute solar radiation."""
        sa = sun.solar_altitude(lat, month, day, hour)
        sz = sun.solar_azimuth(lat, month, day, hour)
        th = np.arccos(np.cos(sa) * np.cos(sz - azm))
        K = 1.0 + 1.148e-04 * alt - 1.108e-08 * alt**2
        Q = self.catm(np.rad2deg(sa), trb)
        sr = K * Q * np.sin(th)
        return np.where(sr > 0.0, sr, 0.0)


class SolarHeatingBase(PowerTerm):
    """Solar heating term."""

    def __init__(
        self,
        lat: floatArrayLike,
        alt: floatArrayLike,
        azm: floatArrayLike,
        tb: floatArrayLike,
        month: intArrayLike,
        day: intArrayLike,
        hour: floatArrayLike,
        D: floatArrayLike,
        alpha: floatArrayLike,
        est: _SRad,
        srad: Optional[floatArrayLike] = None,
        **kwargs: Any,
    ):
        self.alpha = alpha
        if srad is None:
            self.srad = est(np.deg2rad(lat), alt, np.deg2rad(azm), tb, month, day, hour)
        else:
            self.srad = np.maximum(srad, 0.0)
        self.D = D

    def value(self, T: floatArrayLike) -> floatArrayLike:
        r"""Compute solar heating.

        Args:
            T (float | numpy.ndarray): Conductor temperature (°C).

        Returns:
            float | numpy.ndarray: Power term value (W·m⁻¹).

        """
        return self.alpha * self.srad * self.D * np.ones_like(T)

    def derivative(self, conductor_temperature: floatArrayLike) -> floatArrayLike:
        """Compute solar heating derivative."""
        return np.zeros_like(conductor_temperature)
