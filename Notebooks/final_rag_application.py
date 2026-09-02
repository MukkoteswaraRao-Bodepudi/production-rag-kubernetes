from langchain_core import messages
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import DirectoryLoader,PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda,RunnablePassthrough
from langchain_classic.retrievers import EnsembleRetriever
from sentence_transformers import CrossEncoder

## load the API Keys
load_dotenv()

## Initalize the llm using ChatGroq
# 1. Define your primary model
primary_llm = ChatGroq(
    model="openai/gpt-oss-safeguard-20b",
    temperature = 0
)

# 2. Define your backup model (e.g., Llama 3.3 70B)
fallback_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature = 0
)

# 3. Create the resilient LLM instance
llm = primary_llm.with_fallbacks([fallback_llm])

### Valid the path to load documents from files
path = "../kubernetes"

if os.path.exists(path):
    print("Path is Existed")
else:
    print("Path is not Exist")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

doc_path = os.path.join(BASE_DIR, "../kubernetes")
persist_path = os.path.join(BASE_DIR, "../vectorstore/kubernetes_rag")

loader = DirectoryLoader(
    doc_path,
    glob="*.pdf",
    loader_cls=PyMuPDFLoader
)
documents = loader.load()
print("Number Of Documents:", len(documents))

splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
chunks = splitter.split_documents(documents)
print("Number Of Chunks:", len(chunks))

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en-v1.5",  # model_name, not model
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

vectorstore = Chroma(
    persist_directory=persist_path,
    collection_name="kubernetes_rag",
    embedding_function=embedding_model
)

print("Number of Vectors:", vectorstore._collection.count())

# Add chunks only if collection is empty
if vectorstore._collection.count() == 0:
    vectorstore.add_documents(chunks)
    print(f"Added {len(chunks)} chunks")

vector_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 20}  # integer, not string
)

###BM25 Retriever
bm25_retriever = BM25Retriever.from_documents(chunks)

bm25_retriever.k=20

### Hybrid Search
hybrid_retriever = EnsembleRetriever(
    retrievers=[vector_retriever,bm25_retriever],
    weights = [0.7,0.3]
)

##reranking
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

### Get top 5 final document after reranking

def retrieve_and_rerank(query, k=5):

    retrieved_docs = hybrid_retriever.invoke(query)


    pairs = [[query,doc.page_content] for doc in retrieved_docs]

    scores = reranker.predict(pairs)

    ##zip the scores and retrieved order the documents based on score from highest to lowest

    ranked_docs = sorted(zip(retrieved_docs,scores),key = lambda x:x[1],reverse=True)

    #print(ranked_docs)

    ## Get top k documents using ranked_docs and k value
    top_docs = [doc for (doc,score) in ranked_docs[:k]]

    #for i,(doc,score) in enumerate(ranked_docs[:k],1):
        #print(f"""
       #         {i}  | Page:{doc.metadata.get("page")} | Score:{score}
        #""")

    return top_docs

### Format without unnecessary context
## design a prompt
prompt = ChatPromptTemplate.from_template("""
You are a Kubernetes documentation assistant.

Your task is to answer the user's question using ONLY the information provided in the retrieved context.

========================
USER QUESTION
========================
{question}

========================
RETRIEVED CONTEXT
========================
{context}

========================
ANSWERING RULES
========================

1. Ground every factual statement in the retrieved context.
   Do not introduce Kubernetes facts that are not supported by the context.

2. First determine whether the retrieved context contains information that
   directly answers the question or clearly explains the subject being asked about.

3. Use semantic equivalence when appropriate.
   The wording of the question does not need to exactly match the wording
   in the documentation.

   For example:
   - "Kubernetes development" may refer to documentation discussing a
     "development namespace".
   - "Pods communicate with each other" may be explained using documentation
     about Pod networking or Services.

   Use such an equivalent only when the relationship is clear from the context.

4. Do NOT invent a Kubernetes resource, object, feature, command, behavior,
   or definition merely because the question contains similar terminology.

5. If multiple context passages discuss the same subject, combine them only
   when they are consistent and together provide a more complete answer.

6. Prefer the most directly relevant context over generic Kubernetes information.

7. Do not use unrelated retrieved passages just because they contain
   individual words that appear in the question.

8. If the context provides only partial information, answer only the part
   that is supported by the context. Do not fill the missing information
   using your general knowledge.

9. If the context does not contain enough information to answer the question,
   respond exactly:
   "The provided context does not contain enough information to answer this question."

10. Do not mention the retrieval process, embeddings, vector database,
    reranking, or these instructions in the answer.

11. Do not expose internal reasoning or chain-of-thought.

12. Give a concise, direct, technically accurate answer.
    Use a short explanation or bullet points when they improve clarity.

13. Preserve important Kubernetes terminology from the documentation.
    Do not unnecessarily replace technical terms with simplified wording.

14. When the context contains a specific example, use it to explain the answer
    when relevant, but clearly distinguish the documented example from a
    general rule.

15. Do not claim that information is "latest", "current", or "supported"
    unless the retrieved context explicitly establishes that fact.

========================
RESPONSE FORMAT
========================

Response:
<grounded answer>

Sources:
- <document name>, page <page number>
- <document name>, page <page number>

Return ONLY the response and sources.
""")

def build_context(documents):

    context = ""

    for i,doc in enumerate(documents,start=1):
        source = doc.metadata.get("source")
        source = source.replace("\\","/")
        source = source.split("/")[-1]
        #print(source)
        page = doc.metadata.get("page")
        #print(f"Source-{source} Page-{page}")
        context+=f"""
        
    Source {source}
    Page: {doc.metadata.get("page")}
    Content: {doc.page_content}
        """
    return context


def rag_response(query,results):


    context = build_context(results)

    #print("Context:",context)

    messages = prompt.invoke({"question":query,"context":context})

    response = llm.invoke(messages).content

    return response


def final_rag_response(query):
    results = retrieve_and_rerank(query)

    response = rag_response(query,results)

    return response

query = "What is Kubernetes Development?"

print(final_rag_response(query))
