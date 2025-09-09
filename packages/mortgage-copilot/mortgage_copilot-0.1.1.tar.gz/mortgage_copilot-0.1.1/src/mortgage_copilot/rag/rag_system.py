import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
import accelerate

class RAGSYSTEM:
    def __init__(self,underwriting_rules_dir,vector_db):
        self.underwriting_rules_dir = underwriting_rules_dir
        self.vector_db = vector_db
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 100,
            length_function = len
        )
        self.vector_store = None
        self.rules_documents = []
        os.makedirs(self.underwriting_rules_dir,exist_ok=True)
        os.makedirs(self.vector_db,exist_ok=True)
    def load_rules(self):
        """Load the existing vector store or create new one"""
        vector_store_path = os.path.join(self.vector_db,"vector_store")
        try:
            if os.path.exists(vector_store_path):
                self.vector_store = FAISS.load_local(vector_store_path,self.embeddings,allow_dangerous_deserialization=True)
            else:
                self.create_vector_store()
        except Exception as e:
            print(e)
            self.create_vector_store()
    def create_vector_store(self):
        """Create a new vector store"""
        try:
            documents = self.load_documents()
            if documents:
                self.vector_store = FAISS.from_documents(documents,self.embeddings)
                vector_store_path = os.path.join(self.vector_db,"vector_store")
                self.vector_store.save_local(vector_store_path)
        except Exception as e:
            print(e)
    def load_documents(self):
        """Load the documents from the directory"""
        
        try:
            documents = []
            for filename in os.listdir(self.underwriting_rules_dir):
                file_path = os.path.join(self.underwriting_rules_dir,filename)
                with open(file_path,"r") as f:
                    content = f.read()
                text_chunks = self.text_splitter.split_text(content)
                for i, chunk in enumerate(text_chunks):
                    doc = Document(page_content = chunk,metadata={'source':file_path,'chunk':i,'filename':filename})
                    documents.append(doc)
            return documents
        except Exception as e:
            print(e)
            return []
    def search_relevant_documents(self,query):
        """Search for relevant documents"""
        try:
            if not self.vector_store:
                self.load_rules()
            results = self.vector_store.similarity_search_with_score(query,k=3)
            relevant_policies = []
            for doc, score in results:
                relevant_policies.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'relevance_score': float(score),
                    'source': doc.metadata.get('source', 'unknown')
                })
            
            return relevant_policies
            print(" relevant policies found.")

        except Exception as e:
            print(e)
            return ""