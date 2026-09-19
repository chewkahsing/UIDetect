"""
UIDetect Structured Warning AI (v2) -- opt-in, additive
=========================================================

This is a NEW, parallel entry point alongside the existing
`generate_security_ai()` in `warning_ai_consolidated.py`. It is not
called from anywhere yet -- `scanner.py` still imports and uses the
original `generate_security_ai`. Nothing about current behavior
changes unless/until scanner.py is switched to import
`generate_security_ai_structured` from this module instead.

APPROACH
--------
1. `claims_schema.derive_security_claims(data)` computes the ground
   truth claims for this assessment directly from backend data --
   zero AI, zero hallucination risk.
2. Each claim carries 2-3 pre-authored phrasing variants.
3. The local Ollama model's ONLY job is to return, for each claim, the
   index of the variant that reads best -- a small integer, enforced
   by a JSON schema. It never generates free text, so it structurally
   cannot introduce a claim, fact, or sentence we didn't already
   write ourselves ("copy-proof by construction").
4. If the AI call fails, times out, or returns something malformed,
   every claim silently falls back to variant 0 and the popup still
   renders correctly -- there is no hard dependency on the AI call
   succeeding.

Return shape matches `generate_security_ai()` exactly, so it's a
drop-in replacement at the call site in scanner.py:

    {"success": True, "aboutWebsite": "...", "warning": "...", "recommendation": "..."}
    {"success": False, "error": "..."}
"""

import json
import time

from ollama import chat

from logger import (
    log_info,
    log_warning,
    log_error,
)

from modules.claims_schema import derive_security_claims

# Reused as-is -- this is a pure parsing helper in the existing module,
# it does not call Ollama and does not generate or validate content,
# so importing it here does not create any behavioral coupling.
from modules.warning_ai_consolidated import extract_ollama_content


MODEL = "qwen2.5:3b"


# ==========================================================
# Variant selection
# ==========================================================

def _fallback_selection(claims):
    """Default to the first (index 0) variant for every claim."""
    return {claim["id"]: 0 for claim in claims}


def _select_variants_with_ai(claims):
    """
    Ask the model to choose a variant index per claim.

    Returns
    -------
    dict
        {claim_id: variant_index}. Never raises -- falls back to an
        all-zero selection on any failure so the caller can always
        render a popup.
    """

    if not claims:
        return {}

    options_lines = []

    for claim in claims:
        numbered = [
            f'  {index}: "{text}"'
            for index, text in enumerate(claim["variants"])
        ]
        options_lines.append(
            f'- {claim["id"]}:\n' + "\n".join(numbered)
        )

    options_block = "\n".join(options_lines)

    schema_properties = {
        claim["id"]: {
            "type": "integer",
            "minimum": 0,
            "maximum": len(claim["variants"]) - 1,
        }
        for claim in claims
    }

    prompt = f"""
Below is a fixed list of claims about a website security scan. Each
claim already has its content decided -- you are NOT deciding what is
true. For each claim, pick the variant index (an integer) whose
phrasing reads most naturally together with the others. Do not write
any new sentence. Do not merge, drop, or reorder claims.

{options_block}

Return a JSON object mapping each claim id to your chosen integer
index.
"""

    try:

        response = chat(
            model=MODEL,

            format={
                "type": "object",
                "properties": schema_properties,
                "required": list(schema_properties.keys()),
                "additionalProperties": False,
            },

            options={
                "temperature": 0.4,
                "top_p": 0.9,
                "seed": int(time.time() * 1000) % 2_147_483_647,
            },

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a phrasing selector for UIDetect. "
                        "You choose between pre-written sentence "
                        "variants supplied to you. You never write "
                        "new sentences, and you never alter the "
                        "text of a variant."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = extract_ollama_content(response)

        data = json.loads(content)

        if not isinstance(data, dict):
            raise ValueError("Variant selection response was not a JSON object.")

        selection = {}

        for claim in claims:

            index = data.get(claim["id"], 0)

            if not isinstance(index, int) or not (
                0 <= index < len(claim["variants"])
            ):
                index = 0

            selection[claim["id"]] = index

        return selection

    except Exception as error:

        log_warning(
            "Structured warning AI variant selection failed, "
            f"falling back to default phrasing: {error}"
        )

        return _fallback_selection(claims)


# ==========================================================
# Rendering
# ==========================================================

def _render(claims, selection):
    """
    Join the selected pre-authored variants into the three
    user-facing fields. Purely mechanical -- no AI involved here.
    """

    about_parts = []
    warning_parts = []
    recommendation_parts = []

    for claim in claims:

        index = selection.get(claim["id"], 0)

        if not (0 <= index < len(claim["variants"])):
            index = 0

        text = claim["variants"][index]

        if claim["category"] == "about":
            about_parts.append(text)
        elif claim["category"] == "warning":
            warning_parts.append(text)
        elif claim["category"] == "recommendation":
            recommendation_parts.append(text)

    about_website = (
        " ".join(about_parts).strip()
        or "You're visiting this website."
    )

    warning = (
        " ".join(warning_parts).strip()
        or "No confirmed security issues were found."
    )

    recommendation = (
        " ".join(recommendation_parts).strip()
        or "Proceed with normal caution."
    )

    return {
        "aboutWebsite": about_website,
        "warning": warning,
        "recommendation": recommendation,
    }


# ==========================================================
# Public entry point
# ==========================================================

def generate_security_ai_structured(assessment_data):
    """
    Structured-claims counterpart to generate_security_ai().

    Same input contract (the assessment_data dict built in
    scanner.py) and the same output shape as the original function,
    so scanner.py can switch to this by changing only its import.
    """

    if not isinstance(assessment_data, dict):

        log_error(
            "Structured Security AI generation failed: "
            "assessment_data must be a dictionary."
        )

        return {
            "success": False,
            "error": "Invalid assessment data.",
        }

    try:
        claims = derive_security_claims(assessment_data)

    except Exception as error:

        log_error(
            f"Structured claim derivation failed: {error}"
        )

        return {
            "success": False,
            "error": "Failed to derive security claims.",
        }

    selection = _select_variants_with_ai(claims)

    popup = _render(claims, selection)

    log_info(
        "Structured Security AI popup generated "
        f"({len(claims)} claim(s))."
    )

    return {
        "success": True,
        "aboutWebsite": popup["aboutWebsite"],
        "warning": popup["warning"],
        "recommendation": popup["recommendation"],
    }
