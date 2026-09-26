#!/usr/bin/env python
"""Selector persistence: models, candidate feature table, per-seed scores/picks, optimal set.

Everything lands under <cell_output_root>/selector_artifacts_v2/ via tmp + os.replace, so a
partial failure cannot damage any pre-existing output. Nothing here changes what the evaluator
computes; it only records what was already produced in memory.
"""
from __future__ import annotations
import hashlib, json, os, tempfile
from pathlib import Path
import numpy as np
import pandas as pd

# Fixed BEFORE any result is inspected.
TIE_TOL = 1e-12                      # optimal set = within this of the sample max iou80_real
TIE_BREAK = "min_offset"             # exact-best offset when several tie
TARGET = "iou80_real"                # selector target; NOT the evaluator's masked/geom metric


def _atomic(path: Path, write_fn):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    os.close(fd)
    try:
        write_fn(tmp)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


LIST_SERIALIZATION = "json"      # list-valued columns are written as JSON strings


def _table(df: pd.DataFrame, stem: Path):
    """Write `stem` as parquet when an engine exists, else CSV -- and NAME THE FILE for what it
    actually contains. A CSV loses dtypes, so a sidecar `.schema.json` records them plus the
    serialization rule for list-valued columns, which is what makes the CSV round-trippable."""
    stem = Path(stem)
    d = df.copy()
    list_cols = [c for c in d.columns
                 if d[c].map(lambda v: isinstance(v, (list, tuple))).any()]
    for c in list_cols:
        d[c] = d[c].map(lambda v: json.dumps(list(v)) if isinstance(v, (list, tuple)) else v)
    schema = {"columns": [{"name": c, "dtype": str(df[c].dtype),
                           "is_list": c in list_cols,
                           "serialization": LIST_SERIALIZATION if c in list_cols else "scalar"}
                          for c in df.columns],
              "n_rows": int(len(df)), "list_serialization": LIST_SERIALIZATION}
    try:
        import pyarrow                                                   # noqa: F401
        path = stem.with_suffix(".parquet")
        _atomic(path, lambda t: df.to_parquet(t, index=False))
        schema["format"] = "parquet"
    except Exception:                                                    # noqa: BLE001
        path = stem.with_suffix(".csv")
        _atomic(path, lambda t: d.to_csv(t, index=False))
        schema["format"] = "csv"
    schema["file"] = path.name
    _json(schema, stem.with_suffix(".schema.json"))
    return path


def _parquet(df: pd.DataFrame, path: Path):     # kept for call-site compatibility
    return _table(df, Path(path).with_suffix(""))


def _json(obj, path: Path):
    _atomic(path, lambda tmp: Path(tmp).write_text(json.dumps(obj, indent=1, default=str)))


def save_selector_models(models, seeds, outdir, tag, feature_cols, shift, meta_extra):
    import lightgbm as lgb
    outdir = Path(outdir)
    written = []
    for m, sd in zip(models, seeds):
        stem = f"model_{tag}_sel{sd}"
        _atomic(outdir / f"{stem}.txt", lambda t, m=m: m.booster_.save_model(t))
        _json({"selector_seed": int(sd), "lightgbm_version": lgb.__version__,
               "model_params": m.get_params(), "feature_names": list(feature_cols),
               "feature_order": list(range(len(feature_cols))), "target_definition": TARGET,
               "chosen_shift": int(shift), "tie_tolerance": TIE_TOL, "tie_break": TIE_BREAK,
               **meta_extra}, outdir / f"{stem}.json")
        written += [f"{stem}.txt", f"{stem}.json"]
    return written


def save_candidates(cand: pd.DataFrame, feature_cols, outdir, tag, shift, meta_extra):
    # FEATURE_COLS already contains offset / pred_mu / pred_lead / alert_tstar, so the naive
    # concatenation produced duplicate column labels and every later assignment raised.
    wanted = (["sample_id", "offset"] + list(feature_cols) +
              ["iou80_real", "iou80_geom", "feasible", "pred_mu", "pred_lead",
               "true_start", "true_mid", "L", "R", "alert_tstar", "eval_doy"])
    keep, seen = [], set()
    for c in wanted:
        if c in cand.columns and c not in seen:
            keep.append(c); seen.add(c)
    d = cand[keep].copy()
    d["lateness"] = d["alert_tstar"] + d["offset"] - (d["L"] + 1)
    d["chosen_shift"] = int(shift)
    for k, v in meta_extra.items():
        d[k] = v
    d["feature_order"] = ",".join(feature_cols)
    _table(d, Path(outdir) / f"candidates_{tag}")
    return len(d)


def save_scores_picks_optimal(cand, models, seeds, prep_X, outdir, tag, shift, meta_extra):
    outdir = Path(outdir)
    rows = []
    for m, sd in zip(models, seeds):
        s = m.predict(prep_X(cand))
        c = cand[["sample_id", "offset"]].copy()
        c["selector_seed"] = int(sd)
        c["selector_score"] = s
        pick = c.loc[c.groupby("sample_id")["selector_score"].idxmax(), ["sample_id", "offset"]]
        pick = dict(zip(pick.sample_id, pick.offset))
        c["selected_offset"] = c.sample_id.map(pick)
        c["selected"] = (c.offset == c.selected_offset).astype(int)
        rows.append(c)
    S = pd.concat(rows, ignore_index=True)
    for k, v in meta_extra.items():
        S[k] = v
    S["chosen_shift"] = int(shift)
    _table(S, outdir / f"scores_{tag}")

    picks = S[S.selected == 1][["sample_id", "selector_seed", "selected_offset"]].copy()
    for k, v in meta_extra.items():
        picks[k] = v
    picks["is_official_evaluator_pick"] = True
    _table(picks, outdir / f"picks_{tag}")
    # The 5-seed consensus is a DIAGNOSTIC. pest_eval evaluates each seed's picks separately and
    # averages the metrics; it never forms a consensus offset. Kept in its own file so it cannot
    # be mistaken for the official pick.
    cons = (picks.groupby("sample_id").selected_offset
            .agg(lambda x: int(pd.Series(x).mode().min()))
            .rename("consensus_selected_offset").reset_index())
    cons["diagnostic_only"] = True
    cons["not_part_of_official_evaluator"] = True
    cons["consensus_rule"] = "mode across selector seeds, ties broken by min offset"
    for k, v in meta_extra.items():
        cons[k] = v
    _table(cons, outdir / f"picks_consensus_diagnostic_{tag}")

    best = cand.groupby("sample_id")[TARGET].max().rename("oracle_iou80_real").reset_index()
    o = cand.merge(best, on="sample_id", how="left")
    o["in_optimal_set"] = (np.abs(o[TARGET] - o.oracle_iou80_real) <= TIE_TOL).astype(int)
    oo = o[o.in_optimal_set == 1]
    opt = (oo.groupby("sample_id").offset.agg(lambda x: sorted(int(i) for i in x))
           .rename("optimal_offset_set").reset_index())
    exact = oo.groupby("sample_id").offset.min().rename("exact_best_offset").reset_index()
    O = best.merge(opt, on="sample_id", how="left").merge(exact, on="sample_id", how="left")
    sel = picks[["sample_id", "selector_seed", "selected_offset"]].drop_duplicates()
    O = sel.merge(O, on="sample_id", how="left")
    lut = cand.set_index(["sample_id", "offset"])[TARGET]
    O["selected_iou80_real"] = [lut.get((s, o_), np.nan)
                                for s, o_ in zip(O.sample_id, O.selected_offset)]
    O["optimal_set_hit"] = [int(o_ in st) for o_, st in zip(O.selected_offset, O.optimal_offset_set)]
    O["exact_hit"] = (O.selected_offset == O.exact_best_offset).astype(int)
    O["regret"] = O.oracle_iou80_real - O.selected_iou80_real
    O["tie_tolerance"] = TIE_TOL
    O["tie_break"] = TIE_BREAK
    O["target_definition"] = TARGET
    for k, v in meta_extra.items():
        O[k] = v
    _table(O, outdir / f"optimal_{tag}")
    # Official contract: compute each selector seed's metric, then average the seeds. The pooled
    # row mean coincides only while every seed has the same sample count; both are written so a
    # future divergence is visible rather than silent.
    per = O.groupby("selector_seed")[["optimal_set_hit", "exact_hit", "regret"]].mean()
    per_seed = {int(k): {m: float(v) for m, v in row.items()} for k, row in per.iterrows()}
    official = {m: float(per[m].mean()) for m in per.columns}
    pooled = {m: float(O[m].mean()) for m in per.columns}
    summary = {
        "metric_definition": "official = mean over selector seeds of each seed's per-sample mean",
        "official_seed_mean": official, "pooled_row_mean": pooled,
        "per_seed": per_seed,
        "agrees_with_pooled": {m: bool(abs(official[m] - pooled[m]) <= 1e-12) for m in official},
        "n_samples_per_seed": {int(k): int(v) for k, v in O.groupby("selector_seed").size().items()},
        "target_definition": TARGET, "tie_tolerance": TIE_TOL, "tie_break": TIE_BREAK,
        "n_scores": int(len(S)), "n_picks": int(len(picks)), "n_optimal": int(len(O))}
    _json(summary, outdir / f"selector_summary_{tag}.json")
    return dict(n_scores=len(S), n_picks=len(picks), n_optimal=len(O),
                optimal_set_hit_rate=official["optimal_set_hit"],
                exact_hit_rate=official["exact_hit"],
                mean_regret=official["regret"],
                metric_definition="seed_mean")


def split_ids_sha256(ids) -> str:
    return hashlib.sha256(json.dumps(sorted(map(str, ids))).encode()).hexdigest()
