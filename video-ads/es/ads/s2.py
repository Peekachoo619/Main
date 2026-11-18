NAME = "DualLiving_S2_WhyChooseUs"
M = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music"
MUSIC, MUSIC_IN, MUSIC_DB = f"{M}/369.mp3", 11.99, -15
CLIPS = {"e05": (870, 926, 302)}
LINES = [
    dict(clip="e05", win=(2.80, 5.50),   text="I'll tell you why to choose us as your builder.", shots=[(0, "A")], max_gap=0.7),
    dict(clip="e05", win=(8.85, 11.95),  text="Many builders have offered a dual-key product but can't deliver.", shots=[(0, "B")], max_gap=0.6),
    dict(clip="e05", win=(14.30, 16.15), text="Our design and research team", shots=[(0, "A")], max_gap=0.5),
    dict(clip="e05", win=(20.60, 23.70), text="has over 35 years of combined industry experience,", shots=[(0, "B")], max_gap=0.5),
    dict(clip="e05", win=(26.60, 29.80), text="achieving on delivering you the dual-key home", shots=[(0, "I:facade_2"), (0.5, "I:kitchen_6")], max_gap=0.7),
    dict(clip="e05", win=(31.05, 31.90), text="across Victoria.", shots=[(0, "A")], gap=0.25),
]
POPS = [
    ("head", 0, 0.0, 2.2, "WHY CHOOSE US", "AS YOUR BUILDER?"),
    ("num", 3, 2, "35 YEARS", "COMBINED EXPERIENCE", 2.2),
]
END = ("DUAL-KEY HOMES.", "DELIVERED.")
