"""
<description not available>
"""

# this file was auto-generated!

from datetime import datetime, time

from openminds.base import LinkedMetadata
from openminds.properties import Property


class StimulationActivity(LinkedMetadata):
    """
    <description not available>
    """

    type_ = "https://openminds.om-i.org/types/StimulationActivity"
    context = {"@vocab": "https://openminds.om-i.org/props/"}
    schema_version = "latest"

    properties = [
        Property(
            "custom_property_sets",
            "openminds.latest.core.CustomPropertySet",
            "customPropertySet",
            multiple=True,
            unique_items=True,
            min_items=1,
            description="no description available",
            instructions="Add any user-defined parameters grouped in context-specific sets that are not covered in the standardized properties of this activity.",
        ),
        Property(
            "description",
            str,
            "description",
            formatting="text/markdown",
            multiline=True,
            description="Longer statement or account giving the characteristics of the stimulation activity.",
            instructions="Enter a description of this activity.",
        ),
        Property(
            "end_time",
            [datetime, time],
            "endTime",
            description="no description available",
            instructions="Enter the date and/or time on when this activity ended, formatted as either '2023-02-07T16:00:00+00:00' (date-time) or '16:00:00+00:00' (time).",
        ),
        Property(
            "inputs",
            [
                "openminds.latest.core.SubjectGroupState",
                "openminds.latest.core.SubjectState",
                "openminds.latest.core.TissueSampleCollectionState",
                "openminds.latest.core.TissueSampleState",
            ],
            "input",
            multiple=True,
            unique_items=True,
            min_items=1,
            required=True,
            description="Something or someone that is put into or participates in a process or machine.",
            instructions="Add all states of the specimen(s) that are being stimulated during this activity.",
        ),
        Property(
            "is_part_of",
            "openminds.latest.core.DatasetVersion",
            "isPartOf",
            required=True,
            description="Reference to the ensemble of multiple things or beings.",
            instructions="Add the dataset version in which this activity was conducted.",
        ),
        Property(
            "lookup_label",
            str,
            "lookupLabel",
            formatting="text/plain",
            description="no description available",
            instructions="Enter a lookup label for this activity that may help you to find this instance more easily.",
        ),
        Property(
            "outputs",
            [
                "openminds.latest.core.File",
                "openminds.latest.core.FileBundle",
                "openminds.latest.core.SubjectGroupState",
                "openminds.latest.core.SubjectState",
                "openminds.latest.core.TissueSampleCollectionState",
                "openminds.latest.core.TissueSampleState",
            ],
            "output",
            multiple=True,
            unique_items=True,
            min_items=1,
            required=True,
            description="Something or someone that comes out of, is delivered or produced by a process or machine.",
            instructions="Add all states of the specimen(s) that were stimulated as a result of this activity, and all files or file bundles generated.",
        ),
        Property(
            "performed_by",
            ["openminds.latest.computation.SoftwareAgent", "openminds.latest.core.Person"],
            "performedBy",
            multiple=True,
            unique_items=True,
            min_items=1,
            description="no description available",
            instructions="Add all agents that performed this activity.",
        ),
        Property(
            "preparation_design",
            "openminds.latest.controlled_terms.PreparationType",
            "preparationDesign",
            description="no description available",
            instructions="Add the initial preparation type for this activity.",
        ),
        Property(
            "protocols",
            "openminds.latest.core.Protocol",
            "protocol",
            multiple=True,
            unique_items=True,
            min_items=1,
            required=True,
            description="Plan that describes the process of a scientific or medical experiment, treatment, or procedure.",
            instructions="Add all protocols used during this activity.",
        ),
        Property(
            "setup",
            "openminds.latest.core.Setup",
            "setup",
            description="no description available",
            instructions="Add the setup used during this stimulation activity.",
        ),
        Property(
            "start_time",
            [datetime, time],
            "startTime",
            description="no description available",
            instructions="Enter the date and/or time on when this activity started, formatted as either '2023-02-07T16:00:00+00:00' (date-time) or '16:00:00+00:00' (time).",
        ),
        Property(
            "stimuli",
            "openminds.latest.stimulation.EphysStimulus",
            "stimulus",
            multiple=True,
            unique_items=True,
            min_items=1,
            required=True,
            description="no description available",
            instructions="Add all stimuli used during this activity.",
        ),
        Property(
            "study_targets",
            [
                "openminds.latest.controlled_terms.AuditoryStimulusType",
                "openminds.latest.controlled_terms.BiologicalOrder",
                "openminds.latest.controlled_terms.BiologicalSex",
                "openminds.latest.controlled_terms.BreedingType",
                "openminds.latest.controlled_terms.CellCultureType",
                "openminds.latest.controlled_terms.CellType",
                "openminds.latest.controlled_terms.Disease",
                "openminds.latest.controlled_terms.DiseaseModel",
                "openminds.latest.controlled_terms.ElectricalStimulusType",
                "openminds.latest.controlled_terms.GeneticStrainType",
                "openminds.latest.controlled_terms.GustatoryStimulusType",
                "openminds.latest.controlled_terms.Handedness",
                "openminds.latest.controlled_terms.MolecularEntity",
                "openminds.latest.controlled_terms.OlfactoryStimulusType",
                "openminds.latest.controlled_terms.OpticalStimulusType",
                "openminds.latest.controlled_terms.Organ",
                "openminds.latest.controlled_terms.OrganismSubstance",
                "openminds.latest.controlled_terms.OrganismSystem",
                "openminds.latest.controlled_terms.Species",
                "openminds.latest.controlled_terms.SubcellularEntity",
                "openminds.latest.controlled_terms.TactileStimulusType",
                "openminds.latest.controlled_terms.TermSuggestion",
                "openminds.latest.controlled_terms.TissueSampleType",
                "openminds.latest.controlled_terms.UBERONParcellation",
                "openminds.latest.controlled_terms.VisualStimulusType",
                "openminds.latest.sands.CustomAnatomicalEntity",
                "openminds.latest.sands.ParcellationEntity",
                "openminds.latest.sands.ParcellationEntityVersion",
            ],
            "studyTarget",
            multiple=True,
            unique_items=True,
            min_items=1,
            description="Structure or function that was targeted within a study.",
            instructions="Add all study targets of this activity.",
        ),
    ]

    def __init__(
        self,
        id=None,
        custom_property_sets=None,
        description=None,
        end_time=None,
        inputs=None,
        is_part_of=None,
        lookup_label=None,
        outputs=None,
        performed_by=None,
        preparation_design=None,
        protocols=None,
        setup=None,
        start_time=None,
        stimuli=None,
        study_targets=None,
    ):
        return super().__init__(
            id=id,
            custom_property_sets=custom_property_sets,
            description=description,
            end_time=end_time,
            inputs=inputs,
            is_part_of=is_part_of,
            lookup_label=lookup_label,
            outputs=outputs,
            performed_by=performed_by,
            preparation_design=preparation_design,
            protocols=protocols,
            setup=setup,
            start_time=start_time,
            stimuli=stimuli,
            study_targets=study_targets,
        )
