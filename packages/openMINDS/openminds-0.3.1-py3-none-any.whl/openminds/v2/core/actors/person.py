"""
Structured information on a person.
"""

# this file was auto-generated!


from openminds.base import LinkedMetadata
from openminds.properties import Property


class Person(LinkedMetadata):
    """
    Structured information on a person.
    """

    type_ = "https://openminds.ebrains.eu/core/Person"
    context = {"@vocab": "https://openminds.ebrains.eu/vocab/"}
    schema_version = "v2.0"

    properties = [
        Property(
            "affiliations",
            "openminds.v2.core.Affiliation",
            "affiliation",
            multiple=True,
            unique_items=True,
            min_items=1,
            description="Declaration of a person being closely associated to an organization.",
            instructions="Add the current and, if necessary, past affiliations of this person",
        ),
        Property(
            "contact_information",
            "openminds.v2.core.ContactInformation",
            "contactInformation",
            description="Any available way used to contact a person or business (e.g., address, phone number, email address, etc.).",
            instructions="Add the contact information of this person.",
        ),
        Property(
            "digital_identifiers",
            "openminds.v2.core.ORCID",
            "digitalIdentifier",
            multiple=True,
            unique_items=True,
            min_items=1,
            description="Digital handle to identify objects or legal persons.",
            instructions="Add one or several globally unique and persistent digital identifier for this person.",
        ),
        Property(
            "family_name",
            str,
            "familyName",
            formatting="text/plain",
            description="Name borne in common by members of a family.",
            instructions="Enter the family name of this person.",
        ),
        Property(
            "given_name",
            str,
            "givenName",
            formatting="text/plain",
            required=True,
            description="Name given to a person, including all potential middle names, but excluding the family name.",
            instructions="Enter the given name of this person.",
        ),
    ]

    def __init__(
        self,
        id=None,
        affiliations=None,
        contact_information=None,
        digital_identifiers=None,
        family_name=None,
        given_name=None,
    ):
        return super().__init__(
            id=id,
            affiliations=affiliations,
            contact_information=contact_information,
            digital_identifiers=digital_identifiers,
            family_name=family_name,
            given_name=given_name,
        )
