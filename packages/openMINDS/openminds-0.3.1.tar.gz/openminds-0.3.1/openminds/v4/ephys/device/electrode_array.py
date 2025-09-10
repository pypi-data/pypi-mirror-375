"""
Structured information on an electrode array.
"""

# this file was auto-generated!


from openminds.base import LinkedMetadata
from openminds.properties import Property


class ElectrodeArray(LinkedMetadata):
    """
    Structured information on an electrode array.
    """

    type_ = "https://openminds.om-i.org/types/ElectrodeArray"
    context = {"@vocab": "https://openminds.om-i.org/props/"}
    schema_version = "v4.0"

    properties = [
        Property(
            "conductor_material",
            [
                "openminds.v4.chemicals.ChemicalMixture",
                "openminds.v4.chemicals.ChemicalSubstance",
                "openminds.v4.controlled_terms.MolecularEntity",
            ],
            "conductorMaterial",
            description="no description available",
            instructions="Add the conductor material of this electrode array.",
        ),
        Property(
            "description",
            str,
            "description",
            formatting="text/markdown",
            multiline=True,
            description="Longer statement or account giving the characteristics of the electrode array.",
            instructions="Enter a short text describing this device.",
        ),
        Property(
            "device_type",
            "openminds.v4.controlled_terms.DeviceType",
            "deviceType",
            required=True,
            description="no description available",
            instructions="Add the type of this device.",
        ),
        Property(
            "digital_identifier",
            ["openminds.v4.core.DOI", "openminds.v4.core.RRID"],
            "digitalIdentifier",
            description="Digital handle to identify objects or legal persons.",
            instructions="Add the globally unique and persistent digital identifier of this device.",
        ),
        Property(
            "electrode_identifiers",
            str,
            "electrodeIdentifier",
            multiple=True,
            unique_items=True,
            min_items=2,
            formatting="text/plain",
            required=True,
            description="no description available",
            instructions="Enter the identifiers for each electrode of this electrode array. Note that the number of identifiers should match the number of electrodes of the array as stated under 'numberOfElectrodes'.",
        ),
        Property(
            "insulator_material",
            [
                "openminds.v4.chemicals.ChemicalMixture",
                "openminds.v4.chemicals.ChemicalSubstance",
                "openminds.v4.controlled_terms.MolecularEntity",
            ],
            "insulatorMaterial",
            description="no description available",
            instructions="Add the insulator material of this electrode array.",
        ),
        Property(
            "internal_identifier",
            str,
            "internalIdentifier",
            formatting="text/plain",
            description="Term or code that identifies the electrode array within a particular product.",
            instructions="Enter the identifier (or label) of this electrode array that is used within the corresponding data files to identify this electrode array.",
        ),
        Property(
            "intrinsic_resistance",
            ["openminds.v4.core.QuantitativeValue", "openminds.v4.core.QuantitativeValueRange"],
            "intrinsicResistance",
            description="no description available",
            instructions="Enter the intrinsic resistance of this electrode array.",
        ),
        Property(
            "lookup_label",
            str,
            "lookupLabel",
            formatting="text/plain",
            description="no description available",
            instructions="Enter a lookup label for this device that may help you to find this instance more easily.",
        ),
        Property(
            "manufacturers",
            ["openminds.v4.core.Consortium", "openminds.v4.core.Organization", "openminds.v4.core.Person"],
            "manufacturer",
            multiple=True,
            unique_items=True,
            min_items=1,
            description="no description available",
            instructions="Add the manufacturer (private or industrial) that constructed this device.",
        ),
        Property(
            "name",
            str,
            "name",
            formatting="text/plain",
            required=True,
            description="Word or phrase that constitutes the distinctive designation of the electrode array.",
            instructions="Enter a descriptive name for this device, preferably including the model name as defined by the manufacturer.",
        ),
        Property(
            "number_of_electrodes",
            int,
            "numberOfElectrodes",
            required=True,
            description="no description available",
            instructions="Enter the number of electrodes that belong to this electrode array.",
        ),
        Property(
            "owners",
            ["openminds.v4.core.Consortium", "openminds.v4.core.Organization", "openminds.v4.core.Person"],
            "owner",
            multiple=True,
            unique_items=True,
            min_items=1,
            description="no description available",
            instructions="Add all parties that legally own this device.",
        ),
        Property(
            "serial_number",
            str,
            "serialNumber",
            formatting="text/plain",
            description="no description available",
            instructions="Enter the serial number of this device.",
        ),
    ]

    def __init__(
        self,
        id=None,
        conductor_material=None,
        description=None,
        device_type=None,
        digital_identifier=None,
        electrode_identifiers=None,
        insulator_material=None,
        internal_identifier=None,
        intrinsic_resistance=None,
        lookup_label=None,
        manufacturers=None,
        name=None,
        number_of_electrodes=None,
        owners=None,
        serial_number=None,
    ):
        return super().__init__(
            id=id,
            conductor_material=conductor_material,
            description=description,
            device_type=device_type,
            digital_identifier=digital_identifier,
            electrode_identifiers=electrode_identifiers,
            insulator_material=insulator_material,
            internal_identifier=internal_identifier,
            intrinsic_resistance=intrinsic_resistance,
            lookup_label=lookup_label,
            manufacturers=manufacturers,
            name=name,
            number_of_electrodes=number_of_electrodes,
            owners=owners,
            serial_number=serial_number,
        )
