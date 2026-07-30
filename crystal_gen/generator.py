import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

class CrystalGenerator:
    _instance = None

    def __init__(self, model_name="Qwen/Qwen2.5-7B-Instruct"):
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="cuda:0",
            trust_remote_code=True
        )

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def generate_cif(self, formula: str, spacegroup: str = "") -> str:
        prompt = f"Generate a valid crystallographic CIF file for chemical formula: {formula}"
        if spacegroup:
            prompt += f" with space group: {spacegroup}"

        messages = [
            {"role": "system", "content": "You are an expert crystallographer AI. Output ONLY the raw CIF block starting with data_ without markdown formatting or commentary."},
            {"role": "user", "content": prompt}
        ]

        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer([text], return_tensors="pt").to("cuda:0")

        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=512, temperature=0.2, top_p=0.9)

        generated_ids = [out[len(inp):] for inp, out in zip(inputs.input_ids, outputs)]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        if "```" in response:
            lines = response.splitlines()
            cleaned = [l for l in lines if not l.startswith("```")]
            response = "\n".join(cleaned)

        return response.strip()
