"""
<description not available>
"""

# this file was auto-generated!

from openminds.base import IRI

from openminds.base import LinkedMetadata
from openminds.properties import Property


class ProductAccessibility(LinkedMetadata):
    """
    <description not available>
    """

    type_ = "https://openminds.ebrains.eu/controlledTerms/ProductAccessibility"
    context = {"@vocab": "https://openminds.ebrains.eu/vocab/"}
    schema_version = "v3.0"

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
            description="Longer statement or account giving the characteristics of the product accessibility.",
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
            description="Word or phrase that constitutes the distinctive designation of the product accessibility.",
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


ProductAccessibility.controlled_access = ProductAccessibility(
    id="https://openminds.ebrains.eu/instances/productAccessibility/controlledAccess",
    definition="With 'controlled access' selected, data and metadata are both released and available free of charge, but users must logged in and authenticated themselves to access the data.",
    name="controlled access",
)
ProductAccessibility.free_access = ProductAccessibility(
    id="https://openminds.ebrains.eu/instances/productAccessibility/freeAccess",
    definition="With 'free access' selected, data and metadata are both released and become immediately available without any access restrictions.",
    name="free access",
)
ProductAccessibility.paid_access = ProductAccessibility(
    id="https://openminds.ebrains.eu/instances/productAccessibility/paidAccess",
    definition="With 'paid access' selected, data and metadata are both released, but users paid to gain access to the data (e.g., a one-time fee).",
    name="paid access",
)
ProductAccessibility.restricted_access = ProductAccessibility(
    id="https://openminds.ebrains.eu/instances/productAccessibility/restrictedAccess",
    definition="With 'restricted access' selected, metadata are released, but data remain on an access restricted server.",
    name="restricted access",
)
ProductAccessibility.retracted = ProductAccessibility(
    id="https://openminds.ebrains.eu/instances/productAccessibility/retracted",
    definition="With 'retracted' selected, metadata are released, but data are retracted.",
    name="retracted",
)
ProductAccessibility.under_embargo = ProductAccessibility(
    id="https://openminds.ebrains.eu/instances/productAccessibility/underEmbargo",
    definition="With 'under embargo' selected, metadata are released, but data remain unavailable for the public until the embargo is lifted.",
    name="under embargo",
)
