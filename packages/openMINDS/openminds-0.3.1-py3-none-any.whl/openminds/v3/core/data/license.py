"""
Structured information on a used license.
"""

# this file was auto-generated!

from openminds.base import IRI

from openminds.base import LinkedMetadata
from openminds.properties import Property


class License(LinkedMetadata):
    """
    Structured information on a used license.
    """

    type_ = "https://openminds.ebrains.eu/core/License"
    context = {"@vocab": "https://openminds.ebrains.eu/vocab/"}
    schema_version = "v3.0"

    properties = [
        Property(
            "full_name",
            str,
            "fullName",
            formatting="text/plain",
            required=True,
            description="Whole, non-abbreviated name of the license.",
            instructions="Enter the full name of this license.",
        ),
        Property(
            "legal_code",
            IRI,
            "legalCode",
            required=True,
            description="Type of legislation that claims to cover the law system (complete or parts) as it existed at the time the code was enacted.",
            instructions="Enter the internationalized resource identifier (IRI) to the legal code of this license.",
        ),
        Property(
            "short_name",
            str,
            "shortName",
            formatting="text/plain",
            required=True,
            description="Shortened or fully abbreviated name of the license.",
            instructions="Enter a short name (or alias) for this license that could be used as a shortened display title (e.g., for web services with too little space to display the full name).",
        ),
        Property(
            "webpages",
            str,
            "webpage",
            multiple=True,
            unique_items=True,
            min_items=1,
            formatting="text/plain",
            description="Hypertext document (block of information) found on the World Wide Web.",
            instructions="Enter the internationalized resource identifiers (IRIs) to webpages related to this license (e.g., a homepage).",
        ),
    ]

    def __init__(self, id=None, full_name=None, legal_code=None, short_name=None, webpages=None):
        return super().__init__(
            id=id,
            full_name=full_name,
            legal_code=legal_code,
            short_name=short_name,
            webpages=webpages,
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


License.agpl_3_0_only = License(
    id="https://openminds.ebrains.eu/instances/licenses/AGPL-3.0-only",
    full_name="GNU Affero General Public License v3.0 only",
    legal_code=IRI("https://www.gnu.org/licenses/agpl-3.0.txt"),
    short_name="AGPL-3.0-only",
    webpages=[
        "https://www.gnu.org/licenses/agpl-3.0.html",
        "https://spdx.org/licenses/AGPL-3.0-only.html",
        "https://opensource.org/licenses/AGPL-3.0",
    ],
)
License.apache_2_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/Apache-2.0",
    full_name="Apache License 2.0",
    legal_code=IRI("https://www.apache.org/licenses/LICENSE-2.0.txt"),
    short_name="Apache-2.0",
    webpages=[
        "https://www.apache.org/licenses/LICENSE-2.0",
        "https://spdx.org/licenses/Apache-2.0.html",
        "https://opensource.org/licenses/Apache-2.0",
    ],
)
License.bsd_2__clause = License(
    id="https://openminds.ebrains.eu/instances/licenses/BSD-2-Clause",
    full_name="BSD 2-Clause 'Simplified' License",
    legal_code=IRI("https://spdx.org/licenses/BSD-2-Clause.html"),
    short_name="BSD-2-Clause",
    webpages=["https://opensource.org/licenses/BSD-2-Clause", "https://spdx.org/licenses/BSD-2-Clause.html"],
)
License.bsd_3__clause = License(
    id="https://openminds.ebrains.eu/instances/licenses/BSD-3-Clause",
    full_name="BSD 3-Clause 'New' or 'Revised' License",
    legal_code=IRI("https://spdx.org/licenses/BSD-3-Clause.html"),
    short_name="BSD-3-Clause",
    webpages=["https://opensource.org/licenses/BSD-3-Clause", "https://spdx.org/licenses/BSD-3-Clause.html"],
)
License.bsd_4__clause = License(
    id="https://openminds.ebrains.eu/instances/licenses/BSD-4-Clause",
    full_name="BSD 4-Clause 'Original' or 'Old' License",
    legal_code=IRI("https://spdx.org/licenses/BSD-4-Clause.html"),
    short_name="BSD-4-Clause",
    webpages=["https://spdx.org/licenses/BSD-4-Clause.html"],
)
License.cc0_1_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/CC0-1.0",
    full_name="Creative Commons Zero v1.0 Universal",
    legal_code=IRI("https://creativecommons.org/publicdomain/zero/1.0/legalcode"),
    short_name="CC0-1.0",
    webpages=["https://creativecommons.org/publicdomain/zero/1.0", "https://spdx.org/licenses/CC0-1.0.html"],
)
License.cc_by_4_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/CC-BY-4.0",
    full_name="Creative Commons Attribution 4.0 International",
    legal_code=IRI("https://creativecommons.org/licenses/by/4.0/legalcode"),
    short_name="CC-BY-4.0",
    webpages=["https://creativecommons.org/licenses/by/4.0", "https://spdx.org/licenses/CC-BY-4.0.html"],
)
License.cc_by_nc_4_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/CC-BY-NC-4.0",
    full_name="Creative Commons Attribution Non Commercial 4.0 International",
    legal_code=IRI("https://creativecommons.org/licenses/by-nc/4.0/legalcode"),
    short_name="CC-BY-NC-4.0",
    webpages=["https://creativecommons.org/licenses/by-nc/4.0", "https://spdx.org/licenses/CC-BY-NC-4.0.html"],
)
License.cc_by_nc_nd_4_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/CC-BY-NC-ND-4.0",
    full_name="Creative Commons Attribution Non Commercial No Derivatives 4.0 International",
    legal_code=IRI("https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode"),
    short_name="CC-BY-NC-ND-4.0",
    webpages=["https://creativecommons.org/licenses/by-nc-nd/4.0", "https://spdx.org/licenses/CC-BY-NC-ND-4.0.html"],
)
License.cc_by_nc_sa_4_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/CC-BY-NC-SA-4.0",
    full_name="Creative Commons Attribution Non Commercial Share Alike 4.0 International",
    legal_code=IRI("https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode"),
    short_name="CC-BY-NC-SA-4.0",
    webpages=["https://creativecommons.org/licenses/by-nc-sa/4.0", "https://spdx.org/licenses/CC-BY-NC-SA-4.0.html"],
)
License.cc_by_nd_4_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/CC-BY-ND-4.0",
    full_name="Creative Commons Attribution No Derivatives 4.0 International",
    legal_code=IRI("https://creativecommons.org/licenses/by-nd/4.0/legalcode"),
    short_name="CC-BY-ND-4.0",
    webpages=["https://creativecommons.org/licenses/by-nd/4.0", "https://spdx.org/licenses/CC-BY-ND-4.0.html"],
)
License.cc_by_sa_4_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/CC-BY-SA-4.0",
    full_name="Creative Commons Attribution Share Alike 4.0 International",
    legal_code=IRI("https://creativecommons.org/licenses/by-sa/4.0/legalcode"),
    short_name="CC-BY-SA-4.0",
    webpages=["https://creativecommons.org/licenses/by-sa/4.0", "https://spdx.org/licenses/CC-BY-SA-4.0.html"],
)
License.cecill_2_1 = License(
    id="https://openminds.ebrains.eu/instances/licenses/CECILL-2.1",
    full_name="CeCILL Free Software License Agreement v2.1",
    legal_code=IRI("https://spdx.org/licenses/CECILL-2.1.html"),
    short_name="CECILL-2.1",
    webpages=["https://opensource.org/licenses/CECILL-2.1", "https://spdx.org/licenses/CECILL-2.1.html"],
)
License.donders_institute_dua_ru_di_hd_1_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/DondersInstitute-DUA-RU-DI-HD-1-0",
    full_name="Donder’s Institute DUA Version RU-DI-HD-1.0",
    legal_code=IRI("https://data.donders.ru.nl/doc/dua/RU-DI-HD-1.0.html"),
    short_name="RU-DI-HD-1.0",
)
License.ebrains_dua_4_hdg = License(
    id="https://openminds.ebrains.eu/instances/licenses/EBRAINS-DUA-4-HDG",
    full_name="The use of this dataset requires that the user cites the associated DOI and adheres to the conditions of use that are contained in the Data Use Agreement.",
    legal_code=IRI("https://strapi-prod.sos-ch-dk-2.exo.io/EBRAINS_Data_Use_Agreement_90858e7836_ef3ee29d50.pdf"),
    short_name="EBRAINS-DUA-4-HDG",
    webpages=["https://ebrains.eu/terms/#general-terms-of-use"],
)
License.ebrains_dua_4_hdg_nc = License(
    id="https://openminds.ebrains.eu/instances/licenses/EBRAINS-DUA-4-HDG-NC",
    full_name="The use of this dataset requires that the user cites the associated DOI and adheres to the conditions of use that are contained in the Data Use Agreement. You may not use the dataset for commercial purposes.",
    legal_code=IRI("https://strapi-prod.sos-ch-dk-2.exo.io/EBRAINS_Data_Use_Agreement_90858e7836_ef3ee29d50.pdf"),
    short_name="EBRAINS-DUA-4-HDG-NC",
    webpages=["https://ebrains.eu/terms/#general-terms-of-use"],
)
License.eupl_1_2 = License(
    id="https://openminds.ebrains.eu/instances/licenses/EUPL-1.2",
    full_name="European Union Public License 1.2",
    legal_code=IRI("https://joinup.ec.europa.eu/sites/default/files/custom-page/attachment/eupl_v1.2_en.pdf"),
    short_name="EUPL-1.2",
    webpages=[
        "https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12",
        "https://spdx.org/licenses/EUPL-1.2.html",
        "https://opensource.org/licenses/EUPL-1.2",
    ],
)
License.gpl_1_0_only = License(
    id="https://openminds.ebrains.eu/instances/licenses/GPL-1.0-only",
    full_name="GNU General Public License v1.0 only",
    legal_code=IRI("https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html"),
    short_name="GPL-1.0-only",
    webpages=["https://www.gnu.org/licenses/old-licenses/gpl-1.0.html", "https://spdx.org/licenses/GPL-1.0-only.html"],
)
License.gpl_1_0_or_later = License(
    id="https://openminds.ebrains.eu/instances/licenses/GPL-1.0-or-later",
    full_name="GNU General Public License v1.0 or later",
    legal_code=IRI("https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html"),
    short_name="GPL-1.0-or-later",
    webpages=["https://spdx.org/licenses/GPL-1.0-or-later.html"],
)
License.gpl_2_0_only = License(
    id="https://openminds.ebrains.eu/instances/licenses/GPL-2.0-only",
    full_name="GNU General Public License v2.0 only",
    legal_code=IRI("https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html"),
    short_name="GPL-2.0-only",
    webpages=[
        "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
        "https://spdx.org/licenses/GPL-2.0-only.html",
        "https://opensource.org/licenses/GPL-2.0",
    ],
)
License.gpl_2_0_or_later = License(
    id="https://openminds.ebrains.eu/instances/licenses/GPL-2.0-or-later",
    full_name="GNU General Public License v2.0 or later",
    legal_code=IRI("https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html"),
    short_name="GPL-2.0-or-later",
    webpages=["https://spdx.org/licenses/GPL-2.0-or-later.html"],
)
License.gpl_3_0_only = License(
    id="https://openminds.ebrains.eu/instances/licenses/GPL-3.0-only",
    full_name="GNU General Public License v3.0 only",
    legal_code=IRI("https://www.gnu.org/licenses/gpl-3.0-standalone.html"),
    short_name="GPL-3.0-only",
    webpages=[
        "https://www.gnu.org/licenses/gpl-3.0.html",
        "https://spdx.org/licenses/GPL-3.0-only.html",
        "https://opensource.org/licenses/GPL-3.0",
    ],
)
License.gpl_3_0_or_later = License(
    id="https://openminds.ebrains.eu/instances/licenses/GPL-3.0-or-later",
    full_name="GNU General Public License v3.0 or later",
    legal_code=IRI("https://www.gnu.org/licenses/gpl-3.0-standalone.html"),
    short_name="GPL-3.0-or-later",
    webpages=["https://spdx.org/licenses/GPL-3.0-or-later.html"],
)
License.lgpl_2_0_only = License(
    id="https://openminds.ebrains.eu/instances/licenses/LGPL-2.0-only",
    full_name="GNU Library General Public License v2 only",
    legal_code=IRI("https://www.gnu.org/licenses/old-licenses/lgpl-2.0-standalone.html"),
    short_name="LGPL-2.0-only",
    webpages=[
        "https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html",
        "https://spdx.org/licenses/LGPL-2.0-only.html",
    ],
)
License.lgpl_2_0_or_later = License(
    id="https://openminds.ebrains.eu/instances/licenses/LGPL-2.0-or-later",
    full_name="GNU Lesser General Public License v2.0 or later",
    legal_code=IRI("https://www.gnu.org/licenses/old-licenses/lgpl-2.0-standalone.html"),
    short_name="LGPL-2.0-or-later",
    webpages=["https://spdx.org/licenses/LGPL-2.0-or-later.html", "https://spdx.org/licenses/LGPL-2.0+.html"],
)
License.lgpl_2_1_only = License(
    id="https://openminds.ebrains.eu/instances/licenses/LGPL-2.1-only",
    full_name="GNU Lesser General Public License v2.1 only",
    legal_code=IRI("https://www.gnu.org/licenses/old-licenses/lgpl-2.1-standalone.html"),
    short_name="LGPL-2.1-only",
    webpages=[
        "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html",
        "https://spdx.org/licenses/LGPL-2.1-only.html",
        "https://opensource.org/licenses/LGPL-2.1",
    ],
)
License.lgpl_2_1_or_later = License(
    id="https://openminds.ebrains.eu/instances/licenses/LGPL-2.1-or-later",
    full_name="GNU Lesser General Public License v2.1 or later",
    legal_code=IRI("https://www.gnu.org/licenses/old-licenses/lgpl-2.1-standalone.html"),
    short_name="LGPL-2.1-or-later",
    webpages=["https://spdx.org/licenses/LGPL-2.1-or-later.html"],
)
License.lgpl_3_0_only = License(
    id="https://openminds.ebrains.eu/instances/licenses/LGPL-3.0-only",
    full_name="GNU Lesser General Public License v3.0 only",
    legal_code=IRI("https://www.gnu.org/licenses/lgpl-3.0-standalone.html"),
    short_name="LGPL-3.0-only",
    webpages=[
        "https://www.gnu.org/licenses/lgpl-3.0.html",
        "https://spdx.org/licenses/LGPL-3.0-only.html",
        "https://opensource.org/licenses/LGPL-3.0",
    ],
)
License.lgpl_3_0_or_later = License(
    id="https://openminds.ebrains.eu/instances/licenses/LGPL-3.0-or-later",
    full_name="GNU Lesser General Public License v3.0 or later",
    legal_code=IRI("https://www.gnu.org/licenses/lgpl-3.0-standalone.html"),
    short_name="LGPL-3.0-or-later",
    webpages=["https://spdx.org/licenses/LGPL-3.0-or-later.html"],
)
License.mit = License(
    id="https://openminds.ebrains.eu/instances/licenses/MIT",
    full_name="MIT License",
    legal_code=IRI("https://spdx.org/licenses/MIT.html"),
    short_name="MIT",
    webpages=["https://opensource.org/licenses/MIT", "https://spdx.org/licenses/MIT.html"],
)
License.mpl_2_0 = License(
    id="https://openminds.ebrains.eu/instances/licenses/MPL-2.0",
    full_name="Mozilla Public License 2.0",
    legal_code=IRI("https://www.mozilla.org/MPL/2.0/"),
    short_name="MPL-2.0",
    webpages=[
        "https://www.mozilla.org/MPL/",
        "https://spdx.org/licenses/MPL-2.0.html",
        "https://opensource.org/licenses/MPL-2.0",
    ],
)
License.youtube = License(
    id="https://openminds.ebrains.eu/instances/licenses/youtube",
    full_name="Standard YouTube License",
    legal_code=IRI("https://www.youtube.com/t/terms"),
    short_name="youtube",
)
