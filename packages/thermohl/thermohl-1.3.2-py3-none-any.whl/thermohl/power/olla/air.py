# SPDX-FileCopyrightText: 2025 RTE (https://www.rte-france.com)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

import numpy as np

from thermohl import floatArrayLike

_zerok = 273.15


def kelvin(t: floatArrayLike) -> floatArrayLike:
    return t + _zerok


class Air:
    """`Wikipedia <https://fr.wikipedia.org/wiki/Air> models."""

    @staticmethod
    def volumic_mass(Tc: floatArrayLike, alt: floatArrayLike = 0.0) -> floatArrayLike:
        r"""
        Compute air volumic mass.

        If both inputs are numpy arrays, they should have the same size.

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius).
            alt (float | numpy.ndarray, optional): Altitude above sea-level. The default is 0.

        Returns:
            float | numpy.ndarray: Volumic mass in kg·m⁻³.

        """
        Tk = kelvin(Tc)
        return 1.292 * _zerok * np.exp(-3.42e-02 * alt / Tk) / Tk

    @staticmethod
    def dynamic_viscosity(Tc: floatArrayLike) -> floatArrayLike:
        r"""Compute air dynamic viscosity.

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius)

        Returns:
            float | numpy.ndarray: Dynamic viscosity in kg·m⁻¹·s⁻¹.

        """
        Tk = kelvin(Tc)
        return 8.8848e-15 * Tk**3 - 3.2398e-11 * Tk**2 + 6.2657e-08 * Tk + 2.3543e-06

    @staticmethod
    def kinematic_viscosity(
        Tc: floatArrayLike, alt: floatArrayLike = 0.0
    ) -> floatArrayLike:
        r"""Compute air kinematic viscosity.

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius)
            alt (float | numpy.ndarray, optional): Altitude above sea-level. The default is 0.

        Returns:
            float | numpy.ndarray: Kinematic viscosity in m²·s⁻¹.

        """
        return Air.dynamic_viscosity(Tc) / Air.volumic_mass(Tc, alt=alt)

    @staticmethod
    def thermal_conductivity(Tc: floatArrayLike) -> floatArrayLike:
        r"""Compute air thermal conductivity.

        The output is valid for input in [-150, 1300] range (in Celsius)

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius)

        Returns:
            float | numpy.ndarray: Thermal conductivity in W·m⁻¹·K⁻¹.

        """
        Tk = kelvin(Tc)
        return 1.5207e-11 * Tk**3 - 4.8570e-08 * Tk**2 + 1.0184e-04 * Tk - 3.9333e-04
