import jax
import jax.numpy as jnp
from jax import random

from squarem_jaxopt import SquaremAcceleration

import pytest

# Increase precision to 64 bit
jax.config.update("jax_enable_x64", True)


@pytest.mark.parametrize(
    "N",
    [
        (10),
        (100),
        (1000),
    ],
)
def test_solver(N: int) -> None:
    a = random.uniform(random.PRNGKey(111), (N, 1))
    b = random.uniform(random.PRNGKey(112), (1, 1))

    def fun(x: jnp.ndarray) -> jnp.ndarray:
        return a + x @ b

    fxp = SquaremAcceleration(fixed_point_fun=fun)
    result = fxp.run(jnp.zeros_like(a))

    assert jnp.allclose(result.params, fun(result.params)), (
        f"Error: {jnp.linalg.norm(fun(result.params) - result.params)}"
    )
