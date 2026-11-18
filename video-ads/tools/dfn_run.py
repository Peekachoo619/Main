import os
# DeepFilterNet3 with a capped attenuation (keeps the voice natural). usage: dfn_run.py in.wav out.wav [atten_db]
import sys, types
bk = types.ModuleType("torchaudio.backend"); cm = types.ModuleType("torchaudio.backend.common")
class AudioMetaData: pass
cm.AudioMetaData = AudioMetaData; bk.common = cm
sys.modules["torchaudio.backend"] = bk; sys.modules["torchaudio.backend.common"] = cm
import numpy as np, soundfile as sf, torch
from df.enhance import enhance, init_df
model, st, _ = init_df(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dfnmodel") + "/DeepFilterNet3", log_level="ERROR")
a, sr = sf.read(sys.argv[1], dtype="float32")
assert sr == st.sr(), sr
out = enhance(model, st, torch.from_numpy(a)[None], atten_lim_db=float(sys.argv[3]) if len(sys.argv) > 3 else 12)
sf.write(sys.argv[2], out.squeeze(0).numpy(), sr, subtype="PCM_16")
