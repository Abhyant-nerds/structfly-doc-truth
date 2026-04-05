import json

import dspy


class FieldProposalSignature(dspy.Signature):
    """Propose structured entity fields and values from a document.

    Return only a JSON array of field proposals.

    Each array item must be an object with:
    - proposed_name: normalized snake_case entity name such as invoice_number, vendor, customer
    - raw_value: exact value found in the document

    Prefer explicit field names found in the document. Do not emit generic labels such as
    named_entity, value, field, item, text, or unknown unless nothing more specific is possible.
    """

    document_text = dspy.InputField(
        desc="Full extracted document text from which candidate business entities and values must be proposed."
    )
    document_type_guess = dspy.InputField(
        desc="Best current guess for the document category, such as invoice, contract, resume, or generic_document."
    )
    tool_context = dspy.InputField(
        desc="JSON string containing outputs from deterministic helper tools. Use it to ground field proposals in explicit evidence."
    )
    output = dspy.OutputField(
        desc='JSON array of objects with keys "proposed_name" and "raw_value". Each proposed_name should be specific and normalized to snake_case.'
    )


class DocumentDiscoveryReActAgent(dspy.Module):
    """DSPy module that converts document text plus tool evidence into structured field proposals."""

    def __init__(self, tools):
        super().__init__()
        self.tools = tools
        self.propose_fields = dspy.ChainOfThought(FieldProposalSignature)

    def _build_tool_context(self, document_text):
        tool_outputs = {}

        for tool in self.tools:
            tool_name = tool.__name__
            if tool_name == "extract_key_value_pairs":
                tool_outputs[tool_name] = tool({"text": document_text})
            else:
                tool_outputs[tool_name] = tool(document_text)

        return json.dumps(tool_outputs, ensure_ascii=True)

    def forward(self, document_bundle, document_type_guess):
        document_text = document_bundle.get("text", "")
        tool_context = self._build_tool_context(document_text)
        return self.propose_fields(
            document_text=document_text,
            document_type_guess=document_type_guess,
            tool_context=tool_context,
        )
