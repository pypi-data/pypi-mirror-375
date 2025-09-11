from abc import abstractmethod
from typing import List, Optional, Tuple
import cvxpy as cp
from .island import Island, IslandResult
from .utils import VarBank
from .grid import Grid
from .solbase import DEFAULT_SAVETO, GridSolveResult, SolverBase

class ManualSolver(SolverBase):
    """
    A class that use DistFlowSolver to estimate the power flow and then use OpenDSSSolver or NewtonSolver to solve the power flow problem.
    """
    def __init__(self, grid:Grid, eps:float = 1e-6, max_iter:int = 1000, *,
            default_saveto:str = DEFAULT_SAVETO, bank: Optional[VarBank] = None,
            solver = cp.ECOS):
        super().__init__(grid, eps, max_iter, default_saveto = default_saveto)
        self.bank = bank if bank is not None else VarBank()
        self.default_sovler = solver  # Default solver, can be overridden in solve method

    @abstractmethod
    def proc_solution(self, i:int, _t:int, bank: VarBank, grid: Grid, island:Island) -> Tuple[List[cp.Constraint], cp.Expression]:
        """
        Process the solution for the island.
            i: Index of the island in the grid
            _t: Time step to solve
            bank: Variable bank to store the variables and implict constraints
            grid: The grid object
            island: The island to solve
        Returns a tuple of constraints and objective expression.
            The objective will be minimized.
        """
        raise NotImplementedError
    
    def solve(self, _t:int, /, *, timeout_s: float = 1, **kwargs) -> Tuple[GridSolveResult, float]:
        ret = super().solve(_t, timeout_s=timeout_s, **kwargs)
        self.bank.apply()
        return ret
    
    def solve_island(self, i:int, island:Island, _t:int, /, **kwargs) -> Tuple[IslandResult, float]:
        """Solve the island"""
        cons, obj = self.proc_solution(i, _t, self.bank, self._g, island)
        for cname, c in self.bank._autocons.items():
            if island.hasName(cname):
                cons.append(c)
                
        prob = cp.Problem(cp.Minimize(obj), cons)
        try:
            prob.solve(solver=self.default_sovler, verbose=False, max_iters=self.max_iter)
        except cp.SolverError as e:
            if "installed" in e.args[0]:
                raise e
            return IslandResult.Failed, -1
        if prob.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
            return IslandResult.Failed, -1
        return IslandResult.OK, prob.value # type: ignore