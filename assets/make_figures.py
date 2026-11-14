"""Draw the README charts (Netra chart style).

    python assets/make_figures.py

Writes assets/results.png (character error rate of each model, and the full
system's accuracy against latency for each beam width) and assets/word_length.png
(word lengths in the dataset). The numbers are written out below, with where
each comes from; architecture.png and pipeline.png are drawn separately, from
the released model, in the Netra Lab figure style.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "brand"))
from brand_colors import BASELINES, COLOR, OURS, apply, legend_dot, ours_bar  # noqa: E402

# Character error rate (%) of each model alone on the 5,714 held-out words, and its parameters
# (the training notebook's evaluation; Table 1 in the README).
CER = [
    ("AkaraAlpha", 15.07, 78_705),
    ("Transformer", 17.78, 248_337),
    ("Attention\nBiLSTM", 18.26, 96_753),
    ("LSTM", 31.78, 58_417),
    ("GRU", 51.64, 46_385),
    ("RNN", 102.41, 42_609),
]

# The full system with the dictionary check: (label, Top-1 %, Top-K %, latency ms per word) (Table 2).
SYSTEM = [
    ("Greedy", 44.44, 44.44, 21.92),
    ("k=3", 70.06, 78.72, 66.03),
    ("k=5", 73.60, 83.41, 94.15),
    ("k=7", 74.87, 85.60, 122.10),
    ("k=10", 75.85, 87.37, 167.21),
]

# Words of each length in the Khmer Text Transliteration Dataset (Chhunneng, 2023), 28,569 pairs,
# after the package's clean_text: romanized letters and Khmer characters (Unicode code points).
ROMAN = {1: 14, 2: 160, 3: 1049, 4: 2418, 5: 2847, 6: 4080, 7: 4547, 8: 3771, 9: 2752, 10: 2062, 11: 1563,
         12: 1169, 13: 812, 14: 495, 15: 267, 16: 239, 17: 130, 18: 89, 19: 39, 20: 26, 21: 17, 22: 12,
         23: 5, 24: 5, 25: 1}
KHMER = {1: 10, 2: 524, 3: 2322, 4: 3106, 5: 5825, 6: 6308, 7: 3139, 8: 2688, 9: 1703, 10: 1159, 11: 710,
         12: 512, 13: 259, 14: 131, 15: 85, 16: 55, 17: 20, 18: 8, 19: 2, 20: 1, 23: 1, 24: 1}


def params(n: int) -> str:
    return f"{n / 1000:.1f}K"


def results() -> None:
    fig, (cer_ax, sys_ax) = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1.15, 1]})

    # (a) The models alone.
    x = np.arange(len(CER))
    for i, (name, cer, n) in enumerate(CER):
        kw = ours_bar() if i == 0 else {"color": BASELINES[3], "zorder": 3}
        cer_ax.bar(i, cer, 0.62, **kw)
        cer_ax.text(i, cer + 2, f"{cer:.2f}", ha="center", va="bottom", fontsize=9.5, color=COLOR["foreground"])
    cer_ax.set_xticks(x, [f"{name}\n{params(n)}" for name, _, n in CER], fontsize=9.5, linespacing=1.3)
    cer_ax.set_ylim(0, 115)
    cer_ax.set_ylabel("Character error rate (%), lower is better")
    cer_ax.set_title("(a) The model alone", loc="left", fontsize=12)

    # (b) The full system, by beam width.
    lat = [s[3] for s in SYSTEM]
    sys_ax.axvline(100, color=COLOR["muted-2"], linestyle=":", linewidth=1.2, zorder=2)
    sys_ax.text(102, 92, "100 ms", color=COLOR["muted"], fontsize=9.5, va="bottom")
    sys_ax.plot(lat, [s[2] for s in SYSTEM], color=BASELINES[0], marker="o", markersize=6, zorder=3)
    sys_ax.plot(lat, [s[1] for s in SYSTEM], color=OURS, marker="o", markersize=6, zorder=4)
    for label, top1, topk, ms in SYSTEM:
        sys_ax.annotate(label, (ms, topk), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9.5,
                        color=COLOR["foreground"], fontweight="bold" if label == "k=5" else "normal")
    sys_ax.set_xlim(0, 180)
    sys_ax.set_ylim(40, 95)
    sys_ax.set_xlabel("Latency per word (ms)")
    sys_ax.set_ylabel("Word accuracy (%)")
    sys_ax.set_title("(b) With the dictionary check, by beam width", loc="left", fontsize=12)
    sys_ax.legend(handles=[legend_dot(BASELINES[0], "Top-K: the right word is in the list"),
                           legend_dot(OURS, "Top-1: the first suggestion is right")], loc="lower right", fontsize=9.5)
    fig.tight_layout(w_pad=3)
    fig.savefig(HERE / "results.png")
    plt.close(fig)


def word_length() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 3.8), sharey=True)
    lengths = np.arange(1, 26)
    for ax, (title, counts, color) in zip(axes, [("Romanized, letters", ROMAN, BASELINES[0]),
                                                 ("Khmer script, characters", KHMER, BASELINES[1])]):
        ax.bar(lengths, [counts.get(n, 0) for n in lengths], 0.75, color=color, zorder=3)
        ax.set_title(title, loc="left", fontsize=12)
        ax.set_xticks([1, 5, 10, 15, 20, 25])
        ax.set_xlabel("Length")
    axes[0].set_ylabel("Words")
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k" if v else "0"))
    fig.tight_layout(w_pad=3)
    fig.savefig(HERE / "word_length.png")
    plt.close(fig)


if __name__ == "__main__":
    apply()
    plt.rcParams["font.sans-serif"] = ["Kantumruy Pro", "DejaVu Sans"]  # Latin-only labels
    results()
    word_length()
    print("wrote results.png and word_length.png")
