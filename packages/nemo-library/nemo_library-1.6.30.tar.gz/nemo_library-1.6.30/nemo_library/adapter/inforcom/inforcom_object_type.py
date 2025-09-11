from nemo_library.adapter.utils.structures import ETLBaseObjectType


class InforComObjectType(ETLBaseObjectType):
    RELAB = ("RELAB", "0001", [], True)
    RELAC = ("RELAC", "0002", [], False)
    RELACD = ("RELACD", "0003", [], False)
    RELACK = ("RELACK", "0004", [], False)
    RELACP = ("RELACP", "0005", [], False)
    RELACX = ("RELACX", "0006", [], False)
    RELADRESSE = ("RELADRESSE", "0007", [], False)
    RELANSCH=("RELANSCH", "0008", [], True)
    RELFA = ("RELFA", "0009", [], True)
    RELFB = ("RELFB", "0010", [], True)
    RELFI = ("RELFI", "0011", [], True)
    RELFIRMA = ("RELFIRMA", "0012", [], False)
    RELFS = ("RELFS", "0013", [], False)
    RELGB = ("RELGB", "0014", [], False)
    RELKOMM = ("RELKOMM", "0015", [], True)
    RELPERSON = ("RELPERSON", "0016", [], False)
    RELWMSMDATADEFLOCATION = ("RELWMSMDATADEFLOCATION", "0017", [], False)
    RELZTGK = ("RELZTGK", "0018", [], False)
    RELZTLT = ("RELZTLT", "0019", [], False)
    RELZTNUM = ("RELZTNUM", "0020", [], False)