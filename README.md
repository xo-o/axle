# axle

A composable toolset for agentic video workflows.

Axle provides a suite of atomic tools designed to be called by AI agents to handle database operations, asset generation (image, audio, text), storyboard management, and video manipulation.

## Installation

```sh
# Clone the repository
git clone <repo-url>
cd vidgen

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies in editable mode
pip install -e .
```

## Environment Variables

Ensure your `.env` file contains the following keys:

```env
TURSO_DATABASE_URL=...
TURSO_AUTH_TOKEN=...
GEMINI_API_KEY=...
ELEVENLABS_API_KEY=...
ELEVENLABS_URL=https://api.elevenlabs.io (optional)
ELEVENLABS_MODEL=eleven_multilingual_v2 (optional)
DEEPGRAM_API_KEY=...
R2_BUCKET_NAME=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_ACCOUNT_ID=...
R2_CDN=...
```

---

## Tool Categories & Commands

All commands follow the pattern: `python3 -m axle.main <category> <command> [options]`

### 1. `db` (Database Operations)

Manage the Turso database schema.

#### `init`
Initialize the database schema (creates the `storyboards` table).
- **Example**: `python3 -m axle.main db init`
- **Output**: 
  ```text
  Initializing database...
  Database initialized successfully.
  ```

---

### 2. `generate` (AI Asset Generation)

#### `image`
Generate an image using Google Gemini.
- **Options**:
  - `--prompt`, `-p` (Required): Text description.
  - `--output`, `-o` (Required): Save path (e.g., `scene1.png`).
  - `--model`, `-m` (Default: `gemini-3.1-flash-image-preview`): Gemini model.
  - `--aspectRatio`, `-a` (Default: `9:16`): `1:1`, `9:16`, or `16:9`.
- **Output**: 
  ```json
  { "path": "scene1.png" }
  ```

#### `tts`
Generate speech from text using ElevenLabs.
- **Options**:
  - `--text`, `-t` (Required): Script text.
  - `--voiceId`, `-v` (Required): ElevenLabs voice ID.
  - `--output`, `-o` (Required): Save path (e.g., `narration.mp3`).
- **Output**:
  ```json
  { "refId": "voice_uuid", "src": "narration.mp3", "duration": 0 }
  ```

#### `s2s`
Speech-to-Speech voice conversion.
- **Options**:
  - `--audio`, `-a` (Required): Path to source audio.
  - `--voiceId`, `-v` (Required): Target voice ID.
  - `--output`, `-o` (Required): Save path.
- **Output**:
  ```json
  { "refId": "voice_uuid", "src": "output.mp3", "duration": 0 }
  ```

#### `stt`
Transcribe audio using Deepgram.
- **Options**:
  - `--audio`, `-a` (Required): Path or URL to audio.
  - `--output`, `-o` (Required): Path for transcript JSON.
  - `--language`, `-l`: Language code (e.g., `en`).
  - `--model`, `-m` (Default: `nova-3`): Deepgram model.
- **Output**:
  ```json
  { "duration": 15.5, "refId": "request_uuid", "src": "transcript.json" }
  ```

---

### 3. `storyboard` (State Management)

Storyboards use a single-table schema where all segments are stored in a `data` JSON column.

#### `create`
Create a new storyboard project.
- **Options**:
  - `--title`, `-t` (Required): Project title.
  - `--aspectRatio`, `-a` (Default: `9:16`): `9:16`, `16:9`, `1:1`.
  - `--script`, `-s`: Full project script.
  - `--description`, `-d`: Project description.
  - `--type`: `narrative-video`, `product-video-ad`, `ugc-video-ad`.
  - `--pacing`: `fast`, `slow`, `regular`, `dynamic`, `relaxed`.
- **Output**:
  ```json
  { "id": "storyboard_uuid", "title": "My Video" }
  ```

#### `get`
Fetch the complete state of a storyboard including its segments.
- **Argument**: `storyboard_id` (Required)
- **Output**:
  ```json
  {
    "id": "uuid",
    "title": "Title",
    "segments": [ ... ],
    "aspectRatio": "9:16",
    ...
  }
  ```

#### `list`
List all storyboards in the database.
- **Output**: Array of summary objects `[{id, title, description, createdAt}, ...]`.

#### `add-segment`
Add a new segment to a storyboard's JSON data.
- **Options**:
  - `--storyboardId`, `-b` (Required): Target storyboard ID.
  - `--data`, `-d` (Required): JSON string of segment data.
  - `--order`, `-n`: Position index (inserts at end if omitted).
- **Output**:
  ```json
  { "id": "segment_uuid", "storyboardId": "uuid" }
  ```

#### `update-segment`
Merge new data into an existing segment.
- **Argument**: `segment_id` (Required)
- **Options**:
  - `--storyboardId`, `-b` (Required): Parent storyboard ID.
  - `--data`, `-d` (Required): JSON string to merge.
  - `--order`, `-n`: New position index.
- **Output**: `Segment [uuid] updated.`

#### `delete-segment`
- **Argument**: `segment_id` (Required)
- **Options**: `--storyboardId`, `-b` (Required).

---

### 4. `storage` (Asset Persistence)

#### `upload`
Upload a file to R2 cloud storage.
- **Options**:
  - `--file`, `-f` (Required): Local path.
  - `--name`, `-n`: Remote filename (defaults to local name).
- **Output**:
  ```json
  { "url": "https://cdn.example.com/file.png" }
  ```

#### `presign`
Generate a presigned upload URL.
- **Options**:
  - `--path`, `-p` (Required): Remote path.
  - `--expiresIn`, `-e` (Default: `3600`): Seconds.
- **Output**:
  ```json
  { "url": "...", "method": "PUT", "headers": { ... } }
  ```

---

### 5. `video` (FFMPEG Utilities)

#### `trim`
Trim a video segment.
- **Options**:
  - `--input`, `-i` (Required): Input path.
  - `--output`, `-o` (Required): Output path.
  - `--start`, `-s` (Required): Start time (e.g., `00:00:05`).
  - `--end`, `-e`: End time.
  - `--duration`, `-d`: Duration.
- **Output**: `{ "path": "output.mp4" }`

#### `split`
Split a video into two parts at a specific timestamp.
- **Options**:
  - `--input`, `-i` (Required): Input path.
  - `--at`, `-a` (Required): Split time.
  - `--outputA`: First half path.
  - `--outputB`: Second half path.
- **Output**: `{ "partA": "...", "partB": "..." }`

---

### 6. `voice` (ElevenLabs Management)

#### `clone`
Create a new cloned voice from an audio sample.
- **Options**:
  - `--name`, `-n` (Required): Voice name.
  - `--audio`, `-a` (Required): Sample audio path.
  - `--description`, `-d`: Optional description.
- **Output**:
  ```json
  { "name": "Name", "voiceId": "eleven_voice_id" }
  ```

---

### 7. `search` (Asset Discovery)

#### `asset`
Semantic search for media assets.
- **Options**:
  - `--query`, `-q` (Required): Natural language query.
  - `--db`, `-d` (Required): RAG database connection string.
  - `--limit`, `-l` (Default: `1`): Result count.
  - `--type`, `-t`: `video` or `image`.
- **Output**: Array of matching asset objects.
# axle
