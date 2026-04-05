import dspy


class DocumentTypeSignature(dspy.Signature):
    """Classify the broad type of a document from file content, text content, and source metadata."""

    document_text = dspy.InputField(
        desc="Optional extracted text for the document. Use it when available, but also reason over the uploaded file if provided."
    )
    document_file: dspy.File = dspy.InputField(
        desc="Optional uploaded file object passed directly to the model. It may be a PDF, TXT, DOCX, or MSG email file."
    )
    source_type = dspy.InputField(
        desc="Document source or modality such as text, pdf, image_ocr, or email."
    )
    filename = dspy.InputField(
        desc="Original file name when available. Use it as a weak hint only, for example invoice.pdf or candidate_resume.docx."
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

    def forward(self, document_text, document_file, source_type, filename, structure_hint):
        return self.predict(
            document_text=document_text,
            document_file=document_file,
            source_type=source_type,
            filename=filename,
            structure_hint=structure_hint,
        )
