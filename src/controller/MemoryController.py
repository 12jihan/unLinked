import os
from google.genai.types import _DeleteDocumentParameters
import psycopg

from models.DataModels import Document, DocumentCreate, DocumentSearchResult
from pgvector.psycopg import register_vector
from google import genai
from google.genai import Client


class MemoryController:
    def __init__(self):
        self.api_key: str | None = os.getenv("API_KEY")
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "dbname": "vectordb",
            "user": "postgres",
            "password": "postgres",
        }
        self.db_url = "postgresql://postgres:postgres@localhost:5432/vectordb"
        self.embeded_dim = 768

        self.client = Client(api_key=self.api_key)
        self._init_db()

    def _connect(self, register=True):
        # conn = psycopg.connect(self.db_url)
        conn = psycopg.connect(**self.db_config)
        if register:
            register_vector(conn)
        return conn

    def _embed(self, text: str) -> list[float] | None:
        res = self.client.models.embed_content(
            model="text-embedding-004", contents=text
        )

        if res and res.embeddings:
            return res.embeddings[0].values

        return None

    def _init_db(self):
        with self._connect(register=False) as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.commit()

        with self._connect() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS vector (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                embedding vector(768),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                modified_at TIMESTAMPTZ DEFAULT NOW()
            )
            """)
            conn.commit()

    def add(self, doc: DocumentCreate) -> Document | None:
        embedding = self._embed(doc.text)
        with self._connect() as conn:
            row = conn.execute(
                """
                INSERT INTO documents (text, embedding)
                VALUES (%s, %s)
                RETURNING id, text, embedding, created_at, modified_at
                """,
                (doc.text, embedding),
            ).fetchone()
            conn.commit()

            if row:
                return Document(
                    id=row[0],
                    text=row[1],
                    created_at=row[2],
                    modified_at=row[3],
                    embedding=row[4],
                )
            return None

    def update(self, doc_id: int, text: str) -> Document | None:
        embedding = self._embed(text)
        with self._connect() as conn:
            row = conn.execute(
                """
                UPDATE documents 
                SET text = %s, embedding = %s, modified_at = NOW()
                WHERE id = %s
                RETURNING id, text, embedding, created_at, modified_at
                """,
                (text, embedding, doc_id),
            ).fetchone()
            conn.commit()

            if row:
                return Document(
                    id=row[0],
                    text=row[1],
                    embedding=list(row[2]),
                    created_at=row[3],
                    modified_at=row[4],
                )
            return None

    def search(self, query: str, limit: int = 5) -> list[DocumentSearchResult]:
        embedding = self._embed(query)
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, text, created_at, modified_at, 1 - (embedding <=> %s) AS similarity
                FROM documents 
                ORDER BY embedding <=> %s 
                LIMIT %s
                """,
                (embedding, embedding, limit),
            ).fetchall()
            return [
                DocumentSearchResult(
                    id=r[0],
                    text=r[1],
                    created_at=r[0],
                    modified_at=r[0],
                    similarity=r[0],
                )
                for r in rows
            ]

    def get(self, doc_id: int) -> Document | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, text, embedding, created_at, modified_at FROM documents WHERE id = %s",
                (doc_id,),
            ).fetchone()
            if row:
                return Document(
                    id=row[0],
                    text=row[1],
                    embedding=list(row[2]),
                    created_at=row[3],
                    modified_at=row[4],
                )
            return None

    def delete(self, doc_id: int) -> bool:
        with self._connect() as conn:
            result = conn.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
            conn.commit()
            return result.rowcount > 0
