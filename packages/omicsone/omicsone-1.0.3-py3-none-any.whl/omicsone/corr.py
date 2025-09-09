from scipy.stats import spearmanr
import pandas as pd
from tqdm import tqdm

def compute_spearman_correlation(protein_data, glyco_data, samples):
    rows = []

    for index,row in tqdm(protein_data.iterrows()):
        gene = index
        protein_values = row[samples]
        for i,r in glyco_data.iterrows():
            glycan_type = i
            g_values = r[samples]
            corr, pval = spearmanr(protein_values, g_values,nan_policy='omit')
            row = {
                "Gene": gene,
                "GlycanType": glycan_type,
                "SpearmanRho": corr,
                "PValue": pval
            }
            rows.append(row)
            
    corr_df = pd.DataFrame(rows)
    return corr_df

def joblib_spearman_correlation(protein_data, glyco_data, common_tumor_samples, chunk_size=100):
    from joblib import Parallel, delayed

    # 假设已经筛选过 `common_tumor_samples`
    protein_filtered = protein_data[common_tumor_samples].to_numpy()  # 转化为 NumPy 数组
    glyco_filtered = glyco_data[common_tumor_samples].to_numpy()

    # 初始化基因数和糖型数
    n_genes, n_glycans = protein_filtered.shape[0], glyco_filtered.shape[0]

    # 函数：处理一个批次的相关性计算
    def compute_batch(batch):
        """
        Compute Spearman correlations for a batch of (gene, glycan) combinations.

        Args:
            batch: List of tuples [(i, j)], where i is the index for rna_data rows
                and j is the index for glycan_data rows.

        Returns:
            List of dictionaries with results:
            [{ "Gene": i, "GlycanType": j, "SpearmanRho": corr, "PValue": pval }, ...]
        """
        results = []
        for i, j in batch:
            corr, pval = spearmanr(protein_filtered[i], glyco_filtered[j], nan_policy='omit')
            results.append({
                "Gene": protein_data.index[i],          # Gene index
                "GlycanType": glyco_data.index[j],          # Glycan index
                "SpearmanRho": corr,                        # Spearman correlation
                "PValue": pval                              # P-value
            })
        return results

    # 创建任务 (所有基因、糖型对)
    tasks = [(i, j) for i in range(n_genes) for j in range(n_glycans)]

    # 批处理：定义批次大小
    # chunk_size = 100  # 批大小
    batches = [tasks[k:k + chunk_size] for k in range(0, len(tasks), chunk_size)]
    
    

    # 通过 joblib 并行处理所有的任务批次
    results = Parallel(n_jobs=-1, backend="loky")(
        delayed(compute_batch)(batch) for batch in tqdm(batches, desc="Spearman correlation")
    )

    # 将结果合并为 DataFrame
    flat_results = [item for batch_result in results for item in batch_result]  # 展开批次结果
    result_df = pd.DataFrame(flat_results)

    # 如果需要更改列名
    result_df.rename(columns={"Gene": "Gene", "GlycanType": "GlycanType"}, inplace=True)

    # 查看最终结果
    return result_df
