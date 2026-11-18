NAME = "MelbTempPoles_AI04_DualFixed_Night_v2"
AI_CLIP, AI_RANGE = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/gen/a4.mp4", (0.0, 4.2)
FOOTAGE = [("/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/real/street.mp4", 8.0, 3.0)]
FOOTAGE_TAG = "REAL FOOTAGE · OUR CAMERAS"
STILL, STILL_DUR, STILL_FY = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/gen/s4.png", 3.0, 0.25
MUSIC, MUSIC_IN = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/318.mp3", 20.18
GLOW = "&H002030C0&"
END = ("THEY WORK NIGHTS.", "SO DO WE.")

def graphics(g):
    T, P, U, s = g["text"], g["POP"], g["UP"], g["starts"]
    T(0.25, 2.05, "Head", 540, 1010, "THIEVES", P + r"\blur3")
    T(0.50, 2.05, "HeadY", 540, 1120, "WORK NIGHTS.", P)
    T(2.15, s[1], "Head", 540, 1010, "SO DO", P + r"\blur3")
    T(2.40, s[1], "HeadY", 540, 1120, "OUR CAMERAS.", P)
    T(s[1] + 0.3, s[2], "Sub", 540, 1500, "LIVE VIEW · EVERY CORNER", U)
    T(s[2] + 0.15, s[3], "Head", 540, 1000, "2 FIXED CAMERAS", P + r"\blur3")
    T(s[2] + 0.45, s[3], "HeadY", 540, 1110, "SOLAR. 24/7.", P)
