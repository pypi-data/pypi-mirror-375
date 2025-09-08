"""
Output configuration management system for flexible, user-controlled output
selection.

This module provides configuration classes for managing output settings in
CUDA batch solvers, including validation of indices and output types,
and automatic configuration from user-specified parameters.
"""

from typing import List, Tuple, Union, Optional, Sequence
from warnings import warn

import attrs
import numpy as np
from numpy import array_equal
from numpy.typing import NDArray

from cubie.outputhandling import summary_metrics


def _indices_validator(array, max_index):
    """
    Validate that indices are valid numpy arrays within bounds.

    Parameters
    ----------
    array : np.ndarray or None
        Array of indices to validate.
    max_index : int
        Maximum allowed index value (exclusive).

    Raises
    ------
    TypeError
        If array is not a numpy array of integers.
    ValueError
        If indices are out of bounds or contain duplicates.
    """
    if array is not None:
        if not isinstance(array, np.ndarray) or array.dtype != np.int_:
            raise TypeError("Index array must be a numpy array of integers.")

        if np.any((array < 0) | (array >= max_index)):
            raise ValueError(f"Indices must be in the range [0, {max_index})")

        unique_array, duplicate_count = np.unique(array, return_counts=True)
        duplicates = unique_array[duplicate_count > 1]
        if len(duplicates) > 0:
            raise ValueError(f"Duplicate indices found: {duplicates.tolist()}")


@attrs.define
class OutputCompileFlags:
    """
    Compile-time flags for output functionality.

    This class holds boolean flags that determine which output features
    should be compiled into CUDA kernels for optimal performance.

    Attributes
    ----------
    save_state : bool, default False
        Whether to save state variables.
    save_observables : bool, default False
        Whether to save observable variables.
    summarise : bool, default False
        Whether to compute summary statistics.
    summarise_observables : bool, default False
        Whether to compute summaries for observables.
    summarise_state : bool, default False
        Whether to compute summaries for states.
    """

    save_state: bool = attrs.field(
        default=False, validator=attrs.validators.instance_of(bool)
    )
    save_observables: bool = attrs.field(
        default=False, validator=attrs.validators.instance_of(bool)
    )
    summarise: bool = attrs.field(
        default=False, validator=attrs.validators.instance_of(bool)
    )
    summarise_observables: bool = attrs.field(
        default=False, validator=attrs.validators.instance_of(bool)
    )
    summarise_state: bool = attrs.field(
        default=False, validator=attrs.validators.instance_of(bool)
    )


@attrs.define
class OutputConfig:
    """
    Configuration class for output handling with validation.

    This class manages output configuration settings including which variables
    to save, which to summarize, and various validation logic to ensure proper
    configuration. It handles the conversion between user-friendly output type
    specifications and internal boolean flags.

    Parameters
    ----------
    _max_states : int
        Maximum number of state variables in the system.
    _max_observables : int
        Maximum number of observable variables in the system.
    _saved_state_indices : list or NDArray, optional
        Indices of state variables to save. Defaults to empty list.
    _saved_observable_indices : list or NDArray, optional
        Indices of observable variables to save. Defaults to empty list.
    _summarised_state_indices : list or NDArray, optional
        Indices of state variables to summarize. Defaults to empty list.
    _summarised_observable_indices : list or NDArray, optional
        Indices of observable variables to summarize. Defaults to empty list.
    _output_types : list[str], optional
        List of requested output types. Defaults to empty list.

    Notes
    -----
    Uses private attributes with property accessors to handle circular
    dependencies when setting indices and output flags. This design allows
    for proper validation while maintaining a clean public interface.

    The class automatically validates that:
    - At least one output type is requested
    - All indices are within valid ranges
    - No duplicate indices are specified
    """

    # System dimensions, used to validate indices
    _max_states: int = attrs.field(validator=attrs.validators.instance_of(int))
    _max_observables: int = attrs.field(
        validator=attrs.validators.instance_of(int)
    )

    _saved_state_indices: Optional[Union[List | NDArray]] = attrs.field(
        default=attrs.Factory(list),
        eq=attrs.cmp_using(eq=array_equal),
    )
    _saved_observable_indices: Optional[Union[List | NDArray]] = attrs.field(
        default=attrs.Factory(list),
        eq=attrs.cmp_using(eq=array_equal),
    )
    _summarised_state_indices: Optional[Union[List | NDArray]] = attrs.field(
        default=attrs.Factory(list),
        eq=attrs.cmp_using(eq=array_equal),
    )
    _summarised_observable_indices: Optional[Union[List | NDArray]] = (
        attrs.field(
            default=attrs.Factory(list),
            eq=attrs.cmp_using(eq=array_equal),
        )
    )

    _output_types: List[str] = attrs.field(default=attrs.Factory(list))
    _save_state: bool = attrs.field(default=True, init=False)
    _save_observables: bool = attrs.field(default=True, init=False)
    _save_time: bool = attrs.field(default=False, init=False)
    _summary_types: Tuple[str] = attrs.field(
        default=attrs.Factory(tuple), init=False
    )

    def __attrs_post_init__(self):
        """
        Perform post-initialization validation and setup.

        Notes
        -----
        This method is called automatically after object initialization to
        validate indices, set up default arrays, and ensure at least one
        output type is requested.
        """
        self.update_from_outputs_list(self._output_types)
        self._check_saved_indices()
        self._check_summarised_indices()
        self._validate_index_arrays()
        self._check_for_no_outputs()

    def _validate_index_arrays(self):
        """
        Validate that all index arrays are within bounds and contain no
        duplicates.

        Notes
        -----
        Called post-init to allow None arrays to be replaced with default
        arrays before validation.
        """
        index_arrays = [
            self._saved_state_indices,
            self._saved_observable_indices,
            self._summarised_state_indices,
            self._summarised_observable_indices,
        ]
        maxima = [
            self._max_states,
            self._max_observables,
            self._max_states,
            self._max_observables,
        ]
        for i, array in enumerate(index_arrays):
            _indices_validator(array, maxima[i])

    def _check_for_no_outputs(self):
        """
        Ensure at least one output type is requested.

        Raises
        ------
        ValueError
            If no output types are enabled.
        """
        any_output = (
            self._save_state
            or self._save_observables
            or self._save_time
            or self.save_summaries
        )
        if not any_output:
            raise ValueError(
                "At least one output type must be enabled (state, "
                "observables, time, summaries)"
            )

    def _check_saved_indices(self):
        """
        Convert saved indices to numpy arrays and set defaults if empty.

        Notes
        -----
        If index arrays are empty, creates arrays containing all possible
        indices for the respective variable types.
        """
        if len(self._saved_state_indices) == 0:
            self._saved_state_indices = np.arange(
                self._max_states, dtype=np.int_
            )
        else:
            self._saved_state_indices = np.asarray(
                self._saved_state_indices, dtype=np.int_
            )
        if len(self._saved_observable_indices) == 0:
            self._saved_observable_indices = np.arange(
                self._max_observables, dtype=np.int_
            )
        else:
            self._saved_observable_indices = np.asarray(
                self._saved_observable_indices, dtype=np.int_
            )

    def _check_summarised_indices(self):
        """
        Set summarised indices to saved indices if not provided.

        Notes
        -----
        If summarised indices are empty, defaults them to the corresponding
        saved indices arrays.
        """
        if len(self._summarised_state_indices) == 0:
            self._summarised_state_indices = self._saved_state_indices
        else:
            self._summarised_state_indices = np.asarray(
                self._summarised_state_indices, dtype=np.int_
            )
        if len(self._summarised_observable_indices) == 0:
            self._summarised_observable_indices = (
                self._saved_observable_indices
            )
        else:
            self._summarised_observable_indices = np.asarray(
                self._summarised_observable_indices, dtype=np.int_
            )

    @property
    def max_states(self):
        """
        Get the maximum number of states.

        Returns
        -------
        int
            Maximum number of state variables.
        """
        return self._max_states

    @max_states.setter
    def max_states(self, value):
        """
        Set the maximum number of states with automatic index updating.

        Parameters
        ----------
        value : int
            New maximum number of states.

        Notes
        -----
        If saved state indices are currently set to the full range,
        automatically updates them to the new full range.
        """
        if np.array_equal(
            self._saved_state_indices,
            np.arange(self.max_states, dtype=np.int_),
        ):
            self._saved_state_indices = np.arange(value, dtype=np.int_)
        self._max_states = value
        self.__attrs_post_init__()

    @property
    def max_observables(self):
        """
        Get the maximum number of observables.

        Returns
        -------
        int
            Maximum number of observable variables.
        """
        return self._max_observables

    @max_observables.setter
    def max_observables(self, value):
        """
        Set the maximum number of observables with automatic index updating.

        Parameters
        ----------
        value : int
            New maximum number of observables.

        Notes
        -----
        If saved observable indices are currently set to the full range,
        automatically updates them to the new full range.
        """
        if np.array_equal(
            self._saved_observable_indices,
            np.arange(self.max_observables, dtype=np.int_),
        ):
            self._saved_observable_indices = np.arange(value, dtype=np.int_)
        self._max_observables = value
        self.__attrs_post_init__()

    @property
    def save_state(self) -> bool:
        """
        Check if state saving is enabled and has valid indices.

        Returns
        -------
        bool
            True if state saving is enabled and indices are available.
        """
        return self._save_state and (len(self._saved_state_indices) > 0)

    @property
    def save_observables(self):
        """
        Check if observable saving is enabled and has valid indices.

        Returns
        -------
        bool
            True if observable saving is enabled and indices are available.
        """
        return self._save_observables and (
            len(self._saved_observable_indices) > 0
        )

    @property
    def save_time(self):
        """
        Check if time saving is enabled.

        Returns
        -------
        bool
            True if time values should be saved.
        """
        return self._save_time

    @property
    def save_summaries(self) -> bool:
        """
        Check if any summary calculations are needed.

        Returns
        -------
        bool
            True if any summary types are configured.
        """
        return len(self._summary_types) > 0

    @property
    def summarise_state(self) -> bool:
        """
        Check if state variables will be summarised.

        Returns
        -------
        bool
            True if summaries are enabled and state indices are available.
        """
        return self.save_summaries and self.n_summarised_states > 0

    @property
    def summarise_observables(self) -> bool:
        """
        Check if observable variables will be summarised.

        Returns
        -------
        bool
            True if summaries are enabled and observable indices are available.
        """
        return self.save_summaries and self.n_summarised_observables > 0

    @property
    def compile_flags(self) -> OutputCompileFlags:
        """
        Get compile flags for this configuration.

        Returns
        -------
        OutputCompileFlags
            Flags indicating which output features should be compiled.
        """
        return OutputCompileFlags(
            save_state=self.save_state,
            save_observables=self.save_observables,
            summarise=self.save_summaries,
            summarise_observables=self.summarise_observables,
            summarise_state=self.summarise_state,
        )

    @property
    def saved_state_indices(self):
        """
        Get indices of states to save.

        Returns
        -------
        np.ndarray
            Array of state indices, empty if state saving is disabled.
        """
        if not self._save_state:
            return np.asarray([], dtype=np.int_)
        return self._saved_state_indices

    @saved_state_indices.setter
    def saved_state_indices(self, value):
        """
        Set indices of states to save.

        Parameters
        ----------
        value : array-like
            State indices to save.
        """
        self._saved_state_indices = np.asarray(value, dtype=np.int_)
        self._validate_index_arrays()
        self._check_for_no_outputs()

    @property
    def saved_observable_indices(self):
        """
        Get indices of observables to save.

        Returns
        -------
        np.ndarray
            Array of observable indices, empty if observable saving is disabled.
        """
        if not self._save_observables:
            return np.asarray([], dtype=np.int_)
        return self._saved_observable_indices

    @saved_observable_indices.setter
    def saved_observable_indices(self, value):
        """
        Set indices of observables to save.

        Parameters
        ----------
        value : array-like
            Observable indices to save.
        """
        self._saved_observable_indices = np.asarray(value, dtype=np.int_)
        self._validate_index_arrays()
        self._check_for_no_outputs()

    @property
    def summarised_state_indices(self):
        """
        Get indices of states to summarise.

        Returns
        -------
        np.ndarray
            Array of state indices for summary calculations.
        """
        return self._summarised_state_indices

    @summarised_state_indices.setter
    def summarised_state_indices(self, value):
        """
        Set indices of states to summarise.

        Parameters
        ----------
        value : array-like
            State indices for summary calculations.
        """
        self._summarised_state_indices = np.asarray(value, dtype=np.int_)
        self._validate_index_arrays()
        self._check_for_no_outputs()

    @property
    def summarised_observable_indices(self):
        """
        Get indices of observables to summarise.

        Returns
        -------
        np.ndarray
            Array of observable indices for summary calculations.
        """
        return self._summarised_observable_indices

    @summarised_observable_indices.setter
    def summarised_observable_indices(self, value):
        """
        Set indices of observables to summarise.

        Parameters
        ----------
        value : array-like
            Observable indices for summary calculations.
        """
        self._summarised_observable_indices = np.asarray(value, dtype=np.int_)
        self._validate_index_arrays()
        self._check_for_no_outputs()

    @property
    def n_saved_states(self) -> int:
        """
        Get number of states that will be saved.

        Returns
        -------
        int
            Number of state variables to save in time-domain output.

        Notes
        -----
        Returns the length of saved_state_indices when save_state is True,
        otherwise 0.
        """
        return len(self._saved_state_indices) if self._save_state else 0

    @property
    def n_saved_observables(self) -> int:
        """
        Get number of observables that will be saved.

        Returns
        -------
        int
            Number of observable variables to save in time-domain output.
        """
        return (
            len(self._saved_observable_indices)
            if self._save_observables
            else 0
        )

    @property
    def n_summarised_states(self) -> int:
        """
        Get number of states that will be summarised.

        Returns
        -------
        int
            Number of state variables for summary calculations.

        Notes
        -----
        Returns the length of summarised_state_indices when save_summaries
        is active, otherwise 0.
        """
        return (
            len(self._summarised_state_indices) if self.save_summaries else 0
        )

    @property
    def n_summarised_observables(self) -> int:
        """
        Get number of observables that will be summarised.

        Returns
        -------
        int
            Number of observable variables for summary calculations.
        """
        return (
            len(self._summarised_observable_indices)
            if self.save_summaries
            else 0
        )

    @property
    def summary_types(self):
        """
        Get the configured summary types.

        Returns
        -------
        tuple[str]
            Tuple of summary metric names.
        """
        return self._summary_types

    @property
    def summary_legend_per_variable(self):
        """
        Get mapping of summary types to indices per variable.

        Returns
        -------
        dict[str, int]
            Dictionary mapping index numbers to summary type names.
        """
        if not self._summary_types:
            return {}
        legend_tuple = summary_metrics.legend(self._summary_types)
        legend_dict = dict(zip(range(len(self._summary_types)), legend_tuple))
        return legend_dict

    @property
    def summary_parameters(self):
        """
        Get parameters for summary metrics.

        Returns
        -------
        dict
            Parameters required by the summary metrics system.
        """
        return summary_metrics.params(list(self._summary_types))

    @property
    def summaries_buffer_height_per_var(self) -> int:
        """
        Calculate buffer size per variable for summary calculations.

        Returns
        -------
        int
            Buffer height required per variable for summary metrics.
        """
        if not self.summary_types:
            return 0
        # Convert summary_types set to list for summarymetrics
        summary_list = list(self._summary_types)
        total_buffer_size = summary_metrics.summaries_buffer_height(
            summary_list
        )
        return total_buffer_size

    @property
    def summaries_output_height_per_var(self) -> int:
        """
        Calculate output array height per variable for summaries.

        Returns
        -------
        int
            Output height required per variable for summary results.
        """
        if not self._summary_types:
            return 0
        # Convert summary_types tuple to list for summarymetrics
        summary_list = list(self._summary_types)
        total_output_size = summary_metrics.summaries_output_height(
            summary_list
        )
        return total_output_size

    @property
    def state_summaries_buffer_height(self) -> int:
        """
        Calculate total buffer height for state summaries.

        Returns
        -------
        int
            Total buffer height for all state summary calculations.
        """
        return self.summaries_buffer_height_per_var * self.n_summarised_states

    @property
    def observable_summaries_buffer_height(self) -> int:
        """
        Calculate total buffer height for observable summaries.

        Returns
        -------
        int
            Total buffer height for all observable summary calculations.
        """
        return (
            self.summaries_buffer_height_per_var
            * self.n_summarised_observables
        )

    @property
    def total_summary_buffer_size(self) -> int:
        """
        Calculate total size of all summary buffers.

        Returns
        -------
        int
            Combined size of state and observable summary buffers.
        """
        return (
            self.state_summaries_buffer_height
            + self.observable_summaries_buffer_height
        )

    @property
    def state_summaries_output_height(self) -> int:
        """
        Calculate total output height for state summaries.

        Returns
        -------
        int
            Total output height for all state summary results.
        """
        return self.summaries_output_height_per_var * self.n_summarised_states

    @property
    def observable_summaries_output_height(self) -> int:
        """
        Calculate total output height for observable summaries.

        Returns
        -------
        int
            Total output height for all observable summary results.
        """
        return (
            self.summaries_output_height_per_var
            * self.n_summarised_observables
        )

    @property
    def output_types(self) -> List[str]:
        """
        Get the configured output types.

        Returns
        -------
        list[str]
            List of requested output type names.
        """
        return self._output_types

    @output_types.setter
    def output_types(self, value: Sequence[str]):
        """
        Set output types and update configuration accordingly.

        Parameters
        ----------
        value : Sequence[str]
            Output types to configure. Can be list, tuple, or single string.

        Raises
        ------
        TypeError
            If value is not a valid sequence type.
        """
        if isinstance(value, tuple):
            value = list(value)
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            raise TypeError(
                f"Output types must be a list or tuple of strings, "
                f"or a single string. Got {type(value)}"
            )

        self.update_from_outputs_list(value)
        self._check_for_no_outputs()

    def update_from_outputs_list(
        self,
        output_types: list[str],
    ):
        """
        Update configuration from a list of output type names.

        Parameters
        ----------
        output_types : list[str]
            List of output type names to configure.

        Notes
        -----
        Parses the output types list to set internal boolean flags and
        extract summary metric specifications. Unknown output types
        generate warnings but do not cause errors.
        """
        if not output_types:
            self._output_types = []
            self._summary_types = tuple()
            self._save_state = False
            self._save_observables = False
            self._save_time = False

        else:
            self._output_types = output_types
            self._save_state = "state" in output_types
            self._save_observables = "observables" in output_types
            self._save_time = "time" in output_types

            summary_types = []
            for output_type in output_types:
                if any(
                    (
                        output_type.startswith(name)
                        for name in summary_metrics.implemented_metrics
                    )
                ):
                    summary_types.append(output_type)
                elif output_type in ["state", "observables", "time"]:
                    continue
                else:
                    warn(
                        f"Summary type '{output_type}' is not implemented. "
                        f"Ignoring."
                    )

            self._summary_types = tuple(summary_types)

            self._check_for_no_outputs()

    @classmethod
    def from_loop_settings(
        cls,
        output_types: List[str],
        saved_state_indices=None,
        saved_observable_indices=None,
        summarised_state_indices=None,
        summarised_observable_indices=None,
        max_states: int = 0,
        max_observables: int = 0,
    ) -> "OutputConfig":
        """
        Create configuration from integrator-compatible specifications.

        Parameters
        ----------
        output_types : list[str]
            Output types from ["state", "observables", "time"] plus
            summary metrics like ["max", "peaks", "mean", "rms", "min"].
        saved_state_indices : array-like, optional
            Indices of states to save in time-domain output.
        saved_observable_indices : array-like, optional
            Indices of observables to save in time-domain output.
        summarised_state_indices : array-like, optional
            Indices of states for summary calculations. If None,
            defaults to saved_state_indices.
        summarised_observable_indices : array-like, optional
            Indices of observables for summary calculations. If None,
            defaults to saved_observable_indices.
        max_states : int, default 0
            Total number of state variables in the system.
        max_observables : int, default 0
            Total number of observable variables in the system.

        Returns
        -------
        OutputConfig
            Configured output configuration object.

        Notes
        -----
        This class method provides a convenient interface for creating
        OutputConfig objects from the parameter format used by integrator
        classes. It handles None values appropriately by converting them
        to empty arrays.
        """
        # Set boolean compile flags for output types
        output_types = output_types.copy()

        # OutputConfig doesn't play as nicely with Nones as the rest of python does
        if saved_state_indices is None:
            saved_state_indices = np.asarray([], dtype=np.int_)
        if saved_observable_indices is None:
            saved_observable_indices = np.asarray([], dtype=np.int_)
        if summarised_state_indices is None:
            summarised_state_indices = np.asarray([], dtype=np.int_)
        if summarised_observable_indices is None:
            summarised_observable_indices = np.asarray([], dtype=np.int_)

        return cls(
            max_states=max_states,
            max_observables=max_observables,
            saved_state_indices=saved_state_indices,
            saved_observable_indices=saved_observable_indices,
            summarised_state_indices=summarised_state_indices,
            summarised_observable_indices=summarised_observable_indices,
            output_types=output_types,
        )
