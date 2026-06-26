import logging
import gettext

import pycountry


_log = logging.getLogger(__name__)


WITHOUT_TRANSLATION = {None, "-", "", "UNIONE EUROPEA"}
FIXES = {
    "it": {
        "COREA": "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF",
        "MALESIA": "MALAYSIA",
        "TAILANDIA": "THAILAND",
        "TAIWAN": "TAIWAN, PROVINCE OF CHINA",
    }
}


def country_name_to_english(name: str, language: str) -> str | None:
    name = name.strip().upper()

    translation = gettext.translation(
        "iso3166-1",
        pycountry.LOCALES_DIR,
        languages=[language],
    )
    # TODO: cache
    translation_map = {
        v.upper().strip(): k.upper().strip()
        for k, v in translation._catalog.items()
        if k and v
    }

    translated = translation_map.get(name)

    if not translated:
        _log.warning(
            "Unknown country name (not mapped to English): %r (%s)",
            name,
            language,
        )
        return None

    return translated


def country_name_to_alpha_2(name: str, language: str) -> str | None:
    if not name:
        return None

    name = name.strip().upper()

    if name in WITHOUT_TRANSLATION:
        return None

    if name in FIXES.get(language, {}):
        translated_name = FIXES[language][name]
    else:
        translated_name = country_name_to_english(name, language)

    if not translated_name:
        return f"__unknown_translation__{name}"

    country = pycountry.countries.get(name=translated_name)

    if not country:
        _log.warning(
            "Unknown country name (not mapped to ISO): %r (%s)",
            translated_name,
            language,
        )
        return f"__unknown_iso__{translated_name}"

    return country.alpha_2
