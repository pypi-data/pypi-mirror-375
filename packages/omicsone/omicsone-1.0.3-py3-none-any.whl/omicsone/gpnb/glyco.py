import re
import sys
import os
import pandas as pd
from scipy.stats import spearmanr


def get_glyco_steps():
    current_file_path = os.path.abspath(__file__)
    wd = os.path.dirname(current_file_path)

    glymodel = os.path.join(wd, "glycoenz.xlsx")

    glymodel_steps_df = pd.ExcelFile(glymodel).parse('steps')
    return glymodel_steps_df


def get_glycoenzymes():
    glymodel_steps_df = get_glyco_steps()

    glyco_enz_list = glymodel_steps_df['GENE'].tolist()

    return glyco_enz_list


def decide_glycan_type(g):
    m = re.finditer("([A-Z])([\d]+)", g)
    y = [(i.group(1), int(i.group(2))) for i in m]
    d = dict(y)
    glycan_type = "Other"
    if d["N"] == 2 and d["H"] >= 5 and d["F"] == 0 and d["S"] == 0 and d["G"] == 0:
        glycan_type = "HM"
    elif d["N"] >= 2 and d["H"] >= 3 and d["F"] > 0 and d["S"] == 0:
        glycan_type = "only_F"
    elif d["N"] >= 2 and d["H"] >= 3 and d["S"] > 0 and d["F"] == 0:
        glycan_type = "only_S"
    elif d["N"] >= 2 and d["H"] >= 3 and d["S"] > 0 and d["F"] > 0:
        glycan_type = "F+S"
    return glycan_type

def hello():
    print("Hello from glyco.py!")

# def decide_glycan_type(glycan_string):
#     # Parse glycan composition from string
#     composition = dict((match.group(1), int(match.group(2))) for match in re.finditer(r"([A-Z])(\d+)", glycan_string))

#     # Extract relevant monosaccharides with default 0
#     N = composition.get("N", 0)
#     H = composition.get("H", 0)
#     F = composition.get("F", 0)
#     S = composition.get("S", 0)
#     G = composition.get("G", 0)

#     # Determine glycan type
#     if N == 2 and H >= 5 and F == 0 and S == 0 and G == 0:
#         return "HM"
#     elif N >= 2 and H >= 3 and F > 0 and S == 0 and G == 0:
#         if N >=4 and H >= 5 and F > 0 and S == 0 and G == 0:
#             return "Complex_F"
#         elif N == 3 and H >= 5 and F > 0 and S == 0 and G == 0:
#             return "Hybrid_F"
#         else:
#             return "F"
#     elif N >= 2 and H >= 3 and S > 0 and F == 0 and G == 0:
#         if N >=4 and H >= 5 and S > 0 and F == 0 and G == 0:
#             return "Complex_S"
#         elif N == 3 and H >= 6 and S > 0 and F == 0 and G == 0:
#             return "Hybrid_S"
#         else:
#             return "S"
#     elif N >= 2 and H >= 3 and S > 0 and F > 0 and G == 0:
#         if N >=4 and H >= 5 and S > 0 and F > 0 and G == 0:
#             return "Complex_F+S"
#         elif N == 3 and H >= 6 and S > 0 and F > 0 and G == 0:
#             return "Hybrid_F+S"
#         else:
#             return "F+S"
#     else:
#         if N >=4 and H >=4 and F == 0 and S == 0 and G == 0:
#             return "Complex_Undecorated"
#         elif N == 3 and H >= 5 and F == 0 and S == 0 and G == 0:
#             return "Hybrid_Undecorated"
#         elif N == 2 and H == 3 and F == 0 and S == 0 and G == 0:
#             return "Complete_Core"
#         elif N == 2 and H == 4 and F == 0 and S == 0 and G == 0:
#             return "M4"
#         elif N == 2 and H == 2 and F == 0 and S == 0 and G == 0:
#             return "Incomplete_Core"
#         elif N == 2 and H == 1 and F == 0 and S == 0 and G == 0:
#             return "Incomplete_Core"
#         elif N == 2 and H == 0 and F == 0 and S == 0 and G == 0:
#             return "Incomplete_Core"
#         elif N == 1 and H == 0 and F == 0 and S == 0 and G == 0:
#             return "Incomplete_Core"
#         return "Other"

def parse_glycan_composition(glycan_string):
    return {match.group(1): int(match.group(2)) for match in re.finditer(r"([A-Z])(\d+)", glycan_string)}


def classify_f_only(N, H, F, S, G):
    if N >= 4 and H >= 4:
        return "Complex_F"
    elif N == 3 and H >= 4:
        return "Hybrid_F"
    else:
        return "F"


def classify_s_only(N, H, F, S, G):
    if N >= 4 and H >= 5:
        return "Complex_S"
    elif N == 3 and H >= 6:
        return "Hybrid_S"
    else:
        return "S"


def classify_fs(N, H, F, S, G):
    if N >= 4 and H >= 4:
        return "Complex_F+S"
    elif N == 3 and H >= 6:
        return "Hybrid_F+S"
    else:
        return "F+S"


def classify_other(N, H, F, S, G):
    if N >= 4 and H >= 4:
        return "Complex_Undecorated"
    elif N == 3 and H >= 5:
        return "Hybrid_Undecorated"
    elif N == 2 and H == 3:
        return "Complete_Core"
    elif N == 2 and H == 4:
        return "M4"
    elif (N == 2 and H in [0, 1, 2]) or (N == 1 and H == 0):
        return "Incomplete_Core"
    return "Other"


def get_glycan_type(glycan_string):
    comp = parse_glycan_composition(glycan_string)
    N = comp.get("N", 0)
    H = comp.get("H", 0)
    F = comp.get("F", 0)
    S = comp.get("S", 0)
    G = comp.get("G", 0)

    if N == 2 and H >= 5 and F == 0 and S == 0 and G == 0:
        return "HM"
    elif N >= 2 and H >= 3 and F > 0 and S == 0 and G == 0:
        return classify_f_only(N, H, F, S, G)
    elif N >= 2 and H >= 3 and S > 0 and F == 0 and G == 0:
        return classify_s_only(N, H, F, S, G)
    elif N >= 2 and H >= 3 and S > 0 and F > 0 and G == 0:
        return classify_fs(N, H, F, S, G)
    else:
        return classify_other(N, H, F, S, G)
    
    

def is_high_mannose(N,H,F,S):
    # widely used proxy: N==2 (core GlcNAc only), 5<=H<=9, S==0
    return (N == 2) and (5 <= H <= 12) and (S == 0) and (F == 0)

# ---- Feature helpers ----
def antenna_tier(N):
    if N <= 3:
        return "Low"
    elif N <= 5:
        return "Mid"
    else:
        return "High"
    
def category5(glycan):
    pattern = re.compile(r"N(\d+)H(\d+)F(\d+)S(\d+)G(\d+)")
    m = pattern.fullmatch(glycan)
    N,H,F,S,G = map(int, m.groups())
    if is_high_mannose(N,H,F,S):
        return "A. High-mannose"
    ant = antenna_tier(N)
    if ant == "Low":
        return "B. Low-antenna (≤3)"
    if ant == "Mid" and S <= 1:
        return "C. Mid (4–5), low-sialyl"
    if ant == "Mid" and S >= 2:
        return "D. Mid (4–5), sialylated"
    # High antenna
    return "E. High (≥6)"

