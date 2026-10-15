# Palimpsest reaction–transport model

Palimpsest is Prototype 2 of PRIMORDIA. Its research question is:

> Can locally produced structure alter transport strongly enough to create a compartment whose internal dynamics respond differently from the environment?

This is a hypothesis, not a homeostasis claim.

## Additional fields

- **W — waste:** produced by the A/B conversion, diffuses, and decays.
- **M — matrix:** a slow structural-memory field deposited near reaction fronts.

The original A, B, R, and T equations remain. If Palimpsest is disabled, W and M remain zero and Prototype 1 behavior is retained.

## Waste

~~~text
dW/dt = waste_production × reaction
        − waste_decay × W
        + divergence(D_W(M) gradient(W))
~~~

Waste is a reaction product and has no goal or signal semantics.

## Matrix

The local magnitude of the B gradient estimates a reaction front:

~~~text
front = magnitude(central_gradient(B))
~~~

Matrix changes according to:

~~~text
dM/dt = deposition × W × (front + 0.02 B)
        − erosion × M
        − dissolution × W × M
~~~

The small B term leaves weak traces inside active regions; the gradient term favors boundary-like deposits. Matrix is stationary in this prototype and bounded to [0, 1].

## Matrix-dependent transport

For field X:

~~~text
D_X(M) = base_D_X × exp(−permeability_X × M)
~~~

Diffusion is implemented as the divergence of face flux. Adjacent-cell diffusivities are averaged at each face, equal and opposite flux is applied to both cells, and total quantity is conserved in a closed diffusion-only world.

## Boundary-fed environment

The Palimpsest preset uses reflective boundaries and applies resource/thermal exchange only at the outermost cells. Resource and heat must then travel through the world by diffusion. This makes a matrix enclosure capable of changing transport between an interior and the external reservoir.

## Enclosure measurement

Cells with M above `enclosure_threshold` are treated as barrier cells for analysis. A flood fill starts at the rectangular world boundary and travels through non-barrier cells. Non-barrier cells it cannot reach are classified as enclosed.

This detector is an observation tool. It does not affect simulation dynamics.

## Four matched controls

After one dynamic world matures, the runner clones its exact state into:

1. **dynamic** — matrix continues deposition and erosion;
2. **no_matrix** — matrix is removed and its transport effects disabled;
3. **frozen** — the same mature matrix remains but cannot rebuild;
4. **random** — equal matrix values are spatially shuffled and frozen.

All branches receive the same ambient-temperature shift and optional central breach. Their CSV files record global fields, total waste/matrix, matrix variability, enclosed cell count, and interior/exterior temperature and resource.

## Interpretation

A dynamic branch returning toward its earlier state is insufficient. Useful evidence would require a consistent advantage over frozen, random, and no-matrix controls; a resource or dissipation cost; robustness across seeds; and a finite disturbance range beyond which regulation fails.
