from pathlib import Path
from mipi_datamanager import JinjaRepo
from mipi_datamanager.connection import Odbc

#########################
# UNIVERSAL CONFIGURATION
#########################

CLARITY = Odbc(dsn = 'Clarity')
CDW = Odbc(dsn = 'CDW')
BIDW01 = Odbc(dsn = 'BIDW01')
ALL_JUNGLES_ROOT = Path(__file__).parent.parent

CON_DICT = {
    "odbc.Clarity()":CLARITY, #backwards compatability
    "odbc.CDW()":CDW, #backwards compatability
    "odbc.BIDW01()":BIDW01, #backwards compatability
    "CLARITY":CLARITY,
    "CDW":CDW,
    "BIDW01":BIDW01,
}

class CooperJinjaRepo(JinjaRepo):
    def __init__(self, root_dir):
        super().__init__(str(ALL_JUNGLES_ROOT / root_dir), conn_dict=CON_DICT)

########################
# DECLARE COOPER JUNGLES
########################

COOPER_EPIC_JUNGLE = CooperJinjaRepo("cooper_epic_jungle")
EPT = CooperJinjaRepo("ept")
