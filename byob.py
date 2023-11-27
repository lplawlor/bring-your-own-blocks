import click
from PIL import Image, UnidentifiedImageError
from conversions import (
    brightness,
    generate_tab_sprites,
    generate_seperators,
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
def byob(texture: str):
    try:
        texture_file = Image.open(texture)
    except UnidentifiedImageError:
        raise click.BadOptionUsage("texture", f"{texture} is not a valid image file")

    width, height = texture_file.size

    if width != height:
        raise click.BadOptionUsage("texture", f"{texture} is not a square image")

    light_dirt_background = brightness(texture_file, 0.3)
    light_dirt_background.save("light_dirt_background.png")

    tab_sprites = generate_tab_sprites(texture_file)
    mcmeta = tab_sprites_mcmeta(texture_file)
    for name in ("tab", "tab_highlighted", "tab_selected", "tab_selected_highlighted"):
        tab_sprites[name].save(f"{name}.png")

        with open(f"{name}.png.mcmeta", "w") as f:
            f.write(mcmeta)

    header, footer = generate_seperators(texture_file)

    header.save("header_seperator.png")
    footer.save("footer_seperator.png")


if __name__ == "__main__":
    byob()
