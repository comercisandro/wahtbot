from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from transformers import MarianMTModel, MarianTokenizer

model_id = "gpt2"  # Cambiar al modelo deseado, por ejemplo, "EleutherAI/gpt-j-6B" para un modelo más grande
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

model_name = "Helsinki-NLP/opus-mt-en-es"
tokenizer_translator = MarianTokenizer.from_pretrained(model_name)
model_translator = MarianMTModel.from_pretrained(model_name)

def create_pipeline(option):
    if option == 'text-generation':
        return pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=50)
    elif option == 'text-classification':
        # Agregar lógica para crear pipeline de text-classification si es necesario
        pass
    elif option == 'sentiment-analysis':
        # Agregar lógica para crear pipeline de sentiment-analysis si es necesario
        pass
    else:
        raise ValueError("Opción no válida")

def translate(to='es'):
    return pipeline("translation_en_to_es", model=model_translator, tokenizer=tokenizer_translator)
