"""
<description not available>
"""

# this file was auto-generated!


from openminds.base import LinkedMetadata
from openminds.properties import Property


class TermSuggestion(LinkedMetadata):
    """
    <description not available>
    """

    type_ = "https://openminds.ebrains.eu/controlledTerms/TermSuggestion"
    context = {"@vocab": "https://openminds.ebrains.eu/vocab/"}
    schema_version = "v1.0"

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
            description="Longer statement or account giving the characteristics of the term suggestion.",
            instructions="Enter a short text describing this term.",
        ),
        Property(
            "name",
            str,
            "name",
            formatting="text/plain",
            required=True,
            description="Word or phrase that constitutes the distinctive designation of the term suggestion.",
            instructions="Controlled term originating from a defined terminology.",
        ),
        Property(
            "ontology_identifier",
            str,
            "ontologyIdentifier",
            formatting="text/plain",
            description="Term or code used to identify the term suggestion registered within a particular ontology.",
            instructions="Enter the internationalized resource identifier (IRI) pointing to the related ontological term.",
        ),
        Property(
            "terminology",
            "openminds.v1.controlled_terms.Terminology",
            "terminology",
            required=True,
            description="Nomenclature for a particular field of study.",
            instructions="Add the terminology in which the suggested term should be integrated in.",
        ),
    ]

    def __init__(
        self, id=None, definition=None, description=None, name=None, ontology_identifier=None, terminology=None
    ):
        return super().__init__(
            id=id,
            definition=definition,
            description=description,
            name=name,
            ontology_identifier=ontology_identifier,
            terminology=terminology,
        )
