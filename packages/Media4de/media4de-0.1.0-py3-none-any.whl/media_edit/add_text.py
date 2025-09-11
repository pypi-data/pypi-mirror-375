import shutil
from pathlib import Path
from typing import List, Optional

from click import Option
import typer
from PIL import ImageFont, ImageDraw, Image

app = typer.Typer(
    add_completion=True, help="Add multiline text to an image with simple styling."
)


def add_text_to_image(
    text_to_add: List[str],
    image: Image.Image,
    *,
    x: int,
    y: int,
    font_size: int = 50,
    font_spacing: float = 1.25,
    fill_colour: str = "white",
    border_colour: str = "black",
    heading_font: str | Path = "SourceSans3-ExtraBold.ttf",
    body_font: str | Path = "SourceSans3-Regular.ttf",
    stroke_width: int = 4,
) -> Image.Image:
    """Draw lines of text on an image.

    Lines starting with '# ' are rendered with the heading font and ~15% larger size.

    If EIDF is specified as the fill colour then EIDF styling will be used.
    """
    if fill_colour.upper() == "EIDF":
        # Apply EIDF styling
        border_colour = "#2a3c46"
        fill_colour = "#2a3c46"

    draw = ImageDraw.Draw(image)
    heading_font_path = str(heading_font)
    body_font_path = str(body_font)
    for i, raw_line in enumerate(text_to_add):
        line = raw_line
        if raw_line.startswith("#"):
            line = raw_line.lstrip("# ")
            font = _safe_truetype(heading_font_path, int(font_size * 1.15))
        else:
            font = _safe_truetype(body_font_path, font_size)
        y_line = int(y + (i * font_size * font_spacing))
        draw.text(
            (x, y_line),
            line,
            font=font,
            fill=fill_colour,
            stroke_fill=border_colour,
            stroke_width=stroke_width,
        )
    return image


def add_text_from_file(
    image_path,
    text_file,
    *,
    output_path="output.txt",
    x,
    y,
    font_size,
    font_spacing,
    fill_colour,
    border_colour,
    heading_font,
    body_font,
    backup,
):
    if text_file is not None:
        file_text = text_file.read_text(encoding="utf-8")
    else:
        raise ValueError("No text or text file provided")

    add_text_from_list(
        file_text.splitlines(),
        image_path,
        output_path=output_path,
        x=x,
        y=y,
        font_size=font_size,
        font_spacing=font_spacing,
        fill_colour=fill_colour,
        border_colour=border_colour,
        heading_font=heading_font,
        body_font=body_font,
        backup=backup
    )


def add_text_from_list(
    image_path: Path,
    text: List[str],
    output_path: Path,
    x: Optional[int],
    y: Optional[int],
    font_size: Optional[int],
    font_spacing: Optional[float],
    fill_colour: Optional[str],
    border_colour: Optional[str],
    heading_font: Optional[Path],
    body_font: Optional[Path],
    backup: Optional[bool],
):

    with Image.open(image_path) as image:
        width, height = image.size
        fs = font_size if font_size is not None else int(width * 0.01)
        # Defaults: 5% left margin, 5% bottom margin minus text block height
        default_x = int(width * 0.05)
        block_height = int(fs * len(text) * font_spacing)
        default_y = int(height * 0.95) - block_height
        xi = x if x is not None else default_x
        yi = y if y is not None else default_y

        add_text_to_image(
            text,
            image,
            x=xi,
            y=yi,
            font_size=fs,
            font_spacing=font_spacing,
            fill_colour=fill_colour,
            border_colour=border_colour,
            heading_font=heading_font,
            body_font=body_font,
        )
        # Copy backup if requested
        if backup:
            try:
                shutil.copy(str(image_path), str(image_path) + ".backup")
            except OSError:
                # Non-fatal
                pass

        # Let PIL infer format from suffix if possible
        image.save(output_path)


OUTPUT_SIZE = (500, 220)
OUTPUT_MODE = "RGB"


@app.command()
def convert_image_for_xrdp_logo(
    image_path: Path = typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        help="Path to image to convert to xrdp logo format",
    ),
    output_path: Path = typer.Option(
        Path("output_for_xrdp.bmp"), help="Path to save the output bmp image"
    ),
):
    """Convert an image so that it can be used in place of the Logo in XRDP"""

    with Image.open(image_path) as image:
        image = image.convert(OUTPUT_MODE)
        image.thumbnail(OUTPUT_SIZE, Image.Resampling.LANCZOS)
        if output_path.suffix.lower() != ".bmp":
            output_path = output_path.with_suffix(".bmp")
        image.save(output_path, "bmp")


def _safe_truetype(font_path: str, size: int):
    """Attempt to load a TTF font, fall back to the default PIL font if unavailable."""
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.load_default()


@app.command()
def add_text(
    image_path: Path = typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the input image",
    ),
    text: List[str] = typer.Option(
        None,
        help="Text lines to add. Use multiple --text options for multiple lines. \
                Prefix with '# ' for a heading.",
    ),
    text_file: Optional[Path] = typer.Option(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to a text file with lines",
    ),
    output_path: Path = typer.Option(
        Path("output.bmp"),
        help="Path to save the output image (format inferred from extension)",
    ),
    x: Optional[int] = typer.Option(
        None,
        help="X coordinate for the left of the text block. Defaults to 5% off the left margin.",
    ),
    y: Optional[int] = typer.Option(
        None,
        help="Y coordinate for the top of the text block. Defaults to 5% off the bottom margin.",
    ),
    font_size: Optional[int] = typer.Option(
        None, help="Base font size in pixels. Defaults to 1% of image width."
    ),
    font_spacing: float = typer.Option(1.25, help="Line spacing multiplier"),
    fill_colour: str = typer.Option(
        "white",
        help="Fill colour for the text (name or #RRGGBB) (Use 'EIDF' to use EIDF colors)",
    ),
    border_colour: str = typer.Option(
        "black", help="Stroke/border colour for the text"
    ),
    heading_font: Path = typer.Option(
        Path("SourceSans3-ExtraBold.ttf"),
        help="TTF font file for headings. Defaults to UoE fonts",
    ),
    body_font: Path = typer.Option(
        Path("SourceSans3-Regular.ttf"),
        help="TTF font file for body text. Defaults to UoE fonts",
    ),
    backup: bool = typer.Option(
        True, help="Create a .backup copy of the original image. Defaults to True"
    ),
):
    """Add text to an image using the provided options."""
    # Build the lines to render
    if text is not None and len(text) > 0:
        add_text_from_list(
            image_path,
            text,
            output_path,
            x,
            y,
            font_size,
            font_spacing,
            fill_colour,
            border_colour,
            heading_font,
            body_font,
            backup,
        )
    elif text_file is not None:
        add_text_from_file(
            image_path,
            text_file,
            output_path,
            x,
            y,
            font_size,
            font_spacing,
            fill_colour,
            border_colour,
            heading_font,
            body_font,
            backup,
        )
    else:
        raise typer.BadParameter("Either --text or --text-file must be provided")


if __name__ == "__main__":
    app()
