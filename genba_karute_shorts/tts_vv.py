# VOICEVOX CORE でカットごとのナレーションWAVを生成する(オフライン)
from pathlib import Path

VV = Path(__file__).parent / "vv"
SPEED, PITCH, INTONATION = 0.88, -0.02, 0.85  # ゆっくり・抑揚控えめ


def synthesize(texts, style_id, out_paths):
    from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
    ort = Onnxruntime.load_once(filename=str(next((VV / "onnxruntime").glob("lib/libvoicevox_onnxruntime.so.*"))))
    syn = Synthesizer(ort, OpenJtalk(str(VV / "dict")))
    for vvm in sorted((VV / "models").glob("*.vvm")):
        with VoiceModelFile.open(str(vvm)) as m:
            syn.load_voice_model(m)
    for text, out in zip(texts, out_paths):
        q = syn.create_audio_query(text, style_id)
        q.speed_scale, q.pitch_scale, q.intonation_scale = SPEED, PITCH, INTONATION
        q.pre_phoneme_length, q.post_phoneme_length = 0.1, 0.1
        Path(out).write_bytes(syn.synthesis(q, style_id))
        print("tts:", q.kana)
