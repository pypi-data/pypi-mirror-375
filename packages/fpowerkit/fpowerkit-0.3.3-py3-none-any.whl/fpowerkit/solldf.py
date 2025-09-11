from typing import List, Optional, Tuple
import cvxpy as cp
from cvxpy import Constraint
from cvxpy import Expression
from .solbase import DEFAULT_SAVETO, GridSolveResult
from .grid import Grid
from .island import Island
from .utils import VarBank
from .solcvx import ManualSolver


class LinDistFlowSolver(ManualSolver):
    def __init__(self, grid:Grid, eps:float = 1e-6, max_iter:int = 1000, *,
            default_saveto:str = DEFAULT_SAVETO, bank: Optional[VarBank] = None,
            solver = cp.ECOS_BB):
        super().__init__(grid, eps, max_iter, default_saveto=default_saveto, bank=bank, solver=solver)
    
    def solve(self, _t:int, /, *, timeout_s: float = 1) -> Tuple[GridSolveResult, float]:
        return super().solve(_t, timeout_s=timeout_s, calc_line=False)
        
    def proc_solution(self, i: int, _t:int, bank: VarBank, grid: Grid, island: Island) -> Tuple[List[Constraint], Expression]:
        cons = []
        obj = 0
        # Bind GEN vars to Bus
        pg: 'dict[str, list]' = {b: [] for b in island.Buses}
        qg: 'dict[str, list]' = {b: [] for b in island.Buses}
        pd: 'dict[str, float]' = {bID: b.Pd(_t) for bID, b in island.BusItems()}
        qd: 'dict[str, float]' = {bID: b.Qd(_t) for bID, b in island.BusItems()}

        # Collect power generation data and set objective
        for gID, g in island.GenItems():
            act = g.active_var(bank)
            p = g.P_var(bank, _t)
            q = g.Q_var(bank, _t)
            pg[g.BusID].append(p)
            qg[g.BusID].append(q)
            obj += g.CostA(_t) * p ** 2 + g.CostB(_t) * p + g.CostC(_t)
        
        # Collect power generation data for PV and ESS
        for pID, p in island.PVWItems():
            pg[p.BusID].append(p.Pr_var(bank, _t))
            qg[p.BusID].append(p.Qr_var(bank, _t))
        
        for eID, e in island.ESSItems():
            p, q = e.GetLoad(_t, island.grid.ChargePrice(_t), island.grid.DischargePrice(_t))
            e.P = p
            if p > 0:
                pd[e.BusID] += p
                qd[e.BusID] += q
            elif p < 0:
                pg[e.BusID].append(-p)
                qg[e.BusID].append(-q)

        # Add power constraints for each bus
        for j, bus in island.BusItems():
            flow_in = island.grid.LinesOfTBus(j)
            flow_out = island.grid.LinesOfFBus(j)
            
            # P constraint
            inflow = cp.sum([ln.P_var(bank) for ln in flow_in if ln.ID in island.Lines])
            outflow = cp.sum([ln.P_var(bank) for ln in flow_out if ln.ID in island.Lines])
            cons.append(
                inflow + cp.sum(pg[j]) == outflow + pd[j]
            )

            # flow_in and flow_out are Python generators, which cannot be reused, thus needed to be re-assigned
            flow_in = island.grid.LinesOfTBus(j)
            flow_out = island.grid.LinesOfFBus(j)
            # Q constraint
            q_inflow = cp.sum([ln.Q_var(bank) for ln in flow_in if ln.ID in island.Lines])
            q_outflow = cp.sum([ln.Q_var(bank) for ln in flow_out if ln.ID in island.Lines])
            cons.append(
                q_inflow + cp.sum(qg[j]) == q_outflow + qd[j]
            )
        
        # Add line constraints
        for lid, l in island.LineItems():
            fbus = grid.Bus(l.fBus)
            tbus = grid.Bus(l.tBus)
            if fbus is None or tbus is None:
                raise ValueError(f"Line {l.ID} has no bus {l.fBus} or {l.tBus}")
            act = l.active_var(bank)
            vf = fbus.V2_var(bank) if not fbus.FixedV else fbus.V ** 2 # type: ignore
            vt = tbus.V2_var(bank) if not tbus.FixedV else tbus.V ** 2 # type: ignore
            p = l.P_var(bank)
            q = l.Q_var(bank)
            cons.append(vt == (vf - 2*l.R*p - 2*l.X*q))
            l.I = None # Clear the current variable to avoid confusion
        
        return cons, obj # type: ignore
