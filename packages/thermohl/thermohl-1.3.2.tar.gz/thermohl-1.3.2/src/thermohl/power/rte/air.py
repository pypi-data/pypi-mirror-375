# SPDX-FileCopyrightText: 2025 RTE (https://www.rte-france.com)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

from thermohl import floatArrayLike


class Air:
    """Air quantities."""

    @staticmethod
    def volumic_mass(Tc: floatArrayLike, alt: floatArrayLike = 0.0) -> floatArrayLike:
        r"""Compute air volumic mass.

        If both inputs are numpy arrays, they should have the same size.

        Args:
            Tc (float | numpy.ndarray): Air temperature (°C).
            alt (float | numpy.ndarray, optional): Altitude above sea level (m). The default is 0.

        Returns:
            float | numpy.ndarray: Volumic mass in kg·m⁻³.

        """
        return (1.293 - 1.525e-04 * alt + 6.379e-09 * alt**2) / (1.0 + 0.00367 * Tc)

    @staticmethod
    def dynamic_viscosity(Tc: floatArrayLike) -> floatArrayLike:
        r"""Compute air dynamic viscosity.

        Args:
            Tc (float | numpy.ndarray): Air temperature (°C)

        Returns:
            float | numpy.ndarray: Dynamic viscosity in kg·m⁻¹·s⁻¹.

        """
        return (1.458e-06 * (Tc + 273.0) ** 1.5) / (Tc + 383.4)

    @staticmethod
    def thermal_conductivity(Tc: floatArrayLike) -> floatArrayLike:
        r"""Compute air thermal conductivity.

        Args:
            Tc (float | numpy.ndarray): Air temperature (°C)

        Returns:
            float | numpy.ndarray: Thermal conductivity in W·m⁻¹·K⁻¹.

        """
        return 2.424e-02 + 7.477e-05 * Tc - 4.407e-09 * Tc**2
