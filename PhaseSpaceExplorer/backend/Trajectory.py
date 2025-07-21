import numpy as np
from scipy.integrate import solve_ivp

from backend.misc import bring_vector_in_bounds

# TODO add type hinting

class Trajectory():
    def __init__(self, ODEs, initial_state) -> None:
        self._ODEs = ODEs
        self._initial_state = initial_state
        # The result of solve_ivp as if variables are not periodic
        self._y_sol = np.zeros(1)
        self._t_sol = np.zeros(1)
        # List of lists of y solutions and t solutions
        self._y_sols = np.zeros(1)
        self._t_sols = np.zeros(1)
        # List of y events and t_events
        self._y_events = np.zeros(1)
        self._t_events = np.zeros(1)
        return
    
    @property
    def y_sol(self): return self._y_sol
    @property
    def t_sol(self): return self._t_sol
    
    @property
    def y_sols(self): return self._y_sols
    @property
    def t_sols(self): return self._t_sols
    
    @property
    def y_events(self): return self._y_events
    @property
    def t_events(self): return self._t_events

    @property
    def init_state(self): return self._initial_state
    @init_state.setter
    def init_state(self, value): self._initial_state = value
    
    @property
    def last_state(self): return self._y_sol[:,-1]


    def integrate_scipy(self, pars, t_start, t_end, t_N, 
                        periodic_data:dict[int,list[float]]={},
                        alg:str="RK45", rtol:float=1e-5, atol:float=1e-5):
        # TODO add event of integration termination if out of boundaries
        periodic_events = [lambda t, y: np.sin(np.pi*(y[i]-offset)/period)
                  for (i,(offset, period)) in periodic_data.items()]
        t_span = (t_start, t_end)
        # TODO rework this magic number in max_step
        max_step = abs((t_end-t_start)/t_N * 5)
        dt = "+" if (t_end > t_start) else "-"
        sol = solve_ivp(lambda t, U0: self._ODEs(U0, np.array(pars), t), 
                        t_span=t_span, 
                        y0=self._initial_state, 
                        max_step=max_step,
                        method=alg, 
                        rtol=rtol, 
                        atol=atol,
                        events=periodic_events)
        # Get raw solution and raw events from solve_ivp
        y_sol_raw, t_sol_raw = sol.y, sol.t
        y_events_raw, t_events_raw = sol.y_events, sol.t_events
        # Flatten, sort and insert events into solution
        y_events_flat, t_events_flat = self.flatten_events(y_events_raw, t_events_raw)
        y_events_sort, t_events_sort = self.sort_events(y_events_flat, t_events_flat)
        y_sol, t_sol = self.insert_events(y_sol_raw, t_sol_raw, y_events_sort, t_events_sort, dt)
        # Split solution from one events to the next
        # Note that t_events_sort must be sorted for this to work
        y_sols, t_sols = self.split_sol(y_sol, t_sol, t_events_sort)
        y_sols_in_period = self.to_period_sol(y_sols, periodic_data)
        # Save progress
        self._y_sol = y_sol
        self._t_sol = t_sol
        self._y_sols = y_sols_in_period
        self._t_sols = t_sols
        self._y_events = y_events_flat
        self._t_events = t_events_flat
        return
    
    @staticmethod
    def flatten_events(ys, ts):
        ys_flat = [flatten_sub_sub for flatten_sub in ys 
                   for flatten_sub_sub in flatten_sub]
        ts_flat = [flatten_sub_sub for flatten_sub in ts 
                   for flatten_sub_sub in flatten_sub]
        return ys_flat, ts_flat
    
    @staticmethod
    def sort_events(ys, ts):
        if any((not ys, not ts)):
            return ys, ts
        # Combite states and times together so that they are sorted together
        ys_ts_zip = zip(ys, ts)
        ys_ts_sort = sorted(ys_ts_zip, key=lambda y_t: y_t[1])
        # Unzip sorted states and times
        ys_sort, ts_sort = list(zip(*ys_ts_sort))
        return ys_sort, ts_sort
    
    @staticmethod
    def insert_events(y_sol_raw, t_sol_raw, y_events_sort, t_events_sort, dt):
        y_sol = y_sol_raw.copy()
        t_sol = t_sol_raw.copy()
        for (i,t_event) in enumerate(t_events_sort):
            state_to_insert = y_events_sort[i]
            time_to_insert = t_event
            for (j,t) in enumerate(t_sol):
                if (dt == "+") and (t >= t_event):
                    y_sol = np.insert(y_sol, j, state_to_insert, axis=1)
                    t_sol = np.insert(t_sol, j, time_to_insert)
                    break
                if (dt == "-") and (t <= t_event):
                    y_sol = np.insert(y_sol, j, state_to_insert, axis=1)
                    t_sol = np.insert(t_sol, j, time_to_insert)
                    break
        return y_sol, t_sol
    
    @staticmethod
    def split_sol(ys, ts, t_markers):
        if not t_markers:
            return [ys,], [ts,]
        yss, tss = [], []
        # Find temporal indexes of markers in ts
        i_markers = []
        for t_marker in t_markers:
            for (i,t) in enumerate(ts):
                if (t == t_marker):
                    i_markers.append(i)
                    break
        # Add first and last temporal indexes, makes algorithm easier
        if (i_markers[0] != 0): i_markers.insert(0, 0)
        if (i_markers[-1] != len(ts)): i_markers.append(len(ts))
        # Split ys and ts by i_markers
        for i in range(len(i_markers)-1):
            left = i_markers[i]
            right = i_markers[i+1]+1 if (i != len(i_markers)-1) else i_markers[i+1]
            yss.append(ys[:,left:right].copy())
            tss.append(ts[left:right].copy())
        return yss, tss
    
    @staticmethod
    def to_period_sol(yss, periodic_data):
        yss_in_period = [[]]*len(yss)
        for i in range(len(yss)):
            ys = yss[i]
            for (j,data) in periodic_data.items():
                offset, period = data
                ys_in_period = bring_vector_in_bounds(ys[j], offset, period)
                yss_in_period[i].append(ys_in_period)
        return yss_in_period
