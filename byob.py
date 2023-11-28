import json
import click
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from conversions import (
    brightness,
    generate_tab_sprites,
    generate_separators,
    tab_sprites_mcmeta,
)


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
    "--min-version",
    type=int,
    required=False,
    default=1,
    help="Minimum resource pack version to support",
)
@click.option(
    "-M",
    "--max-version",
    type=int,
    required=False,
    default=22,
    help="Maximum resource pack version to support",
)
def byob(texture: str, output: str, min_version: int, max_version: int):
    try:
        texture_file = Image.open(texture).convert("RGBA")

    except UnidentifiedImageError:
        raise click.BadOptionUsage("texture", f"{texture} is not a valid image file")

    if min_version > max_version:
        raise click.BadOptionUsage(
            "min-version", "min-version must be less than or equal to max-version"
        )

    if min_version < 1:
        raise click.BadOptionUsage(
            "min-version", "min-version must be greater than or equal to 1"
        )

    if max_version < 1:
        raise click.BadOptionUsage(
            "max-version", "max-version must be greater than or equal to 1"
        )

    width, height = texture_file.size

    if width != height:
        raise click.BadOptionUsage("texture", f"{texture} is not a square image")

    if width not in (16, 32):
        raise click.BadOptionUsage(
            "texture", "Supported texture sizes are 16x16 or 32x32."
        )

    base_dir = Path(output)
    gui_dir = base_dir / "assets/minecraft/textures/gui"
    gui_dir.mkdir(parents=True, exist_ok=True)

    # options_background.png is used for all pack versions
    texture_file.save(gui_dir / "options_background.png")

    # Files other than options_background.png are not needed pre pack-version 13
    if max_version >= 13:
        light_dirt_background = brightness(texture_file, 0.3)
        light_dirt_background.save(gui_dir / "light_dirt_background.png")

        header, footer = generate_separators(texture_file)

        header.save(gui_dir / "header_separator.png")
        footer.save(gui_dir / "footer_separator.png")

        tab_sprites = generate_tab_sprites(texture_file)

        # The four sprites are bundled together in tab_button.png pre pack-version 16
        if min_version < 16:
            tab_sprites["tab_button"].save(gui_dir / "tab_button.png")

        # Separate sprites stored in the sprites folder are used from pack-version 16 onwards
        if max_version >= 16:
            widget_dir = gui_dir / "sprites/widget"
            widget_dir.mkdir(parents=True, exist_ok=True)

            mcmeta = tab_sprites_mcmeta(texture_file)
            for name in (
                "tab",
                "tab_highlighted",
                "tab_selected",
                "tab_selected_highlighted",
            ):
                # Save each sprite
                tab_sprites[name].save(widget_dir / f"{name}.png")

                # Save the sprite's associated .mcmeta file
                with open(widget_dir / f"{name}.png.mcmeta", "w") as f:
                    f.write(mcmeta)

    if max_version < 16:
        # Before pack-version 16, the supported_formats option did not exist
        # So we will use the max_version as the pack_format
        pack_format = max_version
    else:
        # From pack-version 16 onwards, the supported_formats option exists
        # So we can use min_version as the pack_format,
        # and specify the supported_formats option with the full range
        pack_format = min_version

    # Resize the texture to 64x64 for the pack.png
    texture_file.resize((64, 64), Image.NEAREST).save(base_dir / "pack.png")

    pack_mcmeta = {
        "pack": {
            "pack_format": pack_format,
            "supported_formats": [min_version, max_version],
            # Use \u00a7 for §o, which makes the description italic
            "description": "\u00a7oGenerated by Bring Your Own Blocks!",
        }
    }

    # Write pack.mcmeta
    with open(base_dir / "pack.mcmeta", "w") as f:
        f.write(json.dumps(pack_mcmeta, indent=4))


if __name__ == "__main__":
    byob()
