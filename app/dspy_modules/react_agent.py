import dspy

class DocumentDiscoveryReActAgent(dspy.Module):
    def __init__(self, tools):
        super().__init__()
        self.react = dspy.ReAct(
            "document_bundle, document_type_guess -> output",
            tools=tools
        )

    def forward(self, document_bundle, document_type_guess):
        return self.react(
            document_bundle=document_bundle,
            document_type_guess=document_type_guess
        )
