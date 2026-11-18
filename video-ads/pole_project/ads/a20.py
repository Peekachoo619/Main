NAME = "MelbTempPoles_Ad20_FirstDelivery_v2"
CLIP = "n17"
FACE = (550, 1087, 251)
CAM = (1027, 1071, 300)
MUSIC, MUSIC_IN, MUSIC_DB = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/623.mp3", 16.2, -15
LINES = [
    dict(win=(6.85, 8.05),   text="Your first delivery is booked.", shots=[(0, "B")]),
    dict(win=(9.85, 11.55),  text="Have you thought about site security yet?", shots=[(0, "A"), (0.55, "C")]),
    dict(win=(13.25, 14.75), text="As material starts arriving,", shots=[(0, "F:site")]),
    dict(win=(17.85, 19.35), text="the value is sitting on your job.", shots=[(0, "A"), (0.45, "B")], gap=0.25),
]
POPS = [
    ("head", 0, 0.0, 1.3, "FIRST DELIVERY", "BOOKED?"),
    ("stamp", 1, 0.55, 0.9, "SITE SECURITY?"),
    ("pill", 3, 0.0, 1.6, "$$$ SITTING ON SITE", "PillR", 260),
    ("prod", 1, 0.0, 1.0, "DUAL FIXED"),
]
END = ("PROTECT IT", "FROM DAY ONE.")
