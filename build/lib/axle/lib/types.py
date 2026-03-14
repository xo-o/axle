from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class VoiceConfig(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    speed: Optional[float] = None
    url: Optional[str] = None


class VisualsConfig(BaseModel):
    type: str
    style: str


class MusicConfig(BaseModel):
    id: str
    url: str


class CaptionsConfig(BaseModel):
    id: str
    name: str
    position: Literal['top', 'middle', 'bottom']
    size: Literal['small', 'medium', 'large']


class TextToSpeech(BaseModel):
    refId: str
    src: str
    duration: float


class SpeechToText(BaseModel):
    refId: str
    src: str


class VisualShotDisplay(BaseModel):
    from_: float = Field(alias="from")
    to: float


class VisualShot(BaseModel):
    id: Optional[str] = None
    type: Literal['product', 'generic', 'lifestyle', 'medical_cgi', 'metaphor', 'b-roll']
    category: str
    firstFrame: str
    videoPrompt: str
    scenePrompt: str
    words: Optional[str] = None
    segmentId: Optional[str] = None
    prompt: Optional[str] = None
    triggerWords: Optional[str] = None
    video: Optional[str] = None
    lastFrame: Optional[str] = None
    hasProductInteraction: Optional[bool] = None
    productSizing: Optional[str] = None
    duration: Optional[float] = None
    display: Optional[VisualShotDisplay] = None


class VisualBroll(BaseModel):
    time: Optional[float] = None
    url: Optional[str] = None
    duration: Optional[float] = None
    type: Literal['video', 'image']
    firstFrame: Optional[str] = None
    videoPrompt: Optional[str] = None
    scenePrompt: Optional[str] = None
    words: Optional[str] = None
    productSizing: Optional[str] = None


class Segment(BaseModel):
    id: str
    title: str
    text: str
    description: str
    searchQuery: str
    tags: List[str]
    shots: Optional[List[VisualShot]] = None
    bRolls: Optional[List[VisualBroll]] = None
    duration: float
    textToSpeech: Optional[TextToSpeech] = None
    speechToText: Optional[SpeechToText] = None
    mergeWithNext: Optional[bool] = None
    estimatedDuration: Optional[float] = None
    isContinuation: Optional[bool] = None


class AssetSchema(BaseModel):
    id: str
    name: str
    url: str
    type: Literal['image', 'video']


class AvatarSchema(BaseModel):
    id: str
    name: str
    url: str


class ProductSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Storyboard(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    segments: Optional[List[Segment]] = None
    voice: VoiceConfig
    visuals: VisualsConfig
    music: Optional[MusicConfig] = None
    caption: CaptionsConfig
    aspectRatio: Literal['1:1', '16:9', '9:16', '11']
    product: Optional[ProductSchema] = None
    assets: Optional[List[AssetSchema]] = None
    avatar: Optional[AvatarSchema] = None
    type: Optional[str] = None
    script: Optional[str] = None
    pacing: Optional[Literal['fast', 'slow', 'regular', 'dynamic', 'relaxed']] = None
    quality: Optional[Literal['regular', 'high']] = None
    duration: Optional[float] = None
