import asyncio
import shutil
import subprocess
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from fastmcp import Context

# Global cache to avoid repeatedly checking FFmpeg
FFMPEG_CHECK_CACHE = {
    "checked": False,
    "result": None,
    "timestamp": 0
}

# Tool to check FFmpeg installation
async def check_ffmpeg_installed_impl(ctx: Optional[Context] = None) -> Dict[str, Any]:
    """
    Checks if FFmpeg is installed and accessible in the system PATH.

    Args:
        ctx: Optional Context for logging.

    Returns:
        A dictionary indicating FFmpeg status.
        Example: {"installed": True, "version": "ffmpeg version ..."} or
                 {"installed": False, "error": "FFmpeg not found."}
    """
    # Use cached result if available and less than 10 minutes old
    current_time = time.time()
    if FFMPEG_CHECK_CACHE["checked"] and (current_time - FFMPEG_CHECK_CACHE["timestamp"] < 600):
        if ctx:
            await ctx.info("Using cached FFmpeg check result")
        return FFMPEG_CHECK_CACHE["result"]

    # Skip actual check if the environment variable is set and we're just initializing
    if os.environ.get("MCP_SKIP_FFMPEG_CHECK_ON_INIT", "").lower() in ("true", "1", "yes"):
        # Just assume it's installed for tool listing purposes
        # The actual check will happen when the tool is called
        stub_result = {"installed": True, "version": "FFmpeg (details will be available when tool is called)"}
        FFMPEG_CHECK_CACHE["checked"] = True
        FFMPEG_CHECK_CACHE["result"] = stub_result
        FFMPEG_CHECK_CACHE["timestamp"] = current_time
        return stub_result

    if ctx:
        await ctx.info("Checking if FFmpeg is installed...")
    try:
        # Set a timeout to prevent hanging
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-version",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Use asyncio.wait_for to set a timeout
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)
        except asyncio.TimeoutError:
            if process:
                process.kill()
            if ctx:
                await ctx.error("FFmpeg check timed out after 5 seconds")
            result = {"installed": False, "error": "FFmpeg check timed out - may be installed but not responding quickly"}
            FFMPEG_CHECK_CACHE["checked"] = True
            FFMPEG_CHECK_CACHE["result"] = result
            FFMPEG_CHECK_CACHE["timestamp"] = current_time
            return result

        if process.returncode == 0:
            # FFmpeg typically prints version info to stdout or stderr
            version_info = stdout.decode(errors='replace').strip() or stderr.decode(errors='replace').strip()
            first_line = version_info.splitlines()[0] if version_info else "Unknown version"
            if ctx:
                await ctx.info(f"FFmpeg found: {first_line}")
            result = {"installed": True, "version": first_line}
            FFMPEG_CHECK_CACHE["checked"] = True
            FFMPEG_CHECK_CACHE["result"] = result
            FFMPEG_CHECK_CACHE["timestamp"] = current_time
            return result
        else:
            error_message = stderr.decode(errors='replace').strip() or stdout.decode(errors='replace').strip()
            if ctx:
                await ctx.error(f"FFmpeg command failed: {error_message}")
            result = {"installed": False, "error": f"FFmpeg found but version command failed: {error_message}"}
            FFMPEG_CHECK_CACHE["checked"] = True
            FFMPEG_CHECK_CACHE["result"] = result
            FFMPEG_CHECK_CACHE["timestamp"] = current_time
            return result
    except FileNotFoundError:
        if ctx:
            await ctx.error("FFmpeg not found in system PATH")
        result = {"installed": False, "error": "FFmpeg not found in system PATH."}
        FFMPEG_CHECK_CACHE["checked"] = True
        FFMPEG_CHECK_CACHE["result"] = result
        FFMPEG_CHECK_CACHE["timestamp"] = current_time
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Error checking FFmpeg: {str(e)}")
        result = {"installed": False, "error": f"An unexpected error occurred: {str(e)}"}
        FFMPEG_CHECK_CACHE["checked"] = True
        FFMPEG_CHECK_CACHE["result"] = result
        FFMPEG_CHECK_CACHE["timestamp"] = current_time
        return result

# Tool to convert video
async def convert_video_impl(
    input_file_path_str: str,
    output_format: str,
    ctx: Optional[Context] = None,
    quality: Optional[str] = None,
    framerate: Optional[int] = None
) -> Dict[str, Any]:
    """
    Converts a video file to the specified output format using FFmpeg.

    Args:
        input_file_path_str: The absolute path to the input video file.
        output_format: The desired output format (e.g., "mp4", "webm", "mov").
        ctx: Optional Context for reporting progress.
        quality: Optional quality setting ("low", "medium", "high").
        framerate: Optional framerate for video output.

    Returns:
        A dictionary with the conversion status and output file path if successful.
    """
    input_file_path = Path(input_file_path_str).resolve()
    if not input_file_path.is_file():
        return {"success": False, "error": f"Input file not found: {input_file_path_str}"}

    # Basic check for supported output format (can be expanded)
    supported_video_formats = [
        "mp4", "webm", "mov", "avi", "mkv", "flv", "gif", "mp3", "wav", "ogg", "aac",
        "m4a", "webp", "jpg", "png", "bmp", "tiff"
    ]
    
    if output_format.lower() not in supported_video_formats:
        return {
            "success": False,
            "error": f"Unsupported output format: {output_format}. Supported formats: {', '.join(supported_video_formats)}",
        }

    output_dir = input_file_path.parent / "converted_videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Construct output filename, ensuring it's unique if input has same name
    base_name = input_file_path.stem
    output_file_name = f"{base_name}_converted.{output_format.lower()}"
    output_file_path = output_dir / output_file_name
    
    # Handle potential filename collision (simple approach)
    counter = 1
    while output_file_path.exists():
        output_file_name = f"{base_name}_converted_{counter}.{output_format.lower()}"
        output_file_path = output_dir / output_file_name
        counter += 1

    # FFmpeg command base
    ffmpeg_command = ["ffmpeg", "-y", "-i", str(input_file_path)]
    
    # Add quality settings if provided
    if quality:
        if quality == "high":
            # High quality settings
            if output_format in ["mp4", "mkv", "webm", "mov"]:
                ffmpeg_command.extend(["-crf", "18"])  # Lower CRF means higher quality
            elif output_format in ["mp3", "ogg", "m4a"]:
                ffmpeg_command.extend(["-b:a", "320k"])  # Higher bitrate for audio
        elif quality == "medium":
            # Medium quality settings
            if output_format in ["mp4", "mkv", "webm", "mov"]:
                ffmpeg_command.extend(["-crf", "23"])  # Default for x264
            elif output_format in ["mp3", "ogg", "m4a"]:
                ffmpeg_command.extend(["-b:a", "192k"])
        elif quality == "low":
            # Low quality settings
            if output_format in ["mp4", "mkv", "webm", "mov"]:
                ffmpeg_command.extend(["-crf", "28"])  # Higher CRF means lower quality
            elif output_format in ["mp3", "ogg", "m4a"]:
                ffmpeg_command.extend(["-b:a", "128k"])  # Lower bitrate for audio
    
    # Add framerate settings if provided
    if framerate and output_format in ["mp4", "mkv", "webm", "mov", "avi", "flv"]:
        ffmpeg_command.extend(["-r", str(framerate)])
    
    # Add output file path
    ffmpeg_command.append(str(output_file_path))

    try:
        if ctx:
            await ctx.info(f"Converting file: {input_file_path_str} to {output_format}")
            await ctx.report_progress(progress=10, total=100)

        # Create the output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        if ctx:
            await ctx.info(f"Starting FFmpeg conversion process")
            await ctx.info(f"Command: {' '.join(ffmpeg_command)}")
            await ctx.report_progress(progress=20, total=100)

        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if ctx:
            await ctx.info("FFmpeg process started")
            await ctx.report_progress(progress=30, total=100)

        stdout, stderr = await process.communicate()

        if ctx:
            await ctx.info("FFmpeg process completed")
            await ctx.report_progress(progress=90, total=100)

        if process.returncode == 0:
            if ctx:
                await ctx.info(f"Conversion successful: {output_file_path}")
                await ctx.report_progress(progress=100, total=100)

            # Verify the output file exists and has content
            if not output_file_path.exists():
                error_msg = "Output file was not created despite successful return code"
                if ctx:
                    await ctx.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                }

            if output_file_path.stat().st_size == 0:
                error_msg = "Output file was created but is empty"
                if ctx:
                    await ctx.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                }

            return {
                "success": True,
                "output_file_path": str(output_file_path),
                "message": "Video converted successfully."
            }
        else:
            error_message = stderr.decode(errors='replace').strip()
            if ctx:
                await ctx.error(f"FFmpeg conversion failed: {error_message}")

            return {
                "success": False,
                "error": f"FFmpeg conversion failed. Return code: {process.returncode}. Error: {error_message}",
                "command": " ".join(ffmpeg_command)  # For debugging
            }
    except FileNotFoundError:
        error_msg = "FFmpeg not found. Please ensure it's installed and in PATH."
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"An error occurred during conversion: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}

# Get list of supported formats
async def get_supported_formats_impl(ctx: Optional[Context] = None) -> Dict[str, Any]:
    """
    Returns a list of supported formats for conversion.

    Args:
        ctx: Optional Context for logging.

    Returns:
        A dictionary with lists of supported formats by category.
    """
    if ctx:
        await ctx.info("Retrieving supported formats...")
    return {
        "success": True,
        "formats": {
            "video": ["mp4", "webm", "mov", "avi", "mkv", "flv", "gif"],
            "audio": ["mp3", "wav", "ogg", "aac", "m4a"],
            "image": ["webp", "jpg", "png", "bmp", "tiff"],
        }
    }