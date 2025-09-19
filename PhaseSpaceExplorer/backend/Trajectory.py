from copy import deepcopy
from typing import Callable, List, Tuple, Dict

import numpy as np
from math import isclose
from scipy.integrate import solve_ivp

from backend.misc import flatten


class Trajectory():
    def __init__(self, ODEs, initial_state):
        self._ODEs: Callable = ODEs
        self._initial_state: np.ndarray = initial_state

        self._dt = "+"

        # The result of solve_ivp as if variables are not periodic
        self._y_sol_raw: np.ndarray | None = None
        self._t_sol_raw: np.ndarray | None = None
        self._y_events_raw: List[np.ndarray] | None = None
        self._t_events_raw: List[np.ndarray] | None = None

        # Flattened and sorted raw events
        self._y_events_sorted: np.ndarray | None = None  # TODO Check type
        self._t_events_sorted: np.ndarray | None = None  # TODO Check type

        # Raw solution with inserted events
        self._y_sol_ful: np.ndarray | None = None
        self._t_sol_ful: np.ndarray | None = None

        # Solutions splited by events
        self._y_sols: List[np.ndarray] | None = None
        self._t_sols: List[np.ndarray] | None = None
        return

    @property
    def y_sol(self):
        return self._y_sol_ful

    @property
    def t_sol(self):
        return self._t_sol_ful

    @property
    def y_sols(self):
        return self._y_sols

    @property
    def t_sols(self):
        return self._t_sols

    @property
    def y_events(self):
        return self._y_events

    @property
    def t_events(self):
        return self._t_events

    @property
    def init_state(self):
        return self._initial_state

    @init_state.setter
    def init_state(self, value):
        self._initial_state = value
        return

    @property
    def last_state(self):
        return self._y_sol_ful[:, -1]

    @staticmethod
    def is_empty_events_raw(yev: List[np.ndarray], tev: List[np.ndarray]) -> bool:
        for i in range(len(yev)):
            if len(yev[i]) != 0:
                return False
            if len(tev[i]) != 0:
                return False
        return True

    def integrate_scipy(
            self, pars, t_start, t_end, t_N,
            periodic_events=[],
            alg: str = "RK45", rtol: float = 1e-5, atol: float = 1e-5
    ) -> None:

        all_events = periodic_events  # TODO add "exploded to infinity" event
        t_span = (t_start, t_end)
        self._dt = "+" if (t_end > t_start) else "-"

        # TODO rework this magic number in max_step
        max_step = abs((t_end-t_start)/t_N * 5)

        sol = solve_ivp(
            lambda t, U0: self._ODEs(U0, np.array(pars), t),
            t_span=t_span,
            y0=self._initial_state,
            max_step=max_step,
            method=alg, rtol=rtol, atol=atol,
            events=all_events
        )

        # Get raw solution and raw events from solve_ivp
        self._y_sol_raw, self._t_sol_raw = sol.y, sol.t
        self._y_events_raw, self._t_events_raw = sol.y_events, sol.t_events
        return

    def flatten_and_sort_events(self) -> None:
        if self.is_empty_events_raw(self._y_events_raw, self._t_events_raw):
            self._y_events_sorted = []
            self._t_events_sorted = []
            return

        ys_flat = flatten(self._y_events_raw)
        ts_flat = flatten(self._t_events_raw)
        print(self._t_events_raw)
        print(ts_flat)

        ys_ts_zip = zip(ys_flat, ts_flat)
        ys_ts_sorted = sorted(ys_ts_zip, key=lambda y_t_pair: y_t_pair[1])
        ys_sorted, ts_sorted = list(zip(*ys_ts_sorted))

        self._y_events_sorted = ys_sorted
        self._t_events_sorted = ts_sorted
        return

    def insert_events(self) -> None:
        ys = self._y_sol_raw.copy()
        ts = self._t_sol_raw.copy()

        for (i, t_event) in enumerate(self._t_events_sorted):
            state_to_insert = self._y_events_sorted[i]
            time_to_insert = t_event
            for (j, t) in enumerate(ts):
                if (self._dt == "+") and (t >= t_event):
                    ys = np.insert(ys, j, state_to_insert, axis=1)
                    ts = np.insert(ts, j, time_to_insert)
                    break
                if (self._dt == "-") and (t <= t_event):
                    ys = np.insert(ys, j, state_to_insert, axis=1)
                    ts = np.insert(ts, j, time_to_insert)
                    break

        self._y_sol_ful = ys
        self._t_sol_ful = ts

        # print(self._y_sol_ful)
        # print(self._t_sol_ful)
        # print(self._t_events_raw)
        # print(self._t_events_sorted)
        return

    def split(self) -> None:
        # In case of no events
        if not self._t_events_sorted:
            self._y_sols = [self._y_sol_ful,]
            self._t_sols = [self._t_sol_ful,]
            return

        # Find temporal indexes of events in t_sol
        i_events = []
        for t_event in self._t_events_sorted:
            for (i, t) in enumerate(self._t_sol_ful):
                if (t == t_event) or isclose(t, t_event):
                    i_events.append(i)
                    break

        if self._dt == "-":
            i_events = list(reversed(i_events))

        # Add first and last temporal indexes, makes algorithm easier
        if (i_events[0] != 0):
            i_events.insert(0, 0)
        if (i_events[-1] != len(self._t_sol_ful)):
            i_events.append(len(self._t_sol_ful))

        yss, tss = [], []

        # Split y_sol and t_sol by i_events
        for i in range(len(i_events)-1):
            left = i_events[i]
            right = i_events[i+1] + 1 \
                if (i != len(i_events)-1) else i_events[i+1]
            yss.append(self._y_sol_ful[:, left:right].copy())
            tss.append(self._t_sol_ful[left:right].copy())

        self._y_sols = yss
        self._t_sols = tss
        return

    def translate_to_period(self, periodic_data) -> None:
        new_yss = deepcopy(self._y_sols)

        # Iterate over all subsolutions
        for i in range(len(self._y_sols)):

            # Get subsolution ys[dim,time]
            ys = self._y_sols[i]

            # Calculate mean with respect to time
            ys_mean = np.mean(ys, axis=1)

            # Iterate over dims in periodic_data
            for (j, data) in periodic_data.items():
                offset, period = data

                # Calculate a number of period shifts
                # to be ∈ [offset, offset+period]
                n_periods = 0
                while ys_mean[j] - n_periods*period > offset+period:
                    n_periods += 1
                while ys_mean[j] - n_periods*period < offset:
                    n_periods -= 1

                # Create one-hot-row matrix
                # and shift solution along one spacial dimention
                shift = np.zeros_like(ys)
                shift[j, :] = n_periods*period
                ys = ys - shift

            new_yss[i] = ys

        self._y_sols = new_yss
        return

    def process_periodic_variables(
        self, periodic_data: Dict[int, Tuple[float, float]] = {}
    ) -> None:
        self.flatten_and_sort_events()
        self.insert_events()
        self.split()
        self.translate_to_period(periodic_data)
        return
