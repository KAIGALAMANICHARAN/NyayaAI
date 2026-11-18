# NyayaAI — Indian rental-deposit legal assistant

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run `pip install -r requirements.txt`
4. Run `streamlit run app.py`

The app works without an API key using a transparent rule-based fallback. To enable optional language-model phrasing, set:
- macOS/Linux: `export OPENAI_API_KEY="your-key"`
- Windows PowerShell: `$env:OPENAI_API_KEY="your-key"`

Optional model override: `OPENAI_MODEL` (default `gpt-4o-mini`).

## Scope
This prototype focuses on rental security-deposit disputes in India. It collects a user's account, jurisdiction, agreement status and evidence; produces a structured case summary, missing-facts checklist, practical next steps and an editable request message.

## Legal-safety design
- General information only; no lawyer-client relationship.
- The only preloaded legal note is the limited, qualified point that Transfer of Property Act, 1882 section 108 describes lessor/lessee rights and liabilities subject to contract and local usage. It is not a universal deposit-refund rule.
- The LLM is explicitly prohibited from inventing statutes, sections, judgments, deadlines or outcomes.
- Rule-based fallback remains available without an API key.
- It flags missing jurisdiction/facts and escalates urgent or high-stakes matters to a local advocate.
- No user data is sent to an external model unless the user/operator configures an API key and invokes that optional path. Do not enter highly sensitive identifiers.

## Limitations
- No verified state-by-state rent-law database yet.
- No document upload/OCR, audio transcription or actual speech input in this MVP.
- Language selection is a prompt preference for the optional LLM path; without an API key, fallback text is English.
- The app does not submit complaints, send notices, contact landlords or represent users.
- The 7-day date in the draft is a proposed response period, not a statutory deadline; edit it before use.

## Test cases
See `test_cases.json` and `raw_outputs/`. These are synthetic examples, not real client files.
