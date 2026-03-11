import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# =========================
# CSV読み込み
# =========================

politician = pd.read_csv("output/output_anonymous_full.csv")
chan = pd.read_csv("output/output_real_name_media_full.csv")

politician_scores = pd.to_numeric(politician["Score"], errors="coerce").dropna()
chan_scores = pd.to_numeric(chan["Score"], errors="coerce").dropna()

# =========================
# 基本統計
# =========================

def describe(data, name):
    print(f"\n{name}")
    print("件数:", len(data))
    print("平均:", np.mean(data))
    print("中央値:", np.median(data))
    print("標準偏差:", np.std(data, ddof=1))
    print("最小値:", np.min(data))
    print("最大値:", np.max(data))

print("==== 基本統計 ====")
describe(politician_scores, "政治家")
describe(chan_scores, "4chan")

# =========================
# Welch's t-test
# =========================

t, p = stats.ttest_ind(
    politician_scores,
    chan_scores,
    equal_var=False
)

print("\n==== Welch's t-test ====")
print("t値:", t)
print("p値:", p)

# =========================
# Cohen's d
# =========================

def cohens_d(x, y):
    nx = len(x)
    ny = len(y)

    pooled_std = np.sqrt(
        ((nx - 1) * np.var(x, ddof=1) +
         (ny - 1) * np.var(y, ddof=1)) /
        (nx + ny - 2)
    )

    return (np.mean(x) - np.mean(y)) / pooled_std

d = cohens_d(politician_scores, chan_scores)

print("\n==== 効果量 ====")
print("Cohen's d:", d)

# =========================
# ヒストグラム
# =========================

plt.figure(figsize=(10,5))

plt.hist(
    politician_scores,
    bins=30,
    alpha=0.5,
    label="Politicians"
)

plt.hist(
    chan_scores,
    bins=30,
    alpha=0.5,
    label="4chan"
)

plt.xlabel("Score")
plt.ylabel("Frequency")
plt.title("Score Distribution")
plt.legend()

plt.show()

# =========================
# 箱ひげ図
# =========================

plt.figure(figsize=(6,5))

plt.boxplot(
    [politician_scores, chan_scores],
    tick_labels=["Politicians", "4chan"]
)

plt.ylabel("Score")
plt.title("Score Comparison")

plt.show()

# =========================
# 平均 + CI
# =========================

def mean_ci(data):
    mean = np.mean(data)
    sem = stats.sem(data)
    ci = sem * 1.96
    return mean, ci

mean_p, ci_p = mean_ci(politician_scores)
mean_c, ci_c = mean_ci(chan_scores)

plt.figure(figsize=(6,5))

means = [mean_p, mean_c]
errors = [ci_p, ci_c]

plt.bar(
    ["Politicians", "4chan"],
    means,
    yerr=errors,
    capsize=5
)

plt.ylabel("Score")
plt.title("Mean Score with 95% CI")

plt.show()


# =========================
# CDF
# =========================

def ecdf(data):
    x = np.sort(data)
    y = np.arange(1, len(x)+1) / len(x)
    return x, y

x1, y1 = ecdf(politician_scores)
x2, y2 = ecdf(chan_scores)

plt.figure(figsize=(8,5))

plt.plot(x1, y1, label="Politicians")
plt.plot(x2, y2, label="4chan")

plt.xlabel("Score")
plt.ylabel("Cumulative Probability")
plt.title("CDF Comparison")

plt.legend()

plt.show()

# =========================
# Violin plot
# =========================

plt.figure(figsize=(6,5))

plt.violinplot(
    [politician_scores, chan_scores],
    showmeans=True
)

plt.xticks([1,2], ["Politicians", "4chan"])

plt.ylabel("Score")
plt.title("Distribution Comparison")

plt.show()

# =========================
# KDE 分布
# =========================

plt.figure(figsize=(8,5))

x = np.linspace(1, 4.5, 400)

kde_pol = stats.gaussian_kde(politician_scores)
kde_chan = stats.gaussian_kde(chan_scores)

plt.plot(x, kde_pol(x), label="Politicians")
plt.plot(x, kde_chan(x), label="4chan")

plt.xlabel("Score")
plt.ylabel("Density")
plt.title("KDE Distribution")
plt.legend()

plt.show()

ks_stat, ks_p = stats.ks_2samp(politician_scores, chan_scores)

print("\n==== KS test ====")
print("KS statistic:", ks_stat)
print("p value:", ks_p)