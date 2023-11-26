from PIL import Image, ImageEnhance
from typing import Tuple

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
TRANS = (0, 0, 0, 0)


def brightness(image: Image.Image, factor: float) -> Image.Image:
    """Change the brightness of an image by a factor."""
    return ImageEnhance.Brightness(image).enhance(factor)


def contrast(image: Image.Image, factor: float) -> Image.Image:
    """Change the contrast of an image by a factor."""
    return ImageEnhance.Contrast(image).enhance(factor)


def generate_tab_selected(texture: Image.Image) -> Tuple[Image.Image, Image.Image]:
    """Generate tab_selected.png and tab_selected_highlighted.png from a texture.

    The texture must be a square image of dimensions which are a multiple of 32.
    Textures less than 32x32 will be resized to 32x32 using Nearest-Neighbour sampling.
    """
    # Resize the texture to be at least 32x32
    if texture.size[0] < 32:
        texture = texture.resize((32, 32), Image.NEAREST)

    # The texture is assumed to be square
    texture_l = texture.size[0]

    # Only textures which are a multiple of 32 are supported
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
    tab_selected_highlighed = tab_selected.copy()

    # Add the white bars just inside the black bars
    horizontal_white_bar = Image.new("RGBA", (tab_w - 2 * scale, scale), WHITE)
    veritical_white_bar = Image.new("RGBA", (scale, tab_h), WHITE)
    tab_selected_highlighed.paste(horizontal_white_bar, (scale, scale))
    tab_selected_highlighed.paste(veritical_white_bar, (scale, scale))
    tab_selected_highlighed.paste(veritical_white_bar, (tab_w - 2 * scale, scale))

    # Cut off 2*scale squares from the bottom corners of both images
    corner_cut = Image.new("RGBA", (2 * scale, 2 * scale))
    tab_selected.paste(corner_cut, (0, crop_h))
    tab_selected.paste(corner_cut, (four_tiled_w, crop_h))
    tab_selected_highlighed.paste(corner_cut, (0, crop_h))
    tab_selected_highlighed.paste(corner_cut, (four_tiled_w, crop_h))

    return tab_selected, tab_selected_highlighed
