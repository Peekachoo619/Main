NAME = "DualLiving_S4_TwoIncomesOneProperty"
M = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music"
MUSIC, MUSIC_IN, MUSIC_DB = f"{M}/400.mp3", 14.50, -14
CLIPS = {"e10": (758, 1006, 301), "e09": (657, 947, 298)}
LINES = [
    dict(clip="e10", win=(4.30, 8.55),   text="Investors, imagine purchasing a $750,000 property.", shots=[(0, "A"), (0.4, "B")], max_gap=0.8),
    dict(clip="e10", win=(24.80, 29.85), text="Both dwellings have their own living space, their own bedrooms, their own bathroom and laundry.", shots=[(0, "A"), (0.3, "I:kitchen_7"), (0.68, "I:bath_9")], max_gap=0.5),
    dict(clip="e09", win=(22.75, 24.50), text="Separated for privacy.", shots=[(0, "I:floorplan")], gap=0.15),
    dict(clip="e10", win=(36.50, 41.05), text="With a dual living, you can have two rental incomes for the one property.", shots=[(0, "B"), (0.45, "A")], max_gap=0.5),
    dict(clip="e10", win=(59.50, 61.70), text="Click the link below to get more information.", shots=[(0, "B")], gap=0.2),
]
POPS = [
    ("num", 0, 4, "$750,000", "PROPERTY", 1.8),
    ("label", 3, 0.45, 2.2, "2 RENTAL INCOMES · 1 PROPERTY", 300),
]
END = ("TWO INCOMES.", "ONE PROPERTY.")
