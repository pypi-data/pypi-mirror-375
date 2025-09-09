# SPDX-FileCopyrightText: 2025 RTE (https://www.rte-france.com)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

from typing import Any

import numpy as np

from thermohl import floatArrayLike
from thermohl.power import PowerTerm


class JouleHeating(PowerTerm):
    """Joule heating term."""

    @staticmethod
    def _c(
        TLow: floatArrayLike,
        THigh: floatArrayLike,
        RDCLow: floatArrayLike,
        RDCHigh: floatArrayLike,
    ) -> floatArrayLike:
        return (RDCHigh - RDCLow) / (THigh - TLow)

    def __init__(
        self,
        I: floatArrayLike,
        TLow: floatArrayLike,
        THigh: floatArrayLike,
        RDCLow: floatArrayLike,
        RDCHigh: floatArrayLike,
        **kwargs: Any,
    ):
        r"""Init with args.

        If more than one input are numpy arrays, they should have the same size.

        Args:
            I (float | numpy.ndarray): Transit intensity (A).
            TLow (float | numpy.ndarray): Temperature for RDCLow measurement (°C).
            THigh (float | numpy.ndarray): Temperature for RDCHigh measurement (°C).
            RDCLow (float | numpy.ndarray): Electric resistance per unit length at TLow (Ω·m⁻¹).
            RDCHigh (float | numpy.ndarray): Electric resistance per unit length at THigh (Ω·m⁻¹).

        """
        self.TLow = TLow
        self.THigh = THigh
        self.RDCLow = RDCLow
        self.RDCHigh = RDCHigh
        self.I = I
        self.c = JouleHeating._c(TLow, THigh, RDCLow, RDCHigh)

    def _rdc(self, T: floatArrayLike) -> floatArrayLike:
        return self.RDCLow + self.c * (T - self.TLow)

    def value(self, T: floatArrayLike) -> floatArrayLike:
        r"""Compute joule heating.

        Args:
            T (float | numpy.ndarray): Conductor temperature (°C).

        Returns:
            float | numpy.ndarray: Power term value (W·m⁻¹).

        """
        return self._rdc(T) * self.I**2

    def derivative(self, conductor_temperature: floatArrayLike) -> floatArrayLike:
        r"""Compute joule heating derivative.

        If more than one input are numpy arrays, they should have the same size.

        Args:
            conductor_temperature (float | numpy.ndarray): Conductor temperature (°C).

        Returns:
            float | numpy.ndarray: Power term derivative (W·m⁻¹·K⁻¹).

        """
        return self.c * self.I**2 * np.ones_like(conductor_temperature)
