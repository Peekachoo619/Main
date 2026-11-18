NAME = "DualLiving_S7_PositiveCashFlow"
M = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music"
MUSIC, MUSIC_IN, MUSIC_DB = f"{M}/1068.mp3", 0.0, -11
CLIPS = {"e18": (753, 1510, 422)}
LINES = [
    dict(clip="e18", win=(0.0, 1.12),   text="Positive cash flow,", shots=[(0, "B")]),
    dict(clip="e18", win=(1.36, 3.45),  text="a $750,000 investment.", shots=[(0, "A")]),
    dict(clip="e18", win=(4.02, 6.62),  text="You can get two rental incomes for the one property.", shots=[(0, "I:facade_2"), (0.5, "I:floorplan")], gap=0.15),
    dict(clip="e18", win=(7.72, 10.0),  text="Click the link below and let's have a chat.", shots=[(0, "B")], gap=0.2),
]
POPS = [
    ("num", 1, 1, "$750,000", "INVESTMENT", 1.7),
    ("label", 2, 0.1, 2.2, "2 RENTAL INCOMES · 1 PROPERTY", 300),
]
END = ("POSITIVE", "CASH FLOW.")
