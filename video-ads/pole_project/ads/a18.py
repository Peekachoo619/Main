NAME = "MelbTempPoles_Ad18_TwoFixedViews_v2"
CLIP = "n19"; FACE = (531, 1060, 224); CAM = (1137, 1037, 300)
MUSIC, MUSIC_IN, MUSIC_DB = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/726.mp3", 14.31, -15
LINES = [
    dict(win=(1.95, 3.50),   text="This is our dual fixed camera here.", shots=[(0, "A")]),
    dict(win=(4.95, 6.70),   text="Here's what builders ask for.", shots=[(0, "B")]),
    dict(win=(17.45, 19.45), text="Instead of just concentrating on one direction,", shots=[(0, "A")]),
    dict(win=(22.55, 25.05), text="you set up two fixed views that you care about.", shots=[(0, "C")]),
    dict(win=(28.55, 30.25), text="That might be a gateway and a driveway,", shots=[(0, "F:estate")]),
    dict(win=(33.05, 35.20), text="or material zones and access points.", shots=[(0, "F:site")]),
    dict(win=(38.35, 40.15), text="You get a more useful view of your job,", shots=[(0, "B")]),
    dict(win=(42.85, 45.25), text="without guessing what's happening outside of the frame.", shots=[(0, "A")]),
    dict(win=(45.75, 47.85), text="Click the link below and get in touch today.", shots=[(0, "B")]),
]
POPS = [
    ("prod", 0, 0.2, 1.4, "DUAL FIXED"),
    ("head", 1, 0.0, 1.4, "WHAT BUILDERS", "ASK FOR"),
    ("checks", 4, 0.0, 3.6, ["GATEWAY", "DRIVEWAY", "MATERIALS", "ACCESS POINTS"]),
    ("stamp", 7, 0.3, 1.5, "NO GUESSING"),
    ("pill", 8, 0.0, 2.0, "TAP THE LINK BELOW", "Pill", 1180),
]
END = ("TWO VIEWS.", "NO GUESSING.")
