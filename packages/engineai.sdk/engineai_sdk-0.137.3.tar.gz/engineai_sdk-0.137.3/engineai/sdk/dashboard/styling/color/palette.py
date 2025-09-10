"""Color palette."""

import enum
from typing import Any


class PaletteTypes(enum.Enum):
    """Selection of color palettes.

    Selection of different types of color palettes available.

    Attributes:
        QUALITATIVE (str): Qualitative palette type.
        SEQUENTIAL (str): Sequential palette type.
    """

    QUALITATIVE = "QUALITATIVE"
    SEQUENTIAL = "SEQUENTIAL"


class Palette(enum.Enum):
    """Predefined color palettes.

    Collection of predefined color palettes for various purposes.

    Attributes:
        MINT_GREEN (str): Mint green color.
        SUNSET_ORANGE (str): Sunset orange color.
        BUBBLEGUM_PINK (str): Bubblegum pink color.
        GRASS_GREEN (str): Grass green color.
        LAVENDER_PURPLE (str): Lavender purple color.
        ALMOND_BROWN (str): Almond brown color.
        SKY_BLUE (str): Sky blue color.
        CHILI_RED (str): Chili red color.
        FOREST_GREEN (str): Forest green color.
        PEACOCK_GREEN (str): Peacock green color.
        LAGOON_GREEN (str): Lagoon green color.
        AQUA_GREEN (str): Aqua green color.
        FROST_GREEN (str): Frost green color.
        RUBI_RED (str): Rubi red color.
        SALMON_RED (str): Salmon red color.
        COCONUT_GREY (str): Coconut grey color.
        BABY_BLUE (str): Baby blue color.
        SEA_BLUE (str): Sea blue color.
        CEMENT_GREY (str): Cement grey color.
        COAL_GREY (str): Coal grey color.
        CROW_GREY (str): Crow grey color.
        SEAL_GREY (str): Seal grey color.
        OCEAN_BLUE (str): Ocean blue color.
        TIGER_ORANGE (str): Tiger orange color.
        PARADISE_GREEN (str): Paradise green color.
        RIVER_BLUE (str): River blue color.
        ASHES_GREY (str): Ashes grey color.
        RHINO_GREY (str): Rhino grey color.
        ENGINEAI_BLUE (str): EngineAI blue color.
        TROPICAL_BLUE (str): Tropical blue color.
        JAVA (str): Java color.
        MEDIUM_TURQUOISE (str): Medium turquoise color.
        FUCHSIA_PINK (str): Fuchsia pink color.
        BANANA_YELLOW (str): Banana yellow color.
        JELLYFISH_GREEN (str): Jellyfish green color.
        FROG_GREEN (str): Frog green color.
        SPRING_GREEN (str): Spring green color.
        TEA_GREEN (str): Tea green color.
        LEMON_YELLOW (str): Lemon yellow color.
        GOLD_5 (str): Gold 5 color.
        PURPLE_7 (str): Purple 7 color.
        TEAL_5 (str): Teal 5 color.
        MAGENTA_7 (str): Magenta 7 color.
        BLUE_3 (str): Blue 3 color.
        BLUE_8 (str): Blue 8 color.
        PURPLE_4 (str): Purple 4 color.
        ORANGE_7 (str): Orange 7 color.
        OCEAN_4 (str): Ocean 4 color.
        PURPLE_9 (str): Purple 9 color.
        TRAFFIC_RED (str): Traffic red color.
        TRAFFIC_YELLOW (str): Traffic yellow color.
        TRAFFIC_GREEN (str): Traffic green color.
        LIGHTER_GREY (str): Lighter grey color.
        BLUE_POSITIVE_0 (str): Blue positive 0 color.
        BLUE_POSITIVE_1 (str): Blue positive 1 color.
        BLUE_POSITIVE_2 (str): Blue positive 2 color.
        BLUE_POSITIVE_3 (str): Blue positive 3 color.
        BLUE_POSITIVE_4 (str): Blue positive 4 color.
        RED_NEGATIVE_0 (str): Red negative 0 color.
        RED_NEGATIVE_1 (str): Red negative 1 color.
        RED_NEGATIVE_2 (str): Red negative 2 color.
        RED_NEGATIVE_3 (str): Red negative 3 color.
        RED_NEGATIVE_4 (str): Red negative 4 color.
    """

    # qualitative
    MINT_GREEN = "#57DBD8"
    SUNSET_ORANGE = "#F79F5F"
    BUBBLEGUM_PINK = "#BA5479"
    GRASS_GREEN = "#68B056"
    LAVENDER_PURPLE = "#9A77FF"
    ALMOND_BROWN = "#CE7737"
    SKY_BLUE = "#5BAAF2"
    CHILI_RED = "#DE4A4A"

    # sequential
    FOREST_GREEN = "#166563"
    PEACOCK_GREEN = "#1D8684"
    LAGOON_GREEN = "#27B4B1"
    AQUA_GREEN = "#A3EBEA"
    FROST_GREEN = "#CDF4F4"

    # diverging
    RUBI_RED = "#C83C3C"
    SALMON_RED = "#EF8F8F"
    COCONUT_GREY = "#F1F4F4"
    BABY_BLUE = "#85C9FA"
    SEA_BLUE = "#338CCC"
    CEMENT_GREY = "#899F9F"
    COAL_GREY = "#2C3535"
    CROW_GREY = "#222A2A"
    SEAL_GREY = "#657B7B"

    # diverging risk
    OCEAN_BLUE = "#2574AD"
    TIGER_ORANGE = "#DE653F"
    PARADISE_GREEN = "#39C6C3"
    RIVER_BLUE = "#68B7D9"

    ASHES_GREY = "#354141"
    RHINO_GREY = "#ABBABA"

    # concept colours (dsi, price, etc)
    ENGINEAI_BLUE = "#1A6A7A"
    TROPICAL_BLUE = "#2CADB5"
    JAVA = "#248F9A"
    MEDIUM_TURQUOISE = "#5CC6CA"
    FUCHSIA_PINK = "#DB57BE"
    BANANA_YELLOW = "#F5D789"

    # extra colors
    JELLYFISH_GREEN = "#5AC4B6"
    FROG_GREEN = "#7ED0B9"
    SPRING_GREEN = "#A2DBBD"
    TEA_GREEN = "#C6E7C0"
    LEMON_YELLOW = "#FAF7C5"
    GOLD_5 = "#f1a649"
    PURPLE_7 = "#782080"
    TEAL_5 = "#54baa0"
    MAGENTA_7 = "#b92051"
    BLUE_3 = "#aab5df"
    BLUE_8 = "#1d3baa"
    PURPLE_4 = "#b280b6"
    ORANGE_7 = "#c94100"
    OCEAN_4 = "#6dacbc"
    PURPLE_9 = "#501555"

    TRAFFIC_RED = "#B54853"
    TRAFFIC_YELLOW = "#F0D582"
    TRAFFIC_GREEN = "#4C8056"

    LIGHTER_GREY = "#EEEEEE"

    # all positive sequential
    BLUE_POSITIVE_0 = "#D5E8F6"
    BLUE_POSITIVE_1 = "#96C6E9"
    BLUE_POSITIVE_2 = "#6CAFE0"
    BLUE_POSITIVE_3 = "#2D8DD2"
    BLUE_POSITIVE_4 = "#2574AD"

    # all negative sequential
    RED_NEGATIVE_0 = "#F3D7D7"
    RED_NEGATIVE_1 = "#E8B0B0"
    RED_NEGATIVE_2 = "#DD8888"
    RED_NEGATIVE_3 = "#D26060"
    RED_NEGATIVE_4 = "#C83C3C"

    @property
    def color(self) -> str:
        """Returns color without transparency.

        Returns:
            str: hex color
        """
        return f"{self.value}ff"


class QualitativePalette(enum.Enum):
    """Qualitative Palette.

    Qualitative color palette for distinguishing different categories or series.

    Attributes:
        MINT_GREEN (str): Mint green color.
        SUNSET_ORANGE (str): Sunset orange color.
        BUBBLEGUM_PINK (str): Bubblegum pink color.
        GRASS_GREEN (str): Grass green color.
        LAVENDER_PURPLE (str): Lavender purple color.
        ALMOND_BROWN (str): Almond brown color.
        SKY_BLUE (str): Sky blue color.
        CHILI_RED (str): Chili red color.
    """

    MINT_GREEN = Palette.MINT_GREEN.value
    SUNSET_ORANGE = Palette.SUNSET_ORANGE.value
    BUBBLEGUM_PINK = Palette.BUBBLEGUM_PINK.value
    GRASS_GREEN = Palette.GRASS_GREEN.value
    LAVENDER_PURPLE = Palette.LAVENDER_PURPLE.value
    ALMOND_BROWN = Palette.ALMOND_BROWN.value
    SKY_BLUE = Palette.SKY_BLUE.value
    CHILI_RED = Palette.CHILI_RED.value


class SequentialPaletteTwoSeries(enum.Enum):
    """Sequential Palette for charts with two series.

    Sequential color palette optimized for charts with exactly two data series.

    Attributes:
        LAGOON_GREEN (str): Lagoon green color.
        FROST_GREEN (str): Frost green color.
    """

    LAGOON_GREEN = Palette.LAGOON_GREEN.value
    FROST_GREEN = Palette.FROST_GREEN.value


class SequentialPaletteThreeSeries(enum.Enum):
    """Sequential Palette for charts with three series.

    Sequential color palette optimized for charts with exactly three data series.

    Attributes:
        PEACOCK_GREEN (str): Peacock green color.
        MINT_GREEN (str): Mint green color.
        FROST_GREEN (str): Frost green color.
    """

    PEACOCK_GREEN = Palette.PEACOCK_GREEN.value
    MINT_GREEN = Palette.MINT_GREEN.value
    FROST_GREEN = Palette.FROST_GREEN.value


class SequentialPalette(enum.Enum):
    """Sequential Palette.

    Sequential color palette for representing ordered data with gradual color
    transitions.

    Attributes:
        FOREST_GREEN (str): Forest green color.
        PEACOCK_GREEN (str): Peacock green color.
        LAGOON_GREEN (str): Lagoon green color.
        MINT_GREEN (str): Mint green color.
        AQUA_GREEN (str): Aqua green color.
        FROST_GREEN (str): Frost green color.
    """

    FOREST_GREEN = Palette.FOREST_GREEN.value
    PEACOCK_GREEN = Palette.PEACOCK_GREEN.value
    LAGOON_GREEN = Palette.LAGOON_GREEN.value
    MINT_GREEN = Palette.MINT_GREEN.value
    AQUA_GREEN = Palette.AQUA_GREEN.value
    FROST_GREEN = Palette.FROST_GREEN.value


class PercentageAllPositiveSequentialPalette(enum.Enum):
    """All Positive Sequential Palette.

    Sequential color palette for representing all positive percentage values.

    Attributes:
        POSITIVE_0 (str): Positive 0 color.
        POSITIVE_1 (str): Positive 1 color.
        POSITIVE_2 (str): Positive 2 color.
        POSITIVE_3 (str): Positive 3 color.
        POSITIVE_4 (str): Positive 4 color.
    """

    POSITIVE_0 = Palette.BLUE_POSITIVE_0.value
    POSITIVE_1 = Palette.BLUE_POSITIVE_1.value
    POSITIVE_2 = Palette.BLUE_POSITIVE_2.value
    POSITIVE_3 = Palette.BLUE_POSITIVE_3.value
    POSITIVE_4 = Palette.BLUE_POSITIVE_4.value


class PercentageAllNegativeSequentialPalette(enum.Enum):
    """All Negative Sequential Palette.

    Sequential color palette for representing all negative percentage values.

    Attributes:
        NEGATIVE_0 (str): Negative 0 color.
        NEGATIVE_1 (str): Negative 1 color.
        NEGATIVE_2 (str): Negative 2 color.
        NEGATIVE_3 (str): Negative 3 color.
        NEGATIVE_4 (str): Negative 4 color.
    """

    NEGATIVE_0 = Palette.RED_NEGATIVE_0.value
    NEGATIVE_1 = Palette.RED_NEGATIVE_1.value
    NEGATIVE_2 = Palette.RED_NEGATIVE_2.value
    NEGATIVE_3 = Palette.RED_NEGATIVE_3.value
    NEGATIVE_4 = Palette.RED_NEGATIVE_4.value


def qualitative_palette(*, index: int) -> Palette:
    """Returns color of qualitative palette given index.

    Args:
        index: index of qualitative palette (e.g. index of series of a
            timeseries chart)

    Returns:
        Palette: returns corresponding color of qualitative palette
    """
    colors = list(QualitativePalette.__members__.values())

    return Palette(colors[index % len(colors)].value)


SequentialPaletteType = (
    type[SequentialPalette]
    | type[SequentialPaletteTwoSeries]
    | type[SequentialPaletteThreeSeries]
    | type[PercentageAllPositiveSequentialPalette]
    | type[PercentageAllNegativeSequentialPalette]
)


def sequential_palette(
    *,
    index: int,
    n_series: int | None = None,
    palette: SequentialPaletteType = SequentialPalette,
) -> Palette:
    """Returns color of sequential palette given index.

    Args:
        index: index of sequential palette (e.g. index of series of a
            timeseries chart)
        n_series: total number of series used for sequential palette.
            Determines sub-versions of sequential palette to improve contrast.
            Defaults to None, i.e. uses entire palette.
        palette: enum of sequential palettes to use.

    Returns:
        Palette: returns corresponding color of sequential palette
    """
    colors: Any = list(palette.__members__.values())
    if n_series is not None:
        if n_series <= 2:
            palette = SequentialPaletteTwoSeries
        elif n_series == 3:
            palette = SequentialPaletteThreeSeries

        colors = list(palette.__members__.values())
        if n_series in [4, 5]:
            colors = colors[-n_series:]  # select last n_series colors

    return Palette(colors[index % len(colors)].value)
