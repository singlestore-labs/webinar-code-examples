'''
===========================================
        Module: Open-source LLM Setup
===========================================
'''
from langchain.llms import CTransformers, LlamaCpp
from dotenv import find_dotenv, load_dotenv
import box
import yaml

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))


def build_llm():
        n_gpu_layers = 1  # Metal set to 1 is enough.
        n_batch = 1024  # Should be between 1 and n_ctx, consider the amount of RAM of your Apple Silicon Chip.

        # Make sure the model path is correct for your system!
        llm = LlamaCpp(
                model_path="./models/llama-2-7b-chat.ggmlv3.q2_K.bin",
                n_gpu_layers=n_gpu_layers,
                n_batch=n_batch,
                f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
                verbose=False,
        )

        return llm
