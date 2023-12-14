"""Functions for generating texture and .mcmeta files."""
import json

from PIL import Image, ImageEnhance

# Some colour constants
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
TRANS = (0, 0, 0, 0)

# This is the size to which all textures will be resized
NORMAL_SIZE = 32

# Crop the texture to be the top 11/16ths of the original texture
CROP_H = 22

# These are the dimensions the actual tab sprites
TAB_W = 130
TAB_H = 24

# 1-pixel thin white bars used to construct the *_highlighted.png sprites
HORIZONTAL_WHITE_BAR = Image.new("RGBA", (TAB_W - 2, 1), WHITE)
VERTICAL_WHITE_BAR = Image.new("RGBA", (1, TAB_H), WHITE)

# 1-pixel thin black bars used to construct the *_selected*.png sprites
HORIZONTAL_BLACK_BAR = Image.new("RGBA", (TAB_W, 1), BLACK)
VERTICAL_BLACK_BAR = Image.new("RGBA", (1, TAB_H), BLACK)

# 2x2 blank area, used to cut off the corners of sprites
CORNER_CUT = Image.new("RGBA", (2, 2))


def brightness(image: Image.Image, factor: float) -> Image.Image:
    """Change the brightness of an image by a factor."""
    return ImageEnhance.Brightness(image).enhance(factor)


def contrast(image: Image.Image, factor: float) -> Image.Image:
    """Change the contrast of an image by a factor."""
    return ImageEnhance.Contrast(image).enhance(factor)


def generate_tab_selected(texture: Image.Image) -> Image.Image:
    """Given the input texture, generate the tab_selected.png sprite."""
    normal_texture = texture.resize((NORMAL_SIZE, NORMAL_SIZE), Image.NEAREST)

    cropped = normal_texture.crop((0, 0, NORMAL_SIZE, CROP_H))

    # Tile the cropped image 4 times horizontally
    four_tiled = Image.new("RGBA", (4 * NORMAL_SIZE, CROP_H))
    four_tiled.paste(cropped, (0, 0))
    four_tiled.paste(four_tiled, (NORMAL_SIZE, 0))
    four_tiled.paste(four_tiled, (NORMAL_SIZE * 2, 0))

    # The background used is darkened and decontrasted
    bg = brightness(four_tiled, 0.7)
    bg = contrast(bg, 0.25)

    # The forground is even darker, but the contrast is not changed
    fg = brightness(four_tiled, 0.3)

    # Create the image which will become tab_selected.png
    tab_selected = Image.new("RGBA", (TAB_W, TAB_H))
    tab_selected.paste(bg, (0, 0))
    tab_selected.paste(fg, (2, 2))

    # Take the second column of the texture, darken it  and paste it to the last column
    second_col = tab_selected.crop((2, 0, 4, TAB_H))
    dark_second_col = brightness(second_col, 0.25)
    tab_selected.paste(dark_second_col, (4 * NORMAL_SIZE, 0))

    # Add black bars along the top, left and right edges of the image
    tab_selected.paste(HORIZONTAL_BLACK_BAR, (0, 0))
    tab_selected.paste(VERTICAL_BLACK_BAR, (0, 0))
    tab_selected.paste(VERTICAL_BLACK_BAR, (TAB_W - 1, 0))

    # Cut off 2x2 squares from the bottom corners
    tab_selected.paste(CORNER_CUT, (0, CROP_H))
    tab_selected.paste(CORNER_CUT, (4 * NORMAL_SIZE, CROP_H))

    return tab_selected


def generate_tab_selected_highlighted(tab_selected: Image.Image) -> Image.Image:
    """Given the tab_selected.png sprite, generate the tab_selected_highlighted.png sprite."""
    # Create the image which will become tab_selected_highlighted.png
    # It is the same as tab_selected.png, but with white bars inside of the black bars
    tab_selected_highlighted = tab_selected.copy()

    # Add the white bars just inside the black bars
    tab_selected_highlighted.paste(HORIZONTAL_WHITE_BAR, (1, 1))
    tab_selected_highlighted.paste(VERTICAL_WHITE_BAR, (1, 1))
    tab_selected_highlighted.paste(VERTICAL_WHITE_BAR, (TAB_W - 2, 1))

    # Cut off 2x2 squares from the bottom corners
    tab_selected_highlighted.paste(CORNER_CUT, (0, CROP_H))
    tab_selected_highlighted.paste(CORNER_CUT, (4 * NORMAL_SIZE, CROP_H))

    return tab_selected_highlighted


def generate_tab(tab_selected: Image.Image) -> Image.Image:
    """Given the tab_selected.png sprite, generate the tab.png sprite."""
    # Crop just the section used for tab.png and tab_highlighted.png
    tab_crop = tab_selected.crop((1, 1, TAB_W - 1, TAB_H - 6))

    # Paste the cropped section into the image which will become tab.png
    # Note that it is pasted offcenter vertically, with several transparent rows at the top and bottom
    tab = Image.new("RGBA", (TAB_W, TAB_H))
    tab.paste(tab_crop, (1, 5))

    # Unselected tabs are darker and less contrasted than selected tabs
    tab = brightness(tab, 0.60)
    return contrast(tab, 0.90)


def generate_tab_highlighted(tab: Image.Image) -> Image.Image:
    """Given the tab.png sprite, generate the tab_highlighted.png sprite."""
    # Copy to the image which will become tab_highlighted.png
    tab_highlighted = tab.copy()

    # Add black bars along the top, left and right edges of the image
    tab_highlighted.paste(HORIZONTAL_BLACK_BAR, (0, 4))
    tab_highlighted.paste(VERTICAL_BLACK_BAR, (0, 4))
    tab_highlighted.paste(VERTICAL_BLACK_BAR, (TAB_W - 1, 4))

    # Add white bars along all sides, just inside the black bars
    tab_highlighted.paste(HORIZONTAL_WHITE_BAR, (1, 5))
    tab_highlighted.paste(HORIZONTAL_WHITE_BAR, (1, TAB_H - 3))
    tab_highlighted.paste(VERTICAL_WHITE_BAR, (1, 5))
    tab_highlighted.paste(VERTICAL_WHITE_BAR, (TAB_W - 2, 5))

    # Remove the corners which got touched by the vertical bars
    tab_highlighted.paste(CORNER_CUT, (0, CROP_H))
    tab_highlighted.paste(CORNER_CUT, (4 * NORMAL_SIZE, CROP_H))

    return tab_highlighted


def generate_tab_sprites(texture: Image.Image) -> dict[str, Image.Image]:
    """Generate the tab sprites from a texture.

    Specifically, tab.png, tab_highlighted.png, tab_selected.png and tab_selected_highlighted.png.

    Textures will be resized to NORMAL_SIZExNORMAL_SIZE using Nearest-Neighbour sampling.
    """
    # Use the above methods to generate the four sprites
    tab_selected = generate_tab_selected(texture)
    tab_selected_highlighted = generate_tab_selected_highlighted(tab_selected)
    tab = generate_tab(tab_selected)
    tab_highlighted = generate_tab_highlighted(tab)

    # tab_button.png is just a 256x256 square containing all 4 sprites
    # It is only used for resource packs pre pack-format 16
    tab_button = Image.new("RGBA", (256, 256))

    # Paste the sprites into the image
    tab_button.paste(tab_selected, (0, 0))
    tab_button.paste(tab_selected_highlighted, (0, TAB_H))
    tab_button.paste(tab, (0, 2 * TAB_H))
    tab_button.paste(tab_highlighted, (0, 3 * TAB_H))

    return {
        "tab": tab,
        "tab_highlighted": tab_highlighted,
        "tab_selected": tab_selected,
        "tab_selected_highlighted": tab_selected_highlighted,
        "tab_button": tab_button,
    }


def tab_sprites_mcmeta() -> str:
    """Generate the .mcmeta file used for each of the tab sprites."""
    mcmeta = {
        "gui": {
            "scaling": {
                "type": "nine_slice",
                "width": 130,
                "height": 24,
                "border": {
                    "left": 2,
                    "top": 2,
                    "right": 2,
                    "bottom": 0,
                },
            },
        },
    }

    return json.dumps(mcmeta, indent=4)


def generate_separators(texture: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Generate header_separator.png and footer_separator.png from a texture.

    The texture must be a square image of dimensions which are a multiple of 32.
    Textures less than 32x32 will be resized to 32x32 using Nearest-Neighbour sampling.
    """
    normal_texture = texture.resize((NORMAL_SIZE, NORMAL_SIZE), Image.NEAREST)

    # Get the first 1/16th of the texture for the footer separator
    # And the second 1/16th of the texture for the header separator
    footer = normal_texture.crop((0, 0, NORMAL_SIZE, 2))
    header = normal_texture.crop((0, 2, NORMAL_SIZE, 4))

    # Half of each separator is lighter than the other
    # (note that they are still darkened, just not as much)
    # They are also decontrasted, giving a sepia tone with the default dirt texture
    footer_light = footer.crop((0, 0, NORMAL_SIZE, 1))
    footer_light = contrast(footer_light, 0.35)
    footer_light = brightness(footer_light, 0.75)

    header_light = header.crop((0, 0, NORMAL_SIZE, 1))
    header_light = contrast(header_light, 0.35)
    header_light = brightness(header_light, 0.75)

    # The other half is darker
    footer = brightness(footer, 0.05)
    header = brightness(header, 0.25)

    # Paste the lighter half. Note that for the footer,
    # the lighter half is on bottom, and vice versa for the header
    footer.paste(footer_light, (0, 1))
    header.paste(header_light, (0, 0))

    return header, footer
