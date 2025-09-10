from enumerific import Enumeration, anno


class Format(Enumeration):
    """The Format enumeration defines the JPEG file formats supported by the library."""

    JPEG = anno(
        1,
        description="JPEG Interchange File (JIF)",
    )

    JFIF = anno(
        2,
        description="JPEG File Interchange (JFIF)",
    )

    EXIF = anno(
        3,
        description="JPEG Extensible Image File (EXIF)",
    )

    CCIF = anno(
        4,
        description="Canon Camera Image File Format (CCIF)",
    )

    SPIFF = anno(
        5,
        description="Still Picture Interchange File Format (SPIFF)",
    )
