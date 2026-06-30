import functools
import gettext

import pycountry


WITHOUT_CODE = {"it": {"UNIONE EUROPEA"}}
FIXES = {
    "it": {
        "COREA": "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF",
        "MALESIA": "MALAYSIA",
        "TAILANDIA": "THAILAND",
        "TAIWAN": "TAIWAN, PROVINCE OF CHINA",
    }
}


def gen_translation_map(language: str) -> dict[str, str]:
    translation = gettext.translation(
        "iso3166-1",
        pycountry.LOCALES_DIR,
        languages=[language],
    )

    translation_map = {
        v.upper().strip(): k.upper().strip()
        for k, v in translation._catalog.items()
        if k and v
    }
    translation_map.update(FIXES.get(language, {}))
    return translation_map


@functools.cache
def gen_country_to_alpha_2_map(language: str) -> dict[str, str]:
    if language == "en":
        return {
            country.name.upper(): country.alpha_2 for country in pycountry.countries
        }

    translation_map = gen_translation_map(language)
    country_to_alpha_2 = {}
    for name, english_name in translation_map.items():
        country = pycountry.countries.get(name=english_name)
        if country:
            country_to_alpha_2[name] = country.alpha_2
    country_to_alpha_2.update(
        {name: None for name in WITHOUT_CODE.get(language, set())}
    )
    country_to_alpha_2[""] = None  # Handle empty string case
    country_to_alpha_2["-"] = None  # Handle dash case
    return country_to_alpha_2
