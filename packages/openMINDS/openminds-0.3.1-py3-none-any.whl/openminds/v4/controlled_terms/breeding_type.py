"""
<description not available>
"""

# this file was auto-generated!

from openminds.base import IRI

from openminds.base import LinkedMetadata
from openminds.properties import Property


class BreedingType(LinkedMetadata):
    """
    <description not available>
    """

    type_ = "https://openminds.om-i.org/types/BreedingType"
    context = {"@vocab": "https://openminds.om-i.org/props/"}
    schema_version = "v4.0"

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
            description="Longer statement or account giving the characteristics of the breeding type.",
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
            description="Word or phrase that constitutes the distinctive designation of the breeding type.",
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


BreedingType.coisogenic = BreedingType(
    id="https://openminds.om-i.org/instances/breedingType/coisogenic",
    definition="'Coisogenic' breeding  is a type of inbreeding where the offspring differs at only a single locus through a mutation occurring in the original inbred strain.",
    name="coisogenic",
)
BreedingType.congenic = BreedingType(
    id="https://openminds.om-i.org/instances/breedingType/congenic",
    definition="'Congenic' breeding is the production of offspring from repeated backcrossing into an inbred (background) strain, with selection for a particular marker, ideally a single gene from another strain.",
    name="congenic",
)
BreedingType.hybrid = BreedingType(
    id="https://openminds.om-i.org/instances/breedingType/hybrid",
    definition="A 'hybrid' is an organism that resulted from special outbreeding of two species (normally within the same genus).",
    name="hybrid",
)
BreedingType.inbred = BreedingType(
    id="https://openminds.om-i.org/instances/breedingType/inbred",
    definition="'Inbred' breeding (or inbreeding) is the production of offspring from mating organisms that are genetically closely related (same background breed).",
    name="inbred",
)
BreedingType.outbred = BreedingType(
    id="https://openminds.om-i.org/instances/breedingType/outbred",
    definition="'Outbred' breeding (or outbreeding) is the production of offspring from mating organisms that belong to two different background breeds.",
    name="outbred",
)
BreedingType.selective_inbred = BreedingType(
    id="https://openminds.om-i.org/instances/breedingType/selectiveInbred",
    definition="'Selective inbred' breeding (or selective inbreeding) is the production of offspring from mating organisms that are genetically closely related (same background breed) and have been selected based on a particular phenotype.",
    name="selective inbred",
)
