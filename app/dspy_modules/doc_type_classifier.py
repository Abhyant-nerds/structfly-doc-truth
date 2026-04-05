import dspy


class DocumentTypeSignature(dspy.Signature):
    """Classify the broad type of a document from its textual content and source metadata."""

    document_text = dspy.InputField(
        desc="Full extracted document text to classify. Use the text content as the primary signal."
    )
    source_type = dspy.InputField(
        desc="Document source or modality such as text, pdf, image_ocr, or email."
    )
    structure_hint = dspy.InputField(
        desc="Short hint about expected layout or structure, for example basic, tabular, or semi_structured."
    )
    document_type = dspy.OutputField(
        desc="Predicted document type as a short snake_case label such as invoice, contract, resume, or generic_document."
    )


class DocumentTypeClassifier(dspy.Module):
    """Thin DSPy wrapper for document-type prediction."""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(DocumentTypeSignature)

    def forward(self, document_text, source_type, structure_hint):
        return self.predict(
            document_text=document_text,
            source_type=source_type,
            structure_hint=structure_hint,
        )
