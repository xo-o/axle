"""
Speech-to-Text library using Deepgram SDK v3.
"""
import os
import json
import requests
from deepgram import DeepgramClient


def get_words(deepgram_result: dict) -> list:
    try:
        # Results structure in v3 response dict
        raw_words = deepgram_result['results']['channels'][0]['alternatives'][0]['words']
        return [
            {
                "word": w.get("punctuated_word", w.get("word")),
                "start": w["start"],
                "end": w["end"],
                "confidence": w["confidence"]
            }
            for w in raw_words
        ]
    except (KeyError, IndexError):
        return []


def get_paragraphs(deepgram_result: dict) -> list:
    try:
        raw_paragraphs = (
            deepgram_result['results']['channels'][0]['alternatives'][0]
            .get('paragraphs', {}).get('paragraphs', [])
        )
        return [
            {
                "sentences": [
                    {"text": s.get("text"), "start": s.get("start"), "end": s.get("end")}
                    for s in p.get('sentences', [])
                ],
                "numWords": p.get("num_words", 0),
                "start": p.get("start", 0.0),
                "end": p.get("end", 0.0)
            }
            for p in raw_paragraphs
        ]
    except (KeyError, IndexError):
        return []


def deepgram_to_combo(deepgram_result: dict) -> dict:
    try:
        alt = deepgram_result['results']['channels'][0]['alternatives'][0]
        text = alt['transcript']
    except (KeyError, IndexError):
        text = ""

    detected_language = (
        deepgram_result.get('results', {})
        .get('channels', [{}])[0]
        .get('detected_language')
    )

    return {
        "duration": deepgram_result.get('metadata', {}).get('duration', 0.0),
        "results": {
            "main": {
                "language": detected_language,
                "paragraphs": get_paragraphs(deepgram_result),
                "text": text,
                "words": get_words(deepgram_result),
            }
        }
    }


def transcribe(
    url: str,
    api_key: str = None,
    language: str = None,
    model: str = 'nova-3',
    smart_format: bool = True,
    paragraphs: bool = True,
) -> dict:
    api_key = api_key or os.environ.get("DEEPGRAM_API_KEY")
    if not url:
        raise ValueError('Audio path or URL is required')
    if not api_key:
        raise ValueError('Deepgram API key is required')

    client = DeepgramClient(api_key=api_key)

    options = {
        "model": model,
        "smart_format": smart_format,
        "paragraphs": paragraphs,
    }
    
    if language and language != 'auto':
        options["language"] = language
    else:
        options["detect_language"] = True

    # Check if url is a URL or a local file
    if url.startswith(('http://', 'https://')):
        response = client.listen.v1.media.transcribe_url(url=url, **options)
    else:
        with open(url, "rb") as audio_file:
            response = client.listen.v1.media.transcribe_file(request=audio_file.read(), **options)

    # In v3, response is an object, we need to convert to dict for deepgram_to_combo
    if hasattr(response, 'model_dump'):
        result_dict = response.model_dump()
    elif hasattr(response, 'dict'):
        result_dict = response.dict()
    else:
        result_dict = response

    return deepgram_to_combo(result_dict)
