"""
Transcripción local de audios/videos a texto usando faster-whisper.

Uso:
    python scripts/transcribe.py <ruta-audio> [--output ruta-salida.txt] [--model small|medium]

Por defecto:
    - modelo: small (rápido, calidad razonable)
    - idioma: español (con prompt para acento chileno y contexto Gama Mobility)
    - salida: <misma-carpeta>/transcripcion.txt
"""
import argparse
import os
import sys
import traceback

import imageio_ffmpeg
from faster_whisper import WhisperModel


INITIAL_PROMPT = (
    "Esta es una entrevista de Customer Experience con un cliente de Gama Mobility, "
    "empresa chilena de gestión de flotas y movilidad. Se discuten experiencias de uso, "
    "puntos de dolor, satisfacción con el servicio, condición de vehículos, comunicación "
    "y competidores. El lenguaje es español chileno coloquial."
)


def ensure_ffmpeg_in_path() -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in os.environ["PATH"]:
        os.environ["PATH"] = current_dir + os.pathsep + os.environ["PATH"]
    try:
        ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
    except Exception:
        pass


def transcribe(audio_path: str, output_path: str, model_size: str = "small") -> None:
    ensure_ffmpeg_in_path()

    print(f"Cargando modelo Whisper '{model_size}' (CPU, int8, threads=6)...", flush=True)
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=6)

    print(f"Transcribiendo: {audio_path}", flush=True)
    segments, info = model.transcribe(
        audio_path,
        language="es",
        beam_size=1,
        initial_prompt=INITIAL_PROMPT,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    print(
        f"Idioma detectado: '{info.language}' (prob {info.language_probability:.2f}). "
        f"Duración: {info.duration/60:.1f} min",
        flush=True,
    )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for segment in segments:
            line = "[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text.strip())
            print(line, flush=True)
            f.write(line + "\n")
            f.flush()

    print(f"\nListo. Transcripción guardada en: {output_path}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe audio/video a texto (faster-whisper).")
    parser.add_argument("audio", help="Ruta al archivo de audio o video (.mp4, .mp3, .m4a, .wav, ...)")
    parser.add_argument(
        "--output",
        default=None,
        help="Ruta de salida del .txt. Por defecto: <carpeta-audio>/transcripcion.txt",
    )
    parser.add_argument(
        "--model",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        default="small",
        help="Modelo Whisper. 'small' = rápido. 'medium' = mejor fidelidad chilena.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"No se encontró el archivo: {args.audio}", file=sys.stderr)
        return 1

    output_path = args.output or os.path.join(os.path.dirname(args.audio) or ".", "transcripcion.txt")

    try:
        transcribe(args.audio, output_path, args.model)
        return 0
    except Exception as e:
        print(f"Error en transcripción: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
