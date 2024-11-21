from vllm.entrypoints.openai import api_server

def main():
    api_server.main(
        model="Bllossom/llama-3.2-Korean-Bllossom-3B",
        host="0.0.0.0",
        port=8000,
        tensor_parallel_size=1,
        trust_remote_code=True
    )

if __name__ == "__main__":
    main() 