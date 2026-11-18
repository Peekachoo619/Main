NAME = "DualLiving_S6_ScaredToInvest"
M = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music"
MUSIC, MUSIC_IN, MUSIC_DB = f"{M}/318.mp3", 20.18, -15
CLIPS = {"e21": (842, 1571, 418)}
LINES = [
    dict(clip="e21", win=(0.0, 2.80),   text="Investors, home buyers, you want positive cash flow,", shots=[(0, "A")], max_gap=0.6),
    dict(clip="e21", win=(3.10, 3.90),  text="you're scared to invest?", shots=[(0, "B")]),
    dict(clip="e21", win=(4.22, 5.18),  text="This is the investment.", shots=[(0, "I:facade_4")], gap=0.15),
    dict(clip="e21", win=(6.00, 11.05), text="$750,000 will bring you two rental incomes for $950 to $1,100 weekly.", shots=[(0, "B"), (0.5, "A")], max_gap=0.6),
    dict(clip="e21", win=(12.80, 15.05), text="Click the link below and let's have a chat.", shots=[(0, "B")], gap=0.2),
]
POPS = [
    ("head", 1, 0.0, 0.9, "SCARED", "TO INVEST?"),
    ("num", 3, 0, "$750,000", "INVESTMENT", 1.7),
    ("num", 3, 8, "$950–$1,100", "RENT PER WEEK", 2.2),
]
END = ("TWO INCOMES.", "ONE ROOF.")
