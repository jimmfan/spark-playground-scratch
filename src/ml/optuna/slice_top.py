import numpy as np

def slice_top_cutoff_metrics_fast(
    eval_df,
    cut_off,
    label_col="label",
    amount_col="amount_base",
    score_col="prob_score",
):
    n_total = len(eval_df)
    k = int(np.ceil(cut_off * n_total))
    if k < 1:
        k = 1

    # get just the top k risky rows without sorting everything
    top_slice = eval_df.nlargest(k, score_col)

    # global totals (only need once per trial, still O(N))
    total_bad = eval_df[label_col].sum()
    total_bad_amt = eval_df.loc[eval_df[label_col] == 1, amount_col].sum()

    # slice totals
    slice_bad = top_slice[label_col].sum()
    slice_bad_amt = top_slice.loc[top_slice[label_col] == 1, amount_col].sum()
    slice_good_amt = top_slice.loc[top_slice[label_col] == 0, amount_col].sum()

    cum_total_pct = k / n_total
    cum_bad_pct = slice_bad / total_bad if total_bad > 0 else 0.0
    cum_bad_amt_pct = (
        slice_bad_amt / total_bad_amt if total_bad_amt > 0 else 0.0
    )

    # score threshold = lowest score inside the top slice
    score_threshold = top_slice[score_col].min()

    return {
        "score_threshold": score_threshold,
        "cum_total_pct": cum_total_pct,
        "cum_bad_pct": cum_bad_pct,
        "cum_bad_amt_pct": cum_bad_amt_pct,
        "cum_goods_amt": slice_good_amt,
        "cum_bads_amt": slice_bad_amt,
    }
