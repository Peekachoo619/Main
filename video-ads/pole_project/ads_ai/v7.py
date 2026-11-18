NAME = "MelbTempPoles_AI07_DualFixed_WarehouseNight_v2"
AI_CLIP, AI_RANGE = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/gen/a7.mp4", (0.0, 4.2)
FOOTAGE = [("/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/real/estate_install.mp4", 1.0, 3.0)]
FOOTAGE_TAG = "REAL FOOTAGE · OUR CAMERAS"
STILL, STILL_DUR, STILL_FY = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/gen/s7.png", 3.0, 0.25
MUSIC, MUSIC_IN = "/tmp/claude-0/-home-user-Main/8ec53773-df37-5593-aac2-f95c84bcc5ec/scratchpad/music/318.mp3", 20.18
END = ("YOUR YARD.", "WATCHED 24/7.")

def graphics(g):
    T, P, U, s = g["text"], g["POP"], g["UP"], g["starts"]
    T(0.25, 2.05, "Head", 540, 1010, "WAREHOUSE. YARD.", P + r"\blur3")
    T(0.50, 2.05, "HeadY", 540, 1120, "DEPOT.", P)
    T(2.15, s[1], "Head", 540, 1010, "WATCHED", P + r"\blur3")
    T(2.40, s[1], "HeadY", 540, 1120, "ALL NIGHT.", P)
    T(s[1] + 0.3, s[2], "Sub", 540, 1500, "TWO ANGLES. NO BLIND SPOTS.", U)
    T(s[2] + 0.15, s[3], "Head", 540, 1000, "SOLAR + 4G", P + r"\blur3")
    T(s[2] + 0.45, s[3], "HeadY", 540, 1110, "NO POWER NEEDED.", P)
