import os
from datetime import timedelta
from typing import MutableMapping, Any, Optional, List, Union, Literal
from azure.core.credentials import AzureKeyCredential
from azure.core.paging import ItemPaged
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchItemPaged
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes._generated.models import FieldMapping, IndexingSchedule, IndexingParameters, \
    IndexingParametersConfiguration
from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import SearchIndex, SearchIndexer, SearchIndexerDataSourceConnection

from .ai_search_utils import AISearchAuthStrategy


class AsyncSearchBaseDao:
    """
    Base class for Azure Cognitive Search data access operations.

    Handles environment configuration and authentication setup
    for interacting with Azure AI Search services.
    """

    def __init__(self, auth_strategy: AISearchAuthStrategy = 'ServicePrincipal'):
        """
        Initializes the SearchBaseDao by reading configuration from environment variables.
        """
        self.authentication_method: AISearchAuthStrategy = auth_strategy
        self.service_endpoint = self._get_env_variable("AZURE_AI_SEARCH_ENDPOINT")
        self.api_version = self._get_env_variable('AZURE_AI_SEARCH_API_VERSION', '2025-03-01-preview')

    @staticmethod
    def _get_env_variable(key: str, default_value: str | None = None) -> str:
        """
        Retrieves an environment variable value or returns a default if not set.

        Args:
            key (str): The name of the environment variable.
            default_value (str | None): Optional fallback value.

        Returns:
            str: The value of the environment variable or the default.
        """
        return os.environ.get(key, default_value)

    def _fetch_credentials(self) -> AzureKeyCredential | DefaultAzureCredential:
        """
        Fetches the appropriate credentials for Azure Search based on the configured authentication method.

        Returns:
            AzureKeyCredential | DefaultAzureCredential: A credential object for authenticating requests.

        Raises:
            Exception: If the authentication method is missing or invalid.
        """
        if self.authentication_method == 'Password':
            api_key = self._get_env_variable('AZURE_AI_SEARCH_API_KEY')
            credential = AzureKeyCredential(api_key)
            return credential
        elif self.authentication_method == 'ServicePrincipal':
            credential = DefaultAzureCredential()
            return credential

        error_message = (
            "AZURE_AUTHENTICATION_METHOD was not specified or is invalid. "
            "Must be one of api-search-key or service-principal"
        )
        raise Exception(error_message)


class AsyncSearchIndexDao(AsyncSearchBaseDao):
    """
    Data Access Object (DAO) for interacting with Azure AI Search Indexes.

    Inherits configuration and authentication from SearchBaseDao.
    """

    def __init__(self, auth_strategy: AISearchAuthStrategy = 'ServicePrincipal'):
        """
        Initializes the SearchIndexDao with a SearchIndexClient instance.
        """
        super().__init__(auth_strategy=auth_strategy)
        credentials = self._fetch_credentials()
        self.client = SearchIndexClient(self.service_endpoint, credentials, api_version=self.api_version)

    async def close(self):
        """Shuts down the Data Access Object instance and associated resources

        :rtype: None
        """
        await self.client.close()

    async def retrieve_index_names(self) -> list[str]:
        """
        Retrieves a list of all search index names from the Azure Search service.

        Returns:
            list[str]: A list of index names.
        """
        search_results = await self.client.list_index_names()
        results: list[str] = []

        for search_result in search_results:
            results.append(search_result)

        return results

    async def retrieve_index_schemas(self) -> list[MutableMapping[str, Any]]:
        """
        Retrieves the full schema definition for each search index.

        Returns:
            list[SearchIndex]: A list of serialized index schema definitions.
        """
        search_results: ItemPaged[SearchIndex] = await self.client.list_indexes()
        results = []

        for search_result in search_results:
            results.append(search_result.serialize(keep_readonly=True))

        return results

    async def retrieve_index_schema(self, index_name: str) -> MutableMapping[str, Any]:
        """
        Retrieves the full schema definition for a search index.

        Returns:
            SearchIndex: A serialized index schema definition.
        """
        search_results = await self.client.get_index(index_name)

        return search_results.serialize(keep_readonly=True)

    async def modify_index(self, index_name: str, updated_index_definition: SearchIndex) -> MutableMapping[str, Any]:
        """
        Updates an existing index in the Azure AI Search service.

        Args:
            index_name (SearchIndex): The name of the index to be updated
            updated_index_definition (SearchIndex): The full definition of the index.

        Returns:
            MutableMapping[str, Any]: The serialized response of the created index.
        """

        updated_index_definition.name = index_name
        operation_results = await self.client.create_or_update_index(updated_index_definition)
        return operation_results.serialize(keep_readonly=True)

    async def create_index(self, index_definition: SearchIndex) -> MutableMapping[str, Any]:
        """
        Creates a new index in the Azure AI Search service.

        Args:
            index_definition (SearchIndex): The full definition of the index to be created.

        Returns:
            MutableMapping[str, Any]: The serialized response of the created index.
        """
        operation_results = await self.client.create_index(index_definition)
        return operation_results.serialize(keep_readonly=True)

    async def delete_index(self, index_name: str):
        """
        Deletes an existing index from the Azure AI Search service.

        Args:
            index_name (str): The name of the index to be deleted.

        Returns:
            None
        """
        await self.client.delete_index(index_name)


class AsyncSearchClientDao(AsyncSearchBaseDao):

    def __init__(self, index_name: str, auth_strategy: AISearchAuthStrategy = 'ServicePrincipal'):
        """
        Initializes the SearchIndexDao with a SearchIndexClient instance.
        :param index_name: The name of the index to connect to
        """
        super().__init__(auth_strategy=auth_strategy)
        credentials = self._fetch_credentials()
        self.index_name = index_name
        self.client = SearchClient(self.service_endpoint, index_name, credentials, api_version=self.api_version)

    async def close(self):
        """Shuts down the Data Access Object instance and associated resources

        :rtype: None
        """
        await self.client.close()

    async def get_document_count(self) -> int:
        """
        Return the total number of documents in the index

        Returns:
           int: The total number of documents in the index.
        """
        search_text: str | None = None
        search_results: SearchItemPaged[dict] = await self.client.search(search_text=search_text,
                                                                         include_total_count=True)

        return await search_results.get_count()

    async def add_document(self, document: dict):
        """
        Uploads a single document to the Azure AI Search index.

        Args:
            document (dict): The document to be added to the index.

        Returns:
            MutableMapping[str, Any]: The serialized result of the add operation for the single document.
        """
        documents_to_add = [document]
        operation_results = await self.add_documents(documents_to_add)
        return operation_results[0]

    async def add_documents(self, documents: list[dict]) -> list[MutableMapping[str, Any]]:
        """
        Uploads a batch of documents to the Azure AI Search index.

        Args:
            documents (list[dict]): A list of documents to upload.

        Returns:
            list[MutableMapping[str, Any]]: A list of serialized results for each document upload operation.
        """

        operation_results = await self.client.upload_documents(documents)

        results: list[MutableMapping[str, Any]] = []

        for operation_result in operation_results:
            results.append(operation_result.serialize(keep_readonly=True))

        return results

    async def delete_document(self, key_field_name: str, key_value: str):
        """
        Deletes a single document from the Azure AI Search index.

        Args:
            key_field_name (str): The name of the key field in the index
            key_value (str): The value of the key field

        Returns:
            list[MutableMapping[str, Any]]: A list of serialized results for each document deletion operation.
        """
        document_lookup = {key_field_name: key_value}
        documents = [document_lookup]
        document_keys: list[str] = [key_value]

        results = await self.delete_documents(key_field_name=key_field_name, document_keys=document_keys)

        return results

    async def delete_documents(self, key_field_name: str, document_keys: list[str]) -> list[MutableMapping[str, Any]]:
        """
        Deletes a batch of documents from the Azure AI Search index.

        Args:
            key_field_name (str): The name of the key field in the index
            document_keys (list[str]): A list of document keys to delete.

        Returns:
            list[MutableMapping[str, Any]]: A list of serialized results for each document deletion operation.
        """
        documents_to_delete = []
        for document_key in document_keys:
            documents_to_delete.append({key_field_name: document_key})

        operation_results = await self.client.delete_documents(documents_to_delete)

        results: list[MutableMapping[str, Any]] = []

        for operation_result in operation_results:
            results.append(operation_result.serialize(keep_readonly=True))

        return results

    async def query_index(self,
                          search_text: Optional[str] = None,
                          *,
                          query_filter: Optional[str] = None,
                          order_by: Optional[List[str]] = None,
                          select: Optional[List[str]] = None,
                          skip: Optional[int] = None,
                          top: Optional[int] = None,
                          include_total_count: Optional[bool] = None,
                          ) -> list[dict]:
        """Search the Azure search index for documents.

        :param str search_text: A full-text search query expression; Use "*" or omit this parameter to
            match all documents.
        :param str query_filter: The OData $filter expression to apply to the search query.
        :param list[str] order_by: The list of OData $orderby expressions by which to sort the results. Each
            expression can be either a field name or a call to either the geo.distance() or the
            search.score() functions. Each expression can be followed by asc to indicate ascending, and
            desc to indicate descending. The default is ascending order. Ties will be broken by the match
            scores of documents. If no OrderBy is specified, the default sort order is descending by
            document match score. There can be at most 32 $orderby clauses.
        :param list[str] select: The list of fields to retrieve. If unspecified, all fields marked as retrievable
            in the schema are included.
        :param int skip: The number of search results to skip. This value cannot be greater than 100,000.
            If you need to scan documents in sequence, but cannot use $skip due to this limitation,
            consider using $orderby on a totally-ordered key and $filter with a range query instead.
        :param int top: The number of search results to retrieve. This can be used in conjunction with
            $skip to implement client-side paging of search results. If results are truncated due to
            server-side paging, the response will include a continuation token that can be used to issue
            another Search request for the next page of results.
        :param bool include_total_count: A value that specifies whether to fetch the total count of
            results. Default is false. Setting this value to true may have a performance impact. Note that
            the count returned is an approximation.
        :rtype: list[dict]
        """
        search_results = await self.client.search(
            search_text=search_text,
            include_total_count=include_total_count,
            filter=query_filter,
            order_by=order_by,
            select=select,
            skip=skip,
            top=top
        )

        search_results.get_facets()

        query_results: list[dict] = []

        for search_result_item in search_results:
            query_results.append(search_result_item)

        return query_results


class AsyncSearchIndexerDao(AsyncSearchBaseDao):
    """
    A data access object (DAO) for managing Azure AI Search indexers, data sources, and skillsets.

    This class provides methods for listing, retrieving, creating, and deleting indexers,
    as well as accessing data source connections and skillsets configured in the Azure AI Search service.
    """

    def __init__(self, auth_strategy: AISearchAuthStrategy = 'ServicePrincipal'):
        """
        Initializes the SearchIndexerDao by creating a SearchIndexerClient using credentials
        and service configuration from the base class.
        """
        super().__init__(auth_strategy=auth_strategy)
        credentials = self._fetch_credentials()
        self.client = SearchIndexerClient(self.service_endpoint, credentials, api_version=self.api_version)

    async def close(self):
        """Shuts down the Data Access Object instance and associated resources

        :rtype: None
        """
        await self.client.close()

    async def list_indexers(self) -> list[str]:
        """
        Retrieves the names of all indexers registered in the Azure AI Search service.

        Returns:
            list[str]: A list of indexer names.
        """
        search_results = await self.client.get_indexer_names()
        indexer_names: list[str] = []

        for search_result in search_results:
            indexer_names.append(search_result)
        return indexer_names

    async def get_indexer(self, name: str) -> MutableMapping[str, Any]:
        """
        Retrieves the full definition of a specific indexer.

        Args:
            name (str): The name of the indexer to retrieve.

        Returns:
            MutableMapping[str, Any]: A dictionary representing the serialized indexer definition.
        """
        indexer_details = await self.client.get_indexer(name)
        indexer_result = indexer_details.serialize(keep_readonly=True)
        return indexer_result

    async def create_indexer(self, name: str,
                             data_source_name: str,
                             target_index_name: str,
                             description: str,
                             field_mappings: list[FieldMapping],
                             output_field_mappings: list[FieldMapping],
                             skill_set_name: str = None,
                             ) -> MutableMapping[str, Any]:
        """
        Creates a new indexer in the Azure AI Search service.

        Args:
            name (str): The name of the indexer to be created.
            data_source_name (str): The name of the indexer to be created.
            target_index_name (str): The name of the indexer to be created.
            description (str): The name of the indexer to be created.
            field_mappings (list[FieldMapping]): The name of the indexer to be created.
            output_field_mappings (list[FieldMapping]): The name of the indexer to be created.
            skill_set_name (str): The name of the indexer to be created.

        Returns:
            MutableMapping[str, Any]: A dictionary representing the created indexer.
        """

        interval: timedelta = timedelta(minutes=5)
        schedule: IndexingSchedule = IndexingSchedule(interval=interval)

        parameters = await self._prepare_indexer_parameters(data_source_name)

        indexer_definition = SearchIndexer(
            name=name,
            data_source_name=data_source_name,
            target_index_name=target_index_name,
            description=description,
            skillset_name=skill_set_name,
            field_mappings=field_mappings,
            output_field_mappings=output_field_mappings,
            schedule=schedule,
            parameters=parameters
        )
        indexer_result = await self.client.create_indexer(indexer_definition)
        return await indexer_result.serialize(keep_readonly=True)

    async def _prepare_indexer_parameters(self, data_source_name) -> IndexingParameters | None:

        data_source_detail: SearchIndexerDataSourceConnection = await self.client.get_data_source_connection(
            name=data_source_name)
        data_source_type = data_source_detail.type

        # Possible values include: "azuresql", "cosmosdb", "azureblob", "azuretable", "mysql", "adlsgen2".
        if data_source_type == "azureblob":
            indexing_configuration = IndexingParametersConfiguration(data_to_extract='contentAndMetadata',
                                                                     parsing_mode='json', query_timeout=None)
            parameters = IndexingParameters(configuration=indexing_configuration)
            return parameters
        return None

    async def delete_indexer(self, name: str) -> None:
        """
        Deletes an indexer by name from the Azure AI Search service.

        Args:
            name (str): The name of the indexer to delete.
        """
        await self.client.delete_indexer(name)

    async def list_data_sources(self) -> list[str]:
        """
        Lists the names of all data source connections configured in the AI Search service.

        Returns:
            list[str]: A list of data source connection names.
        """
        data_source_names = await self.client.get_data_source_connection_names()
        search_results: list[str] = []
        for data_source_name in data_source_names:
            search_results.append(data_source_name)
        return search_results

    async def get_data_source(self, name: str) -> MutableMapping[str, Any]:
        """
        Retrieves the full definition of a specific data source connection.

        Args:
            name (str): The name of the data source connection to retrieve.

        Returns:
            MutableMapping[str, Any]: A dictionary representing the serialized data source definition.
        """
        data_source_detail: SearchIndexerDataSourceConnection = await self.client.get_data_source_connection(name=name)
        data_source_result = data_source_detail.serialize(keep_readonly=True)
        return data_source_result

    async def list_skill_sets(self) -> list[str]:
        """
        Lists the names of all skillsets configured in the Azure AI Search service.

        Returns:
            list[str]: A list of skillset names.
        """
        skill_set_names = await self.client.get_skillset_names()
        search_results: list[str] = []
        for skill_set_name in skill_set_names:
            search_results.append(skill_set_name)
        return search_results

    async def get_skill_set(self, skill_set_name: str) -> MutableMapping[str, Any]:
        """
        Retrieves the full definition of a specific skillset.

        Args:
            skill_set_name (str): The name of the skillset to retrieve.

        Returns:
            MutableMapping[str, Any]: A dictionary representing the serialized skillset definition.
        """
        skill_set_result = await self.client.get_skillset(skill_set_name)
        return await skill_set_result.serialize(keep_readonly=True)
