# Running Llama 2 Locally for Document Q&A

## Quickstart
- Ensure you have downloaded the GGML binary file from https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML and placed it into the `models/` folder
- run `pip install -r requirements.txt`
- To start parsing user queries into the application, launch the terminal from the project directory and run the following command:
`python main.py "<user query>" 2>/dev/null`
- For example, `python main.py "What is the minimum guarantee payable by Adidas?" 2>/dev/null`

<br><br>

Reference: https://github.com/kennethleungty/Llama-2-Open-Source-LLM-CPU-Inference

