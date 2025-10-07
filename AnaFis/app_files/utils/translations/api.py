"""
Translation API for AnaFis
Provides functions to get UI and help strings with error handling and fallback.
"""

import importlib
import logging
from typing import Optional, Dict, List, Tuple

# Supported languages
LANGS = ["pt", "en"]

# Load main and help translations for each language
TRANSLATIONS: Dict[str, Dict[str, Dict[str, str]]] = {}
TRANSLATIONS_HELP: Dict[str, Dict[str, Dict[str, str]]] = {}
for lang_code in LANGS:
    main_mod = importlib.import_module(f"app_files.utils.translations.{lang_code}")
    help_mod = importlib.import_module(f"app_files.utils.translations.{lang_code}_help")
    TRANSLATIONS[lang_code] = getattr(main_mod, "TRANSLATIONS", {})
    TRANSLATIONS_HELP[lang_code] = getattr(help_mod, "TRANSLATIONS_HELP", {})


def validate_translations() -> Tuple[List[str], List[str]]:
    """
    Validate that all translation keys exist in all supported languages.

    Returns:
        Tuple of (missing_keys, extra_keys) where:
        - missing_keys: Keys that exist in one language but not another
        - extra_keys: Keys that are inconsistent across languages
    """
    missing_keys = []
    extra_keys = []

    # Use 'pt' as the reference language
    reference_lang = "pt"

    # Validate main translations
    for component in TRANSLATIONS.get(reference_lang, {}):
        ref_keys = set(TRANSLATIONS[reference_lang][component].keys())

        for lang in LANGS:
            if lang == reference_lang:
                continue

            if component not in TRANSLATIONS.get(lang, {}):
                missing_keys.append(f"{lang}: Missing entire component '{component}'")
                continue

            lang_keys = set(TRANSLATIONS[lang][component].keys())

            # Check for missing keys
            for key in ref_keys - lang_keys:
                missing_keys.append(
                    f"{lang}.{component}.{key} (exists in {reference_lang})"
                )

            # Check for extra keys
            for key in lang_keys - ref_keys:
                extra_keys.append(
                    f"{lang}.{component}.{key} " f"(not in {reference_lang})"
                )

    # Validate help translations
    for topic in TRANSLATIONS_HELP.get(reference_lang, {}):
        ref_keys = set(TRANSLATIONS_HELP[reference_lang][topic].keys())

        for lang in LANGS:
            if lang == reference_lang:
                continue

            if topic not in TRANSLATIONS_HELP.get(lang, {}):
                missing_keys.append(f"{lang}: Missing entire help topic '{topic}'")
                continue

            lang_keys = set(TRANSLATIONS_HELP[lang][topic].keys())

            # Check for missing keys
            for key in ref_keys - lang_keys:
                missing_keys.append(
                    f"{lang}_help.{topic}.{key} " f"(exists in {reference_lang})"
                )

            # Check for extra keys
            for key in lang_keys - ref_keys:
                extra_keys.append(
                    f"{lang}_help.{topic}.{key} " f"(not in {reference_lang})"
                )

    return missing_keys, extra_keys


def log_translation_validation() -> bool:
    """
    Validate translations and log any issues.

    Returns:
        True if validation passed (no issues), False otherwise
    """
    missing_keys, extra_keys = validate_translations()

    if missing_keys:
        logging.warning(
            "Translation validation: %d missing translation keys found",
            len(missing_keys),
        )
        for key in missing_keys[:10]:  # Log first 10 to avoid spam
            logging.warning("  Missing: %s", key)
        if len(missing_keys) > 10:
            logging.warning("  ... and %d more missing keys", len(missing_keys) - 10)

    if extra_keys:
        logging.info(
            "Translation validation: %d extra translation keys found", len(extra_keys)
        )
        for key in extra_keys[:10]:  # Log first 10
            logging.info("  Extra: %s", key)
        if len(extra_keys) > 10:
            logging.info("  ... and %d more extra keys", len(extra_keys) - 10)

    if not missing_keys and not extra_keys:
        logging.info("Translation validation: All translations are complete")
        return True

    return len(missing_keys) == 0  # Only fail if keys are missing


def get_language_code_from_name(language_name: str, current_lang: str = "pt") -> str:
    """
    Convert a language display name to its code.

    Args:
        language_name: The display name of the language
        current_lang: The current language for translation lookup

    Returns:
        Language code ('pt' or 'en'), defaults to 'pt' if unknown
    """
    # Check against translated names
    for lang_code in LANGS:
        key = f"language_{lang_code}"
        if key in TRANSLATIONS.get(current_lang, {}).get("main_app", {}):
            if language_name == TRANSLATIONS[current_lang]["main_app"][key]:
                return lang_code

    # Fallback to direct code matching
    if language_name.lower() in ["pt", "português", "portuguese"]:
        return "pt"
    elif language_name.lower() in ["en", "english", "inglês"]:
        return "en"

    # Default to Portuguese
    return "pt"


def get_string(
    component: str, key: str, lang: str, fallback: Optional[str] = None
) -> str:
    """Get a UI string for a given language, component, and key."""
    try:
        return TRANSLATIONS[lang][component][key]
    except KeyError:
        logging.warning(
            "Missing translation: component='%s', key='%s', lang='%s'",
            component,
            key,
            lang,
        )
        if fallback is not None:
            return fallback
        return f"[MISSING: {lang}.{component}.{key}]"


def get_help(topic: str, key: str, lang: str, fallback: Optional[str] = None) -> str:
    """Get a help string for a given language, topic, and key."""
    try:
        return TRANSLATIONS_HELP[lang][topic][key]
    except KeyError:
        logging.warning(
            "Missing help translation: topic='%s', key='%s', lang='%s'",
            topic,
            key,
            lang,
        )
        if fallback is not None:
            return fallback
        return f"[MISSING_HELP: {lang}.{topic}.{key}]"
