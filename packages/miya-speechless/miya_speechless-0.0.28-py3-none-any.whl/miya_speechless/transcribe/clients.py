"""Transcription clients for OpenAI and ElevenLabs."""

import os
import logging
import math
import base64
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Union
from pydub import AudioSegment

from openai import OpenAI
from elevenlabs.client import ElevenLabs
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account
from google.protobuf import json_format

from miya_speechless.transcribe.base import BaseTranscriber

logger = logging.getLogger(__name__)


class OpenAITranscriber(BaseTranscriber):
    """Client wrapper around the **OpenAI Whisper** transcription API."""

    def __init__(self, model: str = "whisper-1") -> None:
        """
        Initialize the OpenAI transcription client.

        Parameters
        ----------
        model : str
            The model to use for transcription.
        """
        self.client = OpenAI()
        self.model = model

    def transcribe(
        self,
        audio_file: Union[str, bytes, os.PathLike],
        *,
        language: str = "en",
        temperature: float = 0,
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file using the OpenAI API.

        Parameters
        ----------
        audio_file : Union[str, bytes, os.PathLike]
            The audio file to transcribe.
        language : str
            The language of the audio file.
        temperature : float
            The temperature of the transcription.

        Returns
        -------
        dict
            The transcription of the audio file.
        """
        response_format = "json" if "gpt" in self.model else "verbose_json"

        try:
            transcript = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.model,
                response_format=response_format,
                timestamp_granularities=["segment"],
                language=language,
                temperature=temperature,
            )
            return transcript.to_dict()
        except Exception as exc:
            logger.error("OpenAI transcription failed: %s", exc)
            return {}


class ElevenLabsTranscriber(BaseTranscriber):
    """Client wrapper around **ElevenLabs Scribe** speech‑to‑text."""

    def __init__(
        self,
        *,
        model_id: str = "scribe_v1",
        tag_audio_events: bool = True,
        diarize: bool = False,
        api_key: str | None = None,
    ) -> None:
        """
        Initialize the ElevenLabs transcription client.

        Parameters
        ----------
        model_id : str
            The model to use for transcription.
        tag_audio_events : bool
            Whether to tag audio events.
        diarize : bool
            Whether to diarize the audio.
        api_key : str, optional
            The API key to use for the ElevenLabs transcription client.
        """
        self.client = ElevenLabs(api_key=api_key or os.getenv("ELEVENLABS_API_KEY"))
        self.model_id = model_id
        self.tag_audio_events = tag_audio_events
        self.diarize = diarize

    def transcribe(
        self,
        audio_file: Union[str, bytes, os.PathLike],
        *,
        language: str = "eng",
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file using the ElevenLabs API.

        Parameters
        ----------
        audio_file : Union[str, bytes, os.PathLike]
            The audio file to transcribe.
        language : str
            The language of the audio file.
        """
        if isinstance(audio_file, (str, Path, os.PathLike)):
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
        elif hasattr(audio_file, "read"):
            audio_bytes = audio_file.read()
            audio_file.seek(0)
        else:
            audio_bytes = audio_file  # assume ``bytes``

        audio_io = BytesIO(audio_bytes)

        try:
            result = self.client.speech_to_text.convert(
                file=audio_io,
                model_id=self.model_id,
                language_code=language,
                tag_audio_events=self.tag_audio_events,
                diarize=self.diarize,
            )
        except Exception as exc:
            logger.error("ElevenLabs transcription failed: %s", exc)
            return {}

        if hasattr(result, "model_dump"):
            return result.model_dump()
        if hasattr(result, "to_dict"):
            return result.to_dict()
        return result


class GoogleTranscriber(BaseTranscriber):
    """Client wrapper around **Google Cloud Speech-to-Text v2**."""

    def __init__(
        self,
        *,
        project_id: str | None = None,
        cred_path: str | None = None,
        location: str = "europe-west4",
        language_code: str = "en-US",
        chunk_length_ms: int = 59990,
    ) -> None:
        """
        Initialize the Google Cloud transcription client.

        Parameters
        ----------
        project_id : str, optional
            GCP Project ID.
        cred_path : str, optional
            Path to GCP service account JSON.
        location : str
            GCP region for Speech-to-Text.
        language_code : str
            Language code for transcription.
        chunk_length_ms : int
            Length of each chunk in milliseconds for local transcription.
        """
        cred_path = cred_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.credentials = service_account.Credentials.from_service_account_file(
            cred_path
        )
        self.client = SpeechClient(
            credentials=self.credentials,
            client_options={"api_endpoint": f"{location}-speech.googleapis.com"},
        )
        self.location = location
        self.language_code = language_code
        self.chunk_length_ms = chunk_length_ms

    def transcribe(
        self,
        audio_file: Union[str, bytes, os.PathLike],
        *,
        language: str = "en-US",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file using Google Cloud Speech-to-Text.

        Parameters
        ----------
        audio_file : Union[str, bytes, os.PathLike]
            Local WAV path or GCS URI.
        language : str
            Language code for transcription.

        Returns
        -------
        dict
            Transcription results.
        """
        self.language_code = language

        try:
            if isinstance(audio_file, str) and audio_file.startswith("gs://"):
                logger.info(f"Starting GCS batch transcription for {audio_file}")
                return self._transcribe_batch(audio_file)
            elif isinstance(audio_file, (str, Path, os.PathLike)):
                logger.info(f"Starting local chunked transcription for {audio_file}")
                return self._transcribe_local(str(audio_file))

            logger.error(
                "Unsupported input for GoogleTranscriber; requires file path or GCS URI."
            )
            return {}
        except Exception as exc:
            logger.error("Google Cloud transcription failed: %s", exc)
            return {}

    def _make_config(self) -> cloud_speech.RecognitionConfig:
        """Make a recognition config for the Google Cloud Speech-to-Text API."""
        return cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=[self.language_code],
            model="chirp_2",
            features=cloud_speech.RecognitionFeatures(
                enable_automatic_punctuation=True,
                profanity_filter=False,
                enable_word_time_offsets=True,
                multi_channel_mode="SEPARATE_RECOGNITION_PER_CHANNEL",
                max_alternatives=1,
            ),
        )

    def _transcribe_chunk(self, chunk: AudioSegment) -> dict:
        """
        Transcribe a chunk of audio using the Google Cloud Speech-to-Text API.

        Parameters
        ----------
        chunk : AudioSegment
            The chunk of audio to transcribe.

        Returns
        -------
        dict
            The transcription of the chunk.
        """
        buffer = BytesIO()
        chunk.export(buffer, format="wav", parameters=["-acodec", "pcm_s16le"])
        buffer.seek(0)
        audio_content = base64.b64encode(buffer.read()).decode("utf-8")

        request = cloud_speech.RecognizeRequest(
            recognizer=f"projects/{self.project_id}/locations/{self.location}/recognizers/_",
            config=self._make_config(),
            content=audio_content,
        )
        response = self.client.recognize(request=request)
        return json_format.MessageToDict(response._pb)

    def _transcribe_local(self, audio_path: str) -> dict:
        """
        Transcribe a local audio file using the Google Cloud Speech-to-Text API.

        Parameters
        ----------
        audio_path : str
            The path to the local audio file to transcribe.

        Returns
        -------
        dict
            The transcription of the local audio file.
        """
        audio = AudioSegment.from_wav(audio_path)
        total_chunks = math.ceil(len(audio) / self.chunk_length_ms)
        results = []

        for i in range(total_chunks):
            start = i * self.chunk_length_ms
            end = min((i + 1) * self.chunk_length_ms, len(audio))
            chunk = audio[start:end]
            logger.debug(
                f"Transcribing chunk {i+1}/{total_chunks} ({start}ms - {end}ms)"  # noqa: WPS237
            )
            result = self._transcribe_chunk(chunk)
            results.append(result)

        return {"chunks": results}

    def _transcribe_batch(self, gcs_uri: str) -> dict:
        """
        Transcribe a batch of audio files using the Google Cloud Speech-to-Text API.

        Parameters
        ----------
        gcs_uri : str
            The GCS URI of the audio file to transcribe.

        Returns
        -------
        dict
            The transcription of the batch of audio files.
        """
        config = self._make_config()
        audio_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=gcs_uri)
        batch_request = cloud_speech.BatchRecognizeRequest(
            config=config,
            files=[audio_metadata],
            recognition_output_config=cloud_speech.RecognitionOutputConfig(
                inline_response_config=cloud_speech.InlineOutputConfig()
            ),
            recognizer=f"projects/{self.project_id}/locations/{self.location}/recognizers/_",
        )
        operation = self.client.batch_recognize(request=batch_request)
        while not operation.done():
            logger.debug("Waiting for batch transcription to complete...")
            time.sleep(2)
        response = operation.result()
        return json_format.MessageToDict(response._pb)
