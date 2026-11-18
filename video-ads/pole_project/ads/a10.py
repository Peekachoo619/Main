NAME = "MelbTempPoles_Ad10_WhosWatching_v2"
CLIP = "n02"; FACE = (694, 1454, 156); CAM = (1053, 1458, 240)
MUSIC, MUSIC_IN, MUSIC_DB = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/369.mp3", 11.99, -15
LINES = [
    dict(win=(5.25, 8.65),   text="Your builders leave at four. Who's watching the site after hours?", shots=[(0, "B"), (0.45, "A")]),
    dict(win=(15.15, 20.25), text="An empty construction site can be an easy target for people trying to steal tools or dump rubbish.", shots=[(0, "A"), (0.5, "F:site")]),
    dict(win=(32.15, 34.55), text="That is why we supply site security cameras", shots=[(0, "B")]),
    dict(win=(36.25, 37.60), text="like this dual fixed setup", shots=[(0, "C")]),
    dict(win=(39.65, 42.30), text="with two fixed views of different areas.", shots=[(0, "A")]),
    dict(win=(46.85, 50.35), text="You can check what's happening at your site, live, 24/7.", shots=[(0, "B"), (0.35, "F:estate")]),
    dict(win=(50.55, 52.55), text="Click the link below and get in touch today.", shots=[(0, "A")]),
]
POPS = [
    ("head", 0, 0.0, 1.6, "BUILDERS LEAVE AT 4", "WHO'S WATCHING?"),
    ("pill", 1, 0.0, 1.5, "EASY TARGET", "PillR", 260),
    ("prod", 3, 0.0, 1.4, "DUAL FIXED"),
    ("checks", 4, 0.1, 2.0, ["VIEW 1: THE GATE", "VIEW 2: THE SIDE"]),
    ("pill", 6, 0.0, 2.0, "TAP THE LINK BELOW", "Pill", 1180),
]
END = ("TWO VIEWS.", "ONE POLE.")
