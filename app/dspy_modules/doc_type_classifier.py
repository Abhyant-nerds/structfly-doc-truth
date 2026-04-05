import dspy

class DocumentTypeSignature(dspy.Signature):
    document_text = dspy.InputField()
    source_type = dspy.InputField()
    structure_hint = dspy.InputField()
    document_type = dspy.OutputField()

class DocumentTypeClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(DocumentTypeSignature)

    def forward(self, document_text, source_type, structure_hint):
        return self.predict(
            document_text=document_text,
            source_type=source_type,
            structure_hint=structure_hint
        )
