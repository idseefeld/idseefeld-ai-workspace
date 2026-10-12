"""Batch transcribe reference audio with the local CUDA faster-whisper setup."""

from __future__ import annotations

import argparse
import os
import site
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

import torch
from faster_whisper import WhisperModel


AUDIO_EXTENSIONS = {
    ".aac",
    ".aif",
    ".aiff",
    ".alac",
    ".amr",
    ".au",
    ".flac",
    ".m4a",
    ".mka",
    ".mp3",
    ".mp4",
    ".oga",
    ".ogg",
    ".opus",
    ".wav",
    ".webm",
    ".wma",
}


@dataclass(frozen=True)
class TranscriptJob:
    source: Path
    target: Path


def configure_cuda_dll_search_path() -> None:
    """Expose pip-installed CUDA 12 DLLs required by CTranslate2 on Windows."""
    if os.name != "nt":
        return

    package_root = Path(site.getusersitepackages()) / "nvidia"
    dll_directories = (
        package_root / "cublas" / "bin",
        package_root / "cuda_nvrtc" / "bin",
        package_root / "cudnn" / "bin",
    )
    existing_directories = [str(directory) for directory in dll_directories if directory.is_dir()]
    if not existing_directories:
        raise RuntimeError(
            "CUDA runtime DLLs were not found. Install nvidia-cublas-cu12 and "
            "nvidia-cudnn-cu12 before running this script."
        )

    os.environ["PATH"] = os.pathsep.join([*existing_directories, os.environ["PATH"]])
    for directory in existing_directories:
        os.add_dll_directory(directory)


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[4]


def discover_jobs(reference_directory: Path, output_directory: Path) -> tuple[list[TranscriptJob], list[Path]]:
    jobs: list[TranscriptJob] = []
    skipped: list[Path] = []

    for source in sorted(reference_directory.rglob("*"), key=lambda path: str(path).casefold()):
        if not source.is_file() or source.suffix.casefold() not in AUDIO_EXTENSIONS:
            continue

        target = output_directory / f"{source.stem}-transcription.txt"
        if target.exists():
            skipped.append(source)
        else:
            jobs.append(TranscriptJob(source=source, target=target))

    return jobs, skipped


def write_transcript(model: WhisperModel, job: TranscriptJob) -> int:
    segments, info = model.transcribe(
        str(job.source),
        beam_size=5,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
    )

    job.target.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=job.target.parent,
        prefix=f".{job.target.stem}-",
        suffix=".tmp",
        delete=False,
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)
        temporary_file.write(f"Quelle: {job.source.name}\n")
        temporary_file.write(
            f"Erkannte Sprache: {info.language} "
            f"(Wahrscheinlichkeit: {info.language_probability:.1%})\n\n"
        )
        segment_count = 0
        for segment in segments:
            temporary_file.write(
                f"[{segment.start:09.2f} - {segment.end:09.2f}] "
                f"{segment.text.strip()}\n"
            )
            segment_count += 1

    temporary_path.replace(job.target)
    return segment_count


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe missing reference audio files with faster-whisper."
    )
    parser.add_argument(
        "--model",
        default="medium",
        help="faster-whisper model name (default: medium)",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    configure_cuda_dll_search_path()

    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is unavailable in PyTorch. Install a CUDA-enabled PyTorch build "
            "and confirm that the NVIDIA GPU is usable."
        )

    root = workspace_root()
    reference_directory = root / "reference"
    output_directory = root / "outputs"
    if not reference_directory.is_dir():
        raise FileNotFoundError(f"Reference directory does not exist: {reference_directory}")

    jobs, skipped = discover_jobs(reference_directory, output_directory)
    print(f"Found {len(jobs)} file(s) to transcribe and {len(skipped)} already transcribed file(s).")
    for source in skipped:
        print(f"SKIPPED {source.relative_to(root)}")

    if not jobs:
        return 0

    model = WhisperModel(arguments.model, device="cuda", compute_type="int8_float16")
    completed = 0
    for job in jobs:
        print(f"TRANSCRIBING {job.source.relative_to(root)}")
        segment_count = write_transcript(model, job)
        completed += 1
        print(f"CREATED {job.target.relative_to(root)} ({segment_count} segment(s))")

    print(f"Completed {completed} transcript(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error
