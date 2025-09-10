"""Implementation of the SQUAREM accelerator method in JAXopt."""

from typing import Any
from typing import Callable
from typing import NamedTuple
from typing import Optional
from typing import Union

from dataclasses import dataclass

import jax.numpy as jnp

from jaxopt._src import base
from jaxopt._src.tree_util import tree_l2_norm, tree_sub


class SquaremState(NamedTuple):
    """Named tuple containing state information.
    Attributes:
      iter_num: iteration number
      error: residuals of current estimate
      aux: auxiliary output of fixed_point_fun when has_aux=True
      num_fun_eval: number of function evaluations
    """

    iter_num: jnp.ndarray | int
    error: jnp.ndarray | float
    aux: Optional[Any] = None
    num_fun_eval: jnp.ndarray | int = jnp.asarray(0)


@dataclass(eq=False)
class SquaremAcceleration(base.IterativeSolver):
    """SQUAREM accelerator method.
    Attributes:
      fixed_point_fun: a function ``fixed_point_fun(x, *args, **kwargs)``
        returning a pytree with the same structure and type as x
        The function should fulfill the Banach fixed-point theorem's assumptions.
      maxiter: maximum number of iterations.
      tol: tolerance (stopping criterion)
      has_aux: wether fixed_point_fun returns additional data. (default: False)
        if True, the fixed is computed only with respect to first element of the
        sequence returned. Other elements are carried during computation.
      verbose: whether to print information on every iteration or not.

      implicit_diff: whether to enable implicit diff or autodiff of unrolled
        iterations.
      implicit_diff_solve: the linear system solver to use.

      jit: whether to JIT-compile the optimization loop (default: True).
      unroll: whether to unroll the optimization loop (default: "auto")
    References:
      https://doi.org/10.18637/jss.v092.i07
    """

    fixed_point_fun: Callable
    maxiter: int = 100
    tol: float = 1e-5
    has_aux: bool = False
    verbose: Union[bool, int] = False
    implicit_diff: bool = True
    implicit_diff_solve: Optional[Callable] = None
    jit: bool = True
    unroll: base.AutoOrBoolean = "auto"

    def init_state(self, init_params, *args, **kwargs) -> SquaremState:
        """Initialize the solver state.

        Args:
          init_params: initial guess of the fixed point, pytree
          *args: additional positional arguments to be passed to ``optimality_fun``.
          **kwargs: additional keyword arguments to be passed to ``optimality_fun``.
        Returns:
          state
        """
        return SquaremState(
            iter_num=jnp.asarray(0),
            error=jnp.asarray(jnp.inf),
            aux=None,
            num_fun_eval=jnp.asarray(0, base.NUM_EVAL_DTYPE),
        )

    def squarem_step(self, params: Any, *args, **kwargs) -> tuple[Any, Any]:
        """Update fixed-point by SQUAREM

        Args:
          params: pytree containing the parameters.
          *args: additional positional arguments to be passed to
            ``fixed_point_fun``.
          **kwargs: additional keyword arguments to be passed to
            ``fixed_point_fun``.

        Returns:
            step_next (OptStep): updated states
        """
        params1 = self._fun(params, *args, **kwargs)[0]
        params2 = self._fun(params1, *args, **kwargs)[0]

        # Accelerated step
        r = params1 - params  # change
        v = params2 - params1 - r  # curvature

        alpha = -jnp.sqrt(jnp.sum(r**2) / jnp.sum(v**2))

        params3 = jnp.where(
            jnp.isnan(alpha), params2, params - 2 * alpha * r + (alpha**2) * v
        )

        return self._fun(params3, *args, **kwargs)

    def update(self, params: Any, state: SquaremState, *args, **kwargs) -> base.OptStep:
        """Performs one iteration of the SQUAREM accelerator method.
        Args:
          params: pytree containing the parameters.
          state: named tuple containing the solver state.
          *args: additional positional arguments to be passed to
            ``fixed_point_fun``.
          **kwargs: additional keyword arguments to be passed to
            ``fixed_point_fun``.
        Returns:
          (params, state)
        """
        next_params, aux = self.squarem_step(params, *args, **kwargs)
        error = tree_l2_norm(tree_sub(next_params, params))
        next_state = SquaremState(
            iter_num=state.iter_num + 1,
            error=error,
            aux=aux,
            num_fun_eval=state.num_fun_eval + 3,
        )

        if self.verbose:
            self.log_info(next_state, error_name="Distance btw Iterates")
        return base.OptStep(params=next_params, state=next_state)

    def optimality_fun(self, params, *args, **kwargs):
        """Optimality function mapping compatible with ``@custom_root``."""
        new_params, _ = self._fun(params, *args, **kwargs)
        return tree_sub(new_params, params)

    def __post_init__(self):
        super().__post_init__()

        if self.has_aux:
            self._fun = self.fixed_point_fun
        else:
            self._fun = lambda *a, **kw: (self.fixed_point_fun(*a, **kw), None)

        self.reference_signature = self.fixed_point_fun
