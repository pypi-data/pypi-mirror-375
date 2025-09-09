"""
🛠️ Основные утилиты для работы с FFmpeg и видео обработкой

Этот модуль содержит все низкоуровневые функции для:
- Запуска FFmpeg команд
- Анализа видеофайлов через FFprobe
- Создания HLS и DASH стримов
- Извлечения превью кадров
- Работы с временными файлами и storage

Автор: akula993
Лицензия: MIT
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum

# Замените строку 26 в utils.py:
try:
    from celery.exceptions import SecurityError
except ImportError:
    class SecurityError(Exception):
        pass

from . import defaults
from .exceptions import (
    FFmpegError,
    FFmpegNotFoundError,
    InvalidVideoError,
    StorageError,
    TimeoutError,
    TranscodingError,
    ConfigurationError,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# КОНТЕКСТНЫЕ МЕНЕДЖЕРЫ
# ==============================================================================


@contextmanager
def tempdir(prefix: str = "hlsfield_"):
    """Контекстный менеджер для временных директорий"""
    temp_path = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        logger.debug(f"Created temporary directory: {temp_path}")
        yield temp_path
    finally:
        try:
            shutil.rmtree(temp_path, ignore_errors=True)
            logger.debug(f"Cleaned up temporary directory: {temp_path}")
        except Exception as e:
            logger.warning(f"Could not clean up temporary directory {temp_path}: {e}")


def ensure_binary_available(binary_name: str, path: str) -> str:
    """Проверяет доступность бинарного файла"""
    if os.path.isabs(path) and os.path.isfile(path) and os.access(path, os.X_OK):
        return path

    full_path = shutil.which(path)
    if full_path:
        return full_path

    raise FFmpegNotFoundError(f"{binary_name} not found: {path}")


# ==============================================================================
# ВЫПОЛНЕНИЕ КОМАНД FFMPEG
# ==============================================================================


def run(cmd: List[str], timeout_sec: Optional[int] = None) -> subprocess.CompletedProcess:
    """Выполняет команду с обработкой ошибок и таймаутами"""
    if not cmd:
        raise ValueError("Command cannot be empty")

    # Добавить проверку на безопасность команд
    if any(dangerous in str(cmd) for dangerous in ['rm -rf', '>', '>>', '&', '|', ';']):
        raise SecurityError("Potentially dangerous command detected")

    # Проверяем бинарные файлы только для FFmpeg команд
    if cmd[0] in [defaults.FFMPEG, defaults.FFPROBE, 'ffmpeg', 'ffprobe']:
        binary_path = ensure_binary_available(cmd[0], cmd[0])
        cmd[0] = binary_path
    else:
        # Для других команд просто проверяем что они доступны
        # Специальная обработка для встроенных команд shell (echo, dir, etc.)
        builtin_commands = ['echo', 'dir', 'type', 'copy', 'move', 'del']

        if cmd[0].lower() in builtin_commands:
            # Для встроенных команд используем shell=True в subprocess
            pass  # Оставляем команду как есть
        else:
            binary_path = shutil.which(cmd[0])
            if not binary_path:
                raise FileNotFoundError(f"Command not found: {cmd[0]}")
            cmd[0] = binary_path

    if timeout_sec is None:
        timeout_sec = defaults.FFMPEG_TIMEOUT

    cmd_str = " ".join(cmd)
    logger.debug(f"Executing command: {cmd_str}")

    start_time = time.time()

    # Определяем нужен ли shell для встроенных команд
    builtin_commands = ['echo', 'dir', 'type', 'copy', 'move', 'del']
    use_shell = cmd[0].lower() in builtin_commands

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_sec, check=False, shell=use_shell,
            encoding='utf-8',  # Явно указываем кодировку UTF-8
        )

        elapsed = time.time() - start_time
        logger.debug(f"Command completed in {elapsed:.2f}s with code {result.returncode}")

        if defaults.VERBOSE_LOGGING:
            if result.stdout:
                logger.debug(f"STDOUT: {result.stdout}")
            if result.stderr:
                logger.debug(f"STDERR: {result.stderr}")

        if result.returncode != 0:
            _handle_ffmpeg_error(cmd, result.returncode, result.stdout, result.stderr)

        return result

    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout_sec}s: {cmd_str}")
        raise TimeoutError(f"Command timed out after {timeout_sec} seconds", timeout_sec) from e

    except FileNotFoundError as e:
        raise FFmpegNotFoundError(cmd[0]) from e

    except Exception as e:
        logger.error(f"Unexpected error running command {cmd_str}: {e}")
        raise FFmpegError(cmd, -1, "", str(e)) from e


def _handle_ffmpeg_error(cmd: List[str], returncode: int, stdout: str, stderr: str):
    """Анализирует ошибки FFmpeg"""
    error_message = stderr.lower()

    if "no such file or directory" in error_message:
        raise InvalidVideoError("Input file not found or inaccessible")
    if "invalid data found" in error_message or "moov atom not found" in error_message:
        raise InvalidVideoError("File is corrupted or not a valid video")
    if "permission denied" in error_message:
        raise StorageError("Permission denied accessing file")
    if "no space left" in error_message or "disk full" in error_message:
        raise StorageError("Insufficient disk space")
    if "unknown encoder" in error_message or "encoder not found" in error_message:
        raise ConfigurationError("Required encoder not available in FFmpeg")

    raise FFmpegError(cmd, returncode, stdout, stderr)


# ==============================================================================
# АНАЛИЗ ВИДЕОФАЙЛОВ
# ==============================================================================


def ffprobe_streams(input_path: Union[str, Path]) -> Dict[str, Any]:
    """Анализирует видеофайл и возвращает информацию о потоках"""
    cmd = [
        defaults.FFPROBE,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(input_path),
    ]

    try:
        result = run(cmd, timeout_sec=30)
        data = json.loads(result.stdout)

        if "streams" not in data:
            raise InvalidVideoError("No streams found in video file")

        return data

    except FFmpegError as e:
        if "Invalid data found" in str(e):
            raise InvalidVideoError("File is not a valid video or is corrupted") from e
        elif "No such file" in str(e):
            raise InvalidVideoError(f"Video file not found: {input_path}") from e
        else:
            raise InvalidVideoError(f"Cannot analyze video file: {e}") from e


def pick_video_audio_streams(info: Dict[str, Any]) -> tuple[Optional[Dict], Optional[Dict]]:
    """Выбирает основные видео и аудио потоки"""
    video_stream = None
    audio_stream = None

    streams = info.get("streams", [])

    for stream in streams:
        codec_type = stream.get("codec_type")

        if codec_type == "video" and video_stream is None:
            video_stream = stream

        if codec_type == "audio" and audio_stream is None:
            audio_stream = stream

    return video_stream, audio_stream


def get_video_info_quick(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Быстро получает основную информацию о видео"""
    try:
        cmd = [
            defaults.FFPROBE,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            str(file_path),
        ]

        result = run(cmd, timeout_sec=15)
        data = json.loads(result.stdout)
        format_info = data.get("format", {})

        return {
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "bitrate": int(format_info.get("bit_rate", 0)),
            "format_name": format_info.get("format_name", "unknown"),
            "nb_streams": int(format_info.get("nb_streams", 0)),
        }

    except Exception as e:
        logger.warning(f"Quick video info failed: {e}")
        return {
            "duration": 0,
            "size": 0,
            "bitrate": 0,
            "format_name": "unknown",
            "nb_streams": 0,
        }


# ==============================================================================
# ИЗВЛЕЧЕНИЕ ПРЕВЬЮ
# ==============================================================================


def extract_preview(
    input_path: Path,
    out_image: Path,
    at_sec: float = 3.0,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Path:
    """Извлекает превью кадр из видео"""
    max_attempts = 3
    attempt_times = [at_sec, 1.0, 0.0]

    for attempt in range(max_attempts):
        try:
            seek_time = attempt_times[attempt] if attempt < len(attempt_times) else attempt

            cmd = [
                defaults.FFMPEG,
                "-y",
                "-ss",
                str(seek_time),
                "-i",
                str(input_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                "-f",
                "image2",
            ]

            if width or height:
                if width and height:
                    scale = f"scale={width}:{height}"
                elif width:
                    scale = f"scale={width}:-1"
                else:
                    scale = f"scale=-1:{height}"
                cmd.extend(["-vf", scale])

            cmd.append(str(out_image))

            run(cmd, timeout_sec=60)

            if out_image.exists() and out_image.stat().st_size > 100:
                logger.debug(f"Preview extracted at {seek_time}s on attempt {attempt + 1}")
                return out_image
            else:
                logger.warning(f"Preview file too small on attempt {attempt + 1}")

        except Exception as e:
            logger.warning(f"Preview extraction attempt {attempt + 1} failed: {e}")

            if out_image.exists():
                try:
                    out_image.unlink()
                except:
                    pass

    raise TranscodingError(f"Failed to extract preview after {max_attempts} attempts")


# ==============================================================================
# ОПТИМИЗИРОВАННЫЙ ТРАНСКОДИНГ - НОВЫЙ КОД
# ==============================================================================

class StreamFormat(Enum):
    HLS = "hls"
    DASH = "dash"

class TranscodingConfig:
    """Конфигурация для транскодирования"""
    def __init__(self, format_type: StreamFormat, segment_duration: int = 6):
        self.format_type = format_type
        self.segment_duration = segment_duration

        # Настройки по умолчанию для каждого формата
        if format_type == StreamFormat.HLS:
            self.segment_duration = segment_duration
            self.file_extension = "ts"
            self.container_format = "hls"
            self.segment_type = "mpegts"
        elif format_type == StreamFormat.DASH:
            self.segment_duration = max(2, segment_duration - 2)
            self.file_extension = "m4s"
            self.container_format = "dash"
            self.segment_type = "mp4"

def _prepare_transcoding(input_path: Path, ladder: List[Dict]) -> Tuple[Dict, Dict, int, List[Dict]]:
    """Общая подготовка для любого типа транскодирования"""
    from .fields import validate_ladder

    validate_ladder(ladder)

    info = ffprobe_streams(input_path)
    video_stream, audio_stream = pick_video_audio_streams(info)

    if not video_stream:
        raise InvalidVideoError("No video stream found in input file")

    has_audio = audio_stream is not None
    source_height = int(video_stream.get("height", 0))
    filtered_ladder = _filter_ladder_by_source(ladder, source_height)

    return video_stream, audio_stream, source_height, filtered_ladder

def _build_base_ffmpeg_command(
    input_path: Path,
    rung: Dict,
    has_audio: bool,
    config: TranscodingConfig
) -> List[str]:
    """Строит базовую команду FFmpeg, общую для HLS и DASH"""
    height = int(rung["height"])
    v_bitrate = int(rung["v_bitrate"])
    a_bitrate = int(rung["a_bitrate"]) if has_audio else 0

    cmd = [
        defaults.FFMPEG,
        "-y",
        "-i", str(input_path),
        "-map", "0:v:0",
    ]

    # Видео фильтры и кодирование
    vf_parts = [
        f"scale=w=-2:h={height}:force_original_aspect_ratio=decrease",
        "pad=ceil(iw/2)*2:ceil(ih/2)*2",
    ]

    cmd.extend([
        "-vf", ",".join(vf_parts),
        "-c:v", "libx264",
        "-profile:v", defaults.H264_PROFILE,
        "-preset", defaults.FFMPEG_PRESET,
        "-b:v", f"{v_bitrate}k",
        "-maxrate", f"{int(v_bitrate * 1.07)}k",
        "-bufsize", f"{v_bitrate * 2}k",
        "-pix_fmt", defaults.PIXEL_FORMAT,
        "-g", str(config.segment_duration * 30),
        "-keyint_min", str(config.segment_duration * 30),
        "-sc_threshold", "0",
    ])

    # Аудио
    if has_audio and a_bitrate > 0:
        cmd.extend([
            "-map", "0:a:0",
            "-c:a", defaults.AUDIO_CODEC,
            "-b:a", f"{a_bitrate}k",
            "-ac", str(defaults.AUDIO_CHANNELS),
            "-ar", str(defaults.AUDIO_SAMPLE_RATE),
        ])
    else:
        cmd.append("-an")

    return cmd

def _create_hls_variant(
    input_path: Path,
    out_dir: Path,
    rung: Dict,
    config: TranscodingConfig,
    has_audio: bool
) -> Dict:
    """Создает один вариант качества HLS"""
    height = int(rung["height"])
    v_bitrate = int(rung["v_bitrate"])
    a_bitrate = int(rung["a_bitrate"]) if has_audio else 0

    variant_dir = out_dir / f"v{height}"
    variant_dir.mkdir(exist_ok=True)
    playlist_file = variant_dir / "index.m3u8"

    # Базовая команда
    cmd = _build_base_ffmpeg_command(input_path, rung, has_audio, config)

    # HLS-специфичные параметры
    cmd.extend([
        "-f", "hls",
        "-hls_time", str(config.segment_duration),
        "-hls_playlist_type", "vod",
        "-hls_segment_type", "mpegts",
        "-hls_segment_filename", str(variant_dir / "seg_%04d.ts"),
        "-hls_flags", "single_file+independent_segments",
        str(playlist_file),
    ])

    run(cmd, timeout_sec=600)

    # Валидация результата
    if not playlist_file.exists():
        raise TranscodingError(f"HLS playlist not created: {playlist_file}")

    segment_files = list(variant_dir.glob("seg_*.ts"))
    if not segment_files:
        raise TranscodingError(f"No HLS segments created in {variant_dir}")

    approx_width = int((height * 16 / 9) // 2 * 2)

    return {
        "height": height,
        "width": approx_width,
        "bandwidth": (v_bitrate + a_bitrate) * 1000,
        "playlist": playlist_file.name,
        "dir": variant_dir.name,
        "resolution": f"{approx_width}x{height}",
        "segments_count": len(segment_files),
    }

def _create_dash_variants(
    input_path: Path,
    out_dir: Path,
    filtered_ladder: List[Dict],
    config: TranscodingConfig,
    has_audio: bool
) -> Path:
    """Создает все варианты DASH одной командой"""
    manifest_file = out_dir / "manifest.mpd"

    cmd = [defaults.FFMPEG, "-y", "-i", str(input_path)]

    # Для каждого качества создаем отдельный поток
    for i, rung in enumerate(filtered_ladder):
        height = int(rung["height"])
        v_bitrate = int(rung["v_bitrate"])

        cmd.extend([
            "-map", "0:v:0",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-profile:v", "main",
            "-b:v", f"{v_bitrate}k",
            "-maxrate", f"{int(v_bitrate * 1.07)}k",
            "-bufsize", f"{v_bitrate * 2}k",
            "-vf", f"scale=-2:{height}",
            "-pix_fmt", "yuv420p",
        ])

        if has_audio:
            a_bitrate = int(rung["a_bitrate"])
            cmd.extend([
                "-map", "0:a:0",
                "-c:a", "aac",
                "-b:a", f"{a_bitrate}k",
                "-ac", "2",
                "-ar", "48000",
            ])

    # DASH параметры
    cmd.extend([
        "-f", "dash",
        "-seg_duration", str(config.segment_duration),
        "-use_template", "1",
        "-use_timeline", "1",
        "-init_seg_name", str(out_dir / "init_$RepresentationID$.m4s"),
        "-media_seg_name", str(out_dir / "chunk_$RepresentationID$_$Number%05d$.m4s"),
        "-adaptation_sets", "id=0,streams=v id=1,streams=a" if has_audio else "id=0,streams=v",
        str(manifest_file)
    ])

    run(cmd, timeout_sec=900)

    # Валидация результата
    if not manifest_file.exists():
        raise TranscodingError("DASH manifest not created")

    segment_files = list(out_dir.glob("chunk_*.m4s"))
    init_files = list(out_dir.glob("init_*.m4s"))

    if not segment_files and not init_files:
        raise TranscodingError("No DASH segments created")

    logger.info(f"DASH created with {len(segment_files)} segments and {len(init_files)} init files")
    return manifest_file

def _create_master_playlist(out_dir: Path, variants: List[Dict]) -> Path:
    """Создает master.m3u8 плейлист для HLS"""
    master_file = out_dir / "master.m3u8"

    lines = ["#EXTM3U", "#EXT-X-VERSION:3"]
    sorted_variants = sorted(variants, key=lambda x: x["height"])

    for variant in sorted_variants:
        stream_inf = f"#EXT-X-STREAM-INF:BANDWIDTH={variant['bandwidth']}"
        stream_inf += f",RESOLUTION={variant['resolution']}"
        stream_inf += f',CODECS="avc1.42E01E,mp4a.40.2"'

        lines.append(stream_inf)
        lines.append(f"{variant['dir']}/{variant['playlist']}")

    master_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return master_file

def transcode_variants(
    input_path: Path,
    out_dir: Path,
    ladder: List[Dict],
    format_type: StreamFormat,
    segment_duration: int = 6
) -> Path:
    """Универсальная функция транскодирования для HLS или DASH"""
    try:
        config = TranscodingConfig(format_type, segment_duration)
        out_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Analyzing input video: {input_path}")
        video_stream, audio_stream, source_height, filtered_ladder = _prepare_transcoding(input_path, ladder)

        has_audio = audio_stream is not None
        logger.info(f"Transcoding {len(filtered_ladder)} {format_type.value.upper()} variants")

        if format_type == StreamFormat.HLS:
            return _transcode_hls(input_path, out_dir, filtered_ladder, config, has_audio)
        elif format_type == StreamFormat.DASH:
            return _transcode_dash(input_path, out_dir, filtered_ladder, config, has_audio)

    except Exception as e:
        logger.error(f"{format_type.value.upper()} transcoding failed: {e}")
        if isinstance(e, (TranscodingError, ConfigurationError, InvalidVideoError)):
            raise
        raise TranscodingError(f"{format_type.value.upper()} transcoding failed: {e}") from e

def _transcode_hls(
    input_path: Path,
    out_dir: Path,
    filtered_ladder: List[Dict],
    config: TranscodingConfig,
    has_audio: bool
) -> Path:
    """Внутренняя функция для HLS транскодирования"""
    variant_infos = []

    for rung in filtered_ladder:
        try:
            variant_info = _create_hls_variant(input_path, out_dir, rung, config, has_audio)
            variant_infos.append(variant_info)
            logger.info(f"Created HLS variant: {variant_info['height']}p")
        except Exception as e:
            logger.error(f"Failed to create {rung['height']}p HLS variant: {e}")
            continue

    if not variant_infos:
        raise TranscodingError("No HLS variants were successfully created")

    master_playlist = _create_master_playlist(out_dir, variant_infos)
    logger.info(f"HLS master playlist created: {master_playlist}")
    return master_playlist

def _transcode_dash(
    input_path: Path,
    out_dir: Path,
    filtered_ladder: List[Dict],
    config: TranscodingConfig,
    has_audio: bool
) -> Path:
    """Внутренняя функция для DASH транскодирования"""
    return _create_dash_variants(input_path, out_dir, filtered_ladder, config, has_audio)


# ==============================================================================
# ПУБЛИЧНЫЕ ФУНКЦИИ (обратная совместимость)
# ==============================================================================

def transcode_hls_variants(
    input_path: Path, out_dir: Path, ladder: List[Dict], segment_duration: int = 6
) -> Path:
    """Создает HLS адаптивный стрим"""
    return transcode_variants(input_path, out_dir, ladder, StreamFormat.HLS, segment_duration)

def transcode_dash_variants(
    input_path: Path, out_dir: Path, ladder: List[Dict], segment_duration: int = 4
) -> Path:
    """Создает DASH адаптивный стрим"""
    return transcode_variants(input_path, out_dir, ladder, StreamFormat.DASH, segment_duration)

def transcode_adaptive_variants(
    input_path: Path, out_dir: Path, ladder: List[Dict], segment_duration: int = 6
) -> Dict[str, Path]:
    """Создает одновременно HLS и DASH стримы"""
    try:
        out_dir.mkdir(parents=True, exist_ok=True)

        hls_dir = out_dir / "hls"
        dash_dir = out_dir / "dash"

        logger.info(f"Starting adaptive transcoding (HLS + DASH) for {input_path.name}")

        # Создаем HLS
        logger.info("Creating HLS stream...")
        hls_master = transcode_variants(input_path, hls_dir, ladder, StreamFormat.HLS, segment_duration)

        # Создаем DASH
        logger.info("Creating DASH stream...")
        dash_segment_duration = max(2, segment_duration - 2)
        dash_manifest = transcode_variants(input_path, dash_dir, ladder, StreamFormat.DASH, dash_segment_duration)

        logger.info("Adaptive transcoding completed successfully")

        return {
            "hls_master": hls_master,
            "dash_manifest": dash_manifest,
            "hls_dir": hls_dir,
            "dash_dir": dash_dir,
        }

    except Exception as e:
        logger.error(f"Adaptive transcoding failed: {e}")
        if isinstance(e, (TranscodingError, ConfigurationError, InvalidVideoError)):
            raise
        raise TranscodingError(f"Adaptive transcoding failed: {e}") from e


# ==============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==============================================================================

def _filter_ladder_by_source(ladder: List[Dict], source_height: int) -> List[Dict]:
    """Фильтрует лестницу качеств по исходному разрешению"""
    filtered = [r for r in ladder if r["height"] <= source_height * 1.1]

    if not filtered:
        filtered = [min(ladder, key=lambda x: x["height"])]
        logger.warning(f"All ladder heights exceed source {source_height}p, using lowest")

    return sorted(filtered, key=lambda x: x["height"])

def _cleanup_dash_files_from_current_dir():
    """Очищает лишние DASH файлы из текущей директории"""
    # Заглушка для совместимости с существующим кодом
    pass

def analyze_video_complexity(input_path: Path) -> Dict[str, Any]:
    """Анализирует сложность видео для оптимизации битрейта"""
    # Заглушка для функции из tasks.py
    return {
        "duration": 0,
        "complexity": "medium",
        "motion_level": 0.5,
        "detail_level": 0.5,
    }


# ==============================================================================
# РАБОТА СО STORAGE
# ==============================================================================


def pull_to_local(storage, name: str, dst_dir: Path) -> Path:
    """Загружает файл из storage в локальную директорию"""
    try:
        # Прямой путь для локального storage
        try:
            direct_path = Path(storage.path(name))
            if direct_path.exists() and direct_path.is_file():
                logger.debug(f"Using direct file access: {direct_path}")
                return direct_path
        except (AttributeError, NotImplementedError):
            pass

        # Копирование через storage API
        dst = dst_dir / Path(name).name
        logger.debug(f"Downloading {name} to {dst}")

        with storage.open(name, "rb") as src:
            with dst.open("wb") as out:
                shutil.copyfileobj(src, out, length=defaults.MAX_FILE_SIZE)

        if not dst.exists() or dst.stat().st_size == 0:
            raise StorageError(f"Downloaded file is empty: {dst}")

        logger.debug(f"Successfully downloaded {dst.stat().st_size} bytes")
        return dst

    except Exception as e:
        logger.error(f"Error pulling file {name}: {e}")
        if "dst" in locals() and dst.exists():
            try:
                dst.unlink()
            except:
                pass
        if isinstance(e, StorageError):
            raise
        raise StorageError(f"Cannot download file {name}: {e}") from e


def save_tree_to_storage(local_root: Path, storage, base_path: str) -> List[str]:
    """Рекурсивно сохраняет дерево файлов в storage"""
    saved_paths = []

    try:
        for root, dirs, files in os.walk(local_root):
            for filename in files:
                local_file_path = Path(root) / filename
                rel_path = local_file_path.relative_to(local_root)
                storage_key = f"{base_path.rstrip('/')}/{str(rel_path).replace(os.sep, '/')}"

                logger.debug(f"Saving {local_file_path} -> {storage_key}")

                try:
                    with local_file_path.open("rb") as fh:
                        saved_name = storage.save(storage_key, fh)
                        saved_paths.append(saved_name)
                except Exception as e:
                    logger.error(f"Failed to save {storage_key}: {e}")
                    raise StorageError(f"Cannot save file {storage_key}: {e}") from e

        logger.info(f"Saved {len(saved_paths)} files to storage under {base_path}")
        return saved_paths

    except Exception as e:
        logger.error(f"Error saving file tree: {e}")
        if isinstance(e, StorageError):
            raise
        raise StorageError(f"Cannot save file tree: {e}") from e


# ==============================================================================
# ВАЛИДАЦИЯ
# ==============================================================================


def validate_video_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Выполняет базовую валидацию видеофайла"""
    path = Path(file_path)

    validation = {"valid": False, "issues": [], "warnings": [], "info": {}}

    # Проверяем существование файла
    if not path.exists():
        validation["issues"].append("File does not exist")
        return validation

    # Проверяем размер файла
    size = path.stat().st_size
    validation["info"]["size"] = size

    if size < defaults.MIN_FILE_SIZE:
        validation["issues"].append(f"File too small: {size} bytes")

    if size > defaults.MAX_FILE_SIZE:
        validation["issues"].append(f"File too large: {size} bytes")

    # Проверяем расширение
    ext = path.suffix.lower()
    validation["info"]["extension"] = ext

    if ext not in defaults.ALLOWED_EXTENSIONS:
        validation["issues"].append(f"Unsupported file extension: {ext}")

    # Анализируем через FFprobe
    try:
        info = ffprobe_streams(path)
        video_stream, audio_stream = pick_video_audio_streams(info)

        validation["info"]["has_video"] = video_stream is not None
        validation["info"]["has_audio"] = audio_stream is not None

        if video_stream:
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))

            validation["info"]["width"] = width
            validation["info"]["height"] = height
            validation["info"]["codec"] = video_stream.get("codec_name", "unknown")

            if height < defaults.MIN_VIDEO_HEIGHT:
                validation["issues"].append(f"Height too small: {height}p")
            if height > defaults.MAX_VIDEO_HEIGHT:
                validation["issues"].append(f"Height too large: {height}p")
            if width % 2 != 0 or height % 2 != 0:
                validation["warnings"].append("Odd dimensions may cause encoding issues")
        else:
            validation["issues"].append("No video stream found")

        # Проверяем длительность
        if format_info := info.get("format"):
            try:
                duration = float(format_info.get("duration", 0))
                validation["info"]["duration"] = duration
                if duration > defaults.MAX_VIDEO_DURATION:
                    validation["issues"].append(f"Video too long: {duration}s")
            except (ValueError, TypeError):
                validation["warnings"].append("Could not determine video duration")

    except Exception as e:
        validation["issues"].append(f"Cannot analyze video: {e}")

    validation["valid"] = len(validation["issues"]) == 0
    return validation


# ==============================================================================
# ЭКСПОРТ ФУНКЦИЙ
# ==============================================================================

__all__ = [
    # Контекстные менеджеры
    "tempdir",
    # Выполнение команд
    "run",
    "ensure_binary_available",
    # Анализ видео
    "ffprobe_streams",
    "pick_video_audio_streams",
    "get_video_info_quick",
    # Превью
    "extract_preview",
    # Транскодинг
    "transcode_hls_variants",
    "transcode_dash_variants",
    "transcode_adaptive_variants",
    # Storage
    "pull_to_local",
    "save_tree_to_storage",
    # Валидация
    "validate_video_file",
]
