from transformers import AutoTokenizer, AutoModelForCausalLM

class AIDocumenter:
    def __init__(self):
        self.model_name = "microsoft/codebert-base-mlm"  # Smaller model, better for code documentation
        print("Loading AI model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=False, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, local_files_only=False, trust_remote_code=True)
        print("AI model loaded successfully!")

    def generate_description(self, code: str) -> str:
        try:
            inputs = self.tokenizer(code, return_tensors="pt", max_length=512, truncation=True)
            outputs = self.model.generate(**inputs, max_length=150, num_return_sequences=1)
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            return f"Code analysis module: {len(code.splitlines())} lines of code"
