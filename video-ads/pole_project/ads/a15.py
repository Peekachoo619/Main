NAME = "MelbTempPoles_Ad15_CableThiefSkit_v2"
CLIP = "n12"; FACE = (864, 900, 200); CAM = (864, 900, 200)
MUSIC, MUSIC_IN, MUSIC_DB = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/281.mp3", 0.0, -8
MAX_GAP = 1.2
LINES = [
    dict(win=(0.30, 6.25), text="Where'd you get all that cable from? This cable? I stole it from a job site that had no site cameras.", shots=[(0, "W")]),
    dict(win=(7.85, 11.60), text="What an idiot. Why wouldn't you have any site cameras on your site?", shots=[(0, "Z")], gap=0.1),
]
POPS = [
    ("head", 0, 0.0, 1.8, "WHERE'D YOU GET", "ALL THAT CABLE?"),
    ("stamp", 0, 0.62, 2.0, "NO SITE CAMERAS"),
    ("pill", 1, 0.0, 1.3, "WHAT AN IDIOT.", "Pill", 260),
]
END = ("DON'T BE", "THAT SITE.")
