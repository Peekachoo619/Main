NAME = "DualLiving_S1_VictoriasNewestInvestment"
M = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music"
MUSIC, MUSIC_IN, MUSIC_DB = f"{M}/726.mp3", 14.31, -15
CLIPS = {"e03": (784, 1336, 128)}
F2 = None
LINES = [
    dict(clip="e03", win=(2.05, 3.75),   text="I'm standing in front of Victoria's most popular", shots=[(0, "A")]),
    dict(clip="e03", win=(5.15, 6.50),   text="newest investment product.", shots=[(0, "B")]),
    dict(clip="e03", win=(7.96, 8.82),   text="The dual living.", shots=[(0, "I:facade_4")], gap=0.15),
    dict(clip="e03", win=(10.20, 11.25), text="One block of land.", shots=[(0, "A")]),
    dict(clip="e03", win=(12.65, 13.55), text="Two separate dwellings", shots=[(0, "I:floorplan")]),
    dict(clip="e03", win=(14.40, 15.25), text="under one roof.", shots=[(0, "I:floorplan")], gap=0.15),
    dict(clip="e03", win=(39.25, 41.80), text="This $750,000 investment", shots=[(0, "B")], face=(758, 1253, 132)),
    dict(clip="e03", win=(45.55, 49.30), text="will bring you $950 to $1,100 a week in rental income.", shots=[(0, "A")], max_gap=0.9, face=(758, 1253, 132)),
    dict(clip="e03", win=(51.02, 53.00), text="That is a positive cash flow income.", shots=[(0, "B")], face=(758, 1253, 132)),
    dict(clip="e03", win=(55.55, 57.60), text="Click the link below for more information.", shots=[(0, "A")], gap=0.2, face=(758, 1253, 132)),
]
POPS = [
    ("head", 0, 0.0, 2.6, "VICTORIA'S NEWEST", "INVESTMENT"),
    ("num", 6, 1, "$750,000", "INVESTMENT", 1.6),
    ("num", 7, 3, "$950–$1,100", "A WEEK IN RENT", 3.0),
    ("label", 8, 0.25, 1.6, "POSITIVE CASH FLOW", 300),
]
END = ("TWO INCOMES.", "ONE ROOF.")
