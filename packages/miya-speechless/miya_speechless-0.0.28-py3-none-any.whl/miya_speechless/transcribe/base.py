"""Base class for transcription clients."""

import os
from typing import Any, Dict, Union


class BaseTranscriber:
    """Interface definition for transcription clients."""

    def transcribe(
        self,
        audio_file: Union[str, bytes, os.PathLike],
        *,
        language: str = "en",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Convert *audio_file* to text.

        Parameters
        ----------
        audio_file : Union[str, bytes, os.PathLike]
            The audio file to transcribe.
        language : str
            The language of the audio file.
        **kwargs : dict
            Additional keyword arguments to pass to the transcription client.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in the subclass.
        """
        raise NotImplementedError
