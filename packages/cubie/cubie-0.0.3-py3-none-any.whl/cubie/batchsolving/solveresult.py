"""Structures used for returning results from the batch solver.

The :class:`SolveSpec` class stores the configuration of a solver run while
the :class:`SolveResult` class aggregates output arrays and related metadata.
"""

from typing import Optional, TYPE_CHECKING, Union, List, Any

if TYPE_CHECKING:
    from cubie.batchsolving.solver import Solver
    from cubie.batchsolving.BatchSolverKernel import BatchSolverKernel

import attrs
import attrs.validators as val
import numpy as np
from numpy.typing import NDArray
from cubie.batchsolving.arrays.BatchOutputArrays import ActiveOutputs
from cubie.batchsolving import ArrayTypes
from cubie._utils import slice_variable_dimension


@attrs.define
class SolveSpec:
    """Container describing a solver run.

    Attributes
    ----------
    dt_min, dt_max : float
        Minimum and maximum time step sizes.
    dt_save : float
        Interval at which state values are stored.
    dt_summarise : float
        Interval for computing summary outputs.
    atol, rtol : float
        Absolute and relative error tolerances.
    duration, warmup : float
        Total integration time and initial warm-up period.
    algorithm : str
        Name of the integration algorithm.
    saved_states, saved_observables : list of str or None
        Labels of variables saved verbatim.
    summarised_states, summarised_observables : list of str or None
        Labels of variables for which summaries were computed.
    output_types : list of str or None
        Types of output arrays generated during the run.
    precision : type
        Floating point precision used.
    """

    dt_min: float = attrs.field(validator=val.instance_of(float))
    dt_max: float = attrs.field(validator=val.instance_of(float))
    dt_save: float = attrs.field(validator=val.instance_of(float))
    dt_summarise: float = attrs.field(validator=val.instance_of(float))
    atol: float = attrs.field(validator=val.instance_of(float))
    rtol: float = attrs.field(validator=val.instance_of(float))
    duration: float = attrs.field(validator=val.instance_of(float))
    warmup: float = attrs.field(validator=val.instance_of(float))
    algorithm: str = attrs.field(validator=val.instance_of(str))
    saved_states: Optional[List[str]] = attrs.field()
    saved_observables: Optional[List[str]] = attrs.field()
    summarised_states: Optional[List[str]] = attrs.field()
    summarised_observables: Optional[List[str]] = attrs.field()
    output_types: Optional[List[str]] = attrs.field()
    precision: type = attrs.field(validator=val.instance_of(type))


@attrs.define
class SolveResult:
    """
    Aggregates output arrays and related metadata for a solver run.

    Parameters
    ----------
    time_domain_array : Optional[NDArray]
        NumPy array containing time-domain results.
    summaries_array : Optional[NDArray]
        NumPy array containing summary results.
    time : Optional[NDArray]
        NumPy array containing time values.
    time_domain_legend : Optional[dict[int, str]]
        Legend mapping time-domain indices to labels.
    summaries_legend : Optional[dict[int, str]]
        Legend mapping summary indices to labels.
    solve_settings : Optional[SolveSpec]
        Solver run configuration.
    _singlevar_summary_legend : Optional[dict[int, str]]
        Legend mapping summary offset indices to labels.
    _active_outputs : Optional[ActiveOutputs]
        Active outputs flags.
    _stride_order : tuple[str, ...]
        Tuple specifying the order of variables in the host arrays..
    """

    time_domain_array: Optional[NDArray] = attrs.field(
        default=attrs.Factory(lambda: np.array([])),
        validator=val.optional(val.instance_of(np.ndarray)),
        eq=attrs.cmp_using(eq=np.array_equal),
    )
    summaries_array: Optional[NDArray] = attrs.field(
        default=attrs.Factory(lambda: np.array([])),
        validator=val.optional(val.instance_of(np.ndarray)),
        eq=attrs.cmp_using(eq=np.array_equal),
    )
    time: Optional[NDArray] = attrs.field(
        default=attrs.Factory(lambda: np.array([])),
        validator=val.optional(val.instance_of(np.ndarray)),
    )
    time_domain_legend: Optional[dict[int, str]] = attrs.field(
        default=attrs.Factory(dict),
        validator=val.optional(val.instance_of(dict)),
    )
    summaries_legend: Optional[dict[int, str]] = attrs.field(
        default=attrs.Factory(dict),
        validator=val.optional(val.instance_of(dict)),
    )
    solve_settings: Optional[SolveSpec] = attrs.field(
        default=None, validator=val.optional(val.instance_of(SolveSpec))
    )
    _singlevar_summary_legend: Optional[dict[int, str]] = attrs.field(
        default=attrs.Factory(dict),
        validator=val.optional(val.instance_of(dict)),
    )
    _active_outputs: Optional[ActiveOutputs] = attrs.field(
        default=attrs.Factory(lambda: ActiveOutputs())
    )
    _stride_order: Union[tuple[str, ...], list[str]] = attrs.field(
        default=("time", "run", "variable")
    )

    @classmethod
    def from_solver(
        cls,
        solver: Union["Solver", "BatchSolverKernel"],
        results_type: str = "full",
    ) -> Union["SolveResult", dict[str, Any]]:
        """Create a :class:`SolveResult` from a solver instance.

        Parameters
        ----------
        solver : Solver or BatchSolverKernel
            Object providing access to output arrays and metadata.
        results_type : {'full', 'numpy', 'numpy_per_summary', 'pandas'}, optional
            Format of the returned results. Default ``'full'``.

        Returns
        -------
        SolveResult or dict
            ``SolveResult`` when ``results_type`` is ``'full'``; otherwise a
            dictionary containing the requested representation of the data.
        """

        active_outputs = solver.active_output_arrays
        state_active = active_outputs.state
        observables_active = active_outputs.observables
        state_summaries_active = active_outputs.state_summaries
        observable_summaries_active = active_outputs.observable_summaries
        solve_settings = solver.solve_info

        time, state_less_time = cls.cleave_time(
            solver.state,
            time_saved=solver.save_time,
            stride_order=solver.output_stride_order,
        )

        time_domain_array = cls.combine_time_domain_arrays(
            state_less_time,
            solver.observables,
            state_active,
            observables_active,
        )

        summaries_array = cls.combine_summaries_array(
            solver.state_summaries,
            solver.observable_summaries,
            state_summaries_active,
            observable_summaries_active,
        )

        time_domain_legend = cls.time_domain_legend_from_solver(solver)

        summaries_legend = cls.summary_legend_from_solver(solver)
        singlevar_summary_legend = solver.summary_legend_per_variable

        user_arrays = cls(
            time_domain_array=time_domain_array,
            summaries_array=summaries_array,
            time=time,
            time_domain_legend=time_domain_legend,
            summaries_legend=summaries_legend,
            active_outputs=active_outputs,
            solve_settings=solve_settings,
            stride_order=solver.output_stride_order,
            singlevar_summary_legend=singlevar_summary_legend,
        )

        if results_type == "full":
            return user_arrays
        elif results_type == "numpy":
            return user_arrays.as_numpy
        elif results_type == "numpy_per_summary":
            return user_arrays.as_numpy_per_summary
        elif results_type == "pandas":
            return user_arrays.as_pandas
        else:
            return user_arrays

    @property
    def as_pandas(self):
        """
        Convert the results to Pandas DataFrames.

        Returns
        -------
        dict[str, DataFrame]
            Dictionary with keys 'time_domain' and 'summaries' containing the
            corresponding DataFrames.

        Raises
        ------
        ImportError
            If the pandas package is not available.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Pandas is required to convert SolveResult to DataFrames. "
                "Pandas is an optional dependency- it's only used here "
                "to make analysis of data easier. Install Pandas to "
                "use this feature."
            )

        run_index = self._stride_order.index("run")
        ndim = len(self._stride_order)
        time_dfs = []
        summaries_dfs = []
        any_summaries = (
            self.active_outputs.state_summaries
            or self.active_outputs.observable_summaries
        )

        n_runs = self.time_domain_array.shape[run_index] if ndim == 3 else 1
        time_headings = list(self.time_domain_legend.values())
        summary_headings = list(self.summaries_legend.values())

        for run in range(n_runs):
            run_slice = slice_variable_dimension(
                slice(run, run + 1, None), run_index, ndim
            )

            singlerun_array = np.squeeze(
                self.time_domain_array[run_slice], axis=run_index
            )
            df = pd.DataFrame(singlerun_array, columns=time_headings)

            # Use time as index if extant
            if self.time is not None:
                if self.time.ndim > 1:
                    time_for_run = (
                        self.time[:, run]
                        if self.time.shape[1] > run
                        else self.time[:, 0]
                    )
                else:
                    time_for_run = self.time
                df.index = time_for_run

            # Create MultiIndex columns with run number as first level
            df.columns = pd.MultiIndex.from_product(
                [[f"run_{run}"], df.columns]
            )
            time_dfs.append(df)

            if any_summaries:
                singlerun_array = np.squeeze(
                    self.summaries_array[run_slice], axis=run_index
                )
                df = pd.DataFrame(singlerun_array, columns=summary_headings)
                summaries_dfs.append(df)
                df.columns = pd.MultiIndex.from_product(
                    [[f"run_{run}"], df.columns]
                )
            else:
                summaries_dfs.append(pd.DataFrame)

        time_domain_df = pd.concat(time_dfs, axis=1)
        summaries_df = pd.concat(summaries_dfs, axis=1)

        return {"time_domain": time_domain_df, "summaries": summaries_df}

    @property
    def as_numpy(self) -> dict[str, Optional[NDArray]]:
        """
        Return the results as copies of NumPy arrays.

        Returns
        -------
        dict[str, Optional[NDArray]]
            Dictionary containing copies of time, time_domain_array, summaries_array,
            time_domain_legend, and summaries_legend.
        """
        return {
            "time": self.time.copy() if self.time is not None else None,
            "time_domain_array": self.time_domain_array.copy(),
            "summaries_array": self.summaries_array.copy(),
            "time_domain_legend": self.time_domain_legend.copy(),
            "summaries_legend": self.summaries_legend.copy(),
        }

    @property
    def as_numpy_per_summary(self) -> dict[str, Optional[NDArray]]:
        """
        Return the results as separate NumPy arrays per summary type.

        Returns
        -------
        dict[str, Optional[NDArray]]
            Dictionary containing time, time_domain_array, time_domain_legend,
            and individual summary arrays.
        """
        arrays = {
            "time": self.time.copy() if self.time is not None else None,
            "time_domain_array": self.time_domain_array.copy(),
            "time_domain_legend": self.time_domain_legend.copy(),
        }
        arrays.update(**self.per_summary_arrays)

        return arrays

    @property
    def per_summary_arrays(self) -> dict[str, NDArray]:
        """
        Split summaries_array into separate arrays keyed by summary type.

        Returns
        -------
        dict[str, NDArray]
            Dictionary where each key is a summary type and the value is the
            corresponding NumPy array. The dictionary also includes a key
            'summary_legend' mapping to the variable legend.
        """
        if (
            self._active_outputs.state_summaries is False
            and self._active_outputs.observable_summaries is False
        ):
            return {}

        variable_index = self._stride_order.index("variable")

        # Split summaries_array by type
        variable_legend = self.time_domain_legend
        singlevar_legend = self._singlevar_summary_legend
        indices_per_var = np.max([k for k in singlevar_legend.keys()]) + 1
        per_summary_arrays = {}

        for offset, label in singlevar_legend.items():
            summ_slice = slice(offset, None, indices_per_var)
            summ_slice = slice_variable_dimension(
                summ_slice, variable_index, len(self._stride_order)
            )
            per_summary_arrays[label] = self.summaries_array[summ_slice].copy()
        per_summary_arrays["summary_legend"] = variable_legend

        return per_summary_arrays

    @property
    def active_outputs(self):
        """
        Get flags indicating which device arrays are active.

        Returns
        -------
        ActiveOutputs
            Object storing active output flags.
        """
        return self._active_outputs

    @staticmethod
    def cleave_time(
        state: ArrayTypes,
        time_saved: bool = False,
        stride_order: Optional[list[str]] = None,
    ) -> tuple[Optional[NDArray], NDArray]:
        """
        Remove time from the state array if saved.

        Parameters
        ----------
        state : ArrayTypes
            The state array to cleave.
        time_saved : bool, optional
            Flag indicating if time is saved in the state array.
        stride_order : Optional[list[str]], optional
            The order of dimensions in the array. Defaults to
            ['time', 'run', 'variable'] if None.

        Returns
        -------
        tuple[Optional[NDArray], NDArray]
            Tuple containing the time array (or None) and the state array with
            time removed.
        """
        if stride_order is None:
            stride_order = ["time", "run", "variable"]
        if time_saved:
            var_index = stride_order.index("variable")
            ndim = len(state.shape)

            time_slice = slice_variable_dimension(
                slice(-1, None, None), var_index, ndim
            )
            state_slice = slice_variable_dimension(
                slice(None, -1), var_index, ndim
            )

            time = np.squeeze(state[time_slice], axis=var_index)
            state_less_time = state[state_slice]
            return time, state_less_time
        else:
            return None, state

    @staticmethod
    def combine_time_domain_arrays(
        state, observables, state_active=True, observables_active=True
    ) -> NDArray:
        """
        Combine state and observable arrays into a single time-domain array.

        Parameters
        ----------
        state : NDArray
            Array of state values.
        observables : NDArray
            Array of observables.
        state_active : bool, optional
            Flag indicating if state is active.
        observables_active : bool, optional
            Flag indicating if observables are active.

        Returns
        -------
        NDArray
            Combined array along the last axis or a copy of the active array.
        """
        if state_active and observables_active:
            return np.concatenate((state, observables), axis=-1)
        elif state_active:
            return state.copy()
        elif observables_active:
            return observables.copy()
        else:
            return np.array([])

    @staticmethod
    def combine_summaries_array(
        state_summaries,
        observable_summaries,
        summarise_states,
        summarise_observables,
    ) -> np.ndarray:
        """
        Combine state and observable summary arrays into a single array.

        Parameters
        ----------
        state_summaries : NDArray
            Array containing state summaries.
        observable_summaries : NDArray
            Array containing observable summaries.
        summarise_states : bool
            Flag indicating if state summaries are active.
        summarise_observables : bool
            Flag indicating if observable summaries are active.

        Returns
        -------
        np.ndarray
            Combined summary array.
        """
        if summarise_states and summarise_observables:
            return np.concatenate(
                (state_summaries, observable_summaries), axis=-1
            )
        elif summarise_states:
            return state_summaries.copy()
        elif summarise_observables:
            return observable_summaries.copy()
        else:
            return np.array([])

    @staticmethod
    def summary_legend_from_solver(solver: "Solver") -> dict[int, str]:
        """
        Generate a summary legend from the solver instance.

        Parameters
        ----------
        solver : Solver
            Solver instance providing saved states, observables, and summary legends.

        Returns
        -------
        dict[int, str]
            Dictionary mapping summary array indices to labels.
        """
        singlevar_legend = solver.summary_legend_per_variable
        state_labels = solver.saved_states
        obs_labels = solver.saved_observables
        summaries_legend = {}

        # state summaries_array
        for i, label in enumerate(state_labels):
            for j, (key, val) in enumerate(singlevar_legend.items()):
                index = i * len(singlevar_legend) + j
                summaries_legend[index] = f"{label} {val}"
        # observable summaries_array
        len_state_legend = len(state_labels) * len(singlevar_legend)
        for i, label in enumerate(obs_labels):
            for j, (key, val) in enumerate(singlevar_legend.items()):
                index = len_state_legend + i * len(singlevar_legend) + j
                summaries_legend[index] = f"{label} {val}"
        return summaries_legend

    @staticmethod
    def time_domain_legend_from_solver(solver: "Solver") -> dict[int, str]:
        """
        Generate a time domain legend from the solver instance.

        Parameters
        ----------
        solver : Solver
            Solver instance providing saved states and observables.

        Returns
        -------
        dict[int, str]
            Dictionary mapping time domain indices to labels.
        """
        time_domain_legend = {}
        state_labels = solver.saved_states
        obs_labels = solver.saved_observables
        offset = 0

        for i, label in enumerate(state_labels):
            time_domain_legend[i] = f"{label}"
            offset = i

        for i, label in enumerate(obs_labels):
            offset += 1
            time_domain_legend[offset + i] = label
        return time_domain_legend
