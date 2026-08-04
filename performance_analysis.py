import os
import json
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
import numpy as np
from scipy import stats


def analyze_by_interaction(log_path: str):
    path = log_path

    interactions = []
    PAM_wins = []
    control_wins = []
    ties = []
    nones = []
    PAM_wins_by_turn = {}

    PAM = 0
    control = 0
    tie = 0
    none = 0
    interaction_index = 0

    for f in os.scandir(path):
        if f.is_file():
            with open(f.path, "r") as file:
                data = json.load(file)

                for interaction in data:
                    pick = interaction["LLM Judge Pick"].lower()
                    if pick == "pam":
                        turn = interaction["Turn"]
                        PAM_wins_by_turn[turn] = PAM_wins_by_turn.get(turn, 0) + 1
                        PAM += 1
                    elif pick == "control":
                        control += 1
                    elif pick == "tie":
                        tie += 1
                    else:
                        none += 1
                    interaction_index += 1

                    PAM_wins.append(PAM)
                    control_wins.append(control)
                    ties.append(tie)
                    nones.append(none)
                    interactions.append(interaction_index)

    plt.figure(figsize=(10, 6))

    plt.plot(interactions, PAM_wins, label="PAM Tutor Wins")
    plt.plot(interactions, control_wins, label="Control Tutor Wins")
    plt.plot(interactions, ties, label="Ties")
    plt.plot(interactions, nones, label="Wrong format/Other Errors")

    plt.title("LLM Judge Picks Over Interactions")
    plt.xlabel("Interactions")
    plt.ylabel("Cumulative Picks")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    total = len(interactions)
    PAM_percentage = (PAM / total) * 100
    control_percentage = (control / total) * 100
    tie_percentage = (tie / total) * 100
    none_percentage = (none / total) * 100

    print("Analysis by each interaction per conversation")
    print(f"Percent of PAM Wins: {PAM_percentage}%")
    print(f"Percent of Control Wins: {control_percentage}%")
    print(f"Percent of Ties: {tie_percentage}%")
    print(f"Percent of Nones: {none_percentage}%")
    print(f"PAM wins by each turn of the interaction: {PAM_wins_by_turn}")
    print(
        "----------------------------------------------------------------------------------------------------"
    )


def analyze_by_conversation(log_path: str):
    path = log_path

    conversations = []
    PAM_wins = []
    control_wins = []
    ties = []

    PAM = 0
    control = 0
    tie = 0
    conversation_index = 0

    for f in os.scandir(path):
        if f.is_file():
            with open(f.path, "r") as file:
                data = json.load(file)

                PAM_wins_convo = 0
                control_wins_convo = 0

                for interaction in data:
                    pick = interaction["LLM Judge Pick"].lower()
                    if pick == "pam":
                        PAM_wins_convo += 1
                    elif pick == "control":
                        control_wins_convo += 1

                conversation_index += 1

                if PAM_wins_convo > control_wins_convo:
                    PAM += 1
                elif control_wins_convo > PAM_wins_convo:
                    control += 1
                else:
                    tie += 1

                PAM_wins.append(PAM)
                control_wins.append(control)
                ties.append(tie)
                conversations.append(conversation_index)

    plt.figure(figsize=(10, 6))

    plt.plot(conversations, PAM_wins, label="PAM Tutor Wins")
    plt.plot(conversations, control_wins, label="Control Tutor Wins")
    plt.plot(conversations, ties, label="Ties")

    plt.title("Best Tutor by Majority Picks Over the Course of a 10 Turn Conversation")
    plt.xlabel("Conversations")
    plt.ylabel("Majority Wins")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    total = len(conversations)
    PAM_percentage = (PAM / total) * 100
    control_percentage = (control / total) * 100
    tie_percentage = (tie / total) * 100

    print(
        "Analysis by which model won the majority of the interactions in a conversation (one winner per conversation)"
    )
    print(f"Percent of PAM Wins: {PAM_percentage}%")
    print(f"Percent of Control Wins: {control_percentage}%")
    print(f"Percent of Ties: {tie_percentage}%")
    print(
            "----------------------------------------------------------------------------------------------------"
        )


def analyze_by_dimension(log_path: str):
    path = log_path
    dimensions = [
        "pedagogical_accuracy",
        "empathy_calibration",
        "conversational_naturalness",
        "scaffolding_appropriateness",
    ]

    # store one row per interaction: {dim: delta, ...} plus judge pick
    rows = []
    skipped = 0

    for f in os.scandir(path):
        if f.is_file():
            with open(f.path, "r") as file:
                data = json.load(file)
            for interaction in data:
                pam_scores = interaction.get("PAM Scores")
                ctrl_scores = interaction.get("Control Scores")

                if not isinstance(pam_scores, dict) or not isinstance(
                    ctrl_scores, dict
                ):
                    skipped += 1
                    continue

                # also guard against a dict that's missing a dimension key
                if not all(d in pam_scores for d in dimensions) or not all(
                    d in ctrl_scores for d in dimensions
                ):
                    skipped += 1
                    continue

                pick = interaction["LLM Judge Pick"].lower()
                row = {"pick": pick}
                for dim in dimensions:
                    row[dim] = pam_scores[dim] - ctrl_scores[dim]
                rows.append(row)

    print(f"Skipped {skipped} wrongly formatted interactions out of {skipped + len(rows)} total")

    n = len(rows)
    print(f"Total interactions with dimension scores: {n}\n")

    # --- Per-dimension summary: mean delta, % positive, % negative, % tied ---
    print(
        f"{'Dimension':<30} {'Mean Δ':>8} {'PAM>Ctrl':>10} {'Ctrl>PAM':>10} {'Tied':>8}"
    )
    deltas_by_dim = {}
    for dim in dimensions:
        vals = np.array([r[dim] for r in rows])
        deltas_by_dim[dim] = vals
        mean_delta = vals.mean()
        pct_pos = (vals > 0).mean() * 100
        pct_neg = (vals < 0).mean() * 100
        pct_tie = (vals == 0).mean() * 100
        print(
            f"{dim:<30} {mean_delta:>8.3f} {pct_pos:>9.1f}% {pct_neg:>9.1f}% {pct_tie:>7.1f}%"
        )

        # Wilcoxon signed-rank test: is this dimension's delta significantly != 0?
        nonzero = vals[vals != 0]
        if len(nonzero) > 0:
            stat, p = stats.wilcoxon(nonzero)
            sig = "*" if p < 0.05 else ""
            print(f"   -> Wilcoxon signed-rank: p={p:.4f} {sig}")
    print()

    # --- Does the judge's categorical pick track naturalness vs empathy? ---
    # crude check: for PAM-picked turns, what's the mean delta on each dimension?
    pam_rows = [r for r in rows if r["pick"] == "pam"]
    ctrl_rows = [r for r in rows if r["pick"] == "control"]
    print("Mean dimension delta conditional on judge's categorical pick:")
    for label, subset in [
        ("Judge picked PAM", pam_rows),
        ("Judge picked Control", ctrl_rows),
    ]:
        print(f"  {label} (n={len(subset)}):")
        for dim in dimensions:
            vals = [r[dim] for r in subset]
            print(f"    {dim:<30} mean Δ = {np.mean(vals):.3f}")
    print()

    # --- Simple logistic regression: which dimension delta predicts the pick? ---
    # only using non-tie rows
    binary_rows = [r for r in rows if r["pick"] in ("pam", "control")]
    if len(binary_rows) > 10:
        X = np.array([[r[dim] for dim in dimensions] for r in binary_rows])
        y = np.array([1 if r["pick"] == "pam" else 0 for r in binary_rows])
        clf = LogisticRegression().fit(X, y)
        print("Logistic regression coefficients (which dimension predicts judge pick):")
        for dim, coef in zip(dimensions, clf.coef_[0]):
            print(f"  {dim:<30} {coef:+.3f}")
        print(f"  (Pseudo R^2 / train accuracy: {clf.score(X, y):.3f})")
    print(
        "----------------------------------------------------------------------------------------------------"
    )


def sign_test_by_conversation(log_path: str):
    """Conversation-level sign test on majority-vote winner (categorical picks)."""
    path = log_path
    pam_wins, control_wins, ties = 0, 0, 0

    for f in os.scandir(path):
        if f.is_file():
            with open(f.path, "r") as file:
                data = json.load(file)
            pam_convo, control_convo = 0, 0
            for interaction in data:
                pick = interaction["LLM Judge Pick"].lower()
                if pick == "pam":
                    pam_convo += 1
                elif pick == "control":
                    control_convo += 1
            if pam_convo > control_convo:
                pam_wins += 1
            elif control_convo > pam_convo:
                control_wins += 1
            else:
                ties += 1

    n_decisive = pam_wins + control_wins
    if n_decisive > 0:
        result = stats.binomtest(pam_wins, n_decisive, p=0.5)
        print(
            f"Conversation-level sign test: PAM wins {pam_wins}/{n_decisive} decisive conversations"
        )
        print(f"  p-value (two-sided binomial test vs 50/50): {result.pvalue:.4f}")
    print(f"  Ties: {ties}")
    print(
        "----------------------------------------------------------------------------------------------------"
    )


if __name__ == "__main__":
    log_path = "data_logs_with_dimension_scores"
    analyze_by_interaction(log_path)
    analyze_by_conversation(log_path)
    analyze_by_dimension(log_path)
    sign_test_by_conversation(log_path)
