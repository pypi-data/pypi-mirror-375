#!/usr/bin/env python

import logging
import os
from pathlib import Path

import typer
from pytubefix import Stream, YouTube

# configure typer cli app
app = typer.Typer(add_completion=False)

# configure logger
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger = logging.getLogger("tubed")


@app.command()
def tubed(
    url: str = typer.Option(
        default=None,
        help="A YouTube watch URL.",
    ),
    url_file: Path = typer.Option(
        default=None,
        help="Path to a file containing YouTube watch URLs.",
    ),
    output_path: Path = typer.Option(
        default="./output",
        help="An output path.",
    ),
    only_audio: bool = typer.Option(
        default=False,
        help="Whether to exclude video.",
    ),
) -> None:
    """YouTube downloader."""

    if not url and not url_file:
        logger.error("One of 'url' or 'url-path' options must be set")
        raise typer.Abort()

    if url:
        stream = _get_stream(url=url, only_audio=only_audio)
        logger.info(f"Downloading: '{stream.title}'")
        stream.download(output_path=output_path)
        return

    if not url_file.exists():
        logger.error(f"The url file '{url_file}' doesn't exist")
        raise typer.Abort()

    if not url_file.is_file():
        logger.error(f"The url file '{url_file}' isn't a regular file")
        raise typer.Abort()

    for url in url_file.read_text().splitlines():
        stream = _get_stream(url=url, only_audio=only_audio)
        logger.info(f"Downloading: '{stream.title}'")
        stream.download(output_path=output_path)


def _get_stream(
    url: str,
    only_audio: bool,
) -> Stream:
    """Get a stream given a YouTube watch URL.

    Args:
        url: A YouTube watch URL
        only_audio: Whether to exclude video

    Returns:
        A stream
    """

    logger.info(f"Processing url: '{url}'")
    yt = YouTube(url)
    return (
        yt.streams.get_audio_only()
        if only_audio
        else yt.streams.get_highest_resolution()
    )


if __name__ == "__main__":
    app()
