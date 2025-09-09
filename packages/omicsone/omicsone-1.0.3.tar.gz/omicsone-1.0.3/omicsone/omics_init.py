# omicsone_init.py

import os
import re
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from pathlib import Path
from scipy import stats
from statsmodels.stats.multitest import multipletests
from collections import Counter
import matplotlib as mpl

# 设置 matplotlib 字体（兼容 PDF）
mpl.rcParams['pdf.fonttype'] = 42

# 设置 seaborn 风格
sns.set_style('white')

# 添加 omicsone 路径（只添加一次）
# omicsone_path = Path(r"C:\Users\yhu39\Documents\GitHub\omicsone")
# if str(omicsone_path) not in sys.path:
#     sys.path.append(str(omicsone_path))

# 可选：打印提示
print("[omicsone_init] Environment initialized.")

# 可选：导出常用变量
__all__ = [
    "pd", "np", "plt", "sns", "tqdm",
    "stats", "multipletests", "Path", "Counter"
]

def main():
    print("This is the omicsone initialization module.")