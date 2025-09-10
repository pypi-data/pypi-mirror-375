"""
<description not available>
"""

# this file was auto-generated!


from openminds.base import LinkedMetadata
from openminds.properties import Property


class SWHID(LinkedMetadata):
    """
    <description not available>
    """

    type_ = "https://openminds.om-i.org/types/SWHID"
    context = {"@vocab": "https://openminds.om-i.org/props/"}
    schema_version = "latest"

    properties = [
        Property(
            "identifier",
            str,
            "identifier",
            formatting="text/plain",
            required=True,
            description="Term or code used to identify the SWHID.",
            instructions="Enter the identifier for software source code artefacts provided by the Software Heritage archive ('SoftWare Heritage persistent IDentifier'; SWHID) as an internationalized resource identifier (IRI) following the defined pattern (i.e., 'https://archive.softwareheritage.org/' + SWHID).",
        ),
    ]

    def __init__(self, id=None, identifier=None):
        return super().__init__(
            id=id,
            identifier=identifier,
        )
