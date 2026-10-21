// Runs the kernel off the main thread so the page stays responsive.
import { measureRGBA } from "./kernel.js";

self.onmessage = (e) => {
  const { id, buffer, w, h } = e.data;
  try {
    const { kernel, fields } = measureRGBA(new Uint8ClampedArray(buffer), w, h);
    self.postMessage({ id, kernel, mask: fields.mask }, [fields.mask.buffer]);
  } catch (err) {
    self.postMessage({ id, error: String(err) });
  }
};
