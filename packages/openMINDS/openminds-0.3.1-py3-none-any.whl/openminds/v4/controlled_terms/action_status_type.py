"""
Structured information about the status of an action.
"""

# this file was auto-generated!

from openminds.base import IRI

from openminds.base import LinkedMetadata
from openminds.properties import Property


class ActionStatusType(LinkedMetadata):
    """
    Structured information about the status of an action.
    """

    type_ = "https://openminds.om-i.org/types/ActionStatusType"
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
            description="Longer statement or account giving the characteristics of the action status type.",
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
            description="Word or phrase that constitutes the distinctive designation of the action status type.",
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


ActionStatusType.active = ActionStatusType(
    id="https://openminds.om-i.org/instances/actionStatusType/active",
    definition="An in-progress action.",
    name="active",
    preferred_ontology_identifier=IRI("https://schema.org/ActiveActionStatus"),
    synonyms=["active action status", "active action"],
)
ActionStatusType.completed = ActionStatusType(
    id="https://openminds.om-i.org/instances/actionStatusType/completed",
    definition="An action that has already taken place with a successful outcome.",
    name="completed",
    preferred_ontology_identifier=IRI("https://schema.org/CompletedActionStatus"),
    synonyms=["completed action status", "completed action", "finished successfully"],
)
ActionStatusType.failed = ActionStatusType(
    id="https://openminds.om-i.org/instances/actionStatusType/failed",
    definition="An action that failed to complete or completed but produced an error.",
    name="failed",
    preferred_ontology_identifier=IRI("https://schema.org/FailedActionStatus"),
    synonyms=["failed action status", "failed action", "finished unsuccessfully", "error"],
)
ActionStatusType.inactive = ActionStatusType(
    id="https://openminds.om-i.org/instances/actionStatusType/inactive",
    definition="A pending or suspended action.",
    name="inactive",
    synonyms=["inactive action status", "inactive action"],
)
ActionStatusType.paused = ActionStatusType(
    id="https://openminds.om-i.org/instances/actionStatusType/paused",
    definition="A temporarily stopped action that can be resumed at a later point in time.",
    name="paused",
    synonyms=["paused action type", "paused action", "suspended"],
)
ActionStatusType.pending = ActionStatusType(
    id="https://openminds.om-i.org/instances/actionStatusType/pending",
    definition="An action which is awaiting execution.",
    name="pending",
    synonyms=["queued", "pending action type", "pending action"],
)
ActionStatusType.potential = ActionStatusType(
    id="https://openminds.om-i.org/instances/actionStatusType/potential",
    definition="A description of an action that is supported.",
    name="potential",
    preferred_ontology_identifier=IRI("https://schema.org/PotentialActionStatus"),
    synonyms=["potential action type", "potential action"],
)
