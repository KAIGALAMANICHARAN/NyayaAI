import os, json, re, tempfile
from datetime import date
import streamlit as st

st.set_page_config(page_title="NyayaAI | Indian Legal Help", page_icon="⚖️", layout="wide")
st.title("⚖️ NyayaAI")
st.caption("Plain-language legal guidance for everyday rental-deposit disputes in India")

DISCLAIMER = ("NyayaAI provides general legal information and drafting support, not legal representation. "
              "It can be wrong or incomplete. It does not create a lawyer-client relationship. "
              "For court deadlines, eviction threats, police matters, large sums, or urgent danger, contact a qualified lawyer.")

with st.sidebar:
    st.subheader("Before you begin")
    language = st.selectbox("Preferred language", ["English", "हिन्दी", "മലയാളം", "తెలుగు", "தமிழ்"])
    state = st.text_input("State / Union Territory", placeholder="e.g. Kerala")
    district = st.text_input("District / city (optional)")
    st.divider()
    st.caption("Privacy: avoid entering Aadhaar, bank account numbers, passwords, or other sensitive identifiers.")
    st.info(DISCLAIMER)

st.markdown("### Tell us what happened")
st.write("Start in your own words. NyayaAI will organise the facts, identify missing evidence, explain practical options and prepare a draft message.")
story = st.text_area("Describe the problem", height=150, placeholder="Example: I rented a flat, paid ₹30,000 deposit, moved out on 1 October, returned the keys, but the landlord has not returned the deposit...")
c1, c2 = st.columns(2)
with c1:
    name = st.text_input("Your name (optional)")
    landlord = st.text_input("Landlord's name (optional)")
    deposit = st.number_input("Deposit paid (₹)", min_value=0, step=500)
with c2:
    move_out = st.date_input("Date you moved out", value=None)
    agreement = st.selectbox("Was there a written rental agreement?", ["Not sure", "Yes", "No"])
    deductions = st.selectbox("Did the landlord explain deductions?", ["Not yet", "Yes, with details", "Yes, but no proof", "No"])

evidence = st.multiselect("What proof do you have?", [
    "Rental agreement", "Deposit payment receipt / bank entry", "WhatsApp / SMS messages",
    "Email", "Move-in / move-out photos", "Key handover proof", "Witness", "No documents yet"
])
extra = st.text_area("Anything else? (optional)", placeholder="Any promised refund date, deductions, damage allegations, or messages?")

def make_case():
    return {
        "jurisdiction": ", ".join(x for x in [district, state] if x) or "Not provided",
        "story": story.strip(), "name": name.strip(), "landlord": landlord.strip(),
        "deposit_inr": deposit, "move_out_date": str(move_out) if move_out else "Not provided",
        "written_agreement": agreement, "deductions": deductions,
        "evidence": evidence, "additional_facts": extra.strip(), "language": language
    }

def fallback_analysis(case):
    missing = []
    if case["jurisdiction"] == "Not provided": missing.append("State and city/district")
    if case["move_out_date"] == "Not provided": missing.append("Exact date possession and keys were handed back")
    if case["written_agreement"] == "Not sure": missing.append("Whether the agreement states a refund timeline or permitted deductions")
    if not case["evidence"]: missing.append("Any proof of deposit payment and handover")
    if case["deductions"] in ["Yes, but no proof", "Yes, with details"]:
        missing.append("Itemised deductions, invoices, photographs and the agreement clause relied on")

    return f"""## Your situation, in brief
You report a rental security-deposit dispute. The amount entered is ₹{case['deposit_inr']:,.0f}. Your account should be checked against the rental agreement, payment proof and handover evidence.

## What this may mean
A landlord's right to retain any part of a deposit depends on the agreement, applicable state/local tenancy law, the facts and evidence. Ordinary wear and tear should be distinguished from damage beyond normal use. Do not assume that every deduction is valid—or that every deduction is automatically unlawful.

As a general starting point, section 108 of the Transfer of Property Act, 1882 describes certain lessor/lessee rights and liabilities, but it applies subject to contract and local usage. It is not a universal deposit-refund formula. State-specific rent laws and the agreement may change the analysis.

## Evidence to preserve
{chr(10).join('- '+x for x in (case['evidence'] or ['No proof selected yet']))}
Keep original messages, bank statements, receipts, dated photographs, the agreement and proof of key handover. Do not edit screenshots; retain the original files.

## Missing facts to confirm
{chr(10).join('- '+x for x in missing) if missing else '- Confirm the facts and dates are accurate.'}

## Practical next steps
1. Read the agreement for the deposit amount, refund deadline, notice requirements and permitted deductions.
2. Send a calm written request asking for the refund and an itemised explanation with supporting bills for each deduction.
3. Give a reasonable response date and keep proof of delivery.
4. If unresolved, consider a local lawyer or appropriate legal-services authority. The correct forum depends on the agreement, location, amount and facts.

## Important limits
This is a preliminary information summary, not a finding that the landlord has broken the law. NyayaAI has not verified your agreement or local state rules. If you receive an eviction threat, court notice, police communication, or a limitation/deadline issue, speak to a qualified local lawyer promptly.
"""

def draft_message(case):
    who = case["landlord"] or "[Landlord's name]"
    tenant = case["name"] or "[Your name]"
    amt = f"₹{case['deposit_inr']:,.0f}" if case["deposit_inr"] else "[deposit amount]"
    return f"""Subject: Request for return of rental security deposit

Dear {who},

I am writing regarding the rental premises occupied by me at [property address]. I paid a security deposit of {amt}. I vacated the premises and handed over possession/keys on {case['move_out_date']}.

Please arrange to return the refundable security deposit to me within 7 days of receiving this message. If you believe any amount is deductible, please share an itemised statement explaining each deduction, the relevant agreement clause, and supporting bills or photographs.

I would prefer to resolve this matter amicably. Please respond in writing so that we have a clear record.

Regards,
{tenant}
[Contact details]"""

def llm_enhance(case, base_text):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        prompt = f"""You are NyayaAI, a cautious Indian legal information assistant. This is NOT legal representation.
Use only the verified legal note below; do not invent statutes, sections, cases, deadlines or legal conclusions.
Clearly separate facts, assumptions, missing facts and general information. If uncertain, say so.
Do not guarantee outcomes. Ask the user to verify state-specific law with a local lawyer.
Answer in {case['language']}. Keep the practical checklist. Do not repeat sensitive identifiers.
Verified legal note: Section 108 of the Transfer of Property Act, 1882 contains lessor/lessee rights and liabilities subject to contract and local usage; it is not a universal security-deposit refund rule.
User facts: {json.dumps(case, ensure_ascii=False)}
Base analysis: {base_text}
"""
        r = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role":"system","content":"Be cautious, clear and nonjudgmental."},
                      {"role":"user","content":prompt}],
            temperature=0.2
        )
        return r.choices[0].message.content
    except Exception as e:
        st.warning("AI service unavailable; showing the deterministic fallback. " + str(e)[:180])
        return None

if st.button("Analyse my situation", type="primary", disabled=not bool(story.strip())):
    case = make_case()
    st.session_state["case"] = case
    fallback = fallback_analysis(case)
    enhanced = llm_enhance(case, fallback)
    st.session_state["analysis"] = enhanced or fallback
    st.session_state["draft"] = draft_message(case)

if "analysis" in st.session_state:
    st.divider()
    st.subheader("Your case summary and next steps")
    st.markdown(st.session_state["analysis"])
    st.subheader("Draft message to your landlord")
    st.text_area("Review and edit before sending", st.session_state["draft"], height=260)
    st.download_button("Download case summary (TXT)", st.session_state["analysis"], file_name="nyayaai_case_summary.txt")
    st.download_button("Download draft message (TXT)", st.session_state["draft"], file_name="deposit_refund_request.txt")
    st.caption("Do not send without checking every fact, date, amount and agreement clause.")

with st.expander("How NyayaAI avoids made-up law"):
    st.markdown("""
- The first version is deliberately limited to rental security-deposit disputes.
- Legal references are restricted to a short, disclosed source note; the model is instructed not to create citations.
- The fallback analysis is generated by transparent rules and labels uncertainty.
- It asks for jurisdiction and agreement details rather than assuming one national rule applies.
- No court case, section number, deadline or guaranteed outcome is generated as a fact.
- A human lawyer is required for urgent, contested or high-stakes matters.
""")
st.caption("Prototype demonstration • Not a substitute for advice from an advocate")
