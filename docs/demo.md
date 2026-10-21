# Browser demo

`docs/index.html` is a static page (GitHub Pages) that runs the kernel in the browser:

- `kernel.js`: JavaScript port of `canon3-v8` (gray, Sobel, P85–P97 mask, all nine metrics, mask QA). Pure functions; also runs in Node.
- `worker.js`: runs the kernel off the main thread.
- `samples/`: the same sample images as `examples/images/`.
- `weight/`: *Where's the weight?*, a game using the same kernel and worker: tap where a picture balances, compare with the lens and with a blind tap at dead center.
- `lighter/`: *Lighter*, a value-judgment game on public-domain paintings (`lighter/works/`); it uses CIE L*, not the kernel.

**How close is it to Python?** On identical pixels, grayscale conversion is bit-exact and metrics agree within a few percent. Placement (Δx, Δy) agrees to about 0.001; `rho_r` is the most sensitive (about 4%), because a few threshold pixels can move the convex hull. Run `python tools/check_js_kernel.py` to see the current figures. In the browser, the larger difference is resizing (canvas smoothing vs OpenCV's INTER_AREA/INTER_CUBIC). Treat browser numbers as a preview and the Python package as the reference.

**Run locally:** `python -m http.server 8765 --directory docs`, then open http://localhost:8765. Module workers need http, so opening the file directly won't work.
