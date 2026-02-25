# Voice Input for Claude Code

Hold **Ctrl** to speak, release to auto-type text into Claude Code. Supports **Chinese-English mixed input**. Fully offline, powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Demo

```
[Hold Ctrl] "帮我写一个 Python function" [Release Ctrl]
  -> Auto-types into Claude Code input
```

## Requirements

- Windows 10/11
- Python 3.10+
- Microphone
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)

## Installation

### Quick Install

```cmd
git clone https://github.com/QH-Liyan123/Claude.git
cd Claude
install.bat
```

The installer will:
1. Install Python dependencies (`faster-whisper`, `sounddevice`, `pynput`)
2. Copy files to `%USERPROFILE%\tools\` and `%USERPROFILE%\.claude\skills\voice\`
3. Download Whisper Small model (~462MB) from HuggingFace
4. Configure Claude Code permissions (no confirmation prompts)
5. Verify installation

### Behind a Proxy?

Set the proxy before running the installer:

```cmd
set HTTPS_PROXY=http://your-proxy-server:port
install.bat
```

## Usage

In Claude Code:

| Command | Action |
|---------|--------|
| `/voice` | Start voice input |
| `/voice stop` | Stop voice input |
| `/voice status` | Check if running |

### How It Works

1. **Hold Ctrl** (0.25s+) to start recording (red indicator appears at top of screen)
2. **Release Ctrl** to recognize and auto-type the text
3. **Say "关闭语音"** or **"停止录音"** to exit voice input
4. Keyboard shortcuts like Ctrl+C/V are filtered out and won't trigger recording

## Technical Details

| Item | Detail |
|------|--------|
| Speech Engine | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2) |
| Model | Whisper Small (~462MB, supports 99 languages) |
| Inference | CPU int8 quantization, ~1-3s latency |
| Privacy | All processing is local, no data uploaded |

### Model Upgrade

To use a larger model for better accuracy, edit `MODEL_SIZE` in `voice_input.py`:

```python
MODEL_SIZE = "medium"  # Options: tiny(75MB), base(141MB), small(461MB), medium(1.5GB), large-v3(3GB)
```

Then re-run `install.bat` or manually download:

```python
python -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-medium', local_dir='%USERPROFILE%/tools/whisper-model')"
```

## File Structure

```
voice-skill/
├── README.md           # This file
├── LICENSE             # MIT License
├── .gitignore
├── voice_input.py      # Main voice input script
├── install.bat         # One-click installer
└── skill/
    └── SKILL.md        # Claude Code skill definition
```

## License

MIT License - see [LICENSE](LICENSE)

---

Created by Leon Li(李岩) - 20260225
