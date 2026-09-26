#!/usr/bin/env python
"""Per-epoch head operating-region diagnostics.

Collected by REUSING the epoch-end validation forward that run_train already performs
(eval_metrics_with_overlap_grouped -> model(...) under model.eval()). A forward hook appends the
tensors the model already stashes; no extra forward is run, no RNG is consumed, and no
model.train/eval state is touched. With the collector disabled the hook returns immediately.

Support is fixed before training:
  event_rows      cells where _last_lead_loss_mask is True  (the mu_event_n contract)
  all_valid_rows  cells where valid_mask is True
Both are written; the support name is recorded on every row.
Quantiles are EXACT over the whole tensor -- the validation cohort is small enough that no
sampling, histogram or reservoir is needed, so there is no approximation error and no RNG.
"""
from __future__ import annotations
import json, os, tempfile
from pathlib import Path
import numpy as np
import torch

QUANTILES = (5, 25, 50, 75, 95)


class HeadRegionCollector:
    def __init__(self, model, lead_min, lead_max, scale, bias, T):
        self.model = model
        self.lead_min, self.lead_max = float(lead_min), float(lead_max)
        self.scale, self.bias, self.T = float(scale), float(bias), int(T)
        self.enabled = False
        self.buf = []
        self._h = model.register_forward_hook(self._hook)

    def _hook(self, mod, inp, out):
        if not self.enabled:
            return
        raw = getattr(mod, "_last_raw_lead_BK", None)
        if raw is None:
            return
        self.buf.append({
            "raw": raw.detach().float().cpu(),
            "logit": mod._last_lead_logit_BK.detach().float().cpu(),
            "lead": mod._last_lead_BK.detach().float().cpu(),
            "mu_pre": mod._last_mu_pre_BK.detach().float().cpu(),
            "mask": (mod._last_lead_loss_mask.detach().cpu()
                     if getattr(mod, "_last_lead_loss_mask", None) is not None else None)})

    def close(self):
        try:
            self._h.remove()
        except Exception:                                                 # noqa: BLE001
            pass

    def start(self):
        self.buf = []
        self.enabled = True

    def stop(self):
        self.enabled = False

    @staticmethod
    def _stats(x, prefix):
        x = np.asarray(x, dtype=np.float64)
        if x.size == 0:
            return {f"{prefix}_{k}": float("nan") for k in
                    ("count", "mean", "sd", *[f"p{q:02d}" for q in QUANTILES])}
        out = {f"{prefix}_count": int(x.size), f"{prefix}_mean": float(x.mean()),
               f"{prefix}_sd": float(x.std(ddof=1)) if x.size > 1 else float("nan")}
        for q, v in zip(QUANTILES, np.percentile(x, QUANTILES)):
            out[f"{prefix}_p{q:02d}"] = float(v)
        return out

    def summarize(self, epoch, support):
        if not self.buf:
            return None
        raw = torch.cat([b["raw"].reshape(-1) for b in self.buf]).numpy()
        logit = torch.cat([b["logit"].reshape(-1) for b in self.buf]).numpy()
        lead = torch.cat([b["lead"].reshape(-1) for b in self.buf]).numpy()
        mu_pre = torch.cat([b["mu_pre"].reshape(-1) for b in self.buf]).numpy()
        if support == "event_rows":
            if any(b["mask"] is None for b in self.buf):
                return None
            m = torch.cat([b["mask"].reshape(-1) for b in self.buf]).numpy().astype(bool)
            raw, logit, lead, mu_pre = raw[m], logit[m], lead[m], mu_pre[m]
        rec = {"epoch": int(epoch), "support": support}
        rec.update(self._stats(raw, "raw_lead"))
        rec.update(self._stats(logit, "transformed_logit"))
        rec.update(self._stats(lead, "lead_pre_clamp"))
        n = max(raw.size, 1)
        for t in (1, 2, 3):
            rec[f"raw_p_ge_{t}"] = float((raw >= t).mean()) if raw.size else float("nan")
        # clip_amount is defined on mu BEFORE the clamp, so a value that legitimately equals
        # T-1 is not counted as clipped.
        clip_amount = np.maximum(mu_pre - (self.T - 1), 0.0)
        is_clipped = clip_amount > 0
        rec["clip_rate"] = float(is_clipped.mean()) if raw.size else float("nan")
        cl = clip_amount[is_clipped]
        rec["clip_amount_mean"] = float(cl.mean()) if cl.size else 0.0
        rec["clip_amount_p50"] = float(np.median(cl)) if cl.size else 0.0
        rec["clip_amount_p95"] = float(np.percentile(cl, 95)) if cl.size else 0.0
        rec["clip_amount_max"] = float(cl.max()) if cl.size else 0.0
        # the sigmoid never reaches its bounds exactly, so contact is a distance, not equality
        for d in (1.0, 0.1):
            tag = str(d).replace(".", "p")
            rec[f"within_{tag}d_of_lead_min"] = float((lead <= self.lead_min + d).mean())
            rec[f"within_{tag}d_of_lead_max"] = float((lead >= self.lead_max - d).mean())
        rec["lead_min"], rec["lead_max"] = self.lead_min, self.lead_max
        rec["logit_scale"], rec["logit_bias"] = self.scale, self.bias
        rec["n_batches"] = len(self.buf)
        return rec


def atomic_write_jsonl(path: Path, rows):
    """tmp + os.replace so a partial failure cannot damage an existing file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(tmp, path)
