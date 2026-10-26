"""Trace every result macro used in the canonical manuscript to its source and recompute it independently.

For each macro in manuscript/main.tex that numbers.tex defines, this script states the source file and JSON path,
recomputes the value without using make_numbers.py, and compares it with numbers.tex. It also lists the literal
numbers in the manuscript prose so they can be classified (design constants vs. results).

Usage: python -I tools/trace_claims.py [--out FILE.md]   (exit 1 on any mismatch/untraced)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = {"E1": "experiments/E1_retrieval_multiverse/analysis/confirmatory-20261018-consistent-query/results.json",
     "E1D": "experiments/E1_retrieval_multiverse/analysis/confirmatory-20261018-consistent-document/results.json",
     "E1P": "experiments/E1_retrieval_multiverse/analysis/confirmatory-20261018/results.json",
     "E2": "experiments/E2_generation/analysis/qwen3-4b-kaggle-gpu/results.json",
     "E2S": "experiments/E2_generation/analysis/posthoc-sensitivity/results.json",
     "E3": "experiments/E3_semantic_dense/analysis/confirmatory-kaggle-gpu-consistent-query/results.json",
     "E3D": "experiments/E3_semantic_dense/analysis/confirmatory-kaggle-gpu-consistent-document/results.json",
     "E3PL": "experiments/E3_semantic_dense/analysis/confirmatory-kaggle-gpu/results.json",
     "PR": "experiments/E1_retrieval_multiverse/analysis/pilot-exploratory-20261018-reconciliation/results.json",
     "PH1": "experiments/E1_retrieval_multiverse/analysis/posthoc-charmetric-20261024",
     "PH3": "experiments/E3_semantic_dense/analysis/posthoc-charmetric-bm25-20261024",
     "SV": "experiments/statistical_checks/results.json", "GC": "experiments/E1_retrieval_multiverse/analysis/posthoc-gold-containment/results.json",
     "E3RUN": "experiments/E3_semantic_dense/runs/confirmatory-kaggle-gpu", "UB": "experiments/budget_underfill/bound-consistent.json",
     "E3P": "experiments/E3_semantic_dense/analysis/exploratory-kaggle-gpu/results.json"}
DSN = {"squad2": "Squadtwo", "covidqa": "Covidqa", "cuad": "Cuad", "qasper": "Qasper"}
WORDS = {"128": "OneTwoEight", "256": "TwoFiveSix", "512": "FiveTwelve", "64": "SixFour"}


def j(key):
    return json.loads((ROOT / P[key]).read_text())


def pct(x):
    return f"{100 * x:.1f}"


def s3(x):
    return f"{x:+.3f}".replace("-", "\\ensuremath{-}")


def table() -> dict[str, tuple[str, str]]:
    """macro -> (value, source)"""
    e1, e2, e3 = j("E1"), j("E2"), j("E3")
    t: dict[str, tuple[str, str]] = {}

    def add(name, value, src):
        t[name] = (value, src)
    add("EoneNq", f"{sum(e1['n_queries'].values()):,}", f"{P['E1']}: sum(n_queries)")
    for d, n in e1["n_queries"].items():
        add(f"EoneNq{DSN[d]}", f"{n:,}", f"{P['E1']}: n_queries.{d}")
    for h, k in (("H1", "HOne"), ("H1b", "HOneB")):
        r = e1[h]
        add(f"{k}Est", pct(r["estimate"]), f"{P['E1']}: {h}.estimate")
        add(f"{k}Lo", pct(r["ci95"][0]), f"{P['E1']}: {h}.ci95[0]")
        add(f"{k}Hi", pct(r["ci95"][1]), f"{P['E1']}: {h}.ci95[1]")
    for h, k in (("H1", "HOne"), ("H1b", "HOneB"), ("H2", "HTwo"), ("H3", "HThree")):
        add(f"{k}Verdict", e1[h]["verdict"], f"{P['E1']}: {h}.verdict")
    p1 = e1["verdict_shares"]["P1"]
    for prot in ("count", "budget"):
        P_ = prot.capitalize()
        add(f"Pone{P_}FiveTwelve", pct(p1[prot]["support_B"]), f"{P['E1']}: verdict_shares.P1.{prot}.support_B")
        add(f"Pone{P_}OneTwoEight", pct(p1[prot]["support_A"]), f"{P['E1']}: verdict_shares.P1.{prot}.support_A")
        add(f"PoneUniverses{P_}", str(p1[prot]["n_universes"]), f"{P['E1']}: verdict_shares.P1.{prot}.n_universes")
    for cid in ("S2-128", "S2-256", "S1-128", "S1-64"):
        fam, w = cid.split("-")
        base = {"S2": "Stwo", "S1": "Sone"}[fam] + WORDS[w]
        for prot in ("count", "budget"):
            for side, key in (("A", "support_A"), ("B", "support_B")):
                add(f"{base}{prot.capitalize()}{side}", pct(e1["verdict_shares"][cid][prot][key]),
                    f"{P['E1']}: verdict_shares.{cid}.{prot}.{key}")
    add("HTwoDatasetEta", f"{e1['H2']['eta2']['dataset']:.2f}", f"{P['E1']}: H2.eta2.dataset")
    add("HTwoRetrieverEta", f"{e1['H2']['eta2']['retriever']:.2f}", f"{P['E1']}: H2.eta2.retriever")
    add("HTwoFraction", pct(e1["H2"]["dataset_largest_fraction"]), f"{P['E1']}: H2.dataset_largest_fraction")
    add("HThreeShare", pct(e1["H3"]["share_universes_requiring_over_500"]), f"{P['E1']}: H3.share_universes_requiring_over_500")
    add("HThreeMedianN", f"{e1['H3']['median_required_n']:,.0f}", f"{P['E1']}: H3.median_required_n")
    for k, key in (("b_without_squad2", "SensNoSquad"), ("c_default_retriever", "SensDefRet"), ("d_cluster_bootstrap", "SensCluster"),
                   ("e_all_budgets", "SensAllBudgets"), ("a_bh_fdr", "SensBH")):
        r = e1["H1_sensitivity"][k]
        add(f"{key}Est", pct(r["estimate"]), f"{P['E1']}: H1_sensitivity.{k}.estimate")
        if "ci95" in r:
            add(f"{key}Lo", pct(r["ci95"][0]), f"{P['E1']}: H1_sensitivity.{k}.ci95[0]")
            add(f"{key}Hi", pct(r["ci95"][1]), f"{P['E1']}: H1_sensitivity.{k}.ci95[1]")
    for c, key in (("P1", "Pone"), ("S3-256", "Sthree")):
        for meas, mk in (("f1", "Fone"), ("em", "Em"), ("coverage", "Cov")):
            r = e2["pooled"][c][meas]
            add(f"Etwo{key}{mk}", s3(r["did"]), f"{P['E2']}: pooled.{c}.{meas}.did")
            add(f"Etwo{key}{mk}Lo", s3(r["lo"]), f"{P['E2']}: pooled.{c}.{meas}.lo")
            add(f"Etwo{key}{mk}Hi", s3(r["hi"]), f"{P['E2']}: pooled.{c}.{meas}.hi")
            add(f"Etwo{key}{mk}Mde", f"{r['mde']:.3f}", f"{P['E2']}: pooled.{c}.{meas}.mde")
    for d, key in (("cuad", "Cuad"), ("qasper", "Qasper")):
        g = e2["datasets"][d]["diagnostics"]
        add(f"EtwoTrunc{key}", str(g["finish_reasons"].get("length", 0)), f"{P['E2']}: datasets.{d}.diagnostics.finish_reasons.length")
        add(f"EtwoJobs{key}", str(g["rows_total"]), f"{P['E2']}: datasets.{d}.diagnostics.rows_total")
    for arm, ak in (("fixed-128", "OneTwoEight"), ("fixed-512", "FiveTwelve")):
        for op, ok in (("count5", "Count"), ("budget1024", "Budget")):
            vals = [e2["datasets"][d]["means"][f"{arm}|{op}"]["em"] for d in e2["datasets"]]
            add(f"EtwoEm{ak}{ok}", f"{sum(vals) / len(vals):.3f}", f"{P['E2']}: mean over datasets of means['{arm}|{op}'].em")
    for arm, key in (("fixed-512", "FiveTwelve"), ("fixed-128", "OneTwoEight")):
        for f, fk in (("f1", "Fone"), ("coverage", "Cov")):
            add(f"EtwoSquad{key}Budget{fk}", f"{e2['datasets']['squad2']['means'][arm + '|budget1024'][f]:.2f}",
                f"{P['E2']}: datasets.squad2.means['{arm}|budget1024'].{f}")
    for h, key in (("H4", "HFour"), ("H4b", "HFourB"), ("H5", "HFive"), ("H5b", "HFiveB")):
        r = e3[h]
        add(f"{key}Est", pct(r["estimate"]), f"{P['E3']}: {h}.estimate")
        add(f"{key}Lo", pct(r["ci95"][0]), f"{P['E3']}: {h}.ci95[0]")
        add(f"{key}Hi", pct(r["ci95"][1]), f"{P['E3']}: {h}.ci95[1]")
        add(f"{key}Verdict", r["verdict"], f"{P['E3']}: {h}.verdict")
    for h, key in (("H4", "HFour"), ("H4b", "HFourB"), ("H5b", "HFiveB")):
        add(f"{key}Count", pct(e3[h]["count_share"]), f"{P['E3']}: {h}.count_share")
        add(f"{key}Budget", pct(e3[h]["budget_share"]), f"{P['E3']}: {h}.budget_share")
    sw = e3["semantic_wins"]["S5-128"]
    for prot in ("count", "budget"):
        add(f"SfiveOneTwoEight{prot.capitalize()}Sem", pct(sw[prot]["support_A"]), f"{P['E3']}: semantic_wins.S5-128.{prot}.support_A")
        add(f"SfiveOneTwoEight{prot.capitalize()}Fix", pct(sw[prot]["support_B"]), f"{P['E3']}: semantic_wins.S5-128.{prot}.support_B")
        add(f"SfiveUniverses{prot.capitalize()}", str(sw[prot]["n_universes"]), f"{P['E3']}: semantic_wins.S5-128.{prot}.n_universes")
        add(f"PoneDenseUniverses{prot.capitalize()}", str(e3["H5"][prot]["n_universes"]), f"{P['E3']}: H5.{prot}.n_universes")
        add(f"HFive{prot.capitalize()}FiveTwelve", pct(e3["H5"][prot]["support_B"]), f"{P['E3']}: H5.{prot}.support_B")
    e3p = j("E3P")
    add("HFiveBPilotCount", pct(e3p["H5b"]["count_share"]), f"{P['E3P']}: H5b.count_share (exploratory pilot)")
    add("HFiveBPilotBudget", pct(e3p["H5b"]["budget_share"]), f"{P['E3P']}: H5b.budget_share (exploratory pilot)")
    add("HFivePilotCountFiveTwelve", pct(e3p["H5"]["count"]["support_B"]), f"{P['E3P']}: H5.count.support_B (exploratory pilot)")
    for k, key in (("f_bm25_only", "HFourBmOnly"), ("f_dense_only", "HFourDenseOnly")):
        r = e3["H4_sensitivity"][k]
        add(f"{key}Est", pct(r["estimate"]), f"{P['E3']}: H4_sensitivity.{k}.estimate")
    for c, key in (("semantic-bp", "SemBp"), ("semantic-cl", "SemCl")):
        lens = [e3["mean_chunk_words"][d][c] for d in e3["mean_chunk_words"]]
        add(f"{key}Min", f"{min(lens):.0f}", f"{P['E3']}: min over datasets of mean_chunk_words.*.{c}")
        add(f"{key}Max", f"{max(lens):.0f}", f"{P['E3']}: max over datasets of mean_chunk_words.*.{c}")
    nc = [s["noncontiguous_share"] for d in e3["datasets"] for s in
          json.loads((ROOT / P["E3RUN"] / d / "manifest.json").read_text())["chunk_stats"] if s["chunking"] == "semantic-cl"]
    add("SemClNoncontigMin", pct(min(nc)), f"{P['E3RUN']}/*/manifest.json: min chunk_stats[semantic-cl].noncontiguous_share")
    for tag, srcs in (("Doc", (("E1D", ("H1", "H1b")), ("E3D", ("H4", "H4b", "H5", "H5b")))),
                      ("Planned", (("E1P", ("H1", "H1b")), ("E3PL", ("H4", "H4b", "H5", "H5b"))))):
        for key_src, hs in srcs:
            res = j(key_src)
            for h in hs:
                k = {"H1": "HOne", "H1b": "HOneB", "H4": "HFour", "H4b": "HFourB", "H5": "HFive", "H5b": "HFiveB"}[h]
                add(f"{k}{tag}Est", pct(res[h]["estimate"]), f"{P[key_src]}: {h}.estimate")
                add(f"{k}{tag}Lo", pct(res[h]["ci95"][0]), f"{P[key_src]}: {h}.ci95[0]")
                add(f"{k}{tag}Hi", pct(res[h]["ci95"][1]), f"{P[key_src]}: {h}.ci95[1]")
                add(f"{k}{tag}Verdict", res[h]["verdict"], f"{P[key_src]}: {h}.verdict")
    e1d, e3d = j("E1D"), j("E3D")
    e1p, e3p_ = j("E1P"), j("E3PL")
    shift = max(abs(q[h]["estimate"] - pl[h]["estimate"]) for q, pl, hs in ((e1, e1p, ("H1", "H1b")),
                (e3, e3p_, ("H4", "H4b", "H5", "H5b"))) for h in hs)
    add("InferenceShiftMax", pct(shift), "max |reported - planned estimate| over the six share hypotheses")
    add("HTwoDocFraction", pct(e1d["H2"]["dataset_largest_fraction"]), f"{P['E1D']}: H2.dataset_largest_fraction")
    add("HTwoDocVerdict", e1d["H2"]["verdict"], f"{P['E1D']}: H2.verdict")
    offs = [abs(r[h]["replicate_mean_minus_estimate"]) for r, hs in ((e1, ("H1", "H1b")), (e3, ("H4", "H4b", "H5", "H5b")),
            (e1d, ("H1", "H1b")), (e3d, ("H4", "H4b", "H5", "H5b"))) for h in hs]
    add("ReplicateOffsetMax", pct(max(offs)), "max |replicate_mean_minus_estimate| over the hypotheses of E1, E3, E1D, E3D")
    add("HFiveReplicateOffset", pct(e3["H5"]["replicate_mean_minus_estimate"]), f"{P['E3']}: H5.replicate_mean_minus_estimate")
    add("PoneDenseOneUniverse", pct(1 / e3["H5"]["count"]["n_universes"]), f"1 / {P['E3']}: H5.count.n_universes")
    sv = j("SV")["posthoc"]
    add("SensBHPooledEst", pct(sv["BH_family_P1_consistent"]["pooled_over_datasets"]),
        f"{P['SV']}: posthoc.BH_family_P1_consistent.pooled_over_datasets (POST-HOC)")
    add("EtwoPoneFoneMdeStrat", f"{sv['tier2_mde']['P1/f1']['equal_weight_estimand']:.3f}", f"{P['SV']}: posthoc.tier2_mde['P1/f1'] (POST-HOC)")
    bm = sv["H1_by_metric_consistent"]
    for metric, key in (("hit_strict", "Strict"), ("hit_lenient", "Lenient"), ("coverage", "Coverage")):
        add(f"HOne{key}Decline", pct(bm["by_metric"][metric]["decline_512"]),
            f"{P['SV']}: posthoc.H1_by_metric_consistent.by_metric.{metric}.decline_512 (POST-HOC)")
    qs = bm["by_dataset_metric"]["qasper/hit_strict"]
    add("QasperStrictBudgetFiveTwelve", pct(qs["budget_512"]), f"{P['SV']}: posthoc.H1_by_metric_consistent qasper/hit_strict budget_512 (POST-HOC)")
    add("QasperStrictBudgetOneTwoEight", pct(qs["budget_128"]), f"{P['SV']}: posthoc.H1_by_metric_consistent qasper/hit_strict budget_128 (POST-HOC)")
    gc = json.loads((ROOT / P["GC"]).read_text())
    for d, dk in (("cuad", "Cuad"), ("qasper", "Qasper")):
        for c, ck in (("fixed-256", "Fixed"), ("sentence-256", "Sentence"), ("paragraph-256", "Paragraph")):
            add(f"Contain{ck}{dk}", pct(gc["contained_share"][f"{d}/{c}"]), f"{P['GC']}: contained_share.{d}/{c} (POST-HOC)")
    add("GoldMedianQasper", f"{gc['median_shortest_gold_words']['qasper']:g}", f"{P['GC']}: median_shortest_gold_words.qasper (POST-HOC)")
    st = gc["s3_256_by_fixed_containment"]
    q = st["qasper"]["budget"]
    add("QasperSplitShare", pct(q["split"]["n"] / (q["split"]["n"] + q["contained"]["n"])),
        f"{P['GC']}: s3_256_by_fixed_containment.qasper.budget split.n / all (POST-HOC)")
    add("QasperSplitDelta", f"{q['split']['mean_delta']:.3f}", f"{P['GC']}: ...qasper.budget.split.mean_delta (POST-HOC)")
    add("QasperContainedDelta", f"{q['contained']['mean_delta']:.3f}", f"{P['GC']}: ...qasper.budget.contained.mean_delta (POST-HOC)")
    add("SquadSplitN", str(st["squad2"]["budget"]["split"]["n"]), f"{P['GC']}: ...squad2.budget.split.n (POST-HOC)")
    add("SquadContainedDelta", f"{st['squad2']['budget']['contained']['mean_delta']:.3f}",
        f"{P['GC']}: ...squad2.budget.contained.mean_delta (POST-HOC)")
    ub = j("UB")
    cells = sorted(ub["cells"], key=lambda c: c["chunking"])
    add("UnderfillCells", str(len(cells)), f"{P['UB']}: number of cells")
    add("UnderfillWordsA", f"{cells[0]['words']:,}", f"{P['UB']}: cells[{cells[0]['chunking']}].words")
    add("UnderfillWordsB", f"{cells[1]['words']:,}", f"{P['UB']}: cells[{cells[1]['chunking']}].words")
    shifts = [abs(f["upper_bound"] - f["stored"]) for f in ub["runs"]["confirmatory-kaggle-gpu"]["changed_fields"]
              if re.fullmatch(r"H(4|4b|5|5b)\.(estimate|ci95\[\d\])", f["field"])]
    add("UnderfillMaxShift", pct(max(shifts, default=0.0)), f"{P['UB']}: max |upper bound - stored| over H4-H5b estimates and CI bounds (POST-HOC)")
    pr = j("PR")["sensitivity"]
    add("PilotMaxDiff", f"{100 * max(v['max_abs_difference_current_vs_stored'] for v in pr.values()):.2f}",
        f"{P['PR']}: max sensitivity.*.max_abs_difference_current_vs_stored")
    add("PilotBounds", str(sum(int(a != b) for v in pr.values() for a, b in zip(v["stored_ci95"], v["current_ci95"]))),
        f"{P['PR']}: number of differing bounds")
    e2s = j("E2S")
    for d, dk in (("cuad", "Cuad"), ("qasper", "Qasper")):
        add(f"EtwoTruncQueries{dk}", str(e2s["excluded_queries"][d]), f"{P['E2S']}: excluded_queries.{d} (POST-HOC)")
    for variant, vk in (("untruncated", "Untrunc"), ("document_resampling", "Doc")):
        r = e2s["pooled"][variant]["P1/em"]
        add(f"EtwoPoneEm{vk}", s3(r["did"]), f"{P['E2S']}: pooled.{variant}['P1/em'].did (POST-HOC)")
        add(f"EtwoPoneEm{vk}Lo", s3(r["lo"]), f"{P['E2S']}: pooled.{variant}['P1/em'].lo (POST-HOC)")
        add(f"EtwoPoneEm{vk}Hi", s3(r["hi"]), f"{P['E2S']}: pooled.{variant}['P1/em'].hi (POST-HOC)")
    for d, dk in (("squad2", "Squad"), ("covidqa", "Covid")):
        add(f"EtwoPoneEm{dk}", s3(e2s["by_dataset"]["P1/em"][d]), f"{P['E2S']}: by_dataset['P1/em'].{d} (POST-HOC)")
    for key, d in (("PosthocEquivElements", "PH1"), ("PosthocEquivElementsB", "PH3")):
        rep = json.loads((ROOT / P[d] / "selection_equivalence.json").read_text())
        tot = sum(v["elements_scores"] + v["elements_words"] for ds, cs in rep.items() if not ds.startswith("_")
                  for ch, v in cs.items() if not ch.startswith("_"))
        add(key, f"{tot:,}", f"{P[d]}/selection_equivalence.json: sum of compared elements (POST-HOC)")
    fl = json.loads((ROOT / P["PH1"] / "summary.json").read_text())["universe_verdict_changes_vs_stored"]["char"]
    add("PosthocCharFlips", f"{fl['changed']:,}", f"{P['PH1']}/summary.json: universe_verdict_changes_vs_stored.char.changed (POST-HOC)")
    add("PosthocUniverses", f"{fl['total']:,}", f"{P['PH1']}/summary.json: ...char.total (POST-HOC)")
    return t


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    tex = (ROOT / "manuscript/main.tex").read_text()
    nums = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{((?:[^{}]|\{[^{}]*\})*)\}", (ROOT / "manuscript/numbers.tex").read_text()))
    used = sorted(set(re.findall(r"\\([A-Z][A-Za-z]+)", tex)) & set(nums))
    t = table()
    bad = 0
    lines = ["# Macro trace (generated by tools/trace_claims.py)", "",
             "Each result macro used in `manuscript/main.tex`, its value in `numbers.tex`, the source, and an independent "
             "recomputation (not using `make_numbers.py`).", "", "| Macro | numbers.tex | Recomputed | Source |", "|---|---|---|---|"]
    for k in used:
        v, src = t.get(k, ("UNTRACED", "—"))
        ok = v == nums[k]
        bad += not ok
        lines.append(f"| `\\{k}` | {nums[k]} | {v}{'' if ok else ' **MISMATCH**'} | {src} |")
    lines.append(f"\n{len(used)} macros used; {len(used) - bad} recomputed identically; {bad} mismatched or untraced.")
    if args.out:
        Path(args.out).write_text("\n".join(lines) + "\n")
    print(lines[-1])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
