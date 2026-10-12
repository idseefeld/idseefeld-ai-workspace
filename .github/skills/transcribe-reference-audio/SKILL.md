---
name: transcribe-reference-audio
description: "Transcribe all audio files from reference into timestamped TXT files in outputs using CUDA-accelerated faster-whisper. Use when: transcribing reference audio, batch transcribing interviews, creating missing audio transcripts, or processing sound files in reference."
argument-hint: "Optional model name, for example: small or medium"
user-invocable: true
disable-model-invocation: false
---

# Transcribe Reference Audio

Create transcripts for every supported audio file under `reference/` that does
not already have a matching transcript under `outputs/`.

## Output Mapping

For an input file named `reference/meeting.ogg`, the transcript path is
`outputs/meeting-transcription.txt`. The filename stem is matched
case-insensitively; existing target files are never overwritten.

## Procedure

1. Confirm that CUDA-enabled PyTorch, `faster-whisper`, FFmpeg, and the
   CTranslate2 CUDA runtime dependencies are installed.
2. Run:

   ```powershell
   python .github\skills\transcribe-reference-audio\scripts\transcribe_reference_audio.py
   ```

3. Use `--model small` when throughput is more important than transcription
   quality. The default `medium` model is the recommended balance for the
   local RTX 2060.
4. Review the script summary and inspect the created TXT files in `outputs/`.
   Report skipped files separately from newly created transcripts.

## Supported Inputs

The script discovers `.aac`, `.aif`, `.aiff`, `.alac`, `.amr`, `.au`, `.flac`,
`.m4a`, `.mka`, `.mp3`, `.mp4`, `.oga`, `.ogg`, `.opus`, `.wav`, `.webm`, and
`.wma` files recursively below `reference/`.

## Failure Handling

Do not treat a failed transcription as completed. The script exits nonzero and
reports the source file that failed. It writes each result atomically, so a
partial transcript cannot be mistaken for a completed result.
