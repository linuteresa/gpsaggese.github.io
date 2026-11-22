"""Rebuild the complete original-dialogue review without inference or network."""
from m3_offline_common import ROOT, OUT, chess_env
from collections import Counter
import csv
import hashlib
import json

import chess
from m3_runtime.annotations import NOTES, CLAIMS, UNCERTAIN
from m3_runtime.policies import canonical
from m3_runtime.source import RecordedStore
from m3_runtime.transfer import visible_hash

DEFINITIONS = {
    "false_attack_or_reply_claim": "A specific factual statement in the public reply contradicts legal-move geometry. Not an inference about hidden reasoning.",
    "actual_rook_loss": "The recorded Black reply captures the White rook, causing insufficient-material draw.",
    "clock_win_lost": "This decision changes a clock-aware Syzygy winning position to a non-winning position while the rook remains; operational evidence of inadequate clock planning, not a measured intervention effect.",
    "board_revisit": "The board, turn, castling and en-passant fields recur within a run, with a larger half-move clock. A descriptive inefficiency, not proof of causation or threefold repetition.",
}


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    original = ROOT / "inputs/m1_original/runs/m1_think"
    store = RecordedStore(original)
    manifest_path = ROOT / "experiments/m2_direct_v2/experiment_manifest.json"
    profiles_path = ROOT / "experiments/m2_direct_v2/primary_profiles.csv"
    decisions = json.loads(manifest_path.read_text())["decisions"]
    profiles = {r["decision_id"]: r for r in csv.DictReader(profiles_path.open())}
    assert len(decisions) == len(profiles) == sum(map(len, NOTES.values())) == 48
    evidence = {}

    def record_file(path):
        evidence[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()

    for p in [manifest_path, profiles_path, original / "manifest.sqlite"]:
        record_file(p)
    rows, dialogues, seen = [], [], {}
    for d in decisions:
        sid = d["before_checkpoint"]
        before, after = store.snapshot(sid), store.snapshot(d["after_checkpoint"])
        contexts = [json.loads(store.get_blob("context", s["context_hash"])) for s in (before, after)]
        games = [json.loads(store.get_blob("env", s["env_hash"])) for s in (before, after)]
        for s in (before, after):
            for kind in ("context", "env"):
                p = original / "blobs" / kind / (s[kind+"_hash"] + ".json")
                record_file(p)
        tape = store.read_tape(d["branch_id"])
        record_file(original / "tapes" / (d["branch_id"] + ".jsonl"))
        step = int(d["step"])
        call, = [e for e in tape if e["kind"] == "model_call" and e["step"] == step]
        command, = [e for e in tape if e["kind"] == "command" and e["step"] == step]
        reply = call["response"]["content"]
        assert hashlib.sha256(reply.encode()).hexdigest() == d["original_reply_sha256"]
        assert call["request"]["input_hash"] == visible_hash(contexts[0]["messages"])
        assert command["response"]["returncode"] == 0
        commands = json.loads(d["commands_json"])
        assert len(commands) == 1 and commands[0].startswith("play move ")
        b, a = map(chess_env.board_of, games)
        mv = b.parse_san(commands[0][len("play move "):])
        assert mv in b.legal_moves
        geometry = b.copy(); geometry.push(mv)
        replay, _, code = chess_env.play(games[0], ["play", "move", b.san(mv)])
        assert code == 0 and canonical(replay) == canonical(games[1])
        vb, va = chess_env.white_value(b), chess_env.white_value(a)
        assert vb["win"] == (d["oracle_before_win"] == "True")
        assert va["win"] == (d["oracle_after_win"] == "True")
        key = (int(d["task_id"].split("-")[1][1:]), int(d["trial"]), step)
        tags = []
        claim = CLAIMS.get(key)
        legal = sorted({chess.square_name(m.to_square) for m in geometry.legal_moves})
        rook_captures = sorted(geometry.san(m) for m in geometry.legal_moves
                               if geometry.piece_type_at(m.to_square) == chess.ROOK)
        if claim:
            checks = []
            if "exact_destinations_claimed" in claim:
                checks.append(sorted(claim["exact_destinations_claimed"]) != legal)
            if "illegal_destinations_claimed_legal" in claim:
                checks.append(all(s not in legal for s in claim["illegal_destinations_claimed_legal"]))
            if "all_replies_on_rank_claimed" in claim:
                checks.append(any(int(s[1]) != claim["all_replies_on_rank_claimed"] for s in legal))
            if claim.get("rook_claimed_safe"):
                checks.append(bool(rook_captures))
            assert checks and all(checks), (key, claim, legal)
            tags.append("false_attack_or_reply_claim")
        rook_loss = len(b.pieces(chess.ROOK, chess.WHITE)) > len(a.pieces(chess.ROOK, chess.WHITE))
        if rook_loss:
            assert games[1]["status"] == "insufficient_material"
            tags.append("actual_rook_loss")
        if vb["win"] and not va["win"] and not rook_loss:
            tags.append("clock_win_lost")
        run_seen = seen.setdefault(d["run_id"], {" ".join(b.fen().split()[:4]): 0})
        structural_key = " ".join(a.fen().split()[:4])
        revisit = run_seen.get(structural_key)
        if revisit is not None:
            tags.append("board_revisit")
        run_seen[structural_key] = step
        p = profiles[d["decision_id"]]
        stats = {k:float(p[k]) for k in ("repair_gain", "gain_ci_low", "gain_ci_high", "fisher_p", "holm_p")}
        stats.update({k:int(p[k]) for k in ("keep_wins", "keep_n", "redecide_wins", "redecide_n")})
        causal = "resolved_harmful_reply_effect" if stats["repair_gain"] > 0 and stats["holm_p"] < .05 else "unresolved"
        rows.append({"decision_id":d["decision_id"], "task_id":d["task_id"], "trial":int(d["trial"]),
            "step":step, "run_id":d["run_id"], "branch_id":d["branch_id"], "command":commands[0],
            "before_checkpoint":sid, "after_checkpoint":d["after_checkpoint"],
            "reply_sha256":d["original_reply_sha256"], "reply_text":reply, "tape_call_sha256":call["hash"],
            "before_fen":b.fen(), "after_fen":a.fen(), "oracle_before":vb, "oracle_after":va,
            "observed_labels":tags, "review_note":NOTES[key[:2]][step-1],
            "uncertain_interpretation":key in UNCERTAIN,
            "claim_check": {"extracted_claim":claim, "geometrical_black_destinations":legal,
                "geometrical_rook_captures":rook_captures,
                "actual_black_reply_occurred":len(games[1]["moves_uci"]) == len(games[0]["moves_uci"])+2} if claim else None,
            "revisited_after_step":revisit, "m2_primary_statistics":stats, "causal_status":causal})
    for bid in sorted({d["branch_id"] for d in decisions}):
        snaps = store.snapshots(bid)
        final = json.loads(store.get_blob("context", snaps[-1]["context_hash"]))
        game = json.loads(store.get_blob("env", snaps[-1]["env_hash"]))
        recorded_replies = [e["response"]["content"] for e in store.read_tape(bid) if e["kind"] == "model_call"]
        exported_replies = [m["content"] for m in final["messages"] if m["role"] == "assistant"]
        assert exported_replies == recorded_replies, "Complete dialogue must contain every original reply in order"
        dialogue = {"branch_id":bid, "run_id":snaps[-1]["run_id"], "final_checkpoint":snaps[-1]["id"],
            "messages":[{k:m[k] for k in ("role", "content") if k in m} for m in final["messages"]],
            "final_game":game, "reviewed_decisions":sum(r["branch_id"] == bid for r in rows)}
        dialogues.append(dialogue)
    store.close()
    for relative, digest in evidence.items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest, relative
    counts = Counter(t for r in rows for t in r["observed_labels"])
    summary = {"schema":"caaf.m3.taxonomy/1", "date":"2026-11-20", "api_calls":0, "api_cost_usd":0,
        "decisions":len(rows), "failed_dialogues":len(dialogues), "distinct_tasks":len({r["task_id"] for r in rows}),
        "label_counts":dict(counts), "uncertain_interpretations":sum(r["uncertain_interpretation"] for r in rows),
        "resolved_harmful_reply_effects":sum(r["causal_status"] != "unresolved" for r in rows),
        "illegal_original_commands":0, "original_format_errors":0,
        "false_completion_claims_observed":0, "source_files_unchanged":True,
        "definitions":DEFINITIONS, "review_scope":"All original public replies, tool observations, boards, and full initial/final dialogue histories; not generated M2 continuations or hidden reasoning.",
        "limitations":["Post-hoc single assistant review; independent human review and inter-rater agreement pending.",
            "Seven selected failures from four positions are not representative population estimates.",
            "Labels overlap. Clock pivots and factual mistakes do not establish the causal mechanism of a reply's measured effect.",
            "Causal status uses the frozen 48-decision M2 primary Holm family only. Unresolved is not evidence of no effect.",
            "The keep arm forces the entire original reply, including prose and action; it does not isolate an attack-reasoning mechanism."],
        "source_files_sha256":dict(sorted(evidence.items()))}
    for name, obj in [("taxonomy.json", {"summary":summary,"decisions":rows}), ("dialogues.json",dialogues)]:
        (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    with (OUT/"taxonomy.csv").open("w",newline="") as f:
        keys = ["decision_id","command","observed_labels","uncertain_interpretation","causal_status","repair_gain","holm_p","review_note"]
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader()
        for r in rows:
            w.writerow({**{k:r[k] for k in keys if k in r}, "observed_labels":";".join(r["observed_labels"]),
                "repair_gain":r["m2_primary_statistics"]["repair_gain"],"holm_p":r["m2_primary_statistics"]["holm_p"]})
    text = ["# Original chess failure taxonomy", "", "Reviewed all 7 failed dialogues and 48 decisions across 4 starting positions. API cost: $0.", "",
        "This is a post-hoc assistant review of recorded public text with deterministic chess checks. Independent human annotation has not been performed. The 7 complete histories are in dialogues.json; every decision has checkpoint, reply and tape identities in taxonomy.json.", "",
        "| Observed label | Decisions / 48 | Runs / 7 |", "|---|---:|---:|"]
    for tag, n in counts.items():
        text.append(f"| {tag} | {n} | {len({r['run_id'] for r in rows if tag in r['observed_labels']})} |")
    text += ["", "Labels overlap. Five trajectories end at the fifty-move limit; two end after actual rook captures. Eight replies contain verified false attack or legal-reply claims, including two final-turn hypothetical claims where the clock prevents any Black reply. Four decisions revisit a board while spending clock. Eight planning or textual interpretations remain explicitly uncertain; a decision may have both a confirmed error and a separate uncertain interpretation.", "",
        "All 48 original commands are legal, with no recorded format errors. No false completion claim was observed. These zero counts are bounded to the original seven dialogues.", "",
        "## Observations and measured effects", "",
        "Only three replies have a harmful effect resolved by the frozen M2 primary Holm-corrected family: m4 trial 0 step 3 (Ke2), m4 trial 0 step 5 (Rd1+), and m4 trial 1 step 1 (Rh3). The other 45 are unresolved. Repair gain is P(win | redecide) − P(win | keep entire original reply). Intervals below are the existing pointwise 95% intervals, not simultaneous intervals; discovery status uses Holm p < 0.05 across all 48 primary comparisons.", "",
        "Ke2 makes a false rook-ray claim without immediately losing the theoretical win, yet has a resolved harmful reply effect. Conversely, m8 trial 0's Ra3 demonstrably hangs the rook, but both M2 arms win 0/30: its intervention effect remains unresolved. Do not turn an observed mistake into a statistically demonstrated mechanism. Clock-aware tablebase pivots establish loss of a feasible perfect-play win, not the probability of repair under this agent.", "",
        "The taxonomy does not establish sparse versus diffuse failure clusters, general model weakness, or transferability. It is suitable for selecting follow-up hypotheses, with post-hoc selection disclosed. No new statistical tests or paid continuations were performed.", "", "## Decision-by-decision review", ""]
    for r in rows:
        s=r["m2_primary_statistics"]
        text += [f"### {r['decision_id']} — {r['command']}", "", r["review_note"], "",
            f"Observed labels: {', '.join(r['observed_labels']) or 'none established'}. Uncertain interpretation: {r['uncertain_interpretation']}. M2 status: {r['causal_status']}; G={s['repair_gain']:.3f}, interval [{s['gain_ci_low']:.3f}, {s['gain_ci_high']:.3f}], Holm p={s['holm_p']:.6g}.", ""]
    (OUT/"TAXONOMY.md").write_text("\n".join(text))
    dialogue_text = ["# Complete original failed dialogues", "", "Public messages only; response payload metadata and hidden reasoning are not exported.", ""]
    for d in dialogues:
        dialogue_text += [f"## {d['run_id']} / {d['branch_id']}", ""]
        for m in d["messages"]:
            dialogue_text += [f"### {m['role']}", "", m.get("content", ""), ""]
    (OUT/"DIALOGUES.md").write_text("\n".join(dialogue_text))
    print(json.dumps({k:v for k,v in summary.items() if k not in {"source_files_sha256","definitions","limitations"}}))
    return summary


if __name__ == "__main__":
    build()
