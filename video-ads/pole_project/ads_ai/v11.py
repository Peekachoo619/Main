NAME = "MelbTempPoles_AI11_DualFixed_WarehouseDay_v2"
AI_CLIP, AI_RANGE = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/gen/a11.mp4", (0.0, 4.4)
FOOTAGE = [("/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/real/walker.mp4", 0.5, 3.0)]
FOOTAGE_TAG = "REAL FOOTAGE · OUR CAMERAS"
STILL, STILL_DUR, STILL_FY = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/gen/s11.png", 3.0, 0.2
MUSIC, MUSIC_IN = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/726.mp3", 14.31
GLOW = "&H00612526&"
BAND = r"\alpha&HB0&"
END = ("TWO VIEWS.", "ONE POLE.")

def graphics(g):
    T, P, U, s = g["text"], g["POP"], g["UP"], g["starts"]
    T(0.25, 2.15, "Head", 540, 1010, "ROLLER DOOR.", P)
    T(0.50, 2.15, "HeadY", 540, 1120, "SIDE GATE.", P)
    T(2.25, s[1], "Head", 540, 1010, "BOTH", P)
    T(2.50, s[1], "HeadY", 540, 1120, "COVERED.", P)
    T(s[1] + 0.3, s[2], "Sub", 540, 1500, "LIVE ON YOUR PHONE", U)
    T(s[2] + 0.15, s[3], "Head", 540, 1000, "DUAL FIXED.", P)
    T(s[2] + 0.45, s[3], "HeadY", 540, 1110, "SOLAR + 4G.", P)
