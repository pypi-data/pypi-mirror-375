import pandas as pd


def get_sample_type(sample_type):
    if sample_type == "Tumor":
        data_type = "T"
    elif sample_type == "NAT":
        data_type = "N"
    elif sample_type == "Normal Duct":
        data_type = "D"
    elif sample_type == "Non-Tumor":
        data_type = "FT"
    elif sample_type in ["Enriched_Normal","Enriched_normal"]:
        data_type = "E"
    elif sample_type in ["Myometrium_Normal","Myometrium_normal"]:
        data_type = "M"
    else:
        data_type = "U" #Unknown
    return data_type


def build_sample_name(row):
    index = row.name
    case_id, data_type, set_no, channel_no = index.split(".")
    simple_sample_type = get_sample_type(row["sample_type"])
    return f"{case_id}.{simple_sample_type}"

def load_meta(meta_path):
    meta_df = pd.read_excel(meta_path, sheet_name="Meta", index_col=0)
    meta_df["sample_name"] = meta_df.apply(build_sample_name, axis=1)
    return meta_df

def load_tumor_samples(meta_path, sheet_name="Tumor_Samples", header=None):
    tumor_df = pd.read_excel(meta_path, sheet_name="Tumor_Samples", header=None)
    tumor_samples = tumor_df.iloc[:,0].tolist()
    tumor_sample_names = [i.split(".")[0] + ".T" for i in tumor_samples]
    return tumor_sample_names

def load_nat_samples(meta_path, sheet_name="NAT_Samples", header=None):
    nat_df = pd.read_excel(meta_path, sheet_name="NAT_Samples", header=None)
    nat_samples = nat_df.iloc[:,0].tolist()
    nat_sample_names = [i.split(".")[0] + ".N" for i in nat_samples]
    return nat_sample_names

def load_nd_samples(meta_path, sheet_name="NormalDuct_Samples", header=None):
    nd_samples = pd.read_excel(meta_path, sheet_name="NormalDuct_Samples", header=None)
    nd_samples = nd_samples.iloc[:,0].tolist()
    nd_sample_names = [i.split(".")[0] + ".D" for i in nd_samples]
    return nd_sample_names
    
def load_data(data_path):
    data = pd.read_csv(data_path, sep="\t",index_col=0, )
    return data

def sorted_common_samples(*sets):
    """
    Find elements that are common across all given sets.

    Args:
        *sets: Variable number of set arguments.

    Returns:
        A set containing elements that are common across all sets.
    """
    if not sets:
        return set()  # If no sets are provided, return an empty set
    
    # Use set intersection to find common elements across all sets
    common_samples = sets[0]  # Start with the first set
    for s in sets[1:]:        # Intersect with the rest of the sets
        common_samples &= s
    
    return sorted(common_samples)

def decide_enzyme_location(row):
    if row["PATH"] == "LLO":
        return "ER"
    elif row["PATH"] == "N-linked":
        if row['PROTEIN'] in ["MOGS","GANAB","PRKCSH","UGGT1","UGGT2","MAN1B1"]:
            return "ER"
        else:
            return "Golgi"
    elif row["PATH"] == "Common":
        return "Golgi"
    else:
        return "Unknown"
    
def load_enzyme_data(enzymes_path):
    enzyme_data = pd.read_excel(enzymes_path, sheet_name="Sheet1")
    enzyme_data['Location'] = enzyme_data.apply(decide_enzyme_location, axis=1)
    return enzyme_data

def sorted_enzymes(enzymes, enzyme_data):
    A = []
    B = set(enzymes)
    for i in enzyme_data['PROTEIN']:
        if i not in A and i in B:
            A.append(i)
    return A
    

    
