"""
An entity comprised of one or more natural persons with a particular purpose. [adapted from Wikipedia](https://en.wikipedia.org/wiki/Organization)
"""

# this file was auto-generated!


from openminds.base import LinkedMetadata
from openminds.properties import Property


class Organization(LinkedMetadata):
    """
    An entity comprised of one or more natural persons with a particular purpose. [adapted from Wikipedia](https://en.wikipedia.org/wiki/Organization)
    """

    type_ = "https://openminds.ebrains.eu/core/Organization"
    context = {"@vocab": "https://openminds.ebrains.eu/vocab/"}
    schema_version = "v2.0"

    properties = [
        Property(
            "digital_identifiers",
            ["openminds.v2.core.GRIDID", "openminds.v2.core.RORID"],
            "digitalIdentifier",
            multiple=True,
            unique_items=True,
            min_items=1,
            description="Digital handle to identify objects or legal persons.",
            instructions="Add one or several globally unique and persistent digital identifier for this organization.",
        ),
        Property(
            "full_name",
            str,
            "fullName",
            formatting="text/plain",
            required=True,
            description="Whole, non-abbreviated name of the organization.",
            instructions="Enter the full name of the organization.",
        ),
        Property(
            "has_parent",
            "openminds.v2.core.Organization",
            "hasParent",
            description="Reference to a parent object or legal person.",
            instructions="Add a parent organization to this organization.",
        ),
        Property(
            "homepage",
            "openminds.v2.core.URL",
            "homepage",
            description="Main website of the organization.",
            instructions="Add the uniform resource locator (URL) to the homepage of this organization.",
        ),
        Property(
            "short_name",
            str,
            "shortName",
            formatting="text/plain",
            description="Shortened or fully abbreviated name of the organization.",
            instructions="Enter the short name of this organization.",
        ),
    ]

    def __init__(
        self, id=None, digital_identifiers=None, full_name=None, has_parent=None, homepage=None, short_name=None
    ):
        return super().__init__(
            id=id,
            digital_identifiers=digital_identifiers,
            full_name=full_name,
            has_parent=has_parent,
            homepage=homepage,
            short_name=short_name,
        )
