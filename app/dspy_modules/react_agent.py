import json

import dspy


class FieldProposalSignature(dspy.Signature):
    """Return only a JSON array of field proposals.

    Each array item must be an object with:
    - proposed_name: normalized snake_case entity name such as invoice_number, vendor, customer
    - raw_value: exact value found in the document

    Prefer explicit field names found in the document. Do not emit generic labels such as
    named_entity, value, field, item, text, or unknown unless nothing more specific is possible.
    """

    document_text = dspy.InputField()
    document_type_guess = dspy.InputField()
    tool_context = dspy.InputField()
    output = dspy.OutputField()


class DocumentDiscoveryReActAgent(dspy.Module):
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
