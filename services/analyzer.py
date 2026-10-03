"""Email analysis and structured triage service utilizing the Google Gemini API."""

import logging
import re
from typing import Optional

from google import genai
from google.genai import errors, types

import config
from schemas import EmailTriageResult

logger = logging.getLogger(__name__)

TRIAGE_SYSTEM_INSTRUCTION = """You are an expert executive email triage and productivity assistant.
Your job is to analyze incoming emails with precision and extract structured operational triage metadata.

Carefully evaluate the email against these guidelines:
1. Priority:
   - HIGH: Urgent, time-sensitive deadlines (within days), job/internship offers or interviews, critical security or financial alerts, immediate blockers.
   - MEDIUM: Important tasks or requests with flexible or distant deadlines, team collaboration updates, project check-ins.
   - LOW: Informational newsletters, marketing, automated receipts/notifications, low-relevance broadcasts.
2. Category:
   Must be strictly one of: INTERNSHIP, COLLEGE, WORK, FINANCE, SHOPPING, NEWSLETTER, PERSONAL.
3. Summary:
   Provide an executive-level summary in 1-2 concise sentences capturing key takeaways.
4. Actions:
   Extract a list of specific, concrete actionable tasks the recipient must perform. If no actions are needed, return an empty list.
5. Deadline:
   Extract explicit deadlines mentioned (ISO date string if identifiable, or textual date/time description). If no deadline is specified or implied, return null.
6. Reply Required:
   Boolean (true if the sender requires or expects a response, false otherwise).
   Provide a concise reason in reply_reason.

You must respond with valid JSON matching the requested schema strictly. Do not include extraneous commentary."""


def _clean_markdown_fences(text: str) -> str:
    """Strip markdown code fences and surrounding whitespace from raw JSON response."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


class EmailAnalyzer:
    """Natural language email triage engine powered by the Gemini API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Initialize the Gemini client and model configuration.

        Args:
            api_key: Optional Gemini API key. Defaults to config.GEMINI_API_KEY.
            model_name: Optional model identifier. Defaults to config.MODEL_NAME.
        """
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.MODEL_NAME
        self.client = genai.Client(api_key=self.api_key)

    def analyze_email(self, raw_text: str, subject: str = "") -> EmailTriageResult:
        """Analyze email text and return structured triage metadata.

        Args:
            raw_text: The email body text to analyze.
            subject: Optional email subject line to provide additional context.

        Returns:
            EmailTriageResult: Validated Pydantic model containing triage metadata.

        Raises:
            ValueError: If raw_text is empty/blank, or if JSON parsing fails.
            PermissionError: If API credentials are invalid.
            RuntimeError: If API quota is exhausted, the model is unavailable,
                         or server errors occur.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("raw_text cannot be empty or blank.")

        email_content = (
            f"Subject: {subject.strip()}\n\nBody:\n{raw_text.strip()}"
            if subject and subject.strip()
            else f"Body:\n{raw_text.strip()}"
        )

        gen_config = types.GenerateContentConfig(
            system_instruction=TRIAGE_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=EmailTriageResult,
            temperature=0.1,
        )

        # Attempt call with configured model, falling back to gemini-3.1-flash-lite if deprecated/unavailable
        models_to_try = [self.model_name]
        if self.model_name not in ("gemini-3.1-flash-lite", "gemini-3.8-flash"):
            models_to_try.append("gemini-3.1-flash-lite")

        response = None
        last_error: Optional[Exception] = None

        for target_model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=target_model,
                    contents=email_content,
                    config=gen_config,
                )
                break
            except errors.ClientError as exc:
                last_error = exc
                # If model is deprecated or not found (404), try next model candidate
                if exc.code == 404 and target_model != models_to_try[-1]:
                    logger.warning(
                        "Model '%s' returned 404. Falling back to '%s'.",
                        target_model,
                        models_to_try[-1],
                    )
                    continue
                if exc.code == 429 or "RESOURCE_EXHAUSTED" in str(exc):
                    raise RuntimeError(
                        "Gemini API quota exhausted or rate limit reached. "
                        "Please verify your API key limits or wait before retrying."
                    ) from exc
                if exc.code in (401, 403):
                    raise PermissionError(
                        "Authentication failed: Gemini API key is invalid or unauthorized."
                    ) from exc
                raise RuntimeError(
                    f"Gemini API client error ({exc.code}): {exc.message}"
                ) from exc
            except errors.ServerError as exc:
                last_error = exc
                # On 503 high demand spike, attempt fallback model if available
                if exc.code == 503 and target_model != models_to_try[-1]:
                    logger.warning(
                        "Model '%s' unavailable (503). Retrying with '%s'.",
                        target_model,
                        models_to_try[-1],
                    )
                    continue
                raise RuntimeError(
                    f"Gemini API server error ({exc.code}): {exc.message}. Please retry later."
                ) from exc
            except errors.APIError as exc:
                raise RuntimeError(
                    f"Gemini API error ({exc.code}): {exc.message}"
                ) from exc
            except Exception as exc:
                raise RuntimeError(
                    f"Unexpected error calling Gemini API: {exc}"
                ) from exc

        if response is None:
            raise RuntimeError(
                f"Failed to generate content after trying models {models_to_try}: {last_error}"
            )

        raw_response_text = response.text or ""
        if not raw_response_text.strip():
            raise RuntimeError(
                "Gemini API returned an empty response. The content may have triggered safety filters."
            )

        # Primary validation using Pydantic
        try:
            return EmailTriageResult.model_validate_json(raw_response_text)
        except Exception:
            # Fallback: strip any accidental markdown fences and re-validate
            cleaned_text = _clean_markdown_fences(raw_response_text)
            try:
                return EmailTriageResult.model_validate_json(cleaned_text)
            except Exception as parse_exc:
                raise ValueError(
                    f"Failed to parse Gemini response into EmailTriageResult: {parse_exc}\n"
                    f"Raw response text:\n{raw_response_text}"
                ) from parse_exc
