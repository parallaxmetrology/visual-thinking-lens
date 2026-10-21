# Lineage: notebooks → package

VTL began as a set of Colab notebooks. This package ports the canonical ones. The goldens in `tests/golden/` were produced by executing the **original notebook cells** (`tools/golden_from_notebooks.py`), and the test suite holds the package to them.

| package | source notebook | version tag | status |
|---|---|---|---|
| `vtl.kernel`, `vtl.qa` | `Canon3_v8_updated_(1).ipynb`: Canonical Gradient Field Extractor, Canon 3 + SDI + Perona–Malik | `canon3-v8` | ported, golden-tested |
| `vtl.color` | `Color_Kernel_v048_updated.ipynb`: color/value kernel | `color-v0.4.8` | `compute_color` ported, golden-tested |
| `vtl.radial` | `RCA2_Dual_Center_fixed_canon5_21.ipynb`: Dual-Center Radial Compliance | `rca2-5.21` | ported, golden-tested |
| `vtl.corpus` | `Fingerprint_5_21_updatedNEW_GRAPH_added.ipynb`: Engine Behavioral Fingerprint v0.3.7 | — | dispersion, operating window, rigidity ported |
| — | `VTL_Full_Readout_VCLIG_fixedv4CANON_6Layer…ipynb`: six-layer readout (RCA, VCLI-G × SCI, tonal, multi-island resistance) | — | **to port** |
| — | `VTL_Parallax_Masks_updated_5_21.ipynb`: ~14 perceptual masks (opponency, cone ceiling, zone system, DoG…) | — | **to port** |
| — | Color notebook: `compute_joint`, salience, `regime_tags` | — | **to port** (needs a decision, see below) |
| — | Fingerprint notebook: noise-sensitivity sweep | — | **to port** |

Superseded and not ported: `VTL_Kernel_Metrics_…Canon_3_SDI (9).ipynb` (Canon 3 without Perona–Malik), `VTL_Full_Readout_Layer6_fixed_5_21.ipynb`, `VTL_Field_Decomposition_Notebook_v2` (teaching material), and the 2025 LSI-lite notebooks.

## Divergent spatial kernels: read before comparing old CSVs

The color and fingerprint notebooks each embed their **own** spatial kernel, and it is *not* Canon 3:

| | Canon 3 v8 (`vtl.measure`) | color / fingerprint notebooks |
|---|---|---|
| mass mask | gradient band P85–P97, 2 px border guard | gradient ≥ P85 |
| `x_p` | unweighted gradient share in outer 15% band | weighted, 8% margin |
| `theta` | 8 bins | 18 bins |
| centroid | unweighted mask mean | weighted |

So `delta_x`, `x_p`, `theta`, etc. in CSVs produced by those notebooks **aren't comparable** with `vtl.measure` output, even though the names match. The package uses Canon 3 everywhere. The color notebook's joint metrics (`compute_joint`, `regime_tags`) were defined on top of its own spatial variant, which is why they aren't ported yet: porting them means either re-basing them on Canon 3 (new numbers) or shipping the variant under a distinct name. That's an open decision, tracked as an issue.

## Related code elsewhere

- `vtl-demo/vtl_core.py` (the Streamlit semiconductor demo) is **VTL v3.1, a different 15-coordinate descriptor** for inspection imagery (Visual Topology of Light). It reuses names like `r_v` and `rho_r` with different meanings. It belongs in its own repository.
- The JavaScript kernels in the site's apps (The Crit, Counterweight) use an Otsu material mask. They are close cousins, not ports. The browser demo in `docs/` is a direct port of Canon 3; see `docs/demo.md`.
