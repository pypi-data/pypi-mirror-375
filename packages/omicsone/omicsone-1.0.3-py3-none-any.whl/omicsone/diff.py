import os
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon, mannwhitneyu, ttest_ind, ttest_rel
from statsmodels.stats.multitest import multipletests
from joblib import Parallel, delayed
from tqdm import tqdm

from numba import njit

@njit(cache=True)
def decide_sig(fdr, log2fc, log2fc_cutoff, fdr_cutoff):
    if log2fc > log2fc_cutoff and fdr < fdr_cutoff:
        return 'S-U'
    elif log2fc < -1 * log2fc_cutoff and fdr < fdr_cutoff:
        return 'S-D'
    elif log2fc > 0 and fdr < fdr_cutoff:
        return 'U'
    elif log2fc < 0 and fdr < fdr_cutoff:
        return 'D'

@njit(cache=True)
def remove_nans(x, y):
    """ 使用 NumPy 布尔索引快速移除 NaN 值 """
    mask = (~np.isnan(x)) & (~np.isnan(y))  # ✅ 创建非 NaN 的布尔掩码
    return x[mask], y[mask]  # ✅ 直接用布尔索引筛选



def compute_row(index, row_values, a, b, method, max_miss_ratio_global, max_miss_ratio_group, min_sample_size):
    """计算单个 `row` 的统计检验"""
    methods = {
        'T-test(Unpaired)': ttest_ind,
        'T-test(Paired)': ttest_rel,
        'Wilcoxon(Unpaired)': mannwhitneyu,
        'Wilcoxon(Paired)': wilcoxon
    }
    
    miss_ratio = sum(pd.isna(row_values[i]) for i in a + b) / len(a + b)
    if miss_ratio > max_miss_ratio_global:
        return None

    x = np.array([row_values[i] for i in a if pd.notna(row_values[i])], dtype=float)
    y = np.array([row_values[i] for i in b if pd.notna(row_values[i])], dtype=float)

    miss_ratio1 = (len(a) - len(x)) / len(a)
    miss_ratio2 = (len(b) - len(y)) / len(b)    

    if miss_ratio1 > max_miss_ratio_group or miss_ratio2 > max_miss_ratio_group:
        return None


    if len(x) < min_sample_size  or len(y) < min_sample_size:
        return None
    
    if method in ['Wilcoxon(Paired)', 'T-test(Paired)']:
        x = np.array([row_values[i] for i in a ], dtype=float)
        y = np.array([row_values[i] for i in b ], dtype=float)

        x, y = remove_nans(x, y)

        if len(x) < min_sample_size  or len(y) < min_sample_size:
            return None

    log2fc_median = np.nanmedian(x) - np.nanmedian(y)
    log2fc_mean = np.nanmean(x) - np.nanmean(y)

    test_stat, p_value = methods[method](x, y)

    return [index, log2fc_median, log2fc_mean, test_stat, p_value]

def compare_two_groups(df, a, b, method, fdr_cutoff=0.01, log2fc_cutoff=1,
                       max_miss_ratio_global=0.5, max_miss_ratio_group=0.5, min_sample_size=4):
    """
    并行计算 `df` 中每一行的统计检验结果。
    """

    # **分块计算**
    BATCH_SIZE = 1000
    rows = list(df.itertuples(index=True, name=None))  # 比 iterrows() 快
    batches = [rows[i:i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]

    # **并行计算**
    results = Parallel(n_jobs=-1, batch_size=20)(
        delayed(compute_row)(index, dict(zip(df.columns,row)), a, b, method, max_miss_ratio_global, max_miss_ratio_group, min_sample_size)
        for batch in tqdm(batches, desc="Processing Batches") 
        for index, *row in batch
    )

    # **移除 None 结果**
    results = [r for r in results if r is not None]

    # **转换为 DataFrame**
    new_df = pd.DataFrame(results, columns=['Feature', 'Log2FC(median)', 'Log2FC(mean)', f'{method}(Stats)', f'{method}(P-value)'])

    # **FDR 校正**
    new_df['FDR'] = multipletests(new_df[f'{method}(P-value)'], method='fdr_bh')[1]
    new_df['-Log10(FDR)'] = -np.log10(new_df['FDR'])

    # **显著性判断**
    new_df['Significance'] = [
        decide_sig(row['FDR'], row['Log2FC(median)'], log2fc_cutoff, fdr_cutoff)
        for _, row in new_df.iterrows()
    ]

    return new_df.set_index('Feature')
