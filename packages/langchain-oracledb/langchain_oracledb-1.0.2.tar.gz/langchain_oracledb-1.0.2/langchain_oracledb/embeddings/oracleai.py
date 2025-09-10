# Copyright (c) 2024, 2025 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
"""
oracleai.py

Implements OracleEmbeddings for generating and handling 
vector embeddings with Oracle AI Vector Search.

Authors:
    - Harichandan Roy (hroy)
    - David Jiang (ddjiang)
"""
from __future__ import annotations

import json
import logging
import traceback
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from oracledb import Connection

import oracledb

logger = logging.getLogger(__name__)

"""OracleEmbeddings class"""


class OracleEmbeddings(BaseModel, Embeddings):
    """Get Embeddings"""

    # Oracle connection
    conn: Any = None
    # embedding parameters
    params: Dict[str, Any]
    # proxy
    proxy: Optional[str] = None

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    model_config = ConfigDict(
        extra="forbid",
    )

    """
    1 - user needs to have create procedure, 
        create mining model, create any directory privilege.
    2 - grant create procedure, create mining model, 
        create any directory to <user>;
    """

    @staticmethod
    def load_onnx_model(
        conn: Connection, dir: str, onnx_file: str, model_name: str
    ) -> None:
        """Load an ONNX model to Oracle Database.
        Args:
            conn: Oracle Connection,
            dir: Oracle Directory,
            onnx_file: ONNX file name,
            model_name: Name of the model.
        """

        try:
            if conn is None or dir is None or onnx_file is None or model_name is None:
                raise Exception("Invalid input")

            cursor = conn.cursor()
            cursor.execute(
                """
                begin
                    dbms_data_mining.drop_model(model_name => :model, force => true);
                    SYS.DBMS_VECTOR.load_onnx_model(:path, :filename, :model, 
                        json('{"function" : "embedding", 
                            "embeddingOutput" : "embedding", 
                            "input": {"input": ["DATA"]}}'));
                end;""",
                path=dir,
                filename=onnx_file,
                model=model_name,
            )

            cursor.close()

        except Exception as ex:
            logger.info(f"An exception occurred :: {ex}")
            traceback.print_exc()
            cursor.close()
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute doc embeddings using an OracleEmbeddings.
        Args:
            texts: The list of texts to embed.
        Returns:
            List of embeddings, one for each input text.
        """

        if texts is None:
            return None

        embeddings: List[List[float]] = []
        try:
            # returns strings or bytes instead of a locator
            oracledb.defaults.fetch_lobs = False
            cursor = self.conn.cursor()

            if self.proxy:
                cursor.execute(
                    "begin utl_http.set_proxy(:proxy); end;", proxy=self.proxy
                )

            chunks = []
            for i, text in enumerate(texts, start=1):
                chunk = {"chunk_id": i, "chunk_data": text}
                chunks.append(json.dumps(chunk))

            vector_array_type = self.conn.gettype("SYS.VECTOR_ARRAY_T")
            inputs = vector_array_type.newobject(chunks)
            cursor.setinputsizes(None, oracledb.DB_TYPE_JSON)
            cursor.execute(
                "select t.* "
                + "from dbms_vector_chain.utl_to_embeddings(:1, "
                + "json(:2)) t",
                [inputs, self.params],
            )

            for row in cursor:
                if row is None:
                    embeddings.append([])
                else:
                    rdata = json.loads(row[0])
                    # dereference string as array
                    vec = json.loads(rdata["embed_vector"])
                    embeddings.append(vec)

            cursor.close()
            return embeddings
        except Exception as ex:
            logger.info(f"An exception occurred :: {ex}")
            traceback.print_exc()
            cursor.close()
            raise

    def embed_query(self, text: str) -> List[float]:
        """Compute query embedding using an OracleEmbeddings.
        Args:
            text: The text to embed.
        Returns:
            Embedding for the text.
        """
        return self.embed_documents([text])[0]


# uncomment the following code block to run the test

"""
# A sample unit test.

import oracledb
# get the Oracle connection 
conn = oracledb.connect(
    user="<user>",
    password="<password>",
    dsn="<hostname>/<service_name>",
)
print("Oracle connection is established...")

# params 
embedder_params = {"provider": "database", "model": "demo_model"}
proxy = ""

# instance
embedder = OracleEmbeddings(conn=conn, params=embedder_params, proxy=proxy)

docs = ["hello world!", "hi everyone!", "greetings!"]
embeds = embedder.embed_documents(docs)
print(f"Total Embeddings: {len(embeds)}")
print(f"Embedding generated by OracleEmbeddings: {embeds[0]}\n")

embed = embedder.embed_query("Hello World!")
print(f"Embedding generated by OracleEmbeddings: {embed}")

conn.close()
print("Connection is closed.")

"""
