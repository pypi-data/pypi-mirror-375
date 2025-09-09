# SPDX-FileCopyrightText: 2025 RTE (https://www.rte-france.com)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

import numpy as np

from thermohl import floatArrayLike


class Air:
    """CIGRE air models."""

    @staticmethod
    def volumic_mass(Tc: floatArrayLike, alt: floatArrayLike = 0.0) -> floatArrayLike:
        r"""Compute air volumic mass.

        If both inputs are numpy arrays, they should have the same size.

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius).
            alt (float | numpy.ndarray, optional): Altitude above sea-level. The default is 0.

        Returns:
            float | numpy.ndarray: Volumic mass in kg·m⁻³.

        """
        return 1.2925 * Air.relative_density(Tc, alt)

    @staticmethod
    def relative_density(
        Tc: floatArrayLike, alt: floatArrayLike = 0.0
    ) -> floatArrayLike:
        """Compute relative density, ie density ratio regarding density at zero altitude.

        This function has temperature and altitude as input for consistency
        regarding other functions in the module, but the temperature has no
        influence, only the altitude for this model.

        If both inputs are numpy arrays, they should have the same size.

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius).
            alt (float | numpy.ndarray, optional): Altitude above sea-level. The default is 0.

        Returns:
            float | numpy.ndarray: Relative density of air.

        """
        return np.exp(-1.16e-04 * alt) * np.ones_like(Tc)

    @staticmethod
    def kinematic_viscosity(Tc: floatArrayLike) -> floatArrayLike:
        r"""Compute air kinematic viscosity.

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius)

        Returns:
            float | numpy.ndarray: Kinematic viscosity in m²·s⁻¹.

        """
        return 1.32e-05 + 9.5e-08 * Tc

    @staticmethod
    def dynamic_viscosity(
        Tc: floatArrayLike, alt: floatArrayLike = 0.0
    ) -> floatArrayLike:
        r"""Compute air dynamic viscosity.

        If both inputs are numpy arrays, they should have the same size.

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius)
            alt (float | numpy.ndarray, optional): Altitude above sea-level. The default is 0.

        Returns:
            float | numpy.ndarray: Dynamic viscosity in kg·m⁻¹·s⁻¹.

        """
        return Air.kinematic_viscosity(Tc) * Air.volumic_mass(Tc, alt)

    @staticmethod
    def thermal_conductivity(Tc: floatArrayLike) -> floatArrayLike:
        r"""Compute air thermal conductivity.

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius)

        Returns:
            float | numpy.ndarray: Thermal conductivity in W·m⁻¹·K⁻¹.

        """
        return 2.42e-02 + 7.2e-05 * Tc

    @staticmethod
    def prandtl(Tc: floatArrayLike) -> floatArrayLike:
        """Compute Prandtl number.

        The Prandtl number (Pr) is a dimensionless number, named after the German
        physicist Ludwig Prandtl, defined as the ratio of momentum diffusivity to
        thermal diffusivity.

        Args:
            Tc (float | numpy.ndarray): Air temperature (in Celsius)

        Returns:
            float | numpy.ndarray: Prandtl number (—)

        """
        return 0.715 - 2.5e-04 * Tc
