"""
Structured information on the usage role of a file instance or bundle.
"""

# this file was auto-generated!

from openminds.base import IRI

from openminds.base import LinkedMetadata
from openminds.properties import Property


class FileUsageRole(LinkedMetadata):
    """
    Structured information on the usage role of a file instance or bundle.
    """

    type_ = "https://openminds.om-i.org/types/FileUsageRole"
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
            description="Longer statement or account giving the characteristics of the file usage role.",
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
            description="Word or phrase that constitutes the distinctive designation of the file usage role.",
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


FileUsageRole.data_descriptor = FileUsageRole(
    id="https://openminds.om-i.org/instances/fileUsageRole/dataDescriptor",
    definition="A 'data descriptor' describes the provenance, the structure, the applied quality assessment, and possible (re)usage of the data. It should not present hypotheses tests, new interpretations, new methods or in-depth analyses.",
    name="data descriptor",
)
FileUsageRole.logo = FileUsageRole(
    id="https://openminds.om-i.org/instances/fileUsageRole/logo",
    definition="A logo is a graphic used to aid and promote public identification and recognition.used to aid and promote public identification and recognition. ",
    name="logo",
)
FileUsageRole.preview = FileUsageRole(
    id="https://openminds.om-i.org/instances/fileUsageRole/preview",
    definition="A preview is a representative image or short movie used to peak interest for a product.",
    name="preview",
)
FileUsageRole.screenshot = FileUsageRole(
    id="https://openminds.om-i.org/instances/fileUsageRole/screenshot",
    definition="A screenshot is an image of the content displayed on the screen of a computer or mobile device.",
    name="screenshot",
)
