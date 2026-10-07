# VOICEVOX CORE でカットごとのナレーションWAVを生成する(オフライン)
# voice は storyboard.json の "voice"(VOICEVOXエディタのプリセット値と同じ項目)
from pathlib import Path

VV = Path(__file__).parent / "vv"


def synthesize(texts, voice, out_paths):
    from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
    ort = Onnxruntime.load_once(filename=str(next((VV / "onnxruntime").glob("lib/libvoicevox_onnxruntime.so.*"))))
    syn = Synthesizer(ort, OpenJtalk(str(VV / "dict")))
    for vvm in sorted((VV / "models").glob("*.vvm")):
        with VoiceModelFile.open(str(vvm)) as m:
            syn.load_voice_model(m)
    style_id = voice["style_id"]
    for text, out in zip(texts, out_paths):
        q = syn.create_audio_query(text, style_id)
        q.speed_scale = voice["speed"]
        q.pitch_scale = voice["pitch"]
        q.intonation_scale = voice["intonation"]
        q.volume_scale = voice["volume"]
        q.pre_phoneme_length = voice["pre_silence"]
        q.post_phoneme_length = voice["post_silence"]
        Path(out).write_bytes(syn.synthesis(q, style_id))
        print("tts:", q.kana)
