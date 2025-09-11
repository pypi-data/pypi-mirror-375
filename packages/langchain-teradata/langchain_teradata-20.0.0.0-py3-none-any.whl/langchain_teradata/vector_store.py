"""
Unpublished work.
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: Sushant.Mhambrey@Teradata.com
Secondary Owner: Aanchal.Kavedia@Teradata.com
                 Snigdha.Biswas@Teradata.com
                 PankajVinod.Purandare@Teradata.com

This file implements TeradataVectorStore class which is a Langchain compatible vector store wrapper for Teradata's managed vector store.
"""
from langchain_core.vectorstores import VectorStore as LCVectorStore
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever
from teradatagenai import VectorStore as TDVectorStore , TeradataAI
from teradatagenai import VSManager as TeradataVectorStoreManager
from teradatagenai import VSPattern as TeradataVectorStorePattern
from teradataml.common.utils import UtilFuncs
from teradataml import copy_to_sql, DataFrame
from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml.common.constants import HTTPRequest, TeradataConstants
import pandas as pd
import json
from teradatagenai.utils.doc_decorator import docstring_handler
from teradatagenai.common.constants import VECTOR_STORE_SEARCH_PARAMS, COMMON_PARAMS, NIM_PARAMS, FILE_BASED_VECTOR_STORE_PARAMS, \
                                           UPDATE_PARAMS, LANGCHAIN_PARAMS


class TeradataVectorStore(TDVectorStore, LCVectorStore):
    """
    LangChain-compatible vector store wrapper for Teradata's backend-managed vector store.
    This integrates Teradata's managed vector store service with LangChain's VectorStore interface.
    """
    _DOCUMENT_TYPES = (str, list, Document)
    _EMBEDDINGS_TYPES = (str, TeradataAI, Embeddings)
    _CHAT_MODEL_TYPES = (str, TeradataAI, BaseChatModel)

    def __init__(
            self,
            name=None,
            log=False,
            **kwargs
    ):
        """
        DESCRIPTION:
            Initializes a TeradataVectorStore instance.

        PARAMETERS:
            name:
                Optional Argument.
                Specifies the name of the vector store to connect to if it
                exists, or to create a new vector store if it does not.
                Types: str
                
            log:
                Optional Argument.
                Specifies whether logging should be enabled for vector store
                methods.
                Note:
                    Errors are logged to Datadog by default, even if logging is disabled.
                Default Value: False
                Types: bool

        RETURNS:
            None.

        RAISES:
            TeradataMLException.

        EXAMPLES:
            >>> vs = TeradataVectorStore(name="vs", log=True)
        """
        super().__init__(name=name, log=log, **kwargs)

    @staticmethod
    def _process_embeddings_object(embedding):
        """
        DESCRIPTION:
            Internal method to process the embeddings object.

        PARAMETERS:
            embedding:
                Required Argument.
                Specifies the embedding model name or TeradataAI 
                embedding object.
                Types: str or TeradataAI object or Langchain Embeddings object.

        RETURNS:
            str

        RAISES:
            None.

        EXAMPLES:
            # Example 1:
            # Create an instance of the VectorStore class.
            >>> vs = TeradataVectorStore()
            >>> vs.__process_embeddings_object(embedding="amazon.titan-embed-text-v1")

            # Example 2:
            # Create an instance of the TeradataAI class.
            >>> from teradatagenai import TeradataAI
            >>> llm_embedding = TeradataAI(api_type = "aws",
                  model_name = "amazon.titan-embed-text-v2:0")
            >>> vs.__process_embeddings_object(embedding=llm_embedding)

            # Example 3:
            # Create an object of the Langchain Embeddings.
            >>> from langchain_aws.embeddings import BedrockEmbeddings
            >>> embedding = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")
            >>> vs.__process_embeddings_object(embedding=embedding)
        """
        if isinstance(embedding, (str, TeradataAI)):
            return TDVectorStore._process_embeddings_object(embedding)

        if isinstance(embedding, Embeddings):
            # Depending on Langchain Embedding the name can be stored in different attributes.
            for attr in ['model_id', 'model', 'model_name']:
                if hasattr(embedding, attr):
                    model_name = getattr(embedding, attr)
                    if model_name:
                        return model_name
    
    @staticmethod
    def _process_chat_model_object(chat_completion_model):
        """
        DESCRIPTION:
            Internal method to process the chat model object.

        PARAMETERS:
            chat_completion_model:
                Required Argument.
                Specifies the chat model name or TeradataAI chat model object.
                Types: str or TeradataAI object or Langchain Chat Model object.

        RETURNS:
            str

        RAISES:
            None.

        EXAMPLES:
            # Example 1:
            # Create an instance of the TeradataAI class.
            >>> from teradatagenai import TeradataAI
            >>> llm_chat_model = TeradataAI(api_type = "azure",
                                            model_name = "gpt-35-turbo-16k")
            >>> vs.__process_chat_model_object(chat_completion_model=llm_chat_model)

            # Example 2:
            # Create an object of the Langchain Chat Model.
            >>> from langchain_aws.chat_models import BedrockChatModel
            >>> chat_model = BedrockChatModel(model_id="anthropic.claude-3-haiku-20240307-v1:0")
            >>> vs.__process_chat_model_object(chat_completion_model=chat_model)
        """
        if isinstance(chat_completion_model, (str, TeradataAI)):
            return TDVectorStore._process_chat_model_object(chat_completion_model)

        if isinstance(chat_completion_model, BaseChatModel):
            # Depending on Langchain Chat Model the name can be stored in different attributes.
            for attr in ['model_id', 'model', 'model_name']:
                if hasattr(chat_completion_model, attr):
                    model_name = getattr(chat_completion_model, attr)
                    if model_name:
                        return model_name

    @staticmethod
    def _process_documents_object(documents):
        """
        DESCRIPTION:
            Internal method to process the documents object.

        PARAMETERS:
            documents:
                Required Argument.
                Specifies the documents to be processed.
                Types: str or Langchain Document object or list of Langchain Document objects.

        RETURNS:
            str or teradataml DataFrame

        RAISES:
            None.

        EXAMPLES:
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore()

            # Example 1:
            # Pass in a file path to a PDF document.
            >>> vs._process_documents_objects(documents="path/to/pdf/file.pdf")

            # Example 2:
            # Pass in a list of Langchain Documents.
            >>> from langchain_core.documents import Document
            >>> doc_lc = [Document(page_content="This is a sample document content.", id="doc1"),
            >>>              Document(page_content="This is another document content.", id="doc2")]
            >>> vs._process_documents_object(documents=doc_lc)
        """
        if isinstance(documents, Document):
            documents = [documents]
        
        # Process list of Document objects
        if isinstance(documents, list) and all(isinstance(doc, Document) for doc in documents):
            # Extract page_content and id (if present)
            data = {
                "text": [doc.page_content for doc in documents],
                "id": [getattr(doc, 'id', None) for doc in documents]  # Use getattr to handle missing id
            }
            df = pd.DataFrame(data)
             
            # Generate temp table name
            table_name = UtilFuncs._generate_temp_table_name(prefix="lc_", 
                                                            table_type=TeradataConstants.TERADATA_TABLE, 
                                                            gc_on_quit=False)
            
            # Copy DataFrame to Teradata SQL table
            copy_to_sql(df, table_name=table_name, if_exists="replace", index=False)
            
            return DataFrame(table_name)
        
        return documents

    
    @collect_queryband(queryband="LC_update")
    @docstring_handler(
        common_params = {**VECTOR_STORE_SEARCH_PARAMS}
    )
    def update(self, **kwargs):
        """
        DESCRIPTION:
            Updates the search parameters of an existing vector store.

        RETURNS:
            None.
        
        RAISES:
            TeradataMLException.
        
        EXAMPLES:
            # Create an instance of the VectorStore class.
            # Note: This step is not needed if the vector store already exists.
            >>> from langchain_teradata import TeradataVectorStore
            >>> vs = TeradataVectorStore.from_datasets(name="vs",
                                                       data = "amazon_reviews_25",
                                                       data_columns = "rev_text",
                                                       key_columns = ["rev_id","aid"],
                                                       embedding = "amazon.titan-embed-text-v1")

            # Example 1: Update the search parameters of an existing vector store.
            >>> vs.update(search_algorithm="KMEANS",
                          initial_centroids_method = "RANDOM",
                          train_numcluster = 25,
                          max_iternum = 32,
                          stop_threshold = 0.04)
        """
        return super().update(**kwargs)

    @classmethod
    @collect_queryband(queryband="LC_from_documents")
    @docstring_handler(
        common_params = {**COMMON_PARAMS, **FILE_BASED_VECTOR_STORE_PARAMS, **LANGCHAIN_PARAMS, **NIM_PARAMS},
        exclude_params=["embeddings_tdgenai", "chat_completion_model_tdgenai"],
    )
    def from_documents(cls,
                      name, 
                      documents, 
                      embedding = None, 
                      **kwargs):
        """
        DESCRIPTION:
            Creates a new vector store, either 'file-based' or 'content-based',
            depending on the type of input documents.
            If the input is PDF file(s) or file path(s), a file-based vector store is created.
            If the input is LangChain Document object(s), a content-based vector store
            is created.
            Raises an error if a vector store with the specified name already exists.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User Guide for details.    

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the vector store.
                Type: str

            documents:
                Required Argument.
                Specifies the input dataset of document files or LangChain Document objects.
                For files:
                    - Accepts a directory path, wildcard pattern or a list of file paths
                    - Only PDF format is supported.
                    - Files are processed and stored as chunks in a database table.
                For LangChain Document objects:
                    - Accepts a list of Document objects
                    - Documents are processed and stored as chunks in a database table.
                Notes:
                    * Input can be either file(s)/file path(s) or LangChain Document
                      objects, not both.
                Examples:
                    Example 1: Multiple files specified within a list
                    >>> documents = ['file1.pdf', 'file2.pdf']

                    Example 2: Path to the directory containing PDF files 
                    >>> documents = "/path/to/pdfs"

                    Example 3: Path to directory containing PDF files as a wildcard string
                    >>> documents = "/path/to/pdfs/*.pdf"

                    Example 4: Path to directory containing PDF files and subdirectories of PDF files
                    >>> documents = "/path/to/pdfs/**/*.pdf"
                    
                    Example 5: List of LangChain Document objects
                    >>> from langchain_core.documents import Document
                    >>> documents = [Document(page_content="This is a test document", id="doc1"),
                                     Document(page_content="This is another test document", id="doc2")]
                Types: str, list, LangChain Document object
            
            object_names:
                Optional Argument.
                Specifies the table name to store file content splits.
                Notes:
                    * Applicable only for file-based inputs.
                    * Only one table name should be specified.
                Type: str
            
            target_database:
                Optional Argument.
                Specifies the database name where the vector store and file content
                splits are created/stored.
                Note:
                    If not specified, uses the current database.
                Type: str

            data_columns:
                Optional Argument.
                Specifies the column name(s) to store the content splits.
                Notes:
                    * Applicable only for file-based inputs.
                Type: str

        RETURNS:
            TeradataVectorStore instance.

        RAISES:
            TeradataMLException.

        EXAMPLES:
            # Example 1: Create a file-based vector store from all the PDF
            #            files in a directory by passing the directory 
            #            path in "documents" and 'amazon.titan-embed-text-v1' model
            #            in "embedding" as a string.
            # Initialize the required imports.
            >>> from langchain_teradata import TeradataVectorStore

            # Get the absolute path of the directory.
            >>> files = "<Enter/path/to/pdfs>"
            >>> vs_instance = TeradataVectorStore.from_documents(name="vs_example_1",
                                                                 documents=files,
                                                                 embedding="amazon.titan-embed-text-v1")

            # Example 2: Create a file-based vector store from
            #            a list of PDF files by passing the list of file names in
            #            "documents" and "embedding" as a TeradataAI object 
            #            of api_type 'aws' and model_name 'amazon.titan-embed-text-v1'.
            # 
            # Initialize the TeradataAI object using environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type="aws",
                                     model_name="amazon.titan-embed-text-v2:0")
            
            # Create the 'file-based' vector store instance.
            >>> files = ["file1.pdf", "file2.pdf"]
            >>> vs_instance = TeradataVectorStore.from_documents(name="vs_example_2",
                                                                 documents=files,
                                                                 embedding=llm_aws)
            
            # Example 3: Create a content-based vector store by passing a list of 
            #            LangChain Document objects in "documents", Langchain 
            #            BedrockEmbeddings object in "embedding" and BedrockChatModel
            #            object in "chat_completion_model".
            # Initialize the required imports.
            >>> from langchain_aws import BedrockEmbeddings
            >>> from langchain_core.documents import Document
            >>> from langchain.chat_models import init_chat_model

            # Initialize the BedrockEmbeddings object, Document object and BedrockChatModel object.
            >>> llm_bedrock = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")
            >>> doc_lc = [Document(page_content="This is a test document.", id="doc1"),
            >>>           Document(page_content="This is another document.", id="doc2")]
            >>> model = init_chat_model("anthropic.claude-3-5-sonnet-20240620-v1:0", 
                                        model_provider="bedrock_converse",
                                        region_name="<Enter AWS Region>")
            
            # Create the 'content-based' vector store instance.
            >>> vs_instance = TeradataVectorStore.from_documents(name="vs_example_3",
                                                                 documents=doc_lc,
                                                                 embedding=llm_bedrock,
                                                                 chat_completion_model=model)
            
            """
        return super().from_documents(name=name, documents=documents, embedding=embedding, **kwargs)

    @classmethod
    @collect_queryband(queryband="LC_from_texts")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES",),
        common_params = {**LANGCHAIN_PARAMS, **NIM_PARAMS},
        exclude_params=["embeddings_tdgenai", "chat_completion_model_tdgenai"],
    )
    def from_texts(cls, 
                   name, 
                   texts, 
                   embedding = None, 
                   **kwargs):
        """     
        EXAMPLES:
            # Example 1: Create an instance of a content-based vector store by
            #            passing list of raw strings in "texts" and
            #            "amazon.titan-embed-text-v1" in "embedding".
            # Initialize the required imports.
            >>> from langchain_teradata import TeradataVectorStore
            
            # Create the vector store instance.
            >>> vs_instance = TeradataVectorStore.from_texts(name = "vs_example_1",
                                                             texts = ["This is a sample text.",
                                                                    "This is another sample text."],
                                                             embedding="amazon.titan-embed-text-v1")
            
            # Example 2: Create an instance of a content-based vector store by
            #            passing list of raw strings in "texts",
            #            Langchain AzureOpenAIEmbeddings object in "embedding".
            #            and Langchain AzureChatOpenAI object in "chat_completion_model".
            # Initialize the required imports.
            >>> from langchain_azure import AzureOpenAIEmbeddings, AzureChatOpenAI
            >>> llm_azure = AzureOpenAIEmbeddings(model_name="text-embedding-ada-002",
                                                  api_key="azure_api_key",
                                                  azure_endpoint="azure_endpoint")
            >>> model = AzureChatOpenAI(api_key = "<Enter Azure API Key>",
                                        model_name = "gpt-35-turbo-16k",
                                        azure_ad_token = "<Enter Azure AD Token>",
                                        azure_endpoint="<Enter Azure Endpoint>",
                                        azure_deployment="<Enter Azure Deployment>",
                                        openai_api_version="<Enter OpenAI API Version>")
                                        
            >>> vs_instance = TeradataVectorStore.from_texts(name = "vs_example_2",
                                                             texts = ["This is a sample text.",
                                                                    "This is another sample text."],
                                                             embedding=llm_azure,
                                                             chat_completion_model=model)
        """
        return super().from_texts(name=name, texts=texts, embedding=embedding, **kwargs)
    
    @classmethod
    @collect_queryband(queryband="LC_from_datasets")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES",),
        common_params = {**LANGCHAIN_PARAMS, **NIM_PARAMS},
        exclude_params=["embeddings_tdgenai", "chat_completion_model_tdgenai"],
    )
    def from_datasets(cls,
                      name, 
                      data, 
                      embedding = None,
                      **kwargs):
        """
        EXAMPLES:
            # Example 1: Create an instance of a content-based vector store by
            #            passing 'amazon_reviews_25' as a DataFrame in "data"
            #            and 'amazon.titan-embed-text-v1' in "embedding".
            # Initialize the required imports.
            >>> from langchain_teradata import TeradataVectorStore
            >>> from teradatagenai import load_data, TeradataAI
            >>> from teradataml import DataFrame
            >>> load_data('byom', 'amazon_reviews_25')
            >>> data = DataFrame('amazon_reviews_25')
            
            # Create the vector store instance.
            >>> vs_instance1 = VectorStore.from_datasets(name = "vs_example_1",
                                                         data = data,
                                                         data_columns = ["rev_text"],
                                                         embedding = "amazon.titan-embed-text-v1")
            
            # Example 2: Create an instance of a content-based vector store by
            #            loading the 'employee_reviews' from teradatagenai and
            #            passing it in "data" along with TeradataAI object
            #            in "embedding".
            # Initialize the required imports.
            >>> from teradatagenai import load_data, TeradataAI
            >>> from teradataml import DataFrame
            >>> import os
            
            # Initialize the TeradataAI object using environment variables.
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "amazon.titan-embed-text-v2:0")
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            
            # Create the vector store instance.
            >>> vs_instance2 = TeradataVectorStore.from_datasets(name = "vs_example_2",
                                                                 data = data,
                                                                 data_columns = ["articles"],
                                                                 embedding = llm_aws)

            # Example 3: Create an instance of a content-based vector store by
            #            passing 'amazon_reviews_25' as a string in "data",
            #            Langchain BedrockEmbeddings object in "embedding" and
            #            additional search parameters.
            # Initialize the required imports.
            >>> from langchain_aws import BedrockEmbeddings
            >>> llm_bedrock = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")
            >>> vs_instance3 = TeradataVectorStore.from_datasets(name = "vs_example_3",
                                                                 data = "amazon_reviews_25",
                                                                 data_columns = ["rev_text"],
                                                                 embedding = llm_bedrock,
                                                                 )
        """
        return super().from_datasets(name=name, data=data, embedding=embedding, **kwargs)

    @classmethod
    @collect_queryband(queryband="LC_from_embeddings")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES",)
    )    
    def from_embeddings(cls,
                        name,
                        data,
                        **kwargs):
        """        
        EXAMPLES:
            # Example 1: Create an instance of an 'embedding-based' vector store 
            #            by passing the 'amazon_reviews_embedded' table to 
            #            "data" and "data_columns" as 'embedding'.
            # Load the amazon reviews embedded data.
            >>> from teradatagenai import VectorStore, load_data
            >>> from teradataml import DataFrame    
            >>> load_data('amazon', 'amazon_reviews_embedded')
            >>> vs_instance = TeradataVectorStore.from_embeddings(name = "vs_example_1",
                                                                  data = 'amazon_reviews_embedded',
                                                                  data_columns = ['embedding'])

            # Example 2: Create an instance of an 'embedding-based' vector store from
            #            embeddings generated using TextAnalyticsAI.
            # Import the required modules.
            >>> import os
            >>> from langchain_teradata import TeradataVectorStore
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> from teradataml import DataFrame
            
            # Load the employee data.
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            
            # Initialize the TeradataAI object using environment variables.
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> llm_embedding = TeradataAI(api_type = "aws",
                                           model_name = "amazon.titan-embed-text-v2:0")
            
            # Create an instance of the TextAnalyticsAI class.
            >>> obj_embeddings = TextAnalyticsAI(llm=llm_embedding)
            
            # Get the embeddings for the 'articles' column in the data.
            >>> TAI_embeddings = obj_embeddings.embeddings(column="articles", 
                                                           data=data,
                                                           accumulate='articles',
                                                           output_format='VECTOR')
            
            # Create an instance of the VectorStore class.
            >>> vs_instance = TeradataVectorStore.from_embeddings(name = "vs_example_2",
                                                                  data = TAI_embeddings,
                                                                  data_columns = ['Embedding'])

        """
        return super().from_embeddings(name=name, data=data, **kwargs)

    @collect_queryband(queryband="LC_add_texts")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES"),
        common_params = {**LANGCHAIN_PARAMS, **NIM_PARAMS},
        exclude_params=["embeddings_tdgenai", "chat_completion_model_tdgenai"],
    )
    def add_texts(self, texts, **kwargs):
        """            
        EXAMPLES:
            # Example 1: Add texts to an existing content-based vector store "vs_example_1"
            # Create an instance of a content-based vector store by
            # passing list of raw strings in "texts" and
            # "amazon.titan-embed-text-v1" in "embedding".
            >>> from langchain_teradata import TeradataVectorStore
            >>> vs = TeradataVectorStore.from_texts(name="vs_example_1",
                                                    texts=["This is a sample text.",
                                                           "This is another sample text."],
                                                    embedding="amazon.titan-embed-text-v1")
            >>> vs.add_texts(texts = ["This is a sample text1.",
                                      "This is another sample text2."])
            # Example 2: Create a new content-based vector store "vs_example_2".
            >>> vs = TeradataVectorStore()
            >>> vs.add_texts(name = "vs_example_2",
                             texts = ["This is a sample text.",
                                       "This is another sample text."],
                             embedding = "amazon.titan-embed-text-v1")
        """
        return super().add_texts(texts=texts, **kwargs)
    
    @collect_queryband(queryband="LC_add_documents")
    @docstring_handler(
        common_params = {**UPDATE_PARAMS, **COMMON_PARAMS, **FILE_BASED_VECTOR_STORE_PARAMS, **LANGCHAIN_PARAMS, **NIM_PARAMS},
        replace_sections = ("PARAMETERS", "EXAMPLES"),
        exclude_params=["embeddings_tdgenai", "chat_completion_model_tdgenai"]
    )
    def add_documents(self, documents, **kwargs):
        """
        DESCRIPTION:
            Adds documents to an existing file-based Vector Store.
            Creates a new Vector Store in case it does not exists.
            If the input is PDF file(s) or file path(s), a file-based vector store is created.
            If the input is LangChain Document object(s), a content-based vector store
            is created.

        PARAMETERS:
            documents:
                Required Argument.
                Specifies the dataset of document files or LangChain Document objects to be added.
                For input files:
                    A directory path or wildcard pattern can be specified.
                    The files are processed internally, converted to chunks, and 
                    stored in a database table.
                For input LangChain Document objects:
                    A list of Document objects can be specified.
                    The Document objects are processed internally and the chunks
                    are stored in a database table.
                Notes:
                    * Only PDF format is currently supported for files.
                    * Multiple document files can be supplied.
                    * Fully qualified file names should be specified.
                    * Input can be either file(s)/file path(s) or LangChain Document objects.
                      A combination of file(s)/file path(s) and LangChain Document objects
                      is not supported as input.
                Examples:
                    Example 1: Multiple files specified within a list
                    >>> documents = ['file1.pdf', 'file2.pdf']
                    Example 2: Path to the directory containing PDF files 
                    >>> documents = "/path/to/pdfs"
                    Example 3: Path to directory containing PDF files as a wildcard string
                    >>> documents = "/path/to/pdfs/*.pdf"
                    Example 4: Path to directory containing PDF files and subdirectories of PDF files
                    >>> documents = "/path/to/pdfs/**/*.pdf"
                    
                    Example 5: List of LangChain Document objects
                    >>> from langchain_core.documents import Document
                    >>> documents = [Document(page_content="This is a test document", id="doc1"),
                                     Document(page_content="This is another test document", id="doc2")]
                Types: str, list, LangChain Document object

            name:
                Optional Argument.
                Specifies the name of the vector store.
                Type: str

            object_names:
                Optional Argument.
                Specifies the table name to store file content splits.
                Notes:
                    * Applicable only for file-based inputs.
                    * Only one table name should be specified.
                Type: str
            
            target_database:
                Optional Argument.
                Specifies the database name where the vector store and file content
                splits are created/stored.
                Note:
                    If not specified, uses the current database.
                Type: str

            data_columns:
                Optional Argument.
                Specifies the column name(s) to store the content splits.
                Notes:
                    * Applicable only for file-based inputs.
                Type: str

        EXAMPLES:
            # Create an instance of an 'file-based' vector store by passing path
            # to a PDF file in "documents".
            >>> from langchain_teradata import TeradataVectorStore
            >>> import teradatagenai
            >>> import os
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> file = os.path.join(base_dir, 'example-data', 'SQL_Fundamentals.pdf')
            >>> vs_instance = TeradataVectorStore.from_documents(name = "vs_example_1",
                                                                 documents = file,
                                                                 embedding = "amazon.titan-embed-text-v1")
            >>> Set credentials for AWS Bedrock 
            >>> os.environ["AWS_DEFAULT_REGION"] = "<your_region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<your_access_key_id>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<your_secret_access_key>"
            
            # Example 1: Add "LLM_handbook.pdf" to an existing'file-based' vector store.
            >>> file = os.path.join(base_dir, 'example-data', 'LLM_handbook.pdf')
            >>> vs_instance.add_documents(documents=file)
            # Example 2: Create a content-based vector store by passing a list of 
            #            LangChain Document objects in "documents" and a Langchain 
            #            BedrockEmbeddings object in "embedding".
            # Initialize the required imports.
            >>> from langchain_aws import BedrockEmbeddings
            >>> from langchain_core.documents import Document
            
            # Initialize the BedrockEmbeddings object and the Document object.
            >>> llm_bedrock = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")
            >>> doc_lc = [Document(page_content="This is a test document.", id="doc1"),
            >>>           Document(page_content="This is another document.", id="doc2")]
            
            # Create the 'content-based' vector store instance.
            >>> vs_instance = TeradataVectorStore.from_documents(name="vs_example_3",
                                                                 documents=doc_lc,
                                                                 embedding=llm_bedrock)
            # Add more LangChain Document objects to the existing 'content-based' vector store.
            >>> doc_lc2 = [Document(page_content="This is a new document.", id="doc3"),
            >>>           Document(page_content="This is another new document.", id="doc4")]
            >>> vs_instance.add_documents(documents=doc_lc2)
            # Example 3: Create a new 'content-based' vector store by passing a list of
            #            LangChain Document objects in "documents" and a Langchain
            #            BedrockEmbeddings object in "embedding".
            # Initialize the required imports.
            >>> from langchain_aws import BedrockEmbeddings
            >>> from langchain_core.documents import Document
            # Initialize the BedrockEmbeddings object and the Document object.
            >>> llm_bedrock = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")
            >>> doc_lc = [Document(page_content="This is a test document.", id="doc1"),
            >>>           Document(page_content="This is another document.", id="doc2")]
            # Create the 'content-based' vector store instance.
            >>> vs_instance = TeradataVectorStore()
            >>> vs_instance.add_documents(name="vs_example_4",
                                                documents=doc_lc,
                                                embedding=llm_bedrock)

        """
        return super().add_documents(documents=documents, **kwargs)
        
    @collect_queryband(queryband="LC_add_datasets")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES"),
        common_params = {**LANGCHAIN_PARAMS, **NIM_PARAMS},
        exclude_params=["embeddings_tdgenai", "chat_completion_model_tdgenai"],
    )
    def add_datasets(self, data, **kwargs):
        """
        EXAMPLES:
            >>> from langchain_teradata import TeradataVectorStore
            >>> from teradataml import DataFrame
            >>> from teradatagenai import load_data
            >>> load_data("byom", "amazon_reviews_25")
            >>> amazon_reviews_25 = DataFrame('amazon_reviews_25')
            >>> amazon_reviews_10 = load_data("byom", "amazon_reviews_10")
            # Example 1: Create an instance of an 'content-based' vector store by passing the 'amazon_reviews_25' table.
            >>> vs_instance1 = TeradataVectorStore.from_datasets(name = "vs_example_1",
                                                                 data = "amazon_reviews_25",
                                                                 data_columns = ["rev_text"],
                                                                 embedding = "amazon.titan-embed-text-v1")
            # Add data to an existing content-based vector store "vs_example_1"
            >>> vs_instance1.add_datasets(data=amazon_reviews_10)
            # Example 2: Create a new 'content-based' vector store by passing the 'amazon_reviews_10' table.
            >>> vs_instance2 = TeradataVectorStore()
            >>> vs_instance2.add_datasets(name = "vs_example_2",
                                          data = "amazon_reviews_10",
                                          data_columns = ["rev_text"],
                                          embedding = "amazon.titan-embed-text-v1")

        """
        return super().add_datasets(data=data, **kwargs)

    @collect_queryband(queryband="LC_add_embeddings")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def add_embeddings(self, data, **kwargs):
        """        
        EXAMPLES:
            >>> from langchain_teradata import TeradataVectorStore
            >>> from teradataml import DataFrame
            >>> from teradatagenai import load_data
            >>> load_data("amazon", "amazon_reviews_embedded")
            >>> amazon_reviews_embedded = DataFrame('amazon_reviews_embedded')
            # Example 1: Create an instance of an 'embedding-based' vector store by passing the 'amazon_reviews_embedded' table to
            # "data" and "embedding" as 'data_columns'.
            >>> vs_instance = TeradataVectorStore.from_embeddings(name = "vs_example_1",
                                                                  data = amazon_reviews_embedded,
                                                                  data_columns = ['embedding'])
            >>> load_data("amazon", "amazon_reviews_embedded_10_alter")
            >>> amazon_reviews_embedded_10_alter = DataFrame('amazon_reviews_embedded_10_alter')
            >>> vs_instance.add_embeddings(data=amazon_reviews_embedded_10_alter)
            # Example 2: Create a new embedding-based vector store "vs_example_2"
            >>> vs_instance2 = TeradataVectorStore()
            >>> vs_instance2.from_embeddings(name = "vs_example_2",
                                             data = amazon_reviews_embedded_10_alter,
                                             data_columns = ['embedding'])
        """
        return super().add_embeddings(data=data, **kwargs)

    @collect_queryband(queryband="LC_delete_documents")    
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def delete_documents(self, documents, **kwargs):
        """
        EXAMPLES:
            # Create an instance of an 'file-based' vector store by passing path
            # to a PDF file in "documents".
            # Note:
            #   This is optional and can be skipped if the vector store is already created.
            >>> from langchain_teradata import TeradataVectorStore
            >>> import teradatagenai
            >>> import os
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> file = os.path.join(base_dir, 'example-data', 'SQL_Fundamentals.pdf')
            >>> vs_instance = TeradataVectorStore.from_documents(name = "vs_example_1",
                                                                 documents = file,
                                                                 embedding = "amazon.titan-embed-text-v1")
            # Delete "SQL_Fundamentals.pdf" from an existing 'file-based' vector store.
            >>> vs_instance.delete_documents(documents=file)
        """
        return super().delete_documents(documents=documents, **kwargs)

    @collect_queryband(queryband="LC_delete_datasets")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def delete_datasets(self, data, **kwargs):
        """
        EXAMPLES:
            # Create an instance of an 'content-based' vector store by passing the 'amazon_reviews_25' table.
            # Note:
            #   This is optional and can be skipped if the vector store is already created.
            >>> from langchain_teradata import TeradataVectorStore
            >>> from teradataml import DataFrame, copy_to_sql
            >>> from teradatagenai import load_data
            >>> load_data("byom", "amazon_reviews_25")       
            >>> amazon_reviews_25 = DataFrame('amazon_reviews_25')
            >>> amazon_reviews_10 = load_data("byom", "amazon_reviews_10")
            >>> vs_instance1 = TeradataVectorStore.from_datasets(name = "vs_example_1",
                                                                 data = [amazon_reviews_25, amazon_reviews_10],
                                                                 key_columns = ["rev_id", "aid"],
                                                                 data_columns = ["rev_text"],
                                                                 embedding = "amazon.titan-embed-text-v1")
            # Delete data from an existing content-based vector store "vs_example_1"
            >>> vs_instance1.delete_datasets(data=amazon_reviews_10)
        """
        return super().delete_datasets(data=data, **kwargs)

    @collect_queryband(queryband="LC_delete_embeddings")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def delete_embeddings(self, data, **kwargs):
        """
        EXAMPLES:
            # Create an instance of an 'embedding-based' vector store by passing the 'amazon_reviews_embedded' and 
            # 'amazon_reviews_embedded_10_alter' tables to "data" and "embedding" as 'data_columns'.
            # Note:
            #   This is optional and can be skipped if the vector store is already created with the embedding data.
            >>> from langchain_teradata import TeradataVectorStore
            >>> from teradataml import DataFrame
            >>> from teradatagenai import load_data
            >>> load_data("amazon", "amazon_reviews_embedded")
            >>> amazon_reviews_embedded = DataFrame('amazon_reviews_embedded')
            >>> vs_instance = TeradataVectorStore.from_embeddings(name = "vs_example_1",
                                                                  data = ['amazon_reviews_embedded', 'amazon_reviews_embedded_10'],
                                                                  data_columns = ['embedding'])

            # Example 1: Delete data from an existing embedding-based vector store "vs_example_1"
            >>> load_data("amazon", "amazon_reviews_embedded_10_alter")
            >>> amazon_reviews_embedded_10_alter = DataFrame('amazon_reviews_embedded_10_alter')
            >>> vs_instance.delete_embeddings(data=amazon_reviews_embedded_10_alter)

            # Example 2: Delete data from an existing embedding-based vector store "vs_example_1"
            >>> vs = TeradataVectorStore(name="vs_example_1")
            >>> amazon_reviews_embedded = DataFrame('amazon_reviews_embedded')
            >>> vs.delete_embeddings(data=amazon_reviews_embedded)
        """
        return super().delete_embeddings(data=data, **kwargs)


    @collect_queryband(queryband="LC_status")
    def status(self):
        """
        DESCRIPTION:
            Checks the status of the operations while creating, updating or destroying a vector store.

        PARAMETERS:
            None.

        RETURNS:
            Pandas DataFrame containing the status of vector store operations.

        RAISES:
            None.

        EXAMPLES:
           # Create an instance of the VectorStore class.
           >>> from langchain_teradata import TeradataVectorStore
           >>> vs = TeradataVectorStore(name="vs")
           # Example 1: Check the status of create operation.

           # Create VectorStore.
           # Note this step is not needed if vector store already exists.
           >>> vs.add_datasets(data="amazon_reviews_25",
                               key_columns=['rev_id', 'aid'],
                               data_columns=['rev_text'],
                               vector_column='VectorIndex',
                               embedding ="amazon.titan-embed-text-v1")

           # Check status.
           >>> vs.status()
        """
        return super().status()

    @collect_queryband(queryband="LC_list_user_permissions")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def list_user_permissions(self):
        """
        EXAMPLES:
            # Create an instance of an already existing vector store.
            >>> from langchain_teradata import TeradataVectorStore
            >>> vs = TeradataVectorStore(name="vs")

            # Example: List the user permissions on the vector store.
            >>> vs.list_user_permissions()
        """
        return super().list_user_permissions()
    
    @collect_queryband(queryband="LC_get_details")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def get_details(self, **kwargs):
        """
        EXAMPLES:
            # Create an instance of the TeradataVectorStore 'vs'
            # which already exists.
            >>> vs = TeradataVectorStore(name="vs")

            # Example: Get details of a vector store.
            >>> vs.get_details()
        """
        return super().get_details(**kwargs)
    

    @collect_queryband(queryband="VS_get_model_info")
    @docstring_handler(inherit_from = TDVectorStore,
                        replace_sections = ("EXAMPLES")
                        )
    def get_model_info(self):
        """
        EXAMPLES:
            >>> vs.get_model_info()
        """
        return super().get_model_info()

    @collect_queryband(queryband="LC_get_indexes_embeddings")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def get_indexes_embeddings(self):
        """
        EXAMPLES:
            >>> vs.get_indexes_embeddings()
        """
        return super().get_indexes_embeddings()

    @collect_queryband(queryband="LC_similarity_search")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def similarity_search(self, 
                          question=None,
                          **kwargs):
        """
        EXAMPLES:
            >>> from langchain_teradata import TeradataVectorStore

            # Example 1: Perform similarity search in the Vector Store for
            #            the input question.

            # Create an instance of TeradataVectorStore.
            >>> vs = TeradataVectorStore.from_documents(name = "vs",
                                                        documents = "<Enter/path/to/pdfs>",
                                                        embedding = "amazon.titan-embed-text-v1",
                                                        top_k=10)

            >>> question = 'Are there any reviews about books?'
            >>> response = vs.similarity_search(question=question)

            Example 2: Perform batch similarity search in the Vector Store.
            # Create an instance of the VectorStore class.
            # Note: This step is not needed if the vector store already exists.
            >>> vs = TeradataVectorStore.from_datasets(name="vs",
                                                       data = "valid_passages",
                                                       data_columns = "passage",
                                                       key_columns = "pid",
                                                       embedding = "amazon.titan-embed-text-v1",
                                                       top_k=10,
                                                       search_algorithm="HNSW",
                                                       vector_column="VectorIndex")

            # Perform batch similarity search in the Vector Store.
            >>> response = vs.similarity_search(batch_data="valid_passages",
                                                batch_id_column="pid",
                                                batch_query_column="passage")

            # Retrieve the batch similarity results.
            from teradatagenai import VSApi
            >>> similarity_results = vs.get_batch_result(api_name=VSApi.SimilaritySearch)
        """
        return super().similarity_search(question=question, **kwargs)
    
    @collect_queryband(queryband="LC_similarity_search_by_vector")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def similarity_search_by_vector(self,
                                    **kwargs):
        """
        EXAMPLES:
            >>> from langchain_teradata import TeradataVectorStore
            >>> from teradatagenai import load_data

            # Create an instance of the embedding-based TeradataVectorStore.
            >>> load_data('amazon', 'amazon_reviews_embedded')
            >>> vs = TeradataVectorStore.from_embeddings(name = "vs",
                                                         data = 'amazon_reviews_embedded',
                                                         data_columns = ['embedding'])
            
            # Check the status of Vector Store creation.
            >>> vs.status()

            # Example 1: Perform similarity search in the Vector Store for
            #            the input question.
            >>> response = vs.similarity_search_by_vector(question='-0.06944,0.080352,0.045963,0.006985,-0.000496,-0.025461,0.045302,-0.028107,0.031248,0.00077,-0.028107,0.016781,-0.023147,-0.068779,-0.07936,-0.030091,0.027611,-0.047616,-0.025461,0.029595,0.024635,-0.025461,-0.029926,0.046294,-0.065142,-0.019013,0.037366,-0.008019,0.065472,-0.054891,-0.009507,0.022816,0.009341,-0.041995,0.022651,0.028603,0.059851,0.047286,0.014467,0.002118,0.016616,-0.009383,-0.001643,0.015624,0.002831,0.005539,0.0248,0.018517,-0.007109,-0.013723,0.029926,0.006903,-0.011325,0.075723,0.009259,0.043648,0.035382,-0.02943,0.023147,-0.036208,-0.017856,-0.032736,0.019013,-0.037035,0.022155,-0.036704,-0.003596,-0.012069,0.021824,0.013805,-0.062827,0.016616,0.008928,-0.04431,-0.019592,-0.002397,0.048608,-0.00341,-0.024139,0.006985,-0.005001,0.002542,0.001777,0.002025,0.026123,0.055883,0.015707,0.014963,0.024304,0.001157,0.042326,-0.004753,-0.044971,0.005373,0.074731,0.002728,-0.028934,0.032736,0.011573,-0.012483,-0.040507,0.040507,0.001736,-0.036539,0.028438,0.053568,0.048278,0.082006,0.011739,0.064811,0.034059,0.062496,-0.013309,-0.065803,0.05456,-0.046624,0.009837,0.005539,-0.015376,0.016947,-0.065472,0.015128,-0.018352,0.062496,0.005539,-0.036208,0.001715,-0.023643,-0.000646,-0.047616,0.035712,0.011325,0.013723,0.07936,-0.010375,-0.021989,0.030091,0.013475,0.038358,-0.034059,-0.068118,0.013475,0.036043,-0.017029,-0.028107,-0.002687,0.00992,-0.001963,-0.04431,-0.009052,-0.088619,-0.016699,-0.027611,0.006861,-0.046624,-0.047286,-0.00744,0.00187,0.004133,-0.008225,-0.018352,0.001405,-0.033067,-0.000858,-0.001705,-0.028107,-0.01984,-0.010251,-0.013888,0.002005,0.046294,0.025461,-0.021163,-0.044971,-0.034886,-0.010747,-0.024304,0.006035,-0.019344,0.001126,-0.018352,0.015045,0.02728,-0.020749,0.000527,0.007523,-0.019427,-0.010499,0.038027,-0.027445,-0.018931,0.021659,0.037035,-0.054891,0.005539,-0.051254,-0.003968,0.011739,-0.041003,0.017029,0.011408,-0.007564,0.051584,0.010499,-0.001788,0.001075,0.032902,0.020997,-0.015624,0.020749,0.038027,0.020749,-0.046955,-0.012069,0.050262,-0.048608,0.028934,-0.074731,0.025461,-0.056875,0.013971,-0.018104,-0.054891,-0.001343,0.013888,0.019427,0.038688,0.057536,-0.011077,0.082006,0.024139,0.033894,0.037366,0.02943,-0.026619,-0.032075,-0.040672,-0.021493,0.001891,-0.013805,-0.005415,0.016451,-0.001963,0.003617,0.003286,0.016533,-0.071424,-0.042987,0.023808,-0.071424,0.008101,0.018683,-0.037862,-0.036208,0.037366,0.006531,0.016203,0.031083,-0.006448,0.008349,-0.045963,0.012648,0.032571,-0.007688,-0.043318,0.025792,0.000889,0.015211,-0.018765,-0.013061,0.040176,-0.035712,0.02232,-0.011243,-0.030091,-0.04431,-0.059851,0.011904,-0.013888,0.060182,0.04431,-0.017691,-0.008721,-0.000509,-0.010375,-0.033563,-0.03968,-0.018104,0.010044,0.020005,-0.024304,0.046955,0.001447,0.017029,-0.011739,-0.042326,0.014219,0.036539,0.028768,-0.008597,-0.005745,0.00868,-0.040011,-0.036704,0.007192,-0.042326,0.061504,0.015789,-0.023147,-0.005373,-0.039184,0.014053,-0.000713,0.003038,-0.009135,0.012483,-0.028107,-0.014549,-0.060512,0.048939,-0.069771,0.000607,0.012648,0.017195,0.018683,0.008804,0.030918,-0.038027,-0.00279,0.027611,0.007068,0.031579,0.029099,-0.004898,0.04431,-0.056875,-0.034886,-0.008267,-0.005911,-0.018517,0.009837,0.0248,0.023147,0.04464,-0.017029,0.016285,-0.0124,0.030091,0.012069,-0.013392,-0.000163,0.038027,0.008721,0.005621,-0.015707,-0.062827,-0.060182,0.026453,0.028107,0.015293,0.014219,-0.047616,0.006076,0.032571,-0.047616,-0.027115,0.046294,-0.006985,-0.027445,0.005167,-0.03191,-0.009383,-0.022981,0.025957,0.001974,0.010127,-0.038854,-0.020253,-0.046955,0.011408,-0.047616,0.006985,-0.058198,0.021989,-0.001674,0.011987,-0.006861,0.043979,0.011408,-0.007853,-0.03439,0.025957,0.013557,0.02976,0.008721,-0.012731,-0.054891,-0.058859,-0.004857,-0.005291,-0.008349,0.007895,-0.020997,0.038854,-0.008349,0.016616,-0.060843,0.040507,0.021824,0.002253,-0.012565,0.006324,0.040011,0.073078,-0.02943,0.014384,-0.031083,0.010995,-0.025131,0.009011,0.015707,0.060182,0.05919,0.017443,0.033563,-0.039184,0.051915,0.040011,-0.021493,0.036208,-0.030091,0.022981,0.056214,0.070432,-0.004071,-0.019013,-0.000377,0.014549,-0.044971,-0.019592,0.013392,0.008308,-0.002563,-0.032902,0.001405,0.013061,0.013061,-0.018269,0.022155,-0.038358,0.048608,0.078699,-0.023477,-0.031744,-0.008308,-0.042326,0.015045,0.072086,0.010333,-0.058859,0.001467,0.040011,-0.011243,0.045302,-0.028107,-0.012731,0.056875,-0.003265,-0.015541,0.007771,0.030091,-0.057206,-0.014632,0.020667,-0.041995,0.030752,0.014053,-0.038027,0.013061,0.012565,0.002366,0.049931,-0.02976,0.015045,0.007564,-0.015459,0.04464,0.005745,-0.029099,-0.013557,-0.005869,0.024304,-0.026784,0.007688,-0.073078,-0.046624,-0.00155,0.000107,0.009259,-0.022155,0.015376,0.003885,-0.080352,0.011408,-0.020749,-0.01612,0.011573,0.055222,0.013557,0.00155,0.000961,0.012069,0.002955,-0.014797,-0.041499,-0.018683,-0.035216,-0.043648,0.103169,-0.007688,-0.024965,-0.005911,-0.012483,-0.024635,0.033398,-0.014053,0.015872,0.013723,0.000314,0.033728,-0.020088,0.016947,-0.061504,-0.046624,0.07407,-0.009383,0.001602,-0.040507,-0.071424,0.000899,-0.010127,-0.024635,-0.005828,0.03968,0.021989,-0.001684,-0.028272,0.035216,-0.046294,-0.002614,-0.027941,-0.020667,0.016368,0.001157,0.005952,0.007523,0.017195,0.038027,0.004402,-0.004505,0.057536,0.042987,-0.028438,-0.033728,0.010747,-0.004629,0.026123,0.014219,-0.003245,-0.028107,0.060182,0.03439,0.016947,-3.8e-05,-0.005229,0.013144,0.042987,0.007275,-0.028768,-0.000734,-0.002687,0.030091,-0.01488,-0.027611,-0.012813,-0.015707,-0.023477,0.001509,0.028934,-0.015376,0.000372,0.005456,-0.041334,0.032571,-0.030422,0.009837,-0.054891,-0.016368,0.005497,0.03224,-0.012648,-0.038027,0.002056,-0.035216,-0.017029,-0.046955,0.035712,0.019013,-0.023477,-0.033894,0.005787,0.021493,0.011491,0.0248,0.026288,0.035712,-0.031248,0.012896,0.025627,0.046955,-0.047947,-0.076054,0.054891,-0.045632,5.1e-05,0.006613,-0.003761,-0.021659,-0.038854,0.031414,-0.028438,-0.013061,-0.05952,-0.01612,-0.018021,0.002997,0.003038,-0.047286,-0.015376,-0.021163,-0.016285,-0.002893,-0.011656,0.021659,0.024469,0.01612,0.09391,0.030918,0.009672,-0.021659,0.056214,-0.04431,0.021824,-0.011325,0.014384,-0.0248,0.043318,0.005249,-0.010664,0.030422,0.060182,-0.006903,-0.038854,-0.000153,0.007936,-0.032075,0.008473,-0.008473,0.021989,0.020749,0.020667,-0.016037,-0.016781,-0.004898,0.00744,0.020088,0.026784,0.020088,0.005022,-0.036208,-0.00186,-0.006861,0.005663,-0.014797,0.052907,-0.013723,0.04431,-0.001963,0.043318,-0.006365,0.002501,-0.011987,0.024304,0.010375,-0.017608,-0.033728,0.018517,0.00092,0.002687,-0.004629,-0.002015,0.041499,0.010664,0.048278,0.011573,-0.065142,0.029926,0.018352,0.007812,-0.03439,0.019592,0.026784,0.0496,-0.007688,0.006531,-0.001457,0.0124,0.016285,0.004505,-0.014963,-0.030091,-0.07936,0.001602,0.013144,-0.026288,-0.00062,0.000297,-0.001225,-0.011408,-0.0124,0.007027,-0.004009,-0.003968,0.029926,0.007895,0.033563,0.013061,0.006696,0.009507,-0.009796,0.05456,-0.048608,0.006076,0.032902,-0.020667,-0.002914,0.000925,0.05423,0.011077,-0.036208,0.008845,-0.030752,-0.05919,0.04431,0.037035,-0.009011,-0.020749,0.007647,0.033894,-0.052246,0.037862,0.041334,0.019344,-0.075723,-0.004795,-0.000889,-0.011325,-0.006944,0.036539,0.021163,0.015211,0.075723,-0.02976,-0.022816,-0.027445,-0.014797,0.068779,0.03472,0.107137,-0.03439,-0.001059,-0.013723,-0.023973,0.046955,-0.000853,-0.05456,-0.025957,-0.044971,-0.0496,0.048608,-0.014219,0.010499,-0.015376,-0.026784,-0.023477,0.042326,0.018104,0.018517,0.046955,0.018269,-0.02976,0.028934,-0.031579,-0.009713,0.010747,-0.023477,0.062496,0.046624,-0.042987,0.070763,0.004898,-1.1e-05,-0.03439,0.001953,0.001788,0.016781,-0.02232,0.028768,0.044971,0.028768,-0.00868,-0.037035,0.001498,-0.02728,-0.006985,0.011656,-0.013557,0.010664,-0.052576,-0.026619,0.002645,0.021328,-0.009383,0.007688,-0.026619,0.045963,-0.037862,-0.024139,0.06448,-0.060843,0.045302,0.070432,-0.013805,0.023973,-0.066795,0.095233,0.006159,0.009011,0.04183,-0.065142,0.026123,-0.007068,-0.02232,0.016947,0.038027,0.014384,0.015211,-0.050262,0.038358,-0.008804,0.021659,0.03439,0.023973,0.00248,0.023477,0.002366,-0.003451,0.002459,0.095894,0.004898,-0.001059,0.034886,0.006944,0.005993,0.05952,-0.021328,0.005373,-0.037035,-0.001297,0.051584,-0.0496,0.028934,0.018021,0.042987,0.003989,-0.03191,0.043318,0.036043,0.017029,0.009383,-0.001405,-0.084651,-0.003079,-0.011325,0.004175,0.01488,-0.012483,0.041995,-0.018765,-0.011243,-0.001591,0.024635,0.01984,0.006241,0.009383,0.003761,0.04927,0.011325,0.020667,-0.022816,-0.0496,-0.014715,0.028107,0.001225,0.012152,-0.013888,-0.058198,0.03935,0.024635,0.072416,-0.048939,0.020336,0.015128,0.004237,-0.008597,0.031414,-0.040507,-0.018765,-0.011325,0.056544,0.029595,0.001044,-0.015789,0.05423,0.032902,-0.0031,-0.010333,-0.022816,-0.025461,0.006241,-0.000273,-0.011987,-0.038027,-0.061174,0.003865,-0.02943,0.012731,0.06448,-0.040507,0.011408,0.047947,0.015128,-0.011739,0.021659,0.012069,0.020997,-0.011325,0.003637,0.014549,-0.015045,0.011077,-0.008184,0.005869,-0.037862,-0.000806,0.018517,0.028603,0.00992,-0.000245,0.005249,-0.005084,-0.000692,-0.00094,-0.019179,-0.000625,-0.009135,-0.002811,-0.018104,-0.060182,-0.0248,0.000605,0.017856,0.005022,-0.017443,0.014384,-0.010127,-0.007523,0.041003,0.033563,-0.037366,0.003927,0.00806,-0.048278,0.016533,-0.021989,-0.009176,0.019013,0.022485,-0.005332,-0.026123,-0.014632,0.023973,-0.022155,0.016947,-0.020088,0.008184,-0.021493,0.027941,0.073408,0.03224,0.018104,-0.01736,-0.007275,0.031414,-0.007357,-0.04464,0.045302,-0.010664,-0.016203,0.010375,0.004567,0.0124,-0.009011,-0.010457')

            # Example 2: Perform similarity search in the Vector Store when question is stored in a table and output
            #            should be returned in 'json' format.
            >>> load_data("amazon", "amazon_review_query")
            >>> response = vs.similarity_search_by_vector(data="amazon_review_query",
                                                          column="queryEmbedding",
                                                          return_type="json")
        """
        return super().similarity_search_by_vector(**kwargs)

    @collect_queryband(queryband="LC_prepare_response")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def prepare_response(self,
                         similarity_results,
                         question=None,
                         prompt=None,
                         **kwargs):
        """
        EXAMPLES:
            # Load necessary imports.
            >>> from langchain_teradata import TeradataVectorStore

            # Create an instance of a TeradataVectorStore.
            >>> vs = TeradataVectorStore.from_texts(name="vs",
                                                    texts=["This is a sample text for testing.",
                                                           "Another sample text for the vector store.",
                                                           "Books talk about the positive user reviews."],
                                                    embedding="amazon.titan-embed-text-v1",
                                                    top_k=10)

            # Perform similarity search in the Vector Store for
            # the input question.
            >>> question = 'Are there any reviews about books?'
            >>> response = vs.similarity_search(question=question)

            # Example 1: Prepare a natural language response to the user
            #            using the input question and similarity_results
            #            provided by similarity_search().

            question='Did any one feel the book is thin?'
            similar_objects_list = response['similar_objects_list']
            >>> vs.prepare_response(question=question,
                                    similarity_results=similar_objects_list)

            # Example 2: Perform batch similarity search in the Vector Store.
            # Creates a Vector Store.
            # Note this step is not needed if vector store already exists.
            >>> vs = TeradataVectorStore.from_datasets(name="vs",
                                                       data = "valid_passages",
                                                       data_columns = "passage",
                                                       key_columns = "pid",
                                                       embedding = "amazon.titan-embed-text-v1",
                                                       top_k=10,
                                                       search_algorithm="HNSW",
                                                       vector_column="VectorIndex")

            # Perform batch similarity search in the Vector Store.
            >>> response = vs.similarity_search(batch_data="valid_passages",
                                                batch_id_column="pid",
                                                batch_query_column="passage")

            # Get the similarity results.
            from teradatagenai import VSApi
            >>> similar_objects_list = vs.get_batch_result(api_name=VSApi.SimilaritySearch)

            # Perform batch prepare response with temperature.
            >>> vs.prepare_response(similarity_results=similar_objects_list,
                                    batch_data="valid_passages",
                                    batch_id_column="pid",
                                    batch_query_column="passage",
                                    temperature=0.7)

            # Retrieve the batch prepare response.
            >>> similarity_results = vs.get_batch_result(api_name=VSApi.PrepareResponse)
        """ 
        return super().prepare_response(similarity_results=similarity_results, 
                                        question=question, 
                                        prompt=prompt, 
                                        **kwargs)

    @collect_queryband(queryband="LC_ask")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def ask(self, 
            question=None,
            prompt=None,
            **kwargs):
        """

        EXAMPLES:
            # Load necessary imports.
            >>> from langchain_teradata import TeradataVectorStore
            >>> from teradatagenai import load_data

            # Load data into the vector store.
            >>> load_data("amazon", "amazon_reviews_25")

            # Create an instance of the TeradataVectorStore.
            >>> vs = TeradataVectorStore.from_datasets(name="vs",
                                                       data="amazon_reviews_25",
                                                       data_columns=['rev_text'],
                                                       key_columns=['rev_id', 'aid'],
                                                       vector_column='VectorIndex',
                                                       embedding="amazon.titan-embed-text-v1",
                                                       search_algorithm='VECTORDISTANCE',
                                                       top_k=10)

            >>> custom_prompt = '''List good reviews about the books. Do not assume information.
                                Only provide information that is present in the data.
                                Format results like this:
                                Review ID:
                                Author ID:
                                Review:
                                '''
            # Example 1: Perform similarity search in the Vector Store for
            #            the input question followed by preparing a natural
            #            language response to the user.

            >>> question = 'Are there any reviews saying that the books are inspiring?'
            >>> response = vs.ask(question=question, prompt=custom_prompt)

            # Example 2: Perform batch similarity search followed by
            #            prepare response in the Vector Store with temperature of 0.7.
            
            # Creates the TeradataVectorStore instance.
            >>> vs = TeradataVectorStore.from_datasets(name="vs",
                                                       data = "valid_passages",
                                                       data_columns = "passage",
                                                       key_columns = "pid",
                                                       embedding = "amazon.titan-embed-text-v1",
                                                       top_k=10,
                                                       search_algorithm="HNSW",
                                                       vector_column="VectorIndex")


            >>> prompt = "Structure the response briefly in 1-2 lines."
            >>> vs.ask(batch_data="home_depot_train",
                       batch_id_column="product_uid",
                       batch_query_column="search_term",
                       prompt=prompt,
                       temperature=0.7)

            # Retrieve the batch ask results.
            from teradatagenai import VSApi
            >>> ask_results = vs.get_batch_result(api_name=VSApi.Ask)
        """
        return super().ask(question=question, prompt=prompt, **kwargs)

    @collect_queryband(queryband="LC_get_batch_result")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def get_batch_result(self, api_name, **kwargs):
        """
        EXAMPLES:
            # Create an instance of the TeradataVectorStore.
            # Note this step is not needed if vector store already exists.
            >>> vs = TeradataVectorStore.from_datasets(name="vs",
                                                       data = "valid_passages",
                                                       data_columns = "passage",
                                                       key_columns = "pid",
                                                       embedding = "amazon.titan-embed-text-v1",
                                                       top_k=10,
                                                       search_algorithm="HNSW",
                                                       vector_column="VectorIndex")

            # Example 1: Perform batch similarity search in the Vector Store.
            >>> vs.similarity_search(batch_data="home_depot_train",
                                     batch_id_column="product_uid",
                                     batch_query_column="search_term")

            
            # Get the batch result for the similarity_search API.
            >>> from teradatagenai import VSApi
            >>> res = vs.get_batch_result(api_name=VSApi.SimilaritySearch)

            # Example 2: Perform batch prepare_response in the Vector Store.
            >>> prompt= "Structure response in question-answering format
                         Question: 
                         Answer:"
            >>> vs.prepare_response(batch_data="home_depot_train",
                                    batch_id_column="product_uid",
                                    batch_query_column="search_term",
                                    prompt=prompt)
            
            # Get the batch result for the prepare_response API.
            >>> res = vs.get_batch_result(api_name=VSApi.PrepareResponse)

            # Example 3: Perform batch ask in the Vector Store.
            >>> vs.ask(batch_data="home_depot_train",
                       batch_id_column="product_uid",
                       batch_query_column="search_term",
                       prompt=prompt)
            
            # Get the batch result for the ask API.
            >>> res = vs.get_batch_result(api_name=VSApi.Ask)
        """
        return super().get_batch_result(api_name=api_name, **kwargs)

    @collect_queryband(queryband="LC_destroy")
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def destroy(self):
        """
        EXAMPLES:
            # Load necessary imports.
            >>> from langchain_teradata import TeradataVectorStore
            >>> from teradatagenai import load_data

            # Load data into the vector store.
            >>> load_data('byom', 'amazon_reviews_25')

            # Example 1: Create a content based vector store for the data
            #            in table 'amazon_reviews_25'.
            #            Use 'amazon.titan-embed-text-v1' embedding model for
            #            creating vector store.

            # Note this step is not needed if vector store already exists.
            >>> vs = TeradataVectorStore.from_datasets(name="vs",
                                                       data="amazon_reviews_25",
                                                       data_columns=['rev_text'],
                                                       embedding="amazon.titan-embed-text-v1",
                                                       top_k=10,
                                                       search_algorithm="HNSW",
                                                       vector_column="VectorIndex")
            # Destroy the vector store.
            >>> vs.destroy()
        """
        return super().destroy()

    @property
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
        )
    def grant(self):
        """
        EXAMPLES:
            # NOTE: It is assumed that vector store "vs" already exits.
            # Create an instance of the TeradataVectorStore class.
            >>> vs = TeradataVectorStore(name="vs")
            # Grant 'admin' permission to the user 'alice' on the vector store 'vs'.
            >>> vs.grant.admin('alice')
            # Grant 'user' permission to the user 'alice' on the vector store 'vs'.
            >>> vs.grant.user('alice')
        """
        return super().grant

    @property
    @docstring_handler(
        inherit_from = TDVectorStore,
        replace_sections = ("EXAMPLES")
    )
    def revoke(self):
        """
        EXAMPLES:
            # NOTE: It is assumed that vector store "vs" already exits.
            # Create an instance of the TeradataVectorStore class.
            >>> vs = TeradataVectorStore(name="vs")
            # Revoke 'admin' permission of user 'alice' on the vector store 'vs'.
            >>> vs.revoke.admin('alice')
            # Revoke 'user' permission of user 'alice' on the vector store 'vs'.
            >>> vs.revoke.user('alice')
        """
        return super().revoke

    @property
    def embeddings(self):
        raise NotImplementedError("Method is not available.")

    def delete(self):
        raise NotImplementedError("Method is not available.")

    def get_by_ids(self):
        raise NotImplementedError("Method is not available.")
    
    @collect_queryband(queryband="LC_as_retriever")
    def as_retriever(self, **kwargs):
        """
        DESCRIPTION:
            Creates and returns a TeradataVectorStoreRetriever 
            instance that can be used to retrieve relevant documents 
            from the vector store based on similarity search.

        PARAMETERS:
            search_type
                Optional Argument
                Specifies the type of search that the Retriever should perform.
                Default Value: "similarity"
                Permitted Values: "similarity", "similarity_score_threshold"
                Types: str
                Note:
                    * "similarity_score_threshold" will be supported in the future release.
            
            search_kwargs
                Optional Argument
                Specifies additional parameters for the search operation.
                Includes the following keys:
                    * top_k
                        Optional Argument
                        Specifies the number of top clusters to be considered while searching
                        Types: int

                    * score_threshold
                        Optional Argument. Required when search_type is "similarity_score_threshold".
                        Specifies the threshold value to consider for matching tables/views
                        while searching. A higher threshold value limits responses 
                        to the top matches only.
                        Types: float                    
                    
                    * filter
                        Specifies the filter conditions to be applied to the document metadata.
                        Types: dict
                Types: dict
                Note:
                    * The argument "search_kwargs" will be supported in the future release.

        RETURNS:
            TeradataVectorStoreRetriever.

        RAISES:
            ValueError.

        EXAMPLES:
            # Example 1: Create a basic instance of the TeradataVectorStoreRetriever.
            #            Instantiate an already present vector store.
            >>> td_vs = TeradataVectorStore(name="test_vs")
            >>> retriever = td_vs.as_retriever()

            # Example 2: Create an instance of the TeradataVectorStoreRetriever 
            #            with a search_type of "similarity_score_threshold",
            #            a threshold of 0.8, and a top_k of 5.
            >>> td_vs = TeradataVectorStore(name="test_Vs")
            >>> retriever = td_vs.as_retriever(search_type="similarity_score_threshold",
                                               search_kwargs={'score_threshold': 0.8,
                                                              'top_k': 5})
        """
        return TeradataVectorStoreRetriever(vectorstore=self, **kwargs)

class TeradataVectorStoreRetriever(VectorStoreRetriever):
    """
    A retriever that uses TeradataVectorStore to retrieve documents
    based on similarity search. This class extends Langchain's 
    VectorStoreRetriever.
    """
    allowed_search_types = ("similarity", "similarity_score_threshold")
 
    def _process_similarity_results(self, results, return_scores=False):
        """    
        DESCRIPTION:
            Internal method to process the results of a similarity search
            and convert them into a list of Langchain Document objects.

        PARAMETERS:
            results:
                Required Argument.
                Specifies the results of the similarity search.
                Types: _SimilaritySearch
            
            return_scores:
                Optional Argument.
                Specifies whether to include the similarity scores in the
                returned documents.
                Default Value: False
                Types: bool

        RETURNS:
            List of Langchain Document objects.

        RAISES:
            None.
        """  

        # Get the name of data_columns from the vector store details to 
        # process similarity search results.
        data_columns = json.loads(self.vectorstore.get_details(return_type="json")["document_columns"])
        content_column = "AttributeValue" if len(data_columns) > 1 else data_columns[0]
        
        # Process all rows
        documents = []
        # Add logic to return scores if return_scores is True.
        for row in results.similar_objects.itertuples():
            page_content = getattr(row, content_column, "")
            metadata = {}
            if return_scores:
                metadata["score"] = row.score
            doc = Document(page_content=page_content, metadata=metadata)
            documents.append(doc)
        
        return documents

    def _get_ls_params(self):
        """
        DESCRIPTION:
            Internal method that overrides the parent class method to return
            an empty dictionary. This is a placeholder for any future parameters
            that might be needed Langsmith for tracing or logging.

        RETURNS:
            Dict
        """

        return {}
    
    def _get_relevant_documents(self, query: str, run_manager = None) -> list[Document]:
        """
        DESCRIPTION:
            Internal method to retrieve relevant documents based on the 
            query using the TeradataVectorStore.

        PARAMETERS:
            query:
                Required Argument.
                The query string to search for.
                Types: str

        RETURNS:
            List of Langchain Document objects.

        RAISES:
            ValueError
        """
        kwargs_ = self.search_kwargs

        # Set score_threshold to search_threshold if present in search_kwargs.
        kwargs_["search_threshold"] = kwargs_.get("score_threshold", None)

        result = self.vectorstore.similarity_search(
            question=query, 
            **kwargs_
        )

        if self.search_type == "similarity":
            return self._process_similarity_results(result)

        else:
            return self._process_similarity_results(result, return_scores=True)
