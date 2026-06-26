import logging
import gettext

import pycountry


_log = logging.getLogger(__name__)


def country_name_to_english(name: str, language: str) -> str | None:
    name = name.strip().upper()

    translation = gettext.translation(
        "iso3166-1",
        pycountry.LOCALES_DIR,
        languages=[language],
    )

    translated = translation.gettext(name)
    translated = translated.strip().upper()

    if translated == name:
        _log.warning(
            "Unknown country name (not mapped to English): %r (%s)",
            name,
            language,
        )
        return None

    return translated


def country_name_to_alpha_2(name: str, language: str) -> str | None:
    if not name or name == "-":
        return None

    translated_name = country_name_to_english(name, language)
    if not translated_name:
        return None

    country = pycountry.countries.get(name=translated_name)

    if not country:
        _log.warning(
            "Unknown country name (not mapped to ISO): %r (%s)",
            translated_name,
            language,
        )
        return None

    return country.alpha_2
