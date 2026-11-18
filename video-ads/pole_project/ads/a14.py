NAME = "MelbTempPoles_Ad14_DualOr360_v2"
CLIP = "n08"; FACE = (896, 1162, 154); CAM = (554, 1153, 200)
MUSIC, MUSIC_IN, MUSIC_DB = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/738.mp3", 0.0, -16
LINES = [
    dict(win=(10.95, 14.85), text="Which site camera actually suits your job, the dual or the 360?", shots=[(0, "B"), (0.6, "A")]),
    dict(win=(58.05, 60.70), text="If you have two areas you want to watch consistently,", shots=[(0, "A")]),
    dict(win=(63.90, 65.85), text="dual fixed can be the smarter option.", shots=[(0, "C")]),
    dict(win=(70.10, 73.50), text="If you want to look around different directions and check more of the site,", shots=[(0, "B"), (0.5, "F:estate_pan")]),
    dict(win=(75.45, 77.00), text="consider the 360.", shots=[(0, "A")]),
    dict(win=(80.70, 82.55), text="The right answer depends on your layout,", shots=[(0, "B")]),
    dict(win=(85.35, 87.55), text="site access and whatever you need to see.", shots=[(0, "A")]),
    dict(win=(88.65, 90.62), text="Click the link below and get in touch today.", shots=[(0, "B")]),
]
POPS = [
    ("head", 0, 0.0, 1.8, "DUAL FIXED", "OR 360?"),
    ("prod", 2, 0.0, 1.6, "DUAL FIXED"),
    ("prod", 4, 0.0, 1.5, "PTZ 360", (1476, 933, 150)),
    ("checks", 5, 0.1, 3.6, ["YOUR LAYOUT", "SITE ACCESS", "WHAT YOU NEED TO SEE"]),
    ("pill", 7, 0.0, 2.0, "TAP THE LINK BELOW", "Pill", 1180),
]
END = ("DUAL OR 360?", "ASK US.")
