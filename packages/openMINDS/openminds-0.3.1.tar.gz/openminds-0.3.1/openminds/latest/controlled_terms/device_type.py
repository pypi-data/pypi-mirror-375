"""
<description not available>
"""

# this file was auto-generated!

from openminds.base import IRI

from openminds.base import LinkedMetadata
from openminds.properties import Property


class DeviceType(LinkedMetadata):
    """
    <description not available>
    """

    type_ = "https://openminds.om-i.org/types/DeviceType"
    context = {"@vocab": "https://openminds.om-i.org/props/"}
    schema_version = "latest"

    properties = [
        Property(
            "definition",
            str,
            "definition",
            formatting="text/markdown",
            multiline=True,
            description="Short, but precise statement of the meaning of a word, word group, sign or a symbol.",
            instructions="Enter one sentence for defining this term.",
        ),
        Property(
            "description",
            str,
            "description",
            formatting="text/markdown",
            multiline=True,
            description="Longer statement or account giving the characteristics of the device type.",
            instructions="Enter a short text describing this term.",
        ),
        Property(
            "interlex_identifier",
            IRI,
            "interlexIdentifier",
            description="Persistent identifier for a term registered in the InterLex project.",
            instructions="Enter the internationalized resource identifier (IRI) pointing to the integrated ontology entry in the InterLex project.",
        ),
        Property(
            "knowledge_space_link",
            IRI,
            "knowledgeSpaceLink",
            description="Persistent link to an encyclopedia entry in the Knowledge Space project.",
            instructions="Enter the internationalized resource identifier (IRI) pointing to the wiki page of the corresponding term in the KnowledgeSpace.",
        ),
        Property(
            "name",
            str,
            "name",
            formatting="text/plain",
            required=True,
            description="Word or phrase that constitutes the distinctive designation of the device type.",
            instructions="Controlled term originating from a defined terminology.",
        ),
        Property(
            "preferred_ontology_identifier",
            IRI,
            "preferredOntologyIdentifier",
            description="Persistent identifier of a preferred ontological term.",
            instructions="Enter the internationalized resource identifier (IRI) pointing to the preferred ontological term.",
        ),
        Property(
            "synonyms",
            str,
            "synonym",
            multiple=True,
            unique_items=True,
            min_items=1,
            formatting="text/plain",
            description="Words or expressions used in the same language that have the same or nearly the same meaning in some or all senses.",
            instructions="Enter one or several synonyms (including abbreviations) for this controlled term.",
        ),
    ]

    def __init__(
        self,
        id=None,
        definition=None,
        description=None,
        interlex_identifier=None,
        knowledge_space_link=None,
        name=None,
        preferred_ontology_identifier=None,
        synonyms=None,
    ):
        return super().__init__(
            id=id,
            definition=definition,
            description=description,
            interlex_identifier=interlex_identifier,
            knowledge_space_link=knowledge_space_link,
            name=name,
            preferred_ontology_identifier=preferred_ontology_identifier,
            synonyms=synonyms,
        )

    @classmethod
    def instances(cls):
        return [value for value in cls.__dict__.values() if isinstance(value, cls)]

    @classmethod
    def by_name(cls, name):
        if cls._instance_lookup is None:
            cls._instance_lookup = {}
            for instance in cls.instances():
                cls._instance_lookup[instance.name] = instance
                if instance.synonyms:
                    for synonym in instance.synonyms:
                        cls._instance_lookup[synonym] = instance
        return cls._instance_lookup[name]


DeviceType.c_tscanner = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/CTscanner",
    definition="A 'CT scanner' is an x-ray machine that creates and combines serial two-dimensional x-ray images (sections) with the aid of a computer to generate cross-sectional views and/or three-dimensional images of internal body structures (e.g., bones, blood vessels or soft tissues).",
    name="CT scanner",
    synonyms=["CAT scanner", "computed axial tomography scanner", "computed tomography scanner"],
)
DeviceType.closed_bore_mri_scanner = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/closedBoreMRIScanner",
    definition="'Closed-bore MRI scanners' are high-field scanners which feature a magnet surrounding the patient creating a capsule-like space (standard or wide) where the patient lies on.",
    name="closed-bore MRI scanner",
    synonyms=[
        "closed-bore magnetic resonance imaging scanner",
        "closed magnetic resonance imaging scanner",
        "closed MRI scanner",
    ],
)
DeviceType.electronic_amplifier = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/electronicAmplifier",
    definition="An 'electronic amplifier' is a device that increases the power (voltage or current) of a time-varying signal.",
    interlex_identifier=IRI("http://uri.interlex.org/base/ilx_0100567"),
    name="electronic amplifier",
    preferred_ontology_identifier=IRI("http://uri.neuinfo.org/nif/nifstd/nlx_27076"),
    synonyms=["amp", "amplifier"],
)
DeviceType.microscope = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/microscope",
    definition="A 'microscope' is an instrument used to obtain a magnified image of small objects and reveal details of structures not otherwise distinguishable.",
    interlex_identifier=IRI("http://uri.interlex.org/base/ilx_0106921"),
    name="microscope",
    preferred_ontology_identifier=IRI("http://uri.neuinfo.org/nif/nifstd/birnlex_2106"),
)
DeviceType.microtome = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/microtome",
    definition="A 'microtome' is a mechanical instrument with a steel, glass or diamond blade used to cut (typically) biological specimens into very thin segments for further treatment and ultimately microscopic or histologic examination.",
    interlex_identifier=IRI("http://uri.interlex.org/base/ilx_0106925"),
    name="microtome",
    preferred_ontology_identifier=IRI("http://purl.obolibrary.org/obo/OBI_0400168"),
)
DeviceType.mr_iscanner = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/MRIscanner",
    definition="An 'MRI scanner' is a machine that uses strong magnetic fields, magnetic field gradients, and radio waves to generate static or time-resolved three-dimensional images of the anatomy and physiological processes of the body.",
    interlex_identifier=IRI("http://uri.interlex.org/base/ilx_0106463"),
    name="MRI scanner",
    preferred_ontology_identifier=IRI("http://uri.neuinfo.org/nif/nifstd/birnlex_2100"),
    synonyms=["magnetic resonance imaging scanner"],
)
DeviceType.open_bore_mri_scanner = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/openBoreMRIScanner",
    definition="'Open-bore MRI scanners' are low-field scanners which have a magnetic top and bottom, but are otherwise open, increasing patient's comfort and unobstructed view of the scanning area.",
    name="open-bore MRI scanner",
    synonyms=[
        "open-bore magnetic resonance imaging scanner",
        "open magnetic resonance imaging scanner",
        "open MRI scanner",
    ],
)
DeviceType.standard_bore_mri_scanner = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/standardBoreMRIScanner",
    definition="A 'standard-bore MRI scanner' is a closed high-field scanner which features a magnet surrounding the patient creating a capsule-like space where the patient lies on.",
    name="standard-bore MRI scanner",
    synonyms=[
        "standard-bore magnetic resonance imaging scanner",
        "standard-bore closed magnetic resonance imaging scanner",
        "standard-bore closed MRI scanner",
    ],
)
DeviceType.vibrating_microtome = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/vibratingMicrotome",
    definition="A 'vibrating microtome' is an mechanical instrument with a vibrating steel blade used to cut (typically) biological specimens into thin segments for further treatment and ultimately microscopic or histologic examination.",
    interlex_identifier=IRI("http://uri.interlex.org/base/ilx_0780522"),
    name="vibrating microtome",
    synonyms=["vibratome"],
)
DeviceType.wide_bore_mri_scanner = DeviceType(
    id="https://openminds.om-i.org/instances/deviceType/wideBoreMRIScanner",
    definition="A 'wide-bore MRI scanner' is a closed high-field scanner which features a widened bore compared to the standard-bore MRI scanner.",
    name="wide-bore MRI scanner",
    synonyms=[
        "wide-bore magnetic resonance imaging scanner",
        "wide-bore closed magnetic resonance imaging scanner",
        "wide-bore closed MRI scanner",
    ],
)
