import pandas as pd
import numpy as np
from scipy import stats


def load_scores(csv_file):
    """
    CSVを読み込み、Score列をfloatとして取得
    """
    df = pd.read_csv(csv_file)

    # 数値化（INVALIDなどを除去）
    scores = pd.to_numeric(df["Score"], errors="coerce")

    # NaN除去
    scores = scores.dropna()

    return scores


def descriptive_stats(scores, name):
    """
    基本統計量を表示
    """
    print(f"\n{name}")
    print(f"件数: {len(scores)}")
    print(f"平均: {np.mean(scores)}")
    print(f"中央値: {np.median(scores)}")
    print(f"標準偏差: {np.std(scores, ddof=1)}")
    print(f"最小値: {np.min(scores)}")
    print(f"最大値: {np.max(scores)}")


def cohens_d(a, b):
    """
    Cohen's d（効果量）
    """
    n1, n2 = len(a), len(b)

    var1 = np.var(a, ddof=1)
    var2 = np.var(b, ddof=1)

    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    d = (np.mean(a) - np.mean(b)) / pooled_std
    return d


def run_analysis(politician_csv, chan_csv):

    pol_scores = load_scores(politician_csv)
    chan_scores = load_scores(chan_csv)

    print("==== 基本統計 ====")

    descriptive_stats(pol_scores, "政治家")
    descriptive_stats(chan_scores, "4chan")

    print("\n==== Welch's t-test ====")

    t_stat, p_value = stats.ttest_ind(pol_scores, chan_scores, equal_var=False)

    print(f"t値: {t_stat}")
    print(f"p値: {p_value}")

    print("\n==== 効果量 ====")

    d = cohens_d(pol_scores, chan_scores)
    print(f"Cohen's d: {d}")


if __name__ == "__main__":

    politician_csv = "output/output_anonymous_full.csv"
    chan_csv = "output/output_real_name_media_full.csv"

    run_analysis(politician_csv, chan_csv)