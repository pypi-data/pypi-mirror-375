"""Sparv plugin to import audio files as text with Whisper."""

from sparv.api import Config

from sbx_whisper_import.whisper_import import parse_mp3, parse_ogg, parse_wav

__all__ = ["parse_mp3", "parse_ogg", "parse_wav"]

__config__ = [
    Config(
        "sbx_whisper_import.model_size",
        "small",
        description="The size of the model. Defaults to 'small'",
        datatype=str,
    ),
    Config(
        "sbx_whisper_import.model_verbosity",
        "standard",
        description="The verbosity of the model. Defaults to 'standard'",
        datatype=str,
    ),
]

__description__ = "Import audio files as text with Whisper."

__version__ = "0.1.0"
