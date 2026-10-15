# Mathematics

## Fields

At grid cell (i, j) and time t, A is the feed reactant, B is the autocatalytic reactant, R is a consumed resource that gates reaction strength, and T is dimensionless local temperature. T = 1 is the reference condition. Values are normalized concentrations or intensities, not molecule counts. Unit cell spacing is assumed.

## Established starting point: Gray–Scott

The standard Gray–Scott model is:

~~~text
dA/dt = D_A Laplacian(A) - A B² + f(1 - A)
dB/dt = D_B Laplacian(B) + A B² - (f + k)B
~~~

D_A and D_B are diffusion coefficients, f is feed, and k is removal. The nonlinear term A B² lets B catalyze conversion of A into more B. Depending on parameters, spatial perturbations can form spots, stripes, waves, or decay.

Reference: John E. Pearson, “Complex Patterns in a Simple System,” *Science* 261 (1993), 189–192, DOI: 10.1126/science.261.5118.189.

## PRIMORDIA modifications

PRIMORDIA replaces A B² with:

~~~text
q = A B² [R / (K_R + R)] exp(clip(alpha(T - 1), -3, 3))
~~~

The resource factor tends to zero as resource vanishes and approaches one when resource is abundant. K_R is the half-saturation scale. The exponential is an Arrhenius-like phenomenological temperature factor; it is bounded to prevent overflow and is not a calibrated chemical law.

Local reaction terms are:

~~~text
dA_reaction/dt = -q + f(1 - A)
dB_reaction/dt =  q - (f + k)B
dR_reaction/dt = -c_R q
dT_reaction/dt =  h_q q
~~~

The last two equations are experimental additions: reaction consumes resource at rate c_R and releases normalized heat at rate h_q. Temperature changes reaction rate, while reaction changes temperature. No target temperature appears in the chemical reaction.

## Environment

Resource exchange is explicit:

~~~text
dR_environment/dt = s_R(R_target - R) - m_R R
~~~

s_R supplies toward environmental concentration R_target, while m_R removes resource. This makes the default world open.

Thermal exchange is:

~~~text
dT_environment/dt = lambda_T(T_ambient - T) + H_external
~~~

This is Newton-style passive exchange with an ambient reservoir plus external heating or cooling. It can restore temperature after a disturbance by passive relaxation. That is not evidence of active homeostasis.

## Diffusion and boundaries

For each field X, diffusion adds D_X Laplacian(X). The five-point stencil is:

~~~text
Laplacian(X)[i,j] =
    X[i+1,j] + X[i-1,j] + X[i,j+1] + X[i,j-1] - 4 X[i,j]
~~~

Periodic boundaries wrap opposite edges, making the grid a torus. Reflective boundaries repeat edge values, approximating zero normal flux. In isolation, both implemented Laplacians sum to zero to floating-point precision.

## Time integration and stability

All derivatives are computed from state n, then forward Euler advances:

~~~text
X[n+1] = X[n] + dt * dX[n]/dt
~~~

The default dt = 0.5 is conservative for the provided coefficients and regimes, but no universal stability guarantee exists for arbitrary edited parameters. Use a smaller step with larger diffusion, reaction, or thermal sensitivity.

After integration, A and B are clamped to [0, 1.5], R to [0, 2], and T to [0, 3]. Clamping prevents numerical divergence but can artificially create or destroy field quantity. Tests isolate a regime where clamps are inactive and verify conservation of diffusion-only totals.

## Conservation and interpretation

The feed/removal terms, resource exchange, thermal exchange, and clamps are sources or sinks. The default world is not conservative. Only deliberately closed configurations should be tested for conservation.

Spatial patterning demonstrates nonlinear dynamics and symmetry breaking. Persistence can be measured, but it does not by itself demonstrate self-maintenance. Recovery after disturbance must be compared with passive and feedback-disabled controls before it can support a homeostasis claim.
