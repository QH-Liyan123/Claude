---
name: voice
description: Voice input for Claude Code. Hold Ctrl to speak, text auto-types into Claude Code input. Say "关闭语音" to stop. Use when user wants voice input, speech-to-text, or hands-free interaction with Claude Code.
---

# Voice Input Skill

Enables voice input for Claude Code using local speech recognition (faster-whisper). Supports Chinese-English mixed input. No cloud services, fully offline.

## Usage

### Start voice input: `/voice`

Run this command to start the voice listener in the background:

```bash
pythonw %USERPROFILE%/tools/voice_input.py &
```

Then confirm to the user:

1. Check if the process started successfully:
```bash
sleep 1 && tail -5 %USERPROFILE%/tools/voice_input.log
```

2. Check if PID file exists:
```bash
cat %USERPROFILE%/tools/voice_input.pid
```

3. Tell the user:
   - Voice input is active
   - **Hold Ctrl** to speak (hold for 0.25s+ to activate)
   - Release Ctrl to auto-type the recognized text
   - Say **"关闭语音"**, **"停止录音"** or similar to stop (recommended, no confirmation needed)

### Stop voice input: `/voice stop`

When user says `/voice stop` or asks to stop voice input, run this single command (no extra confirmation needed):

```bash
PID=$(cat %USERPROFILE%/tools/voice_input.pid 2>/dev/null) && taskkill //F //PID $PID 2>/dev/null; rm -f %USERPROFILE%/tools/voice_input.pid; echo "Voice input stopped"
```

Then tell the user voice input has been stopped.

### Check status: `/voice status`

```bash
if [ -f %USERPROFILE%/tools/voice_input.pid ]; then
  PID=$(cat %USERPROFILE%/tools/voice_input.pid)
  if kill -0 $PID 2>/dev/null; then
    echo "Voice input is running (PID: $PID)"
  else
    echo "Voice input is not running (stale PID file)"
    rm -f %USERPROFILE%/tools/voice_input.pid
  fi
else
  echo "Voice input is not running"
fi
```

## Important Notes

- Before starting, check if voice input is already running (check PID file) to avoid duplicate processes
- The script uses `pythonw` (no console window) to run in background
- Logs are written to `%USERPROFILE%/tools/voice_input.log`
- Uses faster-whisper with local Whisper small model, supports Chinese-English mixed input
- Model is downloaded to `%USERPROFILE%/tools/whisper-model/` during installation

---
Created by Leon Li(李岩) - 20260225
