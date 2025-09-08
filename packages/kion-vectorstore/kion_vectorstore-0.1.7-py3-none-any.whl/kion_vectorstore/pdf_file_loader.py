from typing import List
from pypdf import PdfReader
from kion_vectorstore.file_loader import FileLoader
from kion_vectorstore.document import Document

class KionPDFFileLoader(FileLoader):
    # Constructor to pass PDF file_path
    def __init__(self, file_path, chunk_size, chunk_overlap):
        super().__init__(file_path, chunk_size, chunk_overlap)
        print(f"Initialized KionPDFFileLoader with file_path: {file_path}, chunk_size: {chunk_size}, chunk_overlap: {chunk_overlap}")

    # Load PDF File
    def load_file(self) -> List[Document]:
        reader = PdfReader(self.file_path)
        documents: List[Document] = []
        for i, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            documents.append(Document(page_content=text, metadata={'source': self.file_path, 'page': i}))
        print(f"Number of PDF Documents loaded = {len(documents)}")
        return documents