# miya-speechless

## UV Installation Instructions

### Step 1: Install uv

You can install [uv](https://github.com/astral-sh/uv) by running the official installation script:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Alternatively, you can install it via Homebrew:

```bash
brew install astral-sh/uv/uv
```

### Step 2: Verify uv Installation

After installing, verify that uv is available by running:

```bash
uv --version
```

### Step 3: Install Dependencies

Once uv is installed, you can install the project dependencies by running the following command in the project root. Using the `--dev` flag will install the development dependencies (e.g. pytest, black, isort, etc.).

```bash
uv venv
source .venv/bin/activate
uv sync --dev
```

This will create a virtual environment and install all dependencies specified in the `pyproject.toml` file.

### Step 4: Run the Project or Tests

You can now run the project or the tests using the uv environment:

To activate the environment:

```bash
source .venv/bin/activate
```

To run the tests:

```bash
uv run pytest
```

### Step 5: Convert the model to onnx format

To convert the model to onnx format, run the following command:

```bash
uv run python export_to_onnx.py --checkpoint /path/to/checkpoint --onnx_model /path/to/onnx_model
```

### Step 6: Run the streamlit app

Place the onnx model in the models directory.

To start the streamlit app, run the following command:

```bash
uv run streamlit run app/app.py
```

To start debug mode, run:

```bash
uv run python -m debugpy --listen 5678 -m streamlit run app/app.py
```

In the application, you can set the following parameters:
- overlap: Set the overlap between the transcript and the diaretization (default: 0.1)
- onset_threshold: Set the onset threshold for speaker start (default: 0.1)
- offset_threshold: Set the offset threshold for speaker stop (default: 0.1)

### Step 7: Add OPENAI_API_KEY and/or setup WHISPER_CPP_MODEL

`whisper_1` requires a paid OpenAI subscription. An alternative is [whisper.cpp](https://github.com/ggerganov/whisper.cpp)

Download at least one supported model:

```bash
# Linux
docker run -it --rm -v ./data/models:/models ghcr.io/ggerganov/whisper.cpp:main "./models/download-ggml-model.sh small /models"
# Windows
docker run -it --rm -v "$(pwd -W)/models":/models ghcr.io/ggerganov/whisper.cpp:main "./models/download-ggml-model.sh small /models"
```

When `WHISPER_CPP_MODEL` is set, expect the following to happen instead of calling OpenAI:

```bash
ffmpeg -i data/temp_results/uploaded_audio.mp3 -ar 16000 -ac 1 -c:a pcm_s16le data/audio/output.wav
# Linux
docker run -it --rm -v ./data/models:/models -v ./data/audio:/audios ghcr.io/ggerganov/whisper.cpp:main "./build/bin/whisper-cli -m /models/ggml-small.bin -f /audios/output.wav -ml 16 -oj -l en"
# Windows
docker run -it --rm -v "$(pwd -W)/data/models":/models -v "$(pwd -W)/data":/audios ghcr.io/ggerganov/whisper.cpp:main "./build/bin/whisper-cli -m /models/ggml-small.bin -f /audios/output.wav -ml 16 -oj -l en"
```
