NAME = "MelbTempPoles_Ad12_RubbishDumped_v2"
CLIP = "n04"; FACE = (954, 1416, 140); CAM = (717, 1300, 150)
MUSIC, MUSIC_IN, MUSIC_DB = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/623.mp3", 16.2, -15
LINES = [
    dict(win=(11.75, 17.45), text="Imagine arriving to your site 7am on a Monday morning and finding someone else's rubbish on your site.", shots=[(0, "B"), (0.55, "F:site2")]),
    dict(win=(23.95, 29.80), text="Now you're organising the clean-up, paying for someone else's mess and overall wasting more time.", shots=[(0, "A"), (0.5, "B")]),
    dict(win=(36.55, 41.50), text="A 360 camera gives you a way to look around your entire site remotely from your phone.", shots=[(0, "C"), (0.35, "F:street_pan")]),
    dict(win=(45.15, 47.30), text="It won't physically stop someone from entering,", shots=[(0, "A")]),
    dict(win=(49.85, 53.00), text="but it'll definitely give you more visibility when something goes wrong.", shots=[(0, "B")]),
    dict(win=(55.75, 59.85), text="Don't leave your site completely unwatched. Click the link below and get in touch today.", shots=[(0, "A"), (0.5, "B")]),
]
POPS = [
    ("head", 0, 0.0, 1.6, "MONDAY. 7AM.", "SOMEONE'S RUBBISH?"),
    ("checks", 1, 0.05, 3.0, ["THE CLEAN-UP", "THEIR MESS", "WASTED TIME"]),
    ("prod", 2, 0.0, 1.6, "PTZ 360"),
    ("icon", 4, 0.3, 1.6, "eye", "MORE VISIBILITY", 820, 330),
    ("pill", 5, 0.55, 2.0, "TAP THE LINK BELOW", "Pill", 1180),
]
END = ("DON'T LEAVE IT", "UNWATCHED.")
