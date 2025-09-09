from __future__ import annotations

from enum import IntEnum


class LanguageEnum(IntEnum):
    Ar = 0
    En = 1
    ArEn = 2

    def __str__(self) -> str:
        if self is LanguageEnum.Ar:
            return "ar"
        if self is LanguageEnum.En:
            return "en"
        if self is LanguageEnum.ArEn:
            return "codeswitch"
        return ""


class ASRModelEnum(IntEnum):
    Ar_1 = 0
    En_1 = 1
    ArEn_1 = 2
    Ar_2 = 3
    En_2 = 4

    def __str__(self) -> str:
        if self is ASRModelEnum.Ar_1:
            return "w2v_ar"
        if self is ASRModelEnum.Ar_2:
            return "zip_ar"
        if self is ASRModelEnum.En_1:
            return "fc_en"
        if self is ASRModelEnum.En_2:
            return "zip_en"
        if self is ASRModelEnum.ArEn_1:
            return "zip_cs_ar_en"
        return ""


EVENT_FT_CONNECT = "connect"
EVENT_FT_ERROR = "error"
EVENT_FT_TRANSCRIBE_FILE = "audio_file"
EVENT_FT_TRANSCRIBE_FILE_UPLOAD_SUCCESS = "audio_file_upload_success"
EVENT_FT_TRANSCRIBE_RESULT = "transcription_result"
EVENT_RT_AUDIO_STREAM = "audio_stream"
EVENT_RT_END_AUDIO_STREAM = "end_audio_stream"
