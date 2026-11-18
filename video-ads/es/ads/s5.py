NAME = "DualLiving_S5_WantPositiveCashFlow"
M = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music"
MUSIC, MUSIC_IN, MUSIC_DB = f"{M}/738.mp3", 0.0, -16
CLIPS = {"e14": (676, 1445, 426)}
LINES = [
    dict(clip="e14", win=(0.0, 1.50),  text="Do you want positive cash flow?", shots=[(0, "B")]),
    dict(clip="e14", win=(1.95, 6.50), text="Two rental incomes under one roof for only $750,000.", shots=[(0, "A"), (0.3, "I:facade_4"), (0.62, "B")], max_gap=0.5),
    dict(clip="e14", win=(6.78, 8.80), text="Just a $10K deposit. Click the link below.", shots=[(0, "A")], max_gap=0.5, gap=0.2),
]
POPS = [
    ("head", 0, 0.0, 1.4, "WANT POSITIVE", "CASH FLOW?"),
    ("num", 1, 8, "$750,000", "TWO RENTAL INCOMES", 1.6),
    ("num", 2, 2, "$10K", "DEPOSIT", 1.6),
]
END = ("TWO INCOMES.", "ONE ROOF.")
