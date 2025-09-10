"""
Structured information on the computer system or set of systems in which a computation is deployed and executed.
"""

# this file was auto-generated!


from openminds.base import LinkedMetadata
from openminds.properties import Property


class Environment(LinkedMetadata):
    """
    Structured information on the computer system or set of systems in which a computation is deployed and executed.
    """

    type_ = "https://openminds.om-i.org/types/Environment"
    context = {"@vocab": "https://openminds.om-i.org/props/"}
    schema_version = "latest"

    properties = [
        Property(
            "configuration",
            "openminds.latest.core.Configuration",
            "configuration",
            description="no description available",
            instructions="Add the configuration of this computational environment.",
        ),
        Property(
            "description",
            str,
            "description",
            formatting="text/markdown",
            multiline=True,
            description="Longer statement or account giving the characteristics of the environment.",
            instructions="Enter a short text describing this computational environment.",
        ),
        Property(
            "hardware",
            "openminds.latest.computation.HardwareSystem",
            "hardware",
            required=True,
            description="no description available",
            instructions="Add the hardware system on which this computational environment runs.",
        ),
        Property(
            "name",
            str,
            "name",
            formatting="text/plain",
            required=True,
            description="Word or phrase that constitutes the distinctive designation of the environment.",
            instructions="Enter a descriptive name for this computational environment.",
        ),
        Property(
            "software",
            "openminds.latest.core.SoftwareVersion",
            "software",
            multiple=True,
            unique_items=True,
            min_items=1,
            description="no description available",
            instructions="Add all software versions available in this computational environment.",
        ),
    ]

    def __init__(self, id=None, configuration=None, description=None, hardware=None, name=None, software=None):
        return super().__init__(
            id=id,
            configuration=configuration,
            description=description,
            hardware=hardware,
            name=name,
            software=software,
        )
