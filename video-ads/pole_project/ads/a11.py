NAME = "MelbTempPoles_Ad11_OneCameraOneGate_v2"
CLIP = "n03"; FACE = (668, 1432, 153); CAM = (1037, 1458, 240)
MUSIC, MUSIC_IN, MUSIC_DB = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/726.mp3", 14.31, -15
LINES = [
    dict(win=(3.15, 4.65),   text="One camera pointed at a gate.", shots=[(0, "B")]),
    dict(win=(7.05, 8.55),   text="What about the other side of the build?", shots=[(0, "A")]),
    dict(win=(11.45, 13.85), text="Builders often only focus on the entrance", shots=[(0, "B")]),
    dict(win=(16.05, 18.25), text="and forget about the access down the side.", shots=[(0, "F:street")]),
    dict(win=(22.25, 25.15), text="Our dual fixed camera gives you two sets of viewing", shots=[(0, "A"), (0.4, "C")]),
    dict(win=(28.35, 31.25), text="from one setup, so you can plan the entire coverage.", shots=[(0, "A")]),
    dict(win=(33.65, 36.30), text="Click the link below and get in touch today.", shots=[(0, "B")]),
]
POPS = [
    ("head", 0, 0.0, 1.4, "ONE CAMERA.", "ONE GATE."),
    ("stamp", 1, 0.3, 1.2, "THE OTHER SIDE?"),
    ("pill", 3, 0.2, 1.8, "SIDE ACCESS: UNWATCHED", "PillR", 300),
    ("pip", 5, 0.05, 2.4, "estate"),
    ("pill", 6, 0.0, 2.2, "TAP THE LINK BELOW", "Pill", 1180),
]
END = ("BOTH SIDES.", "ONE POLE.")
