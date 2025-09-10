import io
import types
import os
from typing import Dict

import pytest
import wave
from elevenlabs import ElevenLabs, save
from pydub import AudioSegment

from miya_speechless.transcribe.clients import (
    OpenAITranscriber,
    ElevenLabsTranscriber,
    GoogleTranscriber,
)

DUMMY_WAV = io.BytesIO(b"RIFF....WAVEfmt ")


class _DummyResponse:
    """Mimics the return object of both SDKs."""

    def __init__(self, payload: Dict):
        self._payload = payload

    # OpenAI SDK
    def to_dict(self):  # noqa: D401
        return self._payload

    # ElevenLabs SDK
    def model_dump(self):  # noqa: D401
        return self._payload


def test_openai_transcribe_success(monkeypatch):
    """`transcribe()` should return the payload from `to_dict()` on success."""
    dummy_payload = {"text": "hello from openai"}
    dummy_resp = _DummyResponse(dummy_payload)

    # Stub out client.audio.transcriptions.create
    def _dummy_create(**_):
        return dummy_resp

    dummy_transcriptions = types.SimpleNamespace(create=_dummy_create)
    dummy_audio = types.SimpleNamespace(transcriptions=dummy_transcriptions)
    dummy_client = types.SimpleNamespace(audio=dummy_audio)

    oa = OpenAITranscriber()
    monkeypatch.setattr(oa, "client", dummy_client, raising=False)

    result = oa.transcribe(DUMMY_WAV)
    assert result == dummy_payload


def test_openai_transcribe_failure_returns_empty_dict(monkeypatch):
    """On exception, `transcribe()` should log and return an *empty* dict."""

    def _dummy_create(**_):
        raise RuntimeError("boom")

    dummy_transcriptions = types.SimpleNamespace(create=_dummy_create)
    dummy_audio = types.SimpleNamespace(transcriptions=dummy_transcriptions)
    dummy_client = types.SimpleNamespace(audio=dummy_audio)

    oa = OpenAITranscriber()
    monkeypatch.setattr(oa, "client", dummy_client, raising=False)

    assert oa.transcribe(DUMMY_WAV) == {}


def _elevenlabs_dummy_client(monkeypatch, payload: Dict):
    """Return an `ElevenLabsTranscriber` whose `.convert()` is patched."""
    el = ElevenLabsTranscriber(api_key="test-key")
    dummy_resp = _DummyResponse(payload)

    def _dummy_convert(**_):  # noqa: D401
        return dummy_resp

    dummy_s2t = types.SimpleNamespace(convert=_dummy_convert)
    monkeypatch.setattr(el.client, "speech_to_text", dummy_s2t, raising=False)
    return el


def test_11labs_transcribe_success(monkeypatch):
    payload = {"text": "hello from 11labs"}
    el = _elevenlabs_dummy_client(monkeypatch, payload)
    assert el.transcribe(DUMMY_WAV) == payload


def test_11labs_transcribe_failure_returns_empty_dict(monkeypatch):
    el = ElevenLabsTranscriber(api_key="test-key")

    def _dummy_convert(**_):  # noqa: D401
        raise RuntimeError("boom")

    dummy_s2t = types.SimpleNamespace(convert=_dummy_convert)
    monkeypatch.setattr(el.client, "speech_to_text", dummy_s2t, raising=False)

    assert el.transcribe(DUMMY_WAV) == {}


def _make_silent_wav(path, duration_s: float = 1.0, rate: int = 16_000):
    """Write *duration_s* seconds of 16-kHz 16-bit mono silence to *path*."""
    n_frames = int(duration_s * rate)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(rate)
        wf.writeframes(b"\x00\x00" * n_frames)


@pytest.mark.skipif(
    "OPENAI_API_KEY" not in os.environ,
    reason="Requires OPENAI_API_KEY for live Whisper test",
)
def test_openai_integration(tmp_path):
    """Smoke-test Whisper with 1 s of silence (should return an empty string)."""
    dummy_path = tmp_path / "silence.wav"
    _make_silent_wav(dummy_path)

    oa = OpenAITranscriber()
    result = oa.transcribe(dummy_path)

    assert isinstance(result, dict)


@pytest.mark.skipif(
    "ELEVENLABS_API_KEY" not in os.environ,
    reason="Requires ELEVENLABS_API_KEY for live 11Labs test",
)
def test_11labs_integration(tmp_path):
    """Smoke-test ElevenLabs with 1 s of silence (should return an empty string)."""
    dummy_path = tmp_path / "silence.wav"
    _make_silent_wav(dummy_path)

    el = ElevenLabsTranscriber()
    result = el.transcribe(dummy_path)

    assert isinstance(result, dict)


@pytest.mark.skipif(
    "OPENAI_API_KEY" not in os.environ or "ELEVENLABS_API_KEY" not in os.environ,
    reason="Requires both OPENAI_API_KEY and ELEVENLABS_API_KEY",
)
def test_roundtrip_real_tts_to_stt(tmp_path):
    text = "Hello world this is a test from Slovakia with love"
    audio_path = tmp_path / "hello.mp3"

    client = ElevenLabs()

    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id="EXAVITQu4vr4xnSDxMaL",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    save(audio_stream, str(audio_path))

    openai_text = str(OpenAITranscriber().transcribe(audio_path)).lower()
    el_text = str(ElevenLabsTranscriber().transcribe(audio_path)).lower()

    assert "hello" in openai_text
    assert "hello" in el_text

    assert "slovakia" in openai_text
    assert "slovakia" in el_text


@pytest.mark.integration
def test_google_transcriber_roundtrip_with_real_speech(tmp_path):
    if (
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        or "GOOGLE_CLOUD_PROJECT" not in os.environ
    ):
        pytest.skip(
            "Set GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT for Google STT."
        )

    if "ELEVENLABS_API_KEY" not in os.environ:
        pytest.skip("Set ELEVENLABS_API_KEY for ElevenLabs TTS.")

    text = "Hello world, this is a test from the Miya Speechless pipeline."
    pcm_path = tmp_path / "tts_generated.pcm"

    client = ElevenLabs()
    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id="EXAVITQu4vr4xnSDxMaL",
        model_id="eleven_multilingual_v2",
        output_format="pcm_16000",  # <-- corrected
    )
    save(audio_stream, str(pcm_path))

    # Convert raw PCM to WAV
    pcm_audio = AudioSegment(
        data=pcm_path.read_bytes(),
        sample_width=2,  # 16-bit PCM = 2 bytes
        frame_rate=16000,
        channels=1,
    )
    wav_path = tmp_path / "tts_generated.wav"
    pcm_audio.export(wav_path, format="wav")

    gt = GoogleTranscriber()
    result = gt.transcribe(wav_path)

    assert isinstance(result, dict), f"Expected dict, got {type(result)}: {result}"
    assert "chunks" in result, f"Expected 'chunks' key in result: {result.keys()}"
    assert isinstance(
        result["chunks"], list
    ), f"'chunks' should be list, got {type(result['chunks'])}"

    found_keyword = False
    for chunk in result["chunks"]:
        if "results" in chunk:
            for res in chunk["results"]:
                for alt in res.get("alternatives", []):
                    transcript = alt.get("transcript", "").lower()
                    if "hello" in transcript and "test" in transcript:
                        found_keyword = True
        elif "speechRecognitionResults" in chunk:
            for res in chunk["speechRecognitionResults"]:
                transcript = res.get("transcript", "").lower()
                if "hello" in transcript and "test" in transcript:
                    found_keyword = True

    assert found_keyword, f"Transcription did not contain expected keywords: {result}"
