import os,re,sys
import pandas as pd
from pathlib import Path

class PDAC:
    def __init__(self,  notebook_dir: Path):
        self.project_name = "PDAC_PandG_271_272"
        
        