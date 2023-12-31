"""Click CLI for generating resource packs from a texture."""
import json
from pathlib import Path

import click
from PIL import Image, UnidentifiedImageError

from generators import (
    brightness,
    generate_separators,
    generate_tab_sprites,
    tab_sprites_mcmeta,
)

# Starting with pack format 13, extra sprites are needed for the overhauled Create World page
CREATE_OVERHAUL_FORMAT = 13

# Starting with pack format 16, sprites are split up and included in a sprites/ folder
SPRITES_FOLDER_FORMAT = 16

# Starting with pack format 16, the supported_formats option can be provided in pack.mcmeta
SUPPORTED_MCMETA_FORMAT = 16


@click.command()
@click.option(
    "-t",
    "--texture",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    required=True,
    help="Texture file",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
    required=True,
    help="Output folder",
)
@click.option(
    "-m",
    "--min-format",
    type=int,
    required=False,
    default=1,
    help="Minimum resource pack format to support",
)
@click.option(
    "-M",
    "--max-format",
    type=int,
    required=False,
    default=22,
    help="Maximum resource pack format to support",
)
def byob(texture: str, output: str, min_format: int, max_format: int) -> None:
    """Generate a resource pack from a texture, targeting the given range of resource pack formats."""
    try:
        texture_file = Image.open(texture).convert("RGBA")
    except UnidentifiedImageError as e:
        option = "texture"
        error_message = f"{texture} is not a valid image file"
        raise click.BadOptionUsage(option, error_message) from e

    if texture_file.size[0] != texture_file.size[1]:
        option = "texture"
        error_message = f"{texture} is not a square image."
        raise click.BadOptionUsage(option, error_message)

    if min_format > max_format:
        option = "min-format"
        error_message = "min-format must be less than or equal to max-format"
        raise click.BadOptionUsage(option, error_message)

    if min_format < 1:
        option = "min-format"
        error_message = "min-format must be greater than or equal to 1"
        raise click.BadOptionUsage(option, error_message)

    if max_format < 1:
        option = "max-format"
        error_message = "max-format must be greater than or equal to 1"
        raise click.BadOptionUsage(option, error_message)

    base_dir = Path(output)
    gui_dir = base_dir / "assets/minecraft/textures/gui"
    gui_dir.mkdir(parents=True, exist_ok=True)

    # options_background.png is used for all pack formats
    texture_file.save(gui_dir / "options_background.png")

    # Files other than options_background.png are not needed in early pack formats
    if max_format >= CREATE_OVERHAUL_FORMAT:
        light_dirt_background = brightness(texture_file, 0.3)
        light_dirt_background.save(gui_dir / "light_dirt_background.png")

        header, footer = generate_separators(texture_file)

        header.save(gui_dir / "header_separator.png")
        footer.save(gui_dir / "footer_separator.png")

        tab_sprites = generate_tab_sprites(texture_file)

        # The four sprites are bundled together in tab_button.png in earlier pack formats
        if min_format < SPRITES_FOLDER_FORMAT:
            tab_sprites["tab_button"].save(gui_dir / "tab_button.png")

        # Separate sprites stored in the sprites folder are used in later pack formats
        if max_format >= SPRITES_FOLDER_FORMAT:
            widget_dir = gui_dir / "sprites/widget"
            widget_dir.mkdir(parents=True, exist_ok=True)

            mcmeta = tab_sprites_mcmeta()
            for name in (
                "tab",
                "tab_highlighted",
                "tab_selected",
                "tab_selected_highlighted",
            ):
                # Save each sprite
                tab_sprites[name].save(widget_dir / f"{name}.png")

                # Save the sprite's associated .mcmeta file
                with Path.open(widget_dir / f"{name}.png.mcmeta", "w") as f:
                    f.write(mcmeta)

    # Resize the texture to 64x64 for the pack.png
    texture_file.resize((64, 64), Image.NEAREST).save(base_dir / "pack.png")

    # In earlier formats, the supported_formats option did not exist, so we will use the max_format as the pack_format
    # Otherwise, we can use min_format as the pack_format,and specify the supported_formats option with the full range
    pack_format = max_format if max_format < SUPPORTED_MCMETA_FORMAT else min_format

    pack_mcmeta = {
        "pack": {
            "pack_format": pack_format,
            # No harm in including supported_formats even before it was introduced
            "supported_formats": [min_format, max_format],
            # Use \u00a7 for §o, which makes the description in italics
            "description": "\u00a7oGenerated by Bring Your Own Blocks!",
        }
    }

    # Write pack.mcmeta
    with Path.open(base_dir / "pack.mcmeta", "w") as f:
        f.write(json.dumps(pack_mcmeta, indent=4))


if __name__ == "__main__":
    byob()
