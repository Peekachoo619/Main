NAME = "DualLiving_S3_HowWeMakeItHappen"
M = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music"
MUSIC, MUSIC_IN, MUSIC_DB = f"{M}/623.mp3", 16.2, -15
CLIPS = {"e08": (816, 951, 279)}
LINES = [
    dict(clip="e08", win=(6.20, 10.20),  text="Let me tell you how we can make this house happen for you.", shots=[(0, "A")]),
    dict(clip="e08", win=(19.95, 25.20), text="All you need is a $10K deposit and click the link below to secure your dual living.", shots=[(0, "B"), (0.6, "I:facade_3")], max_gap=0.5),
    dict(clip="e08", win=(32.80, 37.95), text="Our team gets you to the site in 6 weeks and finishes your home in 16 weeks.", shots=[(0, "A"), (0.5, "B")], max_gap=0.5),
    dict(clip="e08", win=(38.25, 42.15), text="That's a total of 22 weeks, gives you zero holding costs.", shots=[(0, "A")], max_gap=0.5, gap=0.25),
]
POPS = [
    ("head", 0, 0.0, 2.6, "HOW WE MAKE IT", "HAPPEN FOR YOU"),
    ("num", 1, 5, "$10K", "DEPOSIT", 1.8),
    ("num", 2, 8, "6 WEEKS", "ON SITE", 1.5),
    ("num", 2, 15, "16 WEEKS", "COMPLETED", 1.4),
    ("num", 3, 4, "22 WEEKS", "TOTAL", 1.5),
    ("label", 3, 0.6, 1.5, "ZERO HOLDING COSTS", 300),
]
END = ("$10K DEPOSIT.", "22 WEEKS.")
