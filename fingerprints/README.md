# Fingerprints

Measured corpora: one CSV per maker, from `vtl measure folder/ -o name.csv` (kernel `canon3-v8`). Only the measurements are here, not the images.

**Add yours:** open a PR with a CSV and a row in the table below, or use the *Share a fingerprint* issue template. Say how the images were made and selected, because the selection is half the result.

| file | n | what | how made / selected |
|---|---|---|---|
| `museum_reproductions.csv` | 116 | digital reproductions of artworks, mostly paintings | downloaded reproductions; 100 carry Metropolitan Museum Open Access image IDs (`DP…`/`DT…`), 16 are named works from other collections (Courtauld, Barnes, Orsay, Wikimedia). Selection not recorded. |
| `ai_images_mixed.csv` | 63 | AI-generated images, mixed engines | source, engines and prompts not recorded (filenames are mostly opaque) |
| `adobe_firefly_1x1.csv` | 100 | Adobe Firefly, 1:1 | everyday-subject prompts (the prompt is in each filename); model version not recorded |

## A first look (and why it's not a verdict)

```
                  within 0.15 of center   x_p (median)   SDI (median)
museum reproductions       91%               0.517          0.253
AI, mixed                  89%               0.445          0.233
Firefly 1:1                67%               0.406          0.227
```

The obvious story, "AI centers, painters don't," **isn't what these numbers say.** The museum set is the most centered here. Where it does separate from Firefly is peripheral pull (xₚ, Cohen's d ≈ 1.4) and dispersion (SDI, d ≈ 1.0): paintings carry more structure out toward the edges and spread it wider. Firefly varies more in packing density (ρᵣ) and cohesion (μ).

**Centered how?** A centered centroid can come from one body in the middle or from masses balancing across it ([interpretation](../docs/interpretation.md#a-centered-centroid-has-two-very-different-causes)). Among the images that read as centered (within 0.15):

```
                  one dominant body (μ > 0.1)   mass spread wide (SDI > 0.25)
museum reproductions          4%                           59%
AI, mixed                    12%                           38%
Firefly 1:1                  31%                           25%
```

The museum set mostly reaches center by spreading and balancing; Firefly more often parks one body there. The cutoffs are quick, untested choices: read this as a direction worth testing, not a result. The kernel doesn't detect counterbalance directly. See the [Image Structure Reader](https://www.parallaxmetrology.com/isr.html) for that.

What this doesn't control: the sets weren't matched on subject (Firefly prompts are everyday scenes; the museum set's subjects weren't chosen to match them), and museum reproductions are usually cropped to the picture edge, while generated images have no edge to crop to. A subject-matched comparison (same subjects, painted vs generated) would say much more. If you have a set like that, please add it.

Reproduce:

```python
import pandas as pd, vtl
m = pd.read_csv("fingerprints/museum_reproductions.csv")
f = pd.read_csv("fingerprints/adobe_firefly_1x1.csv")
vtl.compare(m, f, labels=("museum", "firefly"))
```
