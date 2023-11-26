import click
from PIL import Image, UnidentifiedImageError
from conversions import brightness, generate_tab_selected


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

    (
        tab,
        tab_highlighted,
        tab_selected,
        tab_selected_highlighted,
    ) = generate_tab_selected(texture_file)

    tab.save("tab.png")
    tab_highlighted.save("tab_highlighted.png")
    tab_selected.save("tab_selected.png")
    tab_selected_highlighted.save("tab_selected_highlighted.png")


if __name__ == "__main__":
    byob()
