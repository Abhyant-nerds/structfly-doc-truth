import dspy


class CanonicalFieldSuggestionSignature(dspy.Signature):
    """Merge semantically duplicate field suggestions into canonical final suggestions.

    Return only a JSON array. Keep one field when multiple candidates refer to the same
    semantic entity and raw value, for example invoice_no and invoice_number with INV-1001.
    Prefer the clearest and most standard snake_case field name.
    """

    document_type_guess = dspy.InputField(
        desc="Current best guess for document category, such as invoice, contract, resume, spreadsheet, or generic_document."
    )
    candidate_fields_json = dspy.InputField(
        desc='JSON array of candidate fields. Each item has keys "proposed_name" and "raw_value".'
    )
    output = dspy.OutputField(
        desc='JSON array of canonical field suggestions. Each item must contain "proposed_name" and "raw_value". Remove semantic duplicates and keep only one representative.'
    )


class CanonicalNameSuggestion(dspy.Module):
    """DSPy module that canonicalizes duplicate field suggestions into a final unique set."""

    def __init__(self):
        super().__init__()
        self.suggest = dspy.ChainOfThought(CanonicalFieldSuggestionSignature)

    def forward(self, document_type_guess, candidate_fields_json):
        return self.suggest(
            document_type_guess=document_type_guess,
            candidate_fields_json=candidate_fields_json,
        )
