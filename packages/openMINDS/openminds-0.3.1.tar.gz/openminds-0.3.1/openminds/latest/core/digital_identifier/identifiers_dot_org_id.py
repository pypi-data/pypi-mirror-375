"""
<description not available>
"""

# this file was auto-generated!


from openminds.base import LinkedMetadata
from openminds.properties import Property


class IdentifiersDotOrgID(LinkedMetadata):
    """
    <description not available>
    """

    type_ = "https://openminds.om-i.org/types/IdentifiersDotOrgID"
    context = {"@vocab": "https://openminds.om-i.org/props/"}
    schema_version = "latest"

    properties = [
        Property(
            "identifier",
            str,
            "identifier",
            formatting="text/plain",
            required=True,
            description="Term or code used to identify the identifiers dot org i d.",
            instructions="Enter the resolvable identifier (IRI) of Identifiers.org.",
        ),
    ]

    def __init__(self, id=None, identifier=None):
        return super().__init__(
            id=id,
            identifier=identifier,
        )
