from enumerific import Enumeration, anno


class ColourTransform(Enumeration):
    """The Colour Transform enumeration lists the known JPEG color transforms."""

    Unknown = anno(
        -1,
        description="Unknown",
    )

    RGB = anno(
        0,
        description="RGB",
    )

    YCbCr = anno(
        1,
        description="YCbCr",
    )

    YCCK = anno(
        2,
        description="YCCK",
    )

    Greyscale = anno(
        3,
        description="Greyscale",
    )

    CMYK = anno(
        4,
        description="CMYK",
    )
