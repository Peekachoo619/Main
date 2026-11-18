NAME = "DualLiving_S8_DualLivingIsForYou"
M = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music"
MUSIC, MUSIC_IN, MUSIC_DB = f"{M}/726.mp3", 14.31, -15
CLIPS = {"e22": (793, 1369, 382)}
LINES = [
    dict(clip="e22", win=(8.12, 9.82),    text="Investors, home buyers,", shots=[(0, "A")], max_gap=0.7),
    dict(clip="e22", win=(10.36, 13.22),  text="you want positive cash flow, the dual living is for you.", shots=[(0, "B"), (0.55, "I:facade_3")]),
    dict(clip="e22", win=(13.64, 16.38),  text="Two rental incomes from $950 to $1,100 weekly", shots=[(0, "A"), (0.45, "B")], max_gap=0.5, gap=0.25),
]
POPS = [
    ("head", 0, 0.0, 1.6, "INVESTORS.", "HOME BUYERS."),
    ("num", 2, 4, "$950–$1,100", "RENT PER WEEK", 1.8),
]
END = ("THE DUAL LIVING", "IS FOR YOU.")
