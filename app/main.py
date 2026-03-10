from ingest import build_index_if_needed
from rag_pipeline import ask_rag

def main():                         
#Ties rag_pipeline.py and ingest.py together

    build_index_if_needed()

    print("RAG assistant is ready.")
    print("Ask a question about Fantasy Realms RPG.")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Question: ").strip()

        if query.lower() == "exit":
            print("Goodbye.")
            break

        if not query:
            print("Please enter a question.\n")
            continue

        answer = ask_rag(query)
        print("\nAnswer:")
        print(answer)
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()