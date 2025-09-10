
[![CI](https://github.com/esbenscriver/squarem-JAXopt/actions/workflows/ci.yml/badge.svg)](https://github.com/esbenscriver/squarem-JAXopt/actions/workflows/ci.yml)
[![CD](https://github.com/esbenscriver/squarem-JAXopt/actions/workflows/cd.yml/badge.svg)](https://github.com/esbenscriver/squarem-JAXopt/actions/workflows/cd.yml)
# squarem-JAXopt
squarem-JAXopt is an implementation of the SQUAREM accelerator for solving fixed-point equations, see [Du and Varadhan (2020)](https://doi.org/10.18637/jss.v092.i07). SQUAREM is implemented in [JAX](https://github.com/jax-ml/jax) and [JAXopt](https://github.com/google/jaxopt). The later allow for implicit differentiation of the fixed-point.

## Installation

```bash
pip install squarem-JAXopt
```

## Usage

```python

import jax
import jax.numpy as jnp
from jax import random

from jaxopt import FixedPointIteration, AndersonAcceleration
from squarem_jaxopt import SquaremAcceleration

# Increase precision to 64 bit
jax.config.update("jax_enable_x64", True)

N = 4

a = random.uniform(random.PRNGKey(111), (N, 1))
b = random.uniform(random.PRNGKey(112), (1, 1))


def fun(x: jnp.ndarray) -> jnp.ndarray:
    y = a + x @ b
    return y


fxp_none = FixedPointIteration(fixed_point_fun=fun, verbose=True)
result_none = fxp_none.run(jnp.zeros_like(a))

fxp_anderson = AndersonAcceleration(fixed_point_fun=fun, verbose=True)
result_anderson = fxp_anderson.run(jnp.zeros_like(a))

fxp_squarem = SquaremAcceleration(fixed_point_fun=fun, verbose=True)
result_squarem = fxp_squarem.run(jnp.zeros_like(a))
```