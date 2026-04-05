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
        desc="Optional extracted document text from which candidate business entities and values may be proposed."
    )
    document_file: dspy.File = dspy.InputField(
        desc="Optional uploaded file object passed directly to the model. It may be a PDF, TXT, DOCX, or MSG email file."
    )
    document_type_guess = dspy.InputField(
        desc="Best current guess for the document category, such as invoice, contract, resume, or generic_document."
    )
    filename = dspy.InputField(
        desc="Original file name when available. Use it as a secondary hint for the document type and expected fields."
    )
    tool_context = dspy.InputField(
        desc="JSON string containing outputs from deterministic helper tools. Use it to ground field proposals in explicit evidence when text was available."
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
        if not document_text:
            return json.dumps({}, ensure_ascii=True)

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
        document_file = document_bundle.get("file")
        filename = document_bundle.get("filename", "")
        tool_context = self._build_tool_context(document_text)
        return self.propose_fields(
            document_text=document_text,
            document_file=document_file,
            document_type_guess=document_type_guess,
            filename=filename,
            tool_context=tool_context,
        )
