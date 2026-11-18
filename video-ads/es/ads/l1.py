NAME = "DualLiving_L1_TheDualKeyExplained"
M = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music"
MUSIC, MUSIC_IN, MUSIC_DB = f"{M}/281.mp3", 0.0, -9
CLIPS = {"e13": (872, 1592, 410)}
LINES = [
    dict(clip="e13", win=(4.75, 7.52),     text="Let me explain to you why dual-key is such an interesting opportunity.", shots=[(0, "A")]),
    dict(clip="e13", win=(29.90, 35.70),   text="You're getting two completely independent dwellings under the one roof on the one block.", shots=[(0, "B"), (0.45, "I:facade_3")], max_gap=1.2),
    dict(clip="e13", win=(52.15, 56.90),   text="Dwelling one offers three bedrooms, two bathrooms, a spacious living and a laundry.", shots=[(0, "A"), (0.3, "I:floorplan")], max_gap=0.6),
    dict(clip="e13", win=(57.42, 59.98),   text="Dwelling two offers one large living area,", shots=[(0, "I:kitchen_7")]),
    dict(clip="e13", win=(62.88, 65.88),   text="two bedroom, its own kitchenette and laundry.", shots=[(0, "I:kitchen_5"), (0.5, "I:bath_8")], max_gap=0.7, gap=0.15),
    dict(clip="e13", win=(70.28, 73.92),   text="The estimated combined rental income for two dwellings", shots=[(0, "A")]),
    dict(clip="e13", win=(74.40, 77.00),   text="is from $950 to $1,100 weekly.", shots=[(0, "B")], gap=0.15),
    dict(clip="e13", win=(81.72, 84.15),   text="Here's what separates us from the rest.", shots=[(0, "A")]),
    dict(clip="e13", win=(172.05, 176.70), text="We have successfully handed over more than 100 dual-key homes across Victoria", shots=[(0, "B"), (0.55, "I:facade_2")]),
    dict(clip="e13", win=(178.25, 179.65), text="in the past six months.", shots=[(0, "A")], max_gap=0.5),
    dict(clip="e13", win=(201.36, 203.18), text="Backed by a design and research team", shots=[(0, "B")]),
    dict(clip="e13", win=(238.75, 242.15), text="with over 35 years combined industry experience.", shots=[(0, "A")]),
    dict(clip="e13", win=(257.50, 259.42), text="We offer a fixed complete price,", shots=[(0, "B")]),
    dict(clip="e13", win=(274.22, 275.58), text="complete turnkey packages", shots=[(0, "I:kitchen_6")]),
    dict(clip="e13", win=(282.95, 286.18), text="and 16 independent quality assurance inspections.", shots=[(0, "A")], max_gap=0.25),
    dict(clip="e13", win=(316.65, 319.95), text="We're achieving a 22 week build program.", shots=[(0, "B")]),
    dict(clip="e13", win=(343.12, 347.65), text="We're not just selling you a house, we're helping you explore the correct investment.", shots=[(0, "A"), (0.5, "B")], max_gap=0.6),
    dict(clip="e13", win=(351.15, 353.40), text="Click the link below and let's have a conversation.", shots=[(0, "A")], gap=0.2),
]
POPS = [
    ("head", 0, 0.0, 2.6, "THE DUAL-KEY HOME", "EXPLAINED"),
    ("label", 2, 0.35, 2.6, "DWELLING 1 · 3 BED · 2 BATH", 250),
    ("label", 3, 0.0, 2.0, "DWELLING 2 · 2 BED", 250),
    ("num", 6, 2, "$950–$1,100", "COMBINED RENT PER WEEK", 2.2),
    ("num", 8, 7, "100+", "DUAL-KEY HOMES DELIVERED", 2.2),
    ("num", 11, 2, "35 YEARS", "COMBINED EXPERIENCE", 2.0),
    ("label", 12, 0.3, 1.3, "FIXED PRICE", 300),
    ("num", 14, 1, "16", "INDEPENDENT INSPECTIONS", 2.0),
    ("num", 15, 3, "22 WEEKS", "BUILD PROGRAM", 1.8),
]
END = ("TWO INCOMES.", "ONE ROOF.")
