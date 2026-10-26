"""Generate numbers.tex: the paper's result numbers as LaTeX macros, read from the logged result files.

Usage: python -I manuscript/make_numbers.py [--e1 results.json] [--e2 results.json] [--e3 results.json]
                                           [--e3-run RUN_DIR] [--out numbers.tex] [...]
Defaults are the repository's analysed results and manuscript/numbers.tex. The reported results are the analyses with
the consistent verdict procedure at the query unit; the document-unit analyses and the planned computation supply the
`...Doc...` and `...Planned...` macros. Design constants (dataset names, grid sizes, seeds, thresholds) are written
literally in the manuscript; result values come from these macros.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E1A = ROOT / "experiments/E1_retrieval_multiverse/analysis"
E3A = ROOT / "experiments/E3_semantic_dense/analysis"
E1 = E1A / "confirmatory-20261018-consistent-query/results.json"
E1DOC = E1A / "confirmatory-20261018-consistent-document/results.json"
E1PLAN = E1A / "confirmatory-20261018/results.json"
E2 = ROOT / "experiments/E2_generation/analysis/qwen3-4b-kaggle-gpu/results.json"
E2SENS = ROOT / "experiments/E2_generation/analysis/posthoc-sensitivity/results.json"
E3 = E3A / "confirmatory-kaggle-gpu-consistent-query/results.json"
E3DOC = E3A / "confirmatory-kaggle-gpu-consistent-document/results.json"
E3PLAN = E3A / "confirmatory-kaggle-gpu/results.json"
PILOT = E1A / "pilot-exploratory-20261018-reconciliation/results.json"
E3RUN = ROOT / "experiments/E3_semantic_dense/runs/confirmatory-kaggle-gpu"
E3PILOT = ROOT / "experiments/E3_semantic_dense/analysis/exploratory-kaggle-gpu/results.json"
OUT = ROOT / "manuscript" / "numbers.tex"
POSTHOC_E1 = ROOT / "experiments/E1_retrieval_multiverse/analysis/posthoc-charmetric-20261024"
POSTHOC_E3 = ROOT / "experiments/E3_semantic_dense/analysis/posthoc-charmetric-bm25-20261024"
STATVER = ROOT / "experiments/statistical_checks/results.json"
UNDERFILL = ROOT / "experiments/budget_underfill/bound-consistent.json"
CONTAIN = ROOT / "experiments/E1_retrieval_multiverse/analysis/posthoc-gold-containment/results.json"


def equivalence_elements(path: Path) -> tuple[int, int]:
    rep = json.loads(path.read_text())
    n = bad = 0
    for d, cs in rep.items():
        if d.startswith("_"):
            continue
        for c, v in cs.items():
            if not c.startswith("_"):
                n += v["elements_scores"] + v["elements_words"]
                bad += v["mismatch_scores"] + v["mismatch_words"]
    return n, bad


def pp(x: float) -> str:  # proportion -> percentage points / percent, one decimal
    return f"{100 * x:.1f}"


def f3(x: float) -> str:  # typeset minus sign (macros are used in running text)
    return f"{x:+.3f}".replace("-", "\\ensuremath{-}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--e1", type=Path, default=E1)
    ap.add_argument("--e2", type=Path, default=E2)
    ap.add_argument("--e3", type=Path, default=E3)
    ap.add_argument("--e3-run", type=Path, default=E3RUN)
    ap.add_argument("--e3-pilot", type=Path, default=E3PILOT)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--posthoc-e1", type=Path, default=POSTHOC_E1)
    ap.add_argument("--posthoc-e3", type=Path, default=POSTHOC_E3)
    ap.add_argument("--stat-verification", type=Path, default=STATVER)
    ap.add_argument("--underfill-bound", type=Path, default=UNDERFILL)
    ap.add_argument("--gold-containment", type=Path, default=CONTAIN)
    ap.add_argument("--e1-doc", type=Path, default=E1DOC)
    ap.add_argument("--e3-doc", type=Path, default=E3DOC)
    ap.add_argument("--e1-planned", type=Path, default=E1PLAN)
    ap.add_argument("--e3-planned", type=Path, default=E3PLAN)
    ap.add_argument("--e2-sensitivity", type=Path, default=E2SENS)
    ap.add_argument("--pilot-reconciliation", type=Path, default=PILOT)
    args = ap.parse_args(argv)
    m: dict[str, str] = {}
    e1 = json.loads(args.e1.read_text())
    m["EoneNq"] = f"{sum(e1['n_queries'].values()):,}"
    for d, n in e1["n_queries"].items():
        m[f"EoneNq{d.replace('2', 'two').capitalize()}"] = f"{n:,}"
    for h, key in (("H1", "HOne"), ("H1b", "HOneB")):
        r = e1[h]
        m[f"{key}Est"], m[f"{key}Lo"], m[f"{key}Hi"] = pp(r["estimate"]), pp(r["ci95"][0]), pp(r["ci95"][1])
    p1 = e1["verdict_shares"]["P1"]
    m["PoneCountFiveTwelve"], m["PoneCountOneTwoEight"] = pp(p1["count"]["support_B"]), pp(p1["count"]["support_A"])
    m["PoneBudgetFiveTwelve"], m["PoneBudgetOneTwoEight"] = pp(p1["budget"]["support_B"]), pp(p1["budget"]["support_A"])
    m["PoneUniversesCount"], m["PoneUniversesBudget"] = str(p1["count"]["n_universes"]), str(p1["budget"]["n_universes"])
    for cid, key in (("S2-128", "StwoOneTwoEight"), ("S2-256", "StwoTwoFiveSix"), ("S1-128", "SoneOneTwoEight")):
        v = e1["verdict_shares"][cid]  # S2 compares equal-length arms: the built-in control for the mechanism
        for prot in ("count", "budget"):
            m[f"{key}{prot.capitalize()}A"], m[f"{key}{prot.capitalize()}B"] = pp(v[prot]["support_A"]), pp(v[prot]["support_B"])
    m["HTwoDatasetEta"] = f"{e1['H2']['eta2']['dataset']:.2f}"
    m["HTwoRetrieverEta"] = f"{e1['H2']['eta2']['retriever']:.2f}"
    m["HTwoFraction"] = pp(e1["H2"]["dataset_largest_fraction"])
    for h, key in (("H1", "HOne"), ("H1b", "HOneB"), ("H2", "HTwo"), ("H3", "HThree")):
        m[f"{key}Verdict"] = e1[h]["verdict"]
    m["HThreeShare"], m["HThreeMedianN"] = pp(e1["H3"]["share_universes_requiring_over_500"]), f"{e1['H3']['median_required_n']:,.0f}"
    for k, key in (("b_without_squad2", "SensNoSquad"), ("c_default_retriever", "SensDefRet"),
                   ("d_cluster_bootstrap", "SensCluster"), ("e_all_budgets", "SensAllBudgets"), ("a_bh_fdr", "SensBH")):
        r = e1["H1_sensitivity"][k]
        m[f"{key}Est"] = pp(r["estimate"])
        if "ci95" in r:
            m[f"{key}Lo"], m[f"{key}Hi"] = pp(r["ci95"][0]), pp(r["ci95"][1])

    e2 = json.loads(args.e2.read_text())
    for c, key in (("P1", "Pone"), ("S3-256", "Sthree")):
        for meas, mk in (("f1", "Fone"), ("em", "Em"), ("coverage", "Cov")):
            r = e2["pooled"][c][meas]
            m[f"Etwo{key}{mk}"], m[f"Etwo{key}{mk}Lo"], m[f"Etwo{key}{mk}Hi"] = f3(r["did"]), f3(r["lo"]), f3(r["hi"])
            m[f"Etwo{key}{mk}Mde"] = f"{r['mde']:.3f}"

    e3 = json.loads(args.e3.read_text())
    for h, key in (("H4", "HFour"), ("H4b", "HFourB"), ("H5", "HFive"), ("H5b", "HFiveB")):
        r = e3[h]
        m[f"{key}Est"], m[f"{key}Lo"], m[f"{key}Hi"] = pp(r["estimate"]), pp(r["ci95"][0]), pp(r["ci95"][1])
        m[f"{key}Verdict"] = r["verdict"]
    for h, key in (("H4", "HFour"), ("H4b", "HFourB"), ("H5b", "HFiveB")):
        m[f"{key}Count"], m[f"{key}Budget"] = pp(e3[h]["count_share"]), pp(e3[h]["budget_share"])
    sw = e3["semantic_wins"]["S5-128"]
    m["SfiveOneTwoEightCountSem"], m["SfiveOneTwoEightCountFix"] = pp(sw["count"]["support_A"]), pp(sw["count"]["support_B"])
    m["SfiveOneTwoEightBudgetSem"], m["SfiveOneTwoEightBudgetFix"] = pp(sw["budget"]["support_A"]), pp(sw["budget"]["support_B"])
    for k, key in (("f_bm25_only", "HFourBmOnly"), ("f_dense_only", "HFourDenseOnly")):
        r = e3["H4_sensitivity"][k]
        m[f"{key}Est"], m[f"{key}Lo"], m[f"{key}Hi"] = pp(r["estimate"]), pp(r["ci95"][0]), pp(r["ci95"][1])
        m[f"{key}Count"], m[f"{key}Budget"] = pp(r["count_share"]), pp(r["budget_share"])
    m["HFiveCountFiveTwelve"], m["HFiveBudgetFiveTwelve"] = pp(e3["H5"]["count"]["support_B"]), pp(e3["H5"]["budget"]["support_B"])
    e3p = json.loads(args.e3_pilot.read_text())  # exploratory pilot: the observations behind the H5b amendment
    m["HFiveBPilotCount"], m["HFiveBPilotBudget"] = pp(e3p["H5b"]["count_share"]), pp(e3p["H5b"]["budget_share"])
    m["HFivePilotCountFiveTwelve"] = pp(e3p["H5"]["count"]["support_B"])
    for c, key in (("semantic-bp", "SemBp"), ("semantic-cl", "SemCl")):
        lens = [e3["mean_chunk_words"][d][c] for d in e3["mean_chunk_words"]]
        m[f"{key}Min"], m[f"{key}Max"] = f"{min(lens):.0f}", f"{max(lens):.0f}"
    run3 = args.e3_run
    nc = [s["noncontiguous_share"] for d in e3["datasets"]
          for s in json.loads((run3 / d / "manifest.json").read_text())["chunk_stats"] if s["chunking"] == "semantic-cl"]
    m["SemClNoncontigMin"] = pp(min(nc))
    sw5 = e3["semantic_wins"]["S5-128"]  # universes per S5/S6 contrast (both retrievers) and for dense-only P1
    m["SfiveUniversesCount"], m["SfiveUniversesBudget"] = str(sw5["count"]["n_universes"]), str(sw5["budget"]["n_universes"])
    m["PoneDenseUniversesCount"], m["PoneDenseUniversesBudget"] = (str(e3["H5"]["count"]["n_universes"]),
                                                                   str(e3["H5"]["budget"]["n_universes"]))
    for d, key in (("cuad", "Cuad"), ("qasper", "Qasper")):
        g = e2["datasets"][d]["diagnostics"]
        m[f"EtwoTrunc{key}"], m[f"EtwoJobs{key}"] = str(g["finish_reasons"].get("length", 0)), str(g["rows_total"])
    for arm, ak in (("fixed-128", "OneTwoEight"), ("fixed-512", "FiveTwelve")):  # pooled (equal-weight) EM cell means
        for op, ok in (("count5", "Count"), ("budget1024", "Budget")):
            vals = [e2["datasets"][d]["means"][f"{arm}|{op}"]["em"] for d in e2["datasets"]]
            m[f"EtwoEm{ak}{ok}"] = f"{sum(vals) / len(vals):.3f}"
    v = e1["verdict_shares"]["S1-64"]
    m["SoneSixFourBudgetA"], m["SoneSixFourBudgetB"] = pp(v["budget"]["support_A"]), pp(v["budget"]["support_B"])
    m["SoneSixFourCountB"] = pp(v["count"]["support_B"])
    sq = e2["datasets"]["squad2"]["means"]  # exploratory observation (E2 RESULTS.md), not a planned estimate
    for arm, key in (("fixed-512", "FiveTwelve"), ("fixed-128", "OneTwoEight")):
        m[f"EtwoSquad{key}BudgetFone"] = f"{sq[arm + '|budget1024']['f1']:.2f}"
        m[f"EtwoSquad{key}BudgetCov"] = f"{sq[arm + '|budget1024']['coverage']:.2f}"

    # the same hypotheses at the document unit and under the planned computation
    hyp = {"H1": ("HOne", "e1"), "H1b": ("HOneB", "e1"), "H4": ("HFour", "e3"), "H4b": ("HFourB", "e3"),
           "H5": ("HFive", "e3"), "H5b": ("HFiveB", "e3")}
    variants = {"Doc": {"e1": json.loads(args.e1_doc.read_text()), "e3": json.loads(args.e3_doc.read_text())},
                "Planned": {"e1": json.loads(args.e1_planned.read_text()), "e3": json.loads(args.e3_planned.read_text())}}
    for tag, res in variants.items():
        for h, (key, st) in hyp.items():
            r = res[st][h]
            m[f"{key}{tag}Est"], m[f"{key}{tag}Lo"], m[f"{key}{tag}Hi"] = pp(r["estimate"]), pp(r["ci95"][0]), pp(r["ci95"][1])
            m[f"{key}{tag}Verdict"] = r["verdict"]
    m["InferenceShiftMax"] = pp(max(abs(res_q[h]["estimate"] - variants["Planned"][st][h]["estimate"])
                                    for h, (_, st) in hyp.items() for res_q in ((e1 if st == "e1" else e3),)))
    m["HTwoDocFraction"] = pp(variants["Doc"]["e1"]["H2"]["dataset_largest_fraction"])
    m["HTwoDocVerdict"] = variants["Doc"]["e1"]["H2"]["verdict"]
    reps = [abs(r[h]["replicate_mean_minus_estimate"]) for r, hs in ((e1, ("H1", "H1b")), (e3, ("H4", "H4b", "H5", "H5b")),
            (variants["Doc"]["e1"], ("H1", "H1b")), (variants["Doc"]["e3"], ("H4", "H4b", "H5", "H5b"))) for h in hs]
    m["ReplicateOffsetMax"] = pp(max(reps))
    m["HFiveReplicateOffset"] = pp(e3["H5"]["replicate_mean_minus_estimate"])
    m["PoneDenseOneUniverse"] = pp(1 / e3["H5"]["count"]["n_universes"])

    # post-hoc checks (labelled as such in the text)
    ver = json.loads(args.stat_verification.read_text())["posthoc"]
    m["SensBHPooledEst"] = pp(ver["BH_family_P1_consistent"]["pooled_over_datasets"])
    m["EtwoPoneFoneMdeStrat"] = f"{ver['tier2_mde']['P1/f1']['equal_weight_estimand']:.3f}"
    for key, path in (("PosthocEquivElements", args.posthoc_e1), ("PosthocEquivElementsB", args.posthoc_e3)):
        n, bad = equivalence_elements(path / "selection_equivalence.json")
        if bad:
            raise SystemExit(f"{path}: stored scores/word counts not reproduced ({bad} mismatches); post-hoc numbers not usable")
        m[key] = f"{n:,}"
    by_metric = ver["H1_by_metric_consistent"]
    for metric, key in (("hit_strict", "Strict"), ("hit_lenient", "Lenient"), ("coverage", "Coverage")):
        m[f"HOne{key}Decline"] = pp(by_metric["by_metric"][metric]["decline_512"])
    qs = by_metric["by_dataset_metric"]["qasper/hit_strict"]
    m["QasperStrictBudgetFiveTwelve"], m["QasperStrictBudgetOneTwoEight"] = pp(qs["budget_512"]), pp(qs["budget_128"])
    contain = json.loads(args.gold_containment.read_text())
    for d, dk in (("cuad", "Cuad"), ("qasper", "Qasper")):
        for c, ck in (("fixed-256", "Fixed"), ("sentence-256", "Sentence"), ("paragraph-256", "Paragraph")):
            m[f"Contain{ck}{dk}"] = pp(contain["contained_share"][f"{d}/{c}"])
    m["GoldMedianQasper"] = f"{contain['median_shortest_gold_words']['qasper']:g}"
    strat = contain["s3_256_by_fixed_containment"]["qasper"]["budget"]
    m["QasperSplitShare"] = pp(strat["split"]["n"] / (strat["split"]["n"] + strat["contained"]["n"]))
    m["QasperSplitDelta"], m["QasperContainedDelta"] = f"{strat['split']['mean_delta']:.3f}", f"{strat['contained']['mean_delta']:.3f}"
    sq = contain["s3_256_by_fixed_containment"]["squad2"]["budget"]
    m["SquadSplitN"], m["SquadContainedDelta"] = str(sq["split"]["n"]), f"{sq['contained']['mean_delta']:.3f}"
    ub = json.loads(args.underfill_bound.read_text())
    cells = sorted(ub["cells"], key=lambda c: c["chunking"])
    m["UnderfillCells"] = str(len(cells))
    m["UnderfillWordsA"], m["UnderfillWordsB"] = (f"{c['words']:,}" for c in cells)
    run = ub["runs"]["confirmatory-kaggle-gpu"]
    if run["verdict_changes"]:
        raise SystemExit("underfill bound changes a verdict; the manuscript text must be revised")
    hyp_fields = [f for f in run["changed_fields"] if f["field"].split(".")[0] in ("H4", "H4b", "H5", "H5b")
                  and f["field"].split(".")[1].startswith(("estimate", "ci95"))]
    if any(f["field"].endswith(".estimate") for f in hyp_fields):
        raise SystemExit("underfill bound changes a hypothesis estimate; the manuscript text must be revised")
    m["UnderfillMaxShift"] = pp(max([abs(f["upper_bound"] - f["stored"]) for f in hyp_fields], default=0.0))
    flips = json.loads((args.posthoc_e1 / "summary.json").read_text())["universe_verdict_changes_vs_stored"]
    m["PosthocCharFlips"], m["PosthocUniverses"] = f"{flips['char']['changed']:,}", f"{flips['char']['total']:,}"
    pilot = json.loads(args.pilot_reconciliation.read_text())["sensitivity"]
    if not all(v["reproduces_stored"] for v in pilot.values()):
        raise SystemExit("the stored pilot intervals are not reproduced by the earlier settings")
    m["PilotMaxDiff"] = f"{100 * max(v['max_abs_difference_current_vs_stored'] for v in pilot.values()):.2f}"
    m["PilotBounds"] = str(sum(int(a != b) for v in pilot.values() for a, b in zip(v["stored_ci95"], v["current_ci95"])))
    sens = json.loads(args.e2_sensitivity.read_text())
    m["EtwoTruncQueriesCuad"] = str(sens["excluded_queries"]["cuad"])
    m["EtwoTruncQueriesQasper"] = str(sens["excluded_queries"]["qasper"])
    for variant, vk in (("untruncated", "Untrunc"), ("document_resampling", "Doc")):
        r = sens["pooled"][variant]["P1/em"]
        m[f"EtwoPoneEm{vk}"], m[f"EtwoPoneEm{vk}Lo"], m[f"EtwoPoneEm{vk}Hi"] = f3(r["did"]), f3(r["lo"]), f3(r["hi"])
    changed = [k for k in sens["pooled"]["all"] for v in ("untruncated", "document_resampling")
               if sens["pooled"][v][k]["verdict"] != sens["pooled"]["all"][k]["verdict"]]
    if changed:
        raise SystemExit(f"Tier 2 sensitivity changes a reading {changed}; the manuscript text must be revised")
    for d, dk in (("squad2", "Squad"), ("covidqa", "Covid")):
        m[f"EtwoPoneEm{dk}"] = f3(sens["by_dataset"]["P1/em"][d])
    out = ["% Generated by manuscript/make_numbers.py from logged results. Do not edit by hand."]
    out += [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in sorted(m.items())]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(out) + "\n")
    print(f"{len(m)} macros written to {args.out}")


if __name__ == "__main__":
    main()
