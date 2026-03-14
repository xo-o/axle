import os
import requests
from typing import Optional, Dict, Any, Tuple

class AudioService:
    def __init__(self, url: str, api_key: str, model: str):
        self.base_url = url.rstrip('/')
        self.api_key = api_key
        self.model = model

    def synthesize(self, text: str, voice_id: str) -> Tuple[bool, bytes]:
        if not voice_id or not text:
            raise ValueError("Missing parameters: both voiceId and text are required.")

        url = f"{self.base_url}/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": self.model
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return True, response.content
        except requests.exceptions.RequestException as err:
            print("ElevenLabs Synthesis Error:", err)
            if response is not None:
                print("Response text:", response.text)
            raise RuntimeError("Unable to synthesize speech. Please try again later.") from err

    def speech_to_speech(self, voice_id: str, audio_bytes: bytes, filename: str) -> Tuple[bool, bytes]:
        if not voice_id or not audio_bytes:
            raise ValueError("Missing parameters: both voiceId and audioBuffer are required.")

        url = f"{self.base_url}/v1/speech-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key
        }
        
        files = {
            "audio": (filename, audio_bytes, "audio/mpeg")
        }
        data = {
            "model_id": self.model
        }

        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            return True, response.content
        except requests.exceptions.RequestException as err:
            print("ElevenLabs STS Error:", err)
            if response is not None:
                print("Response text:", response.text)
            raise RuntimeError("Unable to convert speech to speech. Please try again later.") from err

    def get_voices(self, params: Dict[str, Any]) -> Tuple[list, bool, Optional[str]]:
        url = f"{self.base_url}/v1/voices"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        query_params = {
            "sort_direction": "desc",
            "voice_type": "non-default",
            "include_total_count": "false"
        }
        
        for k, v in params.items():
            if v:
                query_params[k] = v
                
        try:
            response = requests.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            data = response.json()
            
            voices = []
            for v in data.get("voices", []):
                if not v:
                    continue
                labels = v.get("labels") or {}
                verified_langs = v.get("verified_languages") or []
                verified = verified_langs[0] if verified_langs and isinstance(verified_langs[0], dict) else {}
                sharing = v.get("sharing") or {}
                sharing_labels = sharing.get("labels") or {}
                
                voices.append({
                    "id": v.get("voice_id"),
                    "name": v.get("name"),
                    "accent": labels.get("accent") or verified.get("accent", ""),
                    "gender": labels.get("gender"),
                    "age": labels.get("age"),
                    "descriptive": labels.get("descriptive") or sharing_labels.get("descriptive", ""),
                    "useCase": labels.get("use_case"),
                    "category": v.get("category"),
                    "language": labels.get("language") or verified.get("language", ""),
                    "locale": labels.get("locale") or verified.get("locale") or sharing_labels.get("locale"),
                    "description": v.get("description"),
                    "previewUrl": v.get("preview_url")
                })
                
            return voices, data.get("has_more", False), data.get("next_page_token")
            
        except requests.exceptions.RequestException as err:
            print("Get voices error:", err)
            raise RuntimeError("Failed to get voices.") from err

    def clone_voice(self, name: str, audio_bytes: bytes, filename: str, description: Optional[str] = None) -> str:
        url = f"{self.base_url}/v1/voices/add"
        headers = {
            "xi-api-key": self.api_key
        }
        
        files = {
            "files": (filename, audio_bytes, "audio/mpeg")
        }
        data = {
            "name": name
        }
        if description:
            data["description"] = description
            
        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            return response.json().get("voice_id")
        except requests.exceptions.RequestException as err:
            print("ElevenLabs Clone Voice Error:", err)
            raise RuntimeError("Unable to clone voice. Please try again later.") from err

    def delete_voice(self, voice_id: str) -> bool:
        url = f"{self.base_url}/v1/voices/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as err:
            print("Delete voice error:", err)
            return False
