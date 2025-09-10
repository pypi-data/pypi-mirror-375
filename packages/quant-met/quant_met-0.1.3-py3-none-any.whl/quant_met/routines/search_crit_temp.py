"""Function to run search for critical temperature."""

import logging
from functools import partial
from multiprocessing import Pool
from typing import Any

import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
import sisl
from scipy import stats

from .self_consistency import self_consistency_loop

logger = logging.getLogger(__name__)

MIN_NUMBER_OF_T_POINTS_FITTING = 4
MAX_ITERATIONS_GET_BOUNDS = 100


def _get_bounds(
    initial_temp: float,
    gap_for_temp_partial: partial[dict[str, Any] | None],
    zero_temperature_gap: npt.NDArray[np.complexfloating],
) -> tuple[list[dict[str, Any]], float, float]:  # pragma: no cover
    delta_vs_temp_list = []
    zero_gap_temp = nonzero_gap_temp = 0.0
    found_zero_gap = False
    found_nonzero_gap = False
    temp = initial_temp
    direction = "down"
    iterations = 0
    while (
        found_zero_gap and found_nonzero_gap
    ) is False and iterations < MAX_ITERATIONS_GET_BOUNDS:
        logger.info("Trying temperature: %s", temp)
        data_dict = gap_for_temp_partial(temp)
        logger.info("Result: %s", data_dict)
        if data_dict is not None:
            delta_vs_temp_list.append(data_dict)
            gap = np.array([data_dict[key] for key in data_dict if key.startswith("delta")])
            if np.allclose(gap, 0, rtol=0, atol=0.10 * np.max(np.abs(zero_temperature_gap))):
                logger.info("Found temperature with zero gap.")
                zero_gap_temp = temp
                found_zero_gap = True
                temp = 0.5 * temp
            elif np.allclose(
                gap,
                zero_temperature_gap,
                atol=0.10 * np.max(np.abs(zero_temperature_gap)),
            ):
                logger.info("Found temperature with nonzero gap.")
                nonzero_gap_temp = temp
                found_nonzero_gap = True
                temp = 2 * temp
            elif direction == "down":
                logger.info("Gap is neither zero nor equal to the zero gap. Reducing temperature.")
                temp = 0.5 * temp
            else:
                logger.info(
                    "Gap is neither zero nor equal to the zero gap. Increasing temperature.",
                )
                temp = 2 * temp
        elif direction == "down":
            logger.info("No data found for temperature %s. Reducing temperature.", temp)
            temp = 0.5 * temp
        else:
            logger.info("No data found for temperature %s. Increasing temperature.", temp)
            temp = 2 * temp

        if found_zero_gap and direction == "up" and not found_nonzero_gap:
            logger.info("Switching direction to decrease temperature.")
            temp = initial_temp / 2
            direction = "down"
        if found_nonzero_gap and direction == "down" and not found_zero_gap:
            logger.info("Switching direction to increase temperature.")
            temp = 2 * initial_temp
            direction = "up"

        iterations += 1
    return delta_vs_temp_list, zero_gap_temp, nonzero_gap_temp


def _fit_for_crit_temp(
    delta_vs_temp: pd.DataFrame,
    orbital: int,
) -> tuple[pd.DataFrame | None, pd.DataFrame, float | None, float | None]:  # pragma: no cover
    filtered_results = delta_vs_temp.iloc[
        np.where(
            np.invert(
                np.logical_or(
                    np.isclose(
                        np.abs(delta_vs_temp[f"delta_{orbital}"]) ** 2,
                        0,
                        rtol=0,
                        atol=0.01 * (np.abs(delta_vs_temp[f"delta_{orbital}"]) ** 2).max(),
                    ),
                    np.isclose(
                        np.abs(delta_vs_temp[f"delta_{orbital}"]) ** 2,
                        (np.abs(delta_vs_temp[f"delta_{orbital}"]) ** 2).max(),
                        rtol=1e-2,
                        atol=0,
                    ),
                ),
            ),
        )
    ]

    err = []
    if len(filtered_results) <= MIN_NUMBER_OF_T_POINTS_FITTING:
        return None, filtered_results, None, None

    lengths = range(MIN_NUMBER_OF_T_POINTS_FITTING, len(filtered_results))

    for length in lengths:
        range_results = filtered_results.iloc[-length:]
        linreg = stats.linregress(
            range_results["T"],
            np.abs(range_results[f"delta_{orbital}"]) ** 2,
        )
        err.append(linreg.stderr)

    min_length = lengths[np.argmin(np.array(err))]
    range_results = filtered_results.iloc[-min_length:]
    linreg = stats.linregress(range_results["T"], np.abs(range_results[f"delta_{orbital}"]) ** 2)

    return range_results, filtered_results, linreg.intercept, linreg.slope


def _gap_for_temp(  # noqa: PLR0913
    temp: float,
    hamiltonian: sisl.Hamiltonian,
    kgrid: sisl.MonkhorstPack,
    hubbard_int_orbital_basis: npt.NDArray[np.float64],
    epsilon: float,
    q: npt.NDArray[np.float64],
    max_iter: int = 1000,
    delta_init: npt.NDArray[np.complex128] | None = None,
) -> dict[str, Any] | None:  # pragma: no cover
    beta = np.inf if temp == 0 else 1 / temp
    try:
        gap = self_consistency_loop(
            hamiltonian=hamiltonian,
            kgrid=kgrid,
            beta=beta,
            hubbard_int_orbital_basis=hubbard_int_orbital_basis,
            epsilon=epsilon,
            max_iter=max_iter,
            delta_init=delta_init,
            q=q,
        )
    except RuntimeError:
        logger.exception("Did not converge.")
        return None
    else:
        data_dict: dict[str, Any] = {
            "T": temp,
        }
        data_dict.update({f"delta_{orbital}": gap[orbital] for orbital in range(len(gap))})
        return data_dict


def search_crit_temp(  # noqa: PLR0913
    hamiltonian: sisl.Hamiltonian,
    kgrid: sisl.MonkhorstPack,
    hubbard_int_orbital_basis: npt.NDArray[np.float64],
    epsilon: float,
    max_iter: int,
    n_temp_points: int,
    q: npt.NDArray[np.float64],
    beta_init: float | None = None,
) -> tuple[pd.DataFrame, list[float], matplotlib.figure.Figure]:  # pragma: no cover
    """Search for critical temperature."""
    logger.info("Start search for bounds for T_C")
    beta = 10 * hubbard_int_orbital_basis[0] if beta_init is None else beta_init
    temp = 1 / beta if not np.isinf(beta) else 1e-8

    delta_vs_temp_list = []
    critical_temp_list = []

    gap_for_temp_partial = partial(
        _gap_for_temp,
        hamiltonian=hamiltonian,
        kgrid=kgrid,
        hubbard_int_orbital_basis=hubbard_int_orbital_basis,
        epsilon=epsilon,
        max_iter=max_iter,
        q=q,
    )

    logger.info("Calculating zero temperature gap")
    data_dict = gap_for_temp_partial(0)
    if data_dict is None:
        err_msg = "Calculation for T = 0 did not converge."
        raise ValueError(err_msg)
    logger.info("Result: %s", data_dict)

    zero_temperature_gap = np.array(
        [data_dict[key] for key in data_dict if key.startswith("delta")],
    )
    delta_vs_temp_list.append(data_dict)

    delta_vs_temp_list_tmp, zero_gap_temp, nonzero_gap_temp = _get_bounds(
        temp,
        gap_for_temp_partial,
        zero_temperature_gap,
    )
    delta_vs_temp_list.extend(delta_vs_temp_list_tmp)
    logger.info("Temperature bounds: %s to %s", nonzero_gap_temp, zero_gap_temp)

    temperature_list = np.concatenate(
        [
            np.linspace(
                0.8 * nonzero_gap_temp,
                nonzero_gap_temp,
                num=int(0.05 * n_temp_points),
                endpoint=False,
            ),
            np.linspace(
                nonzero_gap_temp,
                zero_gap_temp,
                num=int(0.9 * n_temp_points),
                endpoint=False,
            ),
            np.linspace(
                zero_gap_temp,
                1.2 * zero_gap_temp,
                num=int(0.05 * n_temp_points),
                endpoint=True,
            ),
        ],
    )

    with Pool() as p:
        delta_vs_temp_list.extend(p.map(gap_for_temp_partial, temperature_list))  # type: ignore[arg-type]
        delta_vs_temp_list = [x for x in delta_vs_temp_list if x is not None]

    delta_vs_temp = pd.DataFrame(delta_vs_temp_list).sort_values(by=["T"]).reset_index(drop=True)

    fit_fig, fit_axs = plt.subplots(nrows=1, ncols=hamiltonian.no, figsize=(hamiltonian.no * 6, 6))

    for orbital in range(hamiltonian.no):
        fit_range, filtered_range, intercept, slope = _fit_for_crit_temp(delta_vs_temp, orbital)

        ax = fit_axs if hamiltonian.no == 1 else fit_axs[orbital]

        if fit_range is not None and intercept is not None and slope is not None:
            critical_temp = -intercept / slope
            critical_temp_list.append(critical_temp)

            ax.plot(
                filtered_range["T"],
                intercept + slope * filtered_range["T"],
                "r--",
                alpha=0.3,
            )
            ax.plot(
                fit_range["T"],
                intercept + slope * fit_range["T"],
                "r-",
            )
            ax.axvline(x=critical_temp, linestyle="--", color="gray")
        else:
            critical_temp = 0
            critical_temp_list.append(critical_temp)

        ax.plot(
            delta_vs_temp["T"],
            np.abs(delta_vs_temp[f"delta_{orbital}"]) ** 2,
            "--x",
            color=f"C{orbital}",
        )
        ax.set_ylabel(r"$\vert\Delta\vert^2\ [t^2]$")

    return delta_vs_temp, critical_temp_list, fit_fig
