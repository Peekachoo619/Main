NAME = "MelbTempPoles_Ad16_FenceIsntEnough_v2"
CLIP = "n16"; FACE = (510, 1064, 240); CAM = (820, 818, 150)
MUSIC, MUSIC_IN, MUSIC_DB = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/318.mp3", 20.18, -15
LINES = [
    dict(win=(5.55, 10.20),  text="A temporary fence is important, but it's not the same thing as knowing what's actually happening on your site.", shots=[(0, "B"), (0.5, "A")]),
    dict(win=(14.05, 18.20), text="People can still jump over the fence and get inside the property when no one's on site.", shots=[(0, "A"), (0.45, "F:site")]),
    dict(win=(22.30, 26.00), text="Adding this 360 site camera gives you a whole other layer of visibility.", shots=[(0, "C"), (0.5, "A")]),
    dict(win=(29.50, 33.00), text="With remote access on your phone, you can check wherever and whenever.", shots=[(0, "B"), (0.4, "F:street_pan")]),
    dict(win=(39.10, 40.80), text="It has an inbuilt alarm system,", shots=[(0, "A")]),
    dict(win=(41.55, 44.75), text="two-way audio and full 360 human tracking.", shots=[(0, "C"), (0.45, "B")]),
    dict(win=(45.00, 46.95), text="Click the link below and get in touch today.", shots=[(0, "A")]),
]
POPS = [
    ("head", 0, 0.0, 1.8, "A FENCE", "ISN'T ENOUGH."),
    ("prod", 2, 0.5, 1.4, "PTZ 360"),
    ("icon", 4, 0.0, 1.5, "bell", "INBUILT ALARM", 820, 330),
    ("checks", 5, 0.0, 3.0, ["INBUILT ALARM", "TWO-WAY AUDIO", "360 HUMAN TRACKING"]),
    ("pill", 6, 0.0, 1.9, "TAP THE LINK BELOW", "Pill", 1180),
]
END = ("MORE THAN", "A FENCE.")
