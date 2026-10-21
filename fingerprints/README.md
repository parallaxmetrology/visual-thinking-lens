# Fingerprints

Measured corpora: one CSV per maker, from `vtl measure folder/ -o name.csv` (kernel `canon3-v8`). Only the measurements are here, not the images.

**Add yours:** open a PR with a CSV and a row in the table below, or use the *Share a fingerprint* issue template. Say how the images were made and selected, because the selection is half the result.

| file | n | what | how made / selected |
|---|---|---|---|
| `museum_photos.csv` | 116 | photographs of museum paintings | *TODO (Russell): source and framing; are frames/walls included?* |
| `ai_images_mixed.csv` | 63 | AI-generated images, mixed engines | *TODO (Russell): engines, prompts* |
| `adobe_firefly_1x1.csv` | 100 | Adobe Firefly, 1:1 | *TODO (Russell): prompts, model version* |

## A first look (and why it's not a verdict)

```
                  within 0.15 of center   x_p (median)   SDI (median)
museum photos              91%               0.517          0.253
AI, mixed                  89%               0.445          0.233
Firefly 1:1                67%               0.406          0.227
```

The obvious story, "AI centers, painters don't," **isn't what these numbers say.** The museum set is the most centered here. Where it does separate from Firefly is peripheral pull (xₚ, Cohen's d ≈ 1.4) and dispersion (SDI, d ≈ 1.0): paintings carry more structure out toward the edges and spread it wider. Firefly varies more in packing density (ρᵣ) and cohesion (μ).

A likely confound sits right on top of the placement result: if these are photos of paintings, they were centered by whoever took them, possibly frame and all. A cleaner comparison would use edge-to-edge scans of the paintings themselves. If you have a set like that, please add it.

Reproduce:

```python
import pandas as pd, vtl
m = pd.read_csv("fingerprints/museum_photos.csv")
f = pd.read_csv("fingerprints/adobe_firefly_1x1.csv")
vtl.compare(m, f, labels=("museum", "firefly"))
```
