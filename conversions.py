import json
from PIL import Image, ImageEnhance

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
TRANS = (0, 0, 0, 0)


def brightness(image: Image.Image, factor: float) -> Image.Image:
    """Change the brightness of an image by a factor."""
    return ImageEnhance.Brightness(image).enhance(factor)


def contrast(image: Image.Image, factor: float) -> Image.Image:
    """Change the contrast of an image by a factor."""
    return ImageEnhance.Contrast(image).enhance(factor)


def generate_tab_sprites(texture: Image.Image) -> dict[str, Image.Image]:
    """Generate the tab sprites from a texture.

    Specifically, tab.png, tab_highlighted.png, tab_selected.png and tab_selected_highlighted.png.

    The texture must be a square image of dimensions which are a multiple of 32.
    Textures less than 32x32 will be resized to 32x32 using Nearest-Neighbour sampling.
    """
    # Resize the texture to be at least 32x32
    if texture.size[0] < 32:
        texture = texture.resize((32, 32), Image.NEAREST)

    # The texture is assumed to be square
    texture_l = texture.size[0]

    # Scale relative to a 32x32 texture
    scale = texture_l // 32

    # Crop the texture to be the top 11/16ths of the original texture
    crop_h = 22 * scale
    cropped = texture.crop((0, 0, texture_l, crop_h))

    # Tile the cropped image 4 times horizontally
    four_tiled_w = 4 * texture_l
    four_tiled = Image.new("RGBA", (four_tiled_w, crop_h))
    four_tiled.paste(cropped, (0, 0))
    four_tiled.paste(four_tiled, (texture_l, 0))
    four_tiled.paste(four_tiled, (texture_l * 2, 0))

    # The background used is darkened and decontrasted
    bg = brightness(four_tiled, 0.7)
    bg = contrast(bg, 0.25)

    # The forground is even darker, but the contrast is not changed
    fg = brightness(four_tiled, 0.3)

    # These are the dimensions the actual tab sprites
    tab_w = 130 * scale
    tab_h = 24 * scale

    # Create the image which will become tab_selected.png
    tab_selected = Image.new("RGBA", (tab_w, tab_h))
    tab_selected.paste(bg, (0, 0))
    tab_selected.paste(fg, (2 * scale, 2 * scale))

    # Take the second column of the texture, darken it  and paste it to the last column
    second_col = tab_selected.crop((2 * scale, 0, 4 * scale, tab_h))
    dark_second_col = brightness(second_col, 0.25)
    tab_selected.paste(dark_second_col, (four_tiled_w, 0))

    # Add black bars along the top, left and right edges of the image
    horizontal_black_bar = Image.new("RGBA", (tab_w, scale), BLACK)
    vertical_black_bar = Image.new("RGBA", (scale, tab_h), BLACK)
    tab_selected.paste(horizontal_black_bar, (0, 0))
    tab_selected.paste(vertical_black_bar, (0, 0))
    tab_selected.paste(vertical_black_bar, (tab_w - scale, 0))

    # Create the image which will become tab_selected_highlighted.png
    # It is the same as tab_selected.png, but with white bars inside of the black bars
    tab_selected_highlighted = tab_selected.copy()

    # Add the white bars just inside the black bars
    horizontal_white_bar = Image.new("RGBA", (tab_w - 2 * scale, scale), WHITE)
    veritical_white_bar = Image.new("RGBA", (scale, tab_h), WHITE)
    tab_selected_highlighted.paste(horizontal_white_bar, (scale, scale))
    tab_selected_highlighted.paste(veritical_white_bar, (scale, scale))
    tab_selected_highlighted.paste(veritical_white_bar, (tab_w - 2 * scale, scale))

    # Cut off 2*scale squares from the bottom corners of both images
    corner_cut = Image.new("RGBA", (2 * scale, 2 * scale))
    tab_selected.paste(corner_cut, (0, crop_h))
    tab_selected.paste(corner_cut, (four_tiled_w, crop_h))
    tab_selected_highlighted.paste(corner_cut, (0, crop_h))
    tab_selected_highlighted.paste(corner_cut, (four_tiled_w, crop_h))

    # Crop just the section used for tab.png and tab_highlighted.png
    tab_crop = tab_selected.crop((scale, scale, tab_w - scale, tab_h - 6 * scale))

    # Paste the cropped section into the image which will become tab.png
    # Note that it is pasted offcenter vertically, with several transparent rows at the top and bottom
    tab = Image.new("RGBA", (tab_w, tab_h))
    tab.paste(tab_crop, (scale, 5 * scale))

    # Unselected tabs are darker and less contrasted than selected tabs
    tab = brightness(tab, 0.60)
    tab = contrast(tab, 0.90)

    # Copy to the image which will become tab_highlighted.png
    tab_highlighted = tab.copy()

    # Add black bars along the top, left and right edges of the image
    tab_highlighted.paste(horizontal_black_bar, (0, 4 * scale))
    tab_highlighted.paste(vertical_black_bar, (0, 4 * scale))
    tab_highlighted.paste(vertical_black_bar, (tab_w - scale, 4 * scale))

    # Add white bars along all sides, just inside the black bars
    tab_highlighted.paste(horizontal_white_bar, (scale, 5 * scale))
    tab_highlighted.paste(horizontal_white_bar, (scale, tab_h - 3 * scale))
    tab_highlighted.paste(veritical_white_bar, (scale, 5 * scale))
    tab_highlighted.paste(veritical_white_bar, (tab_w - 2 * scale, 5 * scale))

    # Remove the corners which got touched by the vertical bars
    tab_highlighted.paste(corner_cut, (0, crop_h))
    tab_highlighted.paste(corner_cut, (four_tiled_w, crop_h))

    # tab_button.png is just a 256x256 square containing all 4 sprites
    # It is only used for resource packs pre pack-version 16
    tab_button = Image.new("RGBA", (256 * scale, 256 * scale))

    # Paste the sprites into the image
    tab_button.paste(tab_selected, (0, 0))
    tab_button.paste(tab_selected_highlighted, (0, tab_h))
    tab_button.paste(tab, (0, 2 * tab_h))
    tab_button.paste(tab_highlighted, (0, 3 * tab_h))

    return {
        "tab": tab,
        "tab_highlighted": tab_highlighted,
        "tab_selected": tab_selected,
        "tab_selected_highlighted": tab_selected_highlighted,
        "tab_button": tab_button,
    }


def tab_sprites_mcmeta(texture) -> str:
    """Generate the .mcmeta file used for each of the tab sprites."""
    scale = max(1, texture.size[0] // 32)

    mcmeta = {
        "gui": {
            "scaling": {
                "type": "nine_slice",
                "width": 130 * scale,
                "height": 24 * scale,
                "border": {
                    "left": 2 * scale,
                    "top": 2 * scale,
                    "right": 2 * scale,
                    "bottom": 0,
                },
            }
        }
    }

    return json.dumps(mcmeta, indent=4)


def generate_seperators(texture: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Generate header_seperator.png and footer_seperator.png from a texture.

    The texture must be a square image of dimensions which are a multiple of 32.
    Textures less than 32x32 will be resized to 32x32 using Nearest-Neighbour sampling.
    """
    # Resize the texture to be at least 32x32
    if texture.size[0] < 32:
        texture = texture.resize((32, 32), Image.NEAREST)

    # The texture is assumed to be square
    texture_l = texture.size[0]

    # Scale relative to a 32x32 texture
    scale = texture_l // 32

    # Get the first 1/16th of the texture for the footer seperator
    # And the second 1/16th of the texture for the header seperator
    footer = texture.crop((0, 0, texture_l, 2 * scale))
    header = texture.crop((0, 2 * scale, texture_l, 4 * scale))

    # Half of each seperator is lighter than the other
    # (note that they are still darkened, just not as much)
    # They are also decontrasted, giving a sepia tone with the default dirt texture
    footer_light = footer.crop((0, 0, texture_l, scale))
    footer_light = contrast(footer_light, 0.35)
    footer_light = brightness(footer_light, 0.75)

    header_light = header.crop((0, 0, texture_l, scale))
    header_light = contrast(header_light, 0.35)
    header_light = brightness(header_light, 0.75)

    # The other half is darker
    footer = brightness(footer, 0.05)
    header = brightness(header, 0.25)

    # Paste the lighter half. Note that for the footer,
    # the lighter half is on bottom, and vice versa for the header
    footer.paste(footer_light, (0, scale))
    header.paste(header_light, (0, 0))

    return header, footer
