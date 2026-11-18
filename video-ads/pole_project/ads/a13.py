NAME = "MelbTempPoles_Ad13_ThreeSitesAtOnce_v2"
CLIP = "n06"; FACE = (1550, 1638, 180); CAM = (1061, 1424, 150)
MUSIC, MUSIC_IN, MUSIC_DB = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/1068.mp3", 0.0, -10
LINES = [
    dict(win=(2.85, 6.10),   text="Are you managing three to four sites at the same time?", shots=[(0, "B")]),
    dict(win=(9.30, 12.25),  text="You can't physically be at all sites all day,", shots=[(0, "A")]),
    dict(win=(15.05, 18.25), text="and driving around from job to job, wasting your entire day.", shots=[(0, "B")]),
    dict(win=(23.20, 25.45), text="With a connected 360 site camera,", shots=[(0, "C")]),
    dict(win=(28.45, 31.70), text="you can remotely view all sites without even being there.", shots=[(0, "F:estate_pan")]),
    dict(win=(37.25, 41.30), text="It's the most practical way to know what's happening between all three job sites.", shots=[(0, "A"), (0.5, "B")]),
    dict(win=(41.45, 43.28), text="Click the link below and get in touch today.", shots=[(0, "A")]),
]
POPS = [
    ("head", 0, 0.0, 1.8, "3–4 SITES", "AT ONCE?"),
    ("stamp", 1, 0.2, 1.4, "CAN'T BE EVERYWHERE"),
    ("icon", 3, 0.0, 1.6, "phone", "ON YOUR PHONE", 820, 330),
    ("checks", 5, 0.1, 3.4, ["SITE 1  LIVE", "SITE 2  LIVE", "SITE 3  LIVE"]),
    ("pill", 6, 0.0, 1.8, "TAP THE LINK BELOW", "Pill", 1180),
]
END = ("EVERY SITE.", "ONE PHONE.")
