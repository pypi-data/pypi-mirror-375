"""
Structured information about a piece of software or web service that can perform a task autonomously.
"""

# this file was auto-generated!


from openminds.base import LinkedMetadata
from openminds.properties import Property


class SoftwareAgent(LinkedMetadata):
    """
    Structured information about a piece of software or web service that can perform a task autonomously.
    """

    type_ = "https://openminds.om-i.org/types/SoftwareAgent"
    context = {"@vocab": "https://openminds.om-i.org/props/"}
    schema_version = "v4.0"

    properties = [
        Property(
            "environment",
            "openminds.v4.computation.Environment",
            "environment",
            description="no description available",
            instructions="Add the computational environment in which this software agent was running.",
        ),
        Property(
            "name",
            str,
            "name",
            formatting="text/plain",
            required=True,
            description="Word or phrase that constitutes the distinctive designation of the software agent.",
            instructions="Enter a descriptive name for this software agent.",
        ),
        Property(
            "software",
            "openminds.v4.core.SoftwareVersion",
            "software",
            required=True,
            description="no description available",
            instructions="Add the software version that is being run as this software agent.",
        ),
    ]

    def __init__(self, id=None, environment=None, name=None, software=None):
        return super().__init__(
            id=id,
            environment=environment,
            name=name,
            software=software,
        )
