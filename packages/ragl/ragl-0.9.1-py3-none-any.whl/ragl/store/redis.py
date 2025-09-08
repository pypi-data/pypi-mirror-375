# pylint: disable=too-many-lines
"""
Redis-based vector storage implementation for ragl.

This module provides a Redis-backed vector store that enables efficient
storage and retrieval of text embeddings with associated metadata. It
leverages RedisVL (Redis Vector Library) for vector similarity search
operations.

Features:
    - Vector similarity search using HNSW algorithm with cosine distance
    - Metadata storage and filtering (timestamps, tags, source info)
    - Schema validation and versioning
    - Connection pooling and error handling
    - Memory usage monitoring and health checks
    - Automatic text ID generation
    - Tag-based categorization with comma-separated storage

The store supports various metadata fields including chunk position,
timestamps, confidence scores, tags, parent IDs, source information,
language, section, and author details. All metadata is sanitized
according to a predefined schema before storage.

Classes:
    RedisVectorStore:
        Manage storage and retrieval of text embeddings in Redis.
"""

import logging
import time
from contextlib import contextmanager
from typing import (
    Any,
    ClassVar,
    Iterator,
    Mapping,
    cast,
    overload,
)

import numpy as np
import redis  # type: ignore[import-untyped]
import redisvl.exceptions  # type: ignore[import-untyped]
from redisvl.index import SearchIndex  # type: ignore[import-untyped]
from redisvl.query import VectorQuery  # type: ignore[import-untyped]
from redisvl.schema import IndexSchema  # type: ignore[import-untyped]

from ragl.config import RedisConfig
from ragl.constants import TEXT_ID_PREFIX
from ragl.exceptions import (
    ConfigurationError,
    DataError,
    QueryError,
    StorageCapacityError,
    StorageConnectionError,
    ValidationError,
)
from ragl.protocols import TextEmbeddingPair
from ragl.schema import SchemaField, sanitize_metadata
from ragl.textunit import TextUnit


_LOG = logging.getLogger(__name__)


__all__ = ('RedisVectorStore',)


class RedisVectorStore:
    """
    Store and retrieve vectors in Redis.

    This class provides methods to store text and its vector embeddings
    in a Redis database, allowing for efficient similarity search and
    retrieval of relevant texts based on vector queries. It supports
    metadata storage, schema validation, and automatic text ID
    generation.

    It uses RedisVL for vector operations and Redis SearchIndex
    for indexing and querying. The store is designed to handle
    large volumes of text and metadata while enforcing limits on
    text size, metadata size, and individual field sizes.

    It also includes health checks for Redis connection and index
    status, ensuring the store is operational and can handle queries.

    It supports a flexible metadata schema that can be extended
    as needed, while providing default values for common fields.

    It also includes methods for clearing the index, deleting texts,
    and listing all stored texts.

    The store is designed to be robust, with error handling for
    connection issues, query failures, and validation errors.
    It uses a context manager for Redis connections
    to ensure proper resource management and error handling.

    Storage Limits:
        - Text content: 512 MB
        - Total metadata: 64 MB
        - Individual metadata fields: 32 MB
        - Text ID length: 256 characters

    Attributes:
        index:
            Redis SearchIndex instance.
        index_name:
            Name of the Redis search index.
        index_schema:
            Schema defining the index structure.
        redis_client:
            Redis client instance.
        dimensions:
            Size of embedding vectors.
        validation_schema:
            Schema for metadata sanitization.

    Note:
        Metadata fields like tags are stored as strings in Redis
        (e.g., comma-separated for tags), but are returned as their
        expected types (e.g., list for tags) in method results,
        such as get_relevant.

    Example:
        >>> config = RedisConfig(host='localhost', port=6379)
        >>> store = RedisVectorStore(
        ...     redis_config=config,
        ...     dimensions=768,
        ...     index_name='documents'
        ... )
        >>> text_id = store.store_text(
        ...     text="Sample document",
        ...     embedding=some_embedding,
        ...     metadata={'tags': ['important'], 'source': 'docs'}
        ... )
        >>> results = store.get_relevant(embedding=another_embedding, top_k=5)
    """

    SCHEMA_VERSION: ClassVar[int] = 1

    MAX_FIELD_SIZE: ClassVar[int] = (1024 * 1024) * 32
    MAX_METADATA_SIZE: ClassVar[int] = (1024 * 1024) * 64
    MAX_TEXT_SIZE: ClassVar[int] = (1024 * 1024) * 512
    MAX_TEXT_ID_LENGTH: ClassVar[int] = 256

    POOL_DEFAULTS: ClassVar[dict[str, Any]] = {
        'socket_timeout':           5,
        'socket_connect_timeout':   5,
        'retry_on_timeout':         True,
        'max_connections':          50,
        'health_check_interval':    30,
    }

    TAG_SEPARATOR: ClassVar[str] = ','
    TEXT_COUNTER_KEY: ClassVar[str] = 'text_counter'

    LARGE_BATCH_THRESHOLD: ClassVar[int] = 100

    index: SearchIndex
    index_name: str
    index_schema: IndexSchema
    redis_client: redis.Redis
    dimensions: int
    validation_schema: dict[str, SchemaField]

    @overload
    def __init__(
            self,
            *,
            redis_client: redis.Redis,
            dimensions: int | None,
            index_name: str,
    ) -> None:  # noqa: D107
        ...  # pragma: no cover

    @overload
    def __init__(
            self,
            *,
            redis_config: RedisConfig,
            dimensions: int | None,
            index_name: str,
    ) -> None:  # noqa: D107
        ...  # pragma: no cover

    def __init__(
            self,
            *,
            redis_client: redis.Redis | None = None,
            redis_config: RedisConfig | None = None,
            dimensions: int | None = None,
            index_name: str,
    ):
        """
        Initialize Redis store with existing client or configuration.

        Connects to Redis using either a provided client instance or
        configuration. Sets up the vector search index with the
        specified dimensions and index name. Validates the connection
        and schema version. Creates the index if it does not already
        exist.

        Args:
            redis_client:
                Redis client instance. If provided, config is ignored.
            redis_config:
                Redis configuration object. If provided, redis_client
                is ignored.
            dimensions:
                Size of embedding vectors, required for schema
                creation.
            index_name:
                Name of the Redis search index.

        Raises:
            StorageConnectionError:
                If Redis connection or index creation fails.
            ConfigurationError:
                If both redis_client and redis_config are provided, or
                if schema version mismatch occurs.
        """
        self.redis_client = self._initialize_redis(redis_client, redis_config)
        self._validate_dimensions(dimensions)
        self._validate_index_name(index_name)
        assert dimensions is not None
        self.dimensions = dimensions
        self.index_name = index_name

        self._enforce_schema_version()
        self.validation_schema = self._create_validation_schema()
        self.index_schema = self._create_index_schema(index_name)
        self.index = SearchIndex(self.index_schema, self.redis_client)
        self._initialize_search_index()
        _LOG.info('Initialized RedisVectorStore with index: %s', index_name)

    def clear(self) -> None:
        """
        Clear all data from the Redis index.

        This method deletes the existing index and creates a new one,
        resetting the schema version to the current version.
        """
        with self.redis_context() as client:
            self.index.delete(drop=True)
            self.index.create()
            _LOG.info('Index cleared successfully')
            version_key = f'schema_version:{self.index_name}'
            client.set(version_key, self.SCHEMA_VERSION)
            _LOG.info('Reset schema version to %s for index %s',
                      self.SCHEMA_VERSION, self.index_name)

    def close(self) -> None:
        """Close Redis connection pool."""
        _LOG.debug('Closing RedisVectorStore with index: %s', self.index_name)
        if hasattr(self, 'redis_client'):
            self.redis_client.close()

    def delete_text(self, text_id: str) -> bool:
        """
        Delete a text from Redis.

        Deletes the specified text ID from Redis. If the text ID does
        not exist, it returns False. If the deletion is successful,
        it returns True.

        Args:
            text_id:
                ID of text to delete.

        Returns:
            True if the text was deleted, False if it did not exist.
        """
        return bool(self.delete_texts([text_id]))

    def delete_texts(self, text_ids: list[str]) -> int:
        """
        Delete multiple texts from Redis.

        Deletes the specified text IDs from Redis. If a text ID does
        not exist, it is ignored. Returns the number of successfully
        deleted texts.

        Args:
            text_ids:
                List of text IDs to delete.

        Returns:
            The number of deleted text_id.
        """
        _LOG.info('Deleting texts from store')
        _LOG.debug('Deleting text IDs: %s', text_ids)
        if not text_ids:
            return 0

        for text_id in text_ids:
            self._validate_text_id(text_id)

        deleted = len(text_ids)
        with self.redis_context() as client:
            deleted_result = client.delete(*text_ids)
            if isinstance(deleted_result, int):
                deleted = deleted_result

        return deleted

    def get_relevant(
            self,
            embedding: np.ndarray,
            top_k: int,
            *,
            min_time: int | None = None,
            max_time: int | None = None,
    ) -> list[TextUnit]:
        """
        Retrieve relevant texts from Redis.

        Performs a vector search in Redis using the provided embedding
        and returns the top_k most relevant results as TextUnit objects.
        Applies optional timestamp filters to limit results to a
        specific time range.

        Args:
            embedding:
                Query embedding.
            top_k:
                Number of results to return.
            min_time:
                Minimum timestamp filter.
            max_time:
                Maximum timestamp filter.

        Returns:
            List of TextUnit objects, may be fewer than top_k.
        """
        start_time = time.time()
        self._validate_dimensions_match(embedding)

        _LOG.info('Retrieving relevant texts from Redis: '
                  'top_k=%d, time_range=%s-%s',
                  top_k, min_time or 'none', max_time or 'none')
        vector_query = self._build_vector_query(
            embedding=embedding,
            top_k=top_k,
            min_time=min_time,
            max_time=max_time,
        )
        results = self._search_redis(vector_query)
        result_dicts = self._transform_redis_results(results)

        duration = time.time() - start_time
        _LOG.info('Retrieved %d relevant texts in %.3fs',
                  len(result_dicts), duration)

        return [TextUnit.from_dict(result_dict)
                for result_dict in result_dicts]

    def health_check(self) -> dict[str, Any]:
        """
        Check Redis connection and index health.

        Performs a health check on the Redis connection and the vector
        search index. It verifies if Redis is connected, verifies the
        index exists, and retrieves memory usage information. It also
        checks if the index is healthy by verifying the number of
        documents.

        Returns:
            Dictionary with health status and diagnostics.
        """
        _LOG.info('Checking Redis connection and index health')
        health_status = {
            'redis_connected':       False,
            'index_exists':          False,
            'index_healthy':         False,
            'memory_info':           {},
            'last_check':            int(time.time()),
            'errors':                [],
        }

        try:
            with self.redis_context() as client:

                info = client.info()
                if isinstance(info, Mapping):
                    health_status['redis_connected'] = True
                    memory_info = self._extract_memory_info(info)
                    health_status['memory_info'] = memory_info

                    used_memory = info.get('used_memory', 0)
                    maxmemory = info.get('maxmemory', 0)
                    if maxmemory > 0:
                        memory_usage_pct = (used_memory / maxmemory) * 100
                        if memory_usage_pct > 80:
                            _LOG.warning('Redis memory usage high: %.1f%%',
                                         memory_usage_pct)
        except Exception as e:
            msg = f'Redis health check failed: {e}'
            _LOG.error(msg)
            raise

        index_info = self.index.info()
        health_status['index_exists'] = bool(index_info)
        health_status['index_healthy'] = 'num_docs' in index_info
        health_status['document_count'] = index_info.get('num_docs', 0)

        return health_status

    def list_texts(self) -> list[str]:
        """
        List all text IDs in Redis.

        Retrieves all text IDs stored in Redis by searching for keys
        that match the TEXT_ID_PREFIX. It returns a sorted list of
        text IDs, which are used to identify stored texts.

        Returns:
            Sorted list of text IDs.
        """
        _LOG.info('Listing all text IDs in Redis')
        with self.redis_context() as client:
            keys = client.keys(f'{TEXT_ID_PREFIX}*')
            return sorted(cast(list[str], keys))

    @staticmethod
    def prepare_tags_for_storage(tags: Any) -> str:
        """
        Convert tags to a string for Redis store.

        Converts a list of tags or a single tag into a comma-separated
        string for storage in Redis. It ensures that each tag is
        stripped of whitespace and converted to a string. If tags
        is not a list, it converts it to a string directly.

        This method is injected into the data sanitization machinery,
        and is presented as a staticmethod which is callable by external
        objects working with a class rather than instance.

        For more information on how this method is used, see:
            - RedisVectorStore._create_validation_schema()
            - ragl.schema.sanitize_metadata()

        Args:
            tags:
                Tags to convert (list or other).

        Returns:
            Comma-separated string of tags.
        """
        _LOG.debug('Converting tags to string')
        if tags is None:
            tag_list = []
        elif isinstance(tags, str):
            tag_list = [tags]
        elif isinstance(tags, list):
            tag_list = tags
        else:
            msg = f'Invalid tag type: {type(tags).__name__}'
            _LOG.error(msg)
            raise ValidationError(msg)

        validated_tags = []
        delim = getattr(RedisVectorStore, 'TAG_SEPARATOR', ',')

        for tag in tag_list:

            if not isinstance(tag, str):
                msg = f'All tags must be strings, got {type(tag).__name__}'
                _LOG.error(msg)
                raise ValidationError(msg)

            tag = tag.strip()

            if not tag:
                continue

            if delim in tag:
                msg = f'Tag cannot contain delimiter: {delim}'
                _LOG.error(msg)
                raise ValidationError(msg)

            if any(char in tag for char in ('\n', '\r', '\t')):
                msg = 'Tag cannot contain newline, carriage return, or tab'
                _LOG.error(msg)
                raise ValidationError(msg)

            validated_tags.append(tag)

        return delim.join(t for t in validated_tags)

    @contextmanager
    def redis_context(self) -> Iterator[redis.Redis]:
        """
        Context manager for Redis connection and error handling.

        This method ensures that Redis connections are properly managed
        and that errors are caught and logged.
        """
        _LOG.debug('Initializing Redis context manager')
        try:
            self.redis_client.ping()
            yield self.redis_client

        except redis.ConnectionError as e:
            _LOG.error('Redis connection failed: %s', e)
            raise StorageConnectionError(
                f'Redis connection failed: {e}') from e

        except redis.TimeoutError as e:
            _LOG.error('Redis operation timed out: %s', e)
            raise StorageConnectionError(f'Redis timeout: {e}') from e

        except redis.ResponseError as e:
            error_msg = str(e).lower()
            if 'oom' in error_msg or 'memory' in error_msg:
                _LOG.error('Redis out of memory: %s', e)
                raise StorageCapacityError(f'Redis out of memory: {e}') from e
            _LOG.error('Redis operation failed: %s', e)
            raise DataError(f'Redis operation failed: {e}') from e

    def store_text(self, text_unit: TextUnit, embedding: np.ndarray) -> str:
        """
        Store a single text and its embedding in Redis.

        Stores the provided text and its vector embedding in Redis.
        Validates and sanitizes the input before storage.

        Args:
            text_unit:
                TextUnit containing the text and metadata.
            embedding:
                Vector embedding for the text.

        Returns:
            The generated text ID after successful storage.
        """
        text_ids = self.store_texts([(text_unit, embedding)])
        return text_ids[0]

    def store_texts(
            self,
            texts_and_embeddings: list[TextEmbeddingPair],
    ) -> list[str]:
        """
        Store multiple texts and embeddings in batch.

        Processes multiple text-embedding pairs efficiently by batching
        the storage operations. Validates all inputs before storing and
        returns the list of generated text IDs.

        Args:
            texts_and_embeddings:
                List of (TextUnit, np.ndarray) tuples to store.

        Returns:
            List of text IDs for the stored texts.

        Raises:
            ValidationError:
                If any input is invalid.
        """
        self._validate_batch_input_structure(texts_and_embeddings)

        if not texts_and_embeddings:
            return []

        _LOG.info('Storing batch of %d text-embedding pairs',
                  len(texts_and_embeddings))

        batch_data = self._prepare_batch_data(texts_and_embeddings)
        stored_ids = self._execute_batch_storage(batch_data)

        _LOG.debug('Successfully stored batch of %d texts', len(stored_ids))
        return stored_ids

    def _build_vector_query(
            self,
            embedding: np.ndarray,
            top_k: int,
            min_time: int | None,
            max_time: int | None,
    ) -> VectorQuery:
        """
        Build a vector query for Redis search.

        Constructs a VectorQuery object for searching Redis using the
        provided embedding and optional timestamp filters.

        Args:
            embedding:
                Query embedding.
            top_k:
                Number of results to return.
            min_time:
                Minimum timestamp filter.
            max_time:
                Maximum timestamp filter.

        Raises:
            ValidationError:
                If top_k is not positive.

        Returns:
            Configured VectorQuery object.
        """
        _LOG.debug('Building vector query')
        self._validate_top_k(top_k)

        _min_time: int | str | None = min_time
        _max_time: int | str | None = max_time

        if _min_time is None:
            _min_time = '-inf'
        if _max_time is None:
            _max_time = '+inf'

        filter_expr = f'@timestamp:[{_min_time} {_max_time}]'

        return_fields = [
            'text', 'chunk_position', 'parent_id', 'source', 'timestamp',
            'tags', 'confidence', 'language', 'section', 'author'
        ]
        return VectorQuery(
            vector=embedding.tobytes(),
            vector_field_name='embedding',
            return_fields=return_fields,
            num_results=top_k,
            filter_expression=filter_expr if filter_expr else None,
        )

    @staticmethod
    def _clean_tag_value(tag_value: str) -> str:
        """
        Clean and normalize a single tag value.

        Removes leading/trailing whitespace and surrounding quotes
        from the tag value. If the input is not a string, it converts
        it to a string before cleaning.

        Args:
            tag_value: Raw tag value string

        Returns:
            Cleaned tag string, or empty string if invalid
        """
        _LOG.debug('Cleaning tag value: %s', tag_value)
        if not isinstance(tag_value, str):
            tag_value = str(tag_value)

        cleaned = tag_value.strip()

        if len(cleaned) >= 2:
            if (
                (cleaned.startswith("'") and cleaned.endswith("'")) or
                (cleaned.startswith('"') and cleaned.endswith('"'))
            ):
                cleaned = cleaned[1:-1].strip()

        return cleaned

    def _create_index_schema(self, index_name: str) -> IndexSchema:
        """
        Create a Redis-specific schema for the vector search index.

        Configures fields like text, tags, and embeddings for Redis
        store and retrieval using the provided index name and
        dimensions.

        Args:
            index_name:
                Name of the Redis search index.

        Returns:
            Configured IndexSchema object for Redis.
        """
        _LOG.debug('Creating index schema for index: %s', index_name)
        return IndexSchema.from_dict({
            'index':  {
                'name':   index_name,
                'prefix': TEXT_ID_PREFIX,
            },
            'fields': [
                {
                    'name': 'text',
                    'type': 'text',
                },
                {
                    'name': 'chunk_position',
                    'type': 'numeric',
                },
                {
                    'name': 'parent_id',
                    'type': 'text',
                },
                {
                    'name': 'source',
                    'type': 'text',
                },
                {
                    'name': 'timestamp',
                    'type': 'numeric',
                },
                {
                    'name': 'confidence',
                    'type': 'numeric',
                },
                {
                    'name': 'language',
                    'type': 'text',
                },
                {
                    'name': 'section',
                    'type': 'text',
                },
                {
                    'name': 'author',
                    'type': 'text',
                },
                {
                    'name': 'tags',
                    'type': 'tag',
                    'attrs': {'separator': self.TAG_SEPARATOR},
                },
                {
                    'name': 'embedding',
                    'type': 'vector',
                    'attrs': {
                        'dims':             self.dimensions,
                        'algorithm':        'HNSW',
                        'distance_metric':  'COSINE',
                    },
                },
            ]
        })

    @staticmethod
    def _create_validation_schema() -> dict[str, SchemaField]:
        """
        Create the validation schema for metadata fields.

        Defines the expected types and default values for metadata
        fields to ensure consistent sanitization before storage.

        Returns:
            Dictionary mapping field names to their schema definitions.
        """
        _LOG.debug('Creating validation schema')
        return {
            'chunk_position': {
                'type':    int,
                'default': 0,
            },
            'timestamp':      {
                'type':    int,
                'default': 0,
            },
            'confidence':     {
                'type':    float,
                'default': 0.0,
            },
            'tags':           {
                'type':    str,
                'default': '',
                'convert': RedisVectorStore.prepare_tags_for_storage,
            },
            'parent_id':      {
                'type':    str,
                'default': '',
            },
            'source':         {
                'type':    str,
                'default': '',
            },
            'language':       {
                'type':    str,
                'default': '',
            },
            'section':        {
                'type':    str,
                'default': '',
            },
            'author':         {
                'type':    str,
                'default': '',
            },
        }

    def _enforce_schema_version(self) -> None:
        """
        Check whether stored schema matches current version.

        This method checks the Redis store for the schema version
        associated with the current index. If no version is found,
        it sets the schema version to the current version. If a
        version is found but does not match the current version,
        it raises a ConfigurationError indicating a schema mismatch.

        Raises:
            ConfigurationError:
                If schema version mismatch occurs.
        """
        with self.redis_context() as client:
            version_key = f'schema_version:{self.index_name}'
            stored_version = client.get(version_key)

            if stored_version is None:

                client.set(version_key, self.SCHEMA_VERSION)
                _LOG.info('Set schema version to %s for index %s',
                          self.SCHEMA_VERSION, self.index_name)
            else:
                if isinstance(stored_version, str):
                    stored_version = int(stored_version)

                if stored_version != self.SCHEMA_VERSION:
                    raise ConfigurationError(
                        f'Schema version mismatch for {self.index_name=}: '
                        f'{stored_version=}, expected={self.SCHEMA_VERSION}. '
                        f'Clear the index or update schema version.'
                    )
                _LOG.debug('Schema version %s confirmed for index %s',
                           self.SCHEMA_VERSION, self.index_name)

    def _execute_batch_storage(
            self,
            batch_data: dict[str, dict[str, Any]],
    ) -> list[str]:
        """
        Execute the batch storage operation in Redis.

        Performs the actual storage of prepared batch data into Redis.

        Args:
            batch_data:
                Dictionary mapping text IDs to their prepared data.

        Returns:
            List of successfully stored text IDs.

        Raises:
            DataError:
                If storage operation fails.
        """
        keys = list(batch_data.keys())
        values = list(batch_data.values())

        with self.redis_context():
            return self.index.load(data=values, keys=keys)

    @staticmethod
    def _extract_memory_info(info: Mapping) -> dict[str, Any]:
        """
        Extract memory information from Redis meminfo.

        Args:
            info:
                Redis memory info dictionary.
        """
        return {
            'used_memory':               info.get('used_memory', 0),
            'used_memory_human':         info.get('used_memory_human',
                                                  'unknown'),
            'used_memory_peak':          info.get('used_memory_peak', 0),
            'used_memory_peak_human':    info.get('used_memory_peak_human',
                                                  'unknown'),
            'maxmemory':                 info.get('maxmemory', 0),
            'maxmemory_human':           info.get('maxmemory_human',
                                                  'not set'),
            'maxmemory_policy':          info.get('maxmemory_policy',
                                                  'noeviction'),
            'total_system_memory':       info.get('total_system_memory', 0),
            'total_system_memory_human': info.get('total_system_memory_human',
                                                  'unknown'),
        }

    def _initialize_redis(
            self,
            redis_client: redis.Redis | None,
            redis_config: RedisConfig | None,
    ) -> redis.Redis:
        """
        Configure and return Redis client.

        Configures and returns Redis client based on provided
        arguments. Validates connection and raises appropriate
        exceptions for configuration errors or connection failures.

        Args:
            redis_client:
                Redis client instance.
            redis_config:
                Redis configuration object.

        Returns:
            Fully initialized Redis client.

        Raises:
            ConfigurationError: If configuration is invalid.
            StorageConnectionError: If connection fails.
        """
        _LOG.info('Initializing Redis client')
        if redis_client is None and redis_config is None:
            msg = 'Either redis_client or redis_config must be provided'
            _LOG.error(msg)
            raise ConfigurationError(msg)

        if redis_client is not None and redis_config is not None:
            msg = 'Both redis_client and redis_config were provided'
            _LOG.error(msg)
            raise ConfigurationError(msg)

        if redis_client is not None:
            try:
                redis_client.ping()
                _LOG.info('Successfully connected to injected Redis client')
                return redis_client
            except redis.ConnectionError as e:
                msg = f'Injected Redis client connection failed: {e}'
                _LOG.error(msg)
                raise StorageConnectionError(msg) from e
        else:
            if not isinstance(redis_config, RedisConfig):
                msg = 'redis_config must be an instance of RedisConfig'
                _LOG.error(msg)
                raise ConfigurationError(msg)

            pool_config = {**self.POOL_DEFAULTS, **redis_config.to_dict()}
            pool = redis.BlockingConnectionPool(**pool_config)
            return redis.Redis(connection_pool=pool)

    def _initialize_search_index(self) -> None:
        """
        Set up the Redis search index, creating it if it doesn't exist.

        Raises:
            DataError:
                If index creation fails.
            StorageConnectionError:
                If Redis connection fails.
        """
        _LOG.info('Initializing Redis search index: %s', self.index_name)
        try:
            if not self.index.exists():
                self.index.create()
                _LOG.info('Created new index: %s', self.index_name)
                _LOG.info('Connected to index: %s', self.index_name)
            else:
                index_info = self.index.info()
                doc_count = index_info.get('num_docs', 0)
                _LOG.info('Connected to existing index: %s (%d documents)',
                          self.index_name, doc_count)

        except redis.ResponseError as e:
            msg = f'Failed to create Redis index: {e}'
            _LOG.error(msg)
            raise DataError(msg) from e

        except redis.ConnectionError as e:
            msg = f'Failed to connect to Redis: {e}'
            _LOG.error(msg)
            raise StorageConnectionError(msg) from e

        except Exception as e:
            raise DataError(f'Unexpected error creating index: {e}') from e

    def _generate_text_id(self) -> str:
        """
        Generate a unique text ID.

        Generates a unique text ID if not provided. It uses a Redis
        counter to ensure uniqueness. If a text ID is provided,
        it's returned unchanged.

        Returns:
            Generated text ID.
        """
        with self.redis_context() as client:
            counter = client.incr(self.TEXT_COUNTER_KEY)
        return f'{TEXT_ID_PREFIX}{counter}'

    def _parse_list_tags(self, tags_list: list) -> list[str]:
        """
        Parse tags from a list format.

        Handles nested comma-separated strings within list
        elements.

        Args:
            tags_list:
                List containing tag elements

        Returns:
            List of cleaned tag strings
        """
        result = []

        for tag_item in tags_list:
            if isinstance(tag_item, str):

                if self.TAG_SEPARATOR in tag_item:
                    split_tags = tag_item.split(self.TAG_SEPARATOR)
                    for split_tag in split_tags:
                        cleaned = self._clean_tag_value(split_tag)
                        if cleaned:
                            result.append(cleaned)

                else:
                    cleaned = self._clean_tag_value(tag_item)
                    if cleaned:
                        result.append(cleaned)

            else:
                cleaned = self._clean_tag_value(str(tag_item))
                if cleaned:
                    result.append(cleaned)

        return result

    def _parse_string_tags(self, tags_str: str) -> list[str]:
        """
        Parse tags from a string format.

        Handles both comma-separated strings and string
        representations of lists.

        Args:
            tags_str:
                String containing tags

        Returns:
            List of cleaned tag strings
        """
        # Handle string representation of list (e.g., "['tag1', 'tag2']")
        if tags_str.startswith('[') and tags_str.endswith(']'):
            # Remove brackets and split by comma
            inner = tags_str[1:-1]
            if not inner.strip():
                return []

            # Split and clean each tag
            raw_tags = [tag.strip() for tag in inner.split(',')]
            return [self._clean_tag_value(tag)
                    for tag in raw_tags if tag.strip()]

        # Handle comma-separated string (e.g., "tag1,tag2,tag3")
        if self.TAG_SEPARATOR in tags_str:
            raw_tags = tags_str.split(self.TAG_SEPARATOR)
            return [self._clean_tag_value(tag)
                    for tag in raw_tags if tag.strip()]

        # Single tag
        cleaned = self._clean_tag_value(tags_str)
        return [cleaned] if cleaned else []

    def _parse_tags_from_retrieval(self, tags) -> list[str]:
        """
        Parse tags from Redis retrieval into a clean list.

        Cleans and splits tags from Redis retrieval into a list of
        tag strings. It handles both string and list formats, removing
        unnecessary characters and whitespace. If tags are None,
        it returns an empty list.

        Args:
            tags: Tags from Redis.

        Returns:
            List of tag strings.
        """
        if tags is None:
            return []

        if isinstance(tags, str):
            return self._parse_string_tags(tags)

        if isinstance(tags, list):
            return self._parse_list_tags(tags)

        return []

    def _prepare_batch_data(
            self,
            texts_and_embeddings: list[TextEmbeddingPair],
    ) -> dict[str, dict[str, Any]]:
        """
        Prepare batch data for storage.

        Prepares each text-embedding pair for storage in Redis. Ensures
        that each entry is valid and properly formatted before returning
        a dictionary of prepared data.

        Args:
            texts_and_embeddings:
                List of (TextUnit, np.ndarray) tuples to validate and prepare.

        Returns:
            Batch data dictionary mapping text IDs to prepared data.

        Raises:
            ValidationError:
                If any input is invalid.
        """
        _LOG.debug('Preparing batch data for %d items',
                   len(texts_and_embeddings))

        batch_data = {}

        total_items = len(texts_and_embeddings)
        if total_items > self.LARGE_BATCH_THRESHOLD:
            _LOG.info('Processing large batch: %d items', total_items)

        for i, (text_unit, embedding) in enumerate(texts_and_embeddings):

            very_large_batch = self.LARGE_BATCH_THRESHOLD * 10
            chunk = very_large_batch / 2
            if total_items > very_large_batch and (i + 1) % chunk == 0:
                _LOG.info('Processed %d/%d items (%.1f%%)',
                          i + 1, total_items, ((i + 1) / total_items) * 100)

            text_id, prepared_data = self._prepare_single_text_entry(
                text_unit=text_unit,
                embedding=embedding,
            )
            batch_data[text_id] = prepared_data

        return batch_data

    @staticmethod
    def _prepare_redis_payload(
            text: str,
            embedding: np.ndarray,
            metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create data structured for Redis store.

        Prepares a dictionary containing the text, embedding, and
        sanitized metadata for storage in Redis. The embedding is
        converted to bytes for Redis storage. The metadata is expected
        to be sanitized according to the schema defined in the store.

        Args:
            text:
                Text to store.
            embedding:
                Vector embedding.
            metadata:
                Sanitized metadata.

        Returns:
            Dict with text, embedding, and metadata.
        """
        _LOG.debug('Preparing Redis payload')
        return {
            'text':             text,
            'embedding':        embedding.tobytes(),
            **metadata,
        }

    def _prepare_single_text_entry(
            self,
            text_unit: TextUnit,
            embedding: np.ndarray,
    ) -> tuple[str, dict[str, Any]]:
        """
        Prepare a single text entry for Redis storage.

        Validates and sanitizes a single TextUnit and its embedding
        for storage in Redis. It ensures the text and metadata meet
        size and format requirements, generates a text ID if needed,
        and prepares the data dictionary for Redis.

        Args:
            text_unit:
                TextUnit containing text and metadata.
            embedding:
                Vector embedding for the text.

        Returns:
            Tuple of (text_id, prepared_data_dict).

        Raises:
            ValidationError:
                If input validation fails.
        """
        text_data = text_unit.to_dict()
        text = text_data.pop('text')

        if not text.strip():
            msg = 'text cannot be empty be empty'
            _LOG.error(msg)
            raise ValidationError(msg)

        text_id = text_unit.text_id
        if text_id is None:
            text_id = self._generate_text_id()
            text_unit.text_id = text_id

        self._validate_input_sizes(text, text_data)
        self._validate_text_id(text_id)
        self._validate_dimensions_match(embedding)

        sanitized = sanitize_metadata(
            metadata=text_data,
            schema=self.validation_schema,
        )

        prepared_data = self._prepare_redis_payload(
            text=text,
            embedding=embedding,
            metadata=sanitized,
        )

        return text_id, prepared_data

    def _search_redis(self, vector_query: VectorQuery) -> Any:
        """
        Execute a vector search in Redis.

        Executes a vector search using the provided VectorQuery object.
        It handles various exceptions that may occur during the search
        operation, including connection errors, query errors, and memory
        issues. If the search is successful, it returns the results.

        Args:
            vector_query:
                Query to execute.

        Raises:
            StorageConnectionError:
                If Redis connection fails.
            QueryError:
                If search operation fails.

        Returns:
            Redis search results.
        """
        _LOG.debug('Executing Redis vector search')
        try:
            return self.index.search(
                vector_query.query,
                query_params=vector_query.params,
            )

        except redisvl.exceptions.RedisVLError as e:
            error_msg = str(e).lower()
            if 'oom' in error_msg or 'memory' in error_msg:
                msg = f'Redis out of memory during search: {e}'
                _LOG.error(msg)
                raise StorageCapacityError(msg) from e

            msg = f'Redis search failed: {e}'
            _LOG.error(msg)
            raise QueryError(msg) from e

        except redis.ResponseError as e:
            msg = f'Redis operation failed: {e}'
            _LOG.error(msg)
            raise QueryError(msg) from e

        except redis.ConnectionError as e:
            msg = f'connection failed: {e}'
            _LOG.error(msg)
            raise StorageConnectionError(msg) from e

    def _transform_redis_results(self, results: Any) -> list[dict[str, Any]]:
        """
        Transform Redis results into dicts.

        Converts raw Redis search results into a list of dictionaries
        with structured fields. It extracts relevant fields like text,
        text ID, parent ID, source, language, section, author, distance,
        tags, timestamp, confidence, and chunk position. It also handles
        the conversion of tags from a string format to a list.

        Args:
            results:
                Raw Redis search results.

        Returns:
            List of result dicts.
        """
        _LOG.debug('Transforming Redis results')

        def _build_doc_dict(doc):
            return {
                'text_id':          doc.id,
                'text':             doc.text,
                'parent_id':        doc.parent_id,
                'source':           doc.source,
                'language':         doc.language,
                'section':          doc.section,
                'author':           doc.author,
                'distance':         float(doc.vector_distance),
                'tags':             self._parse_tags_from_retrieval(doc.tags),
                'timestamp':        int(doc.timestamp) if doc.timestamp else 0,
                'confidence':       (float(doc.confidence)
                                     if doc.confidence else None),
                'chunk_position':   (int(doc.chunk_position)
                                     if doc.chunk_position else None),
            }

        return [_build_doc_dict(doc) for doc in results.docs]

    @staticmethod
    def _validate_batch_input_structure(
            texts_and_embeddings: list[TextEmbeddingPair],
    ) -> None:
        """
        Validate the structure of the batch input.

        Ensures that the input is a list of tuples, each containing
        exactly two elements: a TextUnit and a numpy array.

        Args:
            texts_and_embeddings:
                List of (TextUnit, np.ndarray) tuples to validate.

        Raises:
            ValidationError:
                If input structure is invalid.
        """
        if not isinstance(texts_and_embeddings, list):
            msg = 'texts_and_embeddings must be a list'
            _LOG.error(msg)
            raise ValidationError(msg)

        for i, item in enumerate(texts_and_embeddings):
            if not isinstance(item, tuple):
                msg = f'Item {i} must be a tuple, got {type(item).__name__}'
                _LOG.error(msg)
                raise ValidationError(msg)

            if len(item) != 2:
                msg = (f'Item {i} must be a tuple of length 2, '
                       f'got length {len(item)}')
                _LOG.error(msg)
                raise ValidationError(msg)

            text_unit, embedding = item

            if not isinstance(text_unit, TextUnit):
                msg = (f'Item {i}: first element must be a TextUnit, '
                       f'got {type(text_unit).__name__}')
                _LOG.error(msg)
                raise ValidationError(msg)

            if not isinstance(embedding, np.ndarray):
                msg = (f'Item {i}: first element must be a numpy array, '
                       f'got {type(embedding).__name__}')
                _LOG.error(msg)
                raise ValidationError(msg)

    @staticmethod
    def _validate_dimensions(dimensions: int | None) -> None:
        """
        Validate dimensions for Redis schema creation.

        Args:
            dimensions:
                Size of embedding vectors to validate.

        Raises:
            ValidationError:
                If dimensions do not match the configured dimensions.
        """
        if dimensions is None:
            msg = 'Dimensions required for Schema creation'
            _LOG.error(msg)
            raise ConfigurationError(msg)

        if not isinstance(dimensions, int) or dimensions <= 0:
            msg = 'Dimensions must be positive'
            _LOG.error(msg)
            raise ConfigurationError(msg)

    def _validate_dimensions_match(self, embedding: np.ndarray) -> None:
        """
        Validate embedding dimensions against store dimensions.

        Ensures that the provided embedding vector matches the
        expected dimensions of the store. Raises a ConfigurationError
        if the dimensions do not match.

        Args:
            embedding:
                Embedding vector to validate.
        """
        dim = embedding.shape[0]
        if dim != self.dimensions:
            msg = f'Embedding dimension mismatch: {dim} != {self.dimensions}'
            _LOG.error(msg)
            raise ConfigurationError(msg)

    @staticmethod
    def _validate_index_name(index_name: str) -> None:
        """
        Validate the index name format and length.

        Ensures that the provided index name is not empty, does not
        exceed the maximum length, and starts with the required
        TEXT_ID_PREFIX. Raises ValidationError if any of these
        conditions are not met.

        Args:
            index_name:
                Index name to validate.

        Raises:
            ValidationError:
                If index_name is invalid.
        """
        if not index_name or not index_name.strip():
            msg = 'index_name cannot be empty'
            _LOG.error(msg)
            raise ConfigurationError(msg)

        if len(index_name) > RedisVectorStore.MAX_TEXT_ID_LENGTH:
            msg = (f'index_name too long: {len(index_name)} > '
                   f'{RedisVectorStore.MAX_TEXT_ID_LENGTH}')
            _LOG.error(msg)
            raise ConfigurationError(msg)

    def _validate_input_sizes(
            self,
            text: str,
            metadata: Mapping[str, Any] | None,
    ) -> None:
        """
        Validate input doesn't exceed Redis limits.

        Validates the size of the text and metadata against Redis
        limits. It checks that the text does not exceed the maximum
        text size, that the total metadata size does not exceed the
        maximum metadata size, and that individual metadata fields
        do not exceed the maximum field size. Raises ValidationError
        if any of these limits are exceeded.

        Args:
            text:
                Text content to validate
            metadata:
                Optional metadata to validate

        Raises:
            ValidationError:
                If inputs exceed Redis limits
        """
        text_bytes = len(text.encode('utf-8'))
        if text_bytes > self.MAX_TEXT_SIZE:
            msg = (f'Text too large: {text_bytes} bytes '
                   f'(max: {self.MAX_TEXT_SIZE})')
            _LOG.error(msg)
            raise ValidationError(msg)

        if metadata:
            total_metadata_size = 0
            for key, value in metadata.items():
                key_bytes = len(str(key).encode('utf-8'))
                value_bytes = len(str(value).encode('utf-8'))

                if key_bytes > self.MAX_FIELD_SIZE:
                    msg = f'Metadata key too large: "{key}" {key_bytes} bytes'
                    _LOG.error(msg)
                    raise ValidationError(msg)

                if value_bytes > self.MAX_FIELD_SIZE:
                    msg = (f'Metadata value too large: "{key}" '
                           f'{value_bytes} bytes')
                    _LOG.error(msg)
                    raise ValidationError(msg)

                total_metadata_size += key_bytes + value_bytes

            if total_metadata_size > self.MAX_METADATA_SIZE:
                msg = (f'Total metadata too large: '
                       f'{total_metadata_size} bytes')
                _LOG.error(msg)
                raise ValidationError(msg)

    def _validate_text_id(self, text_id: str) -> None:
        """
        Validate text ID format and length.

        Validates that the provided text ID is not empty, does not
        exceed the maximum length, and starts with the required
        TEXT_ID_PREFIX. Raises ValidationError if any of these
        conditions are not met.

        Args:
            text_id:
                Text ID to validate.

        Raises:
            ValidationError:
                If text_id is invalid.
        """
        if not text_id or not text_id.strip():
            msg = 'text_id cannot be empty'
            _LOG.error(msg)
            raise ValidationError(msg)

        if len(text_id) > self.MAX_TEXT_ID_LENGTH:
            msg = (f'text_id too long: {len(text_id)} > '
                   f'{self.MAX_TEXT_ID_LENGTH}')
            _LOG.error(msg)
            raise ValidationError(msg)

        if not text_id.startswith(TEXT_ID_PREFIX):
            msg = f'text_id must start with "{TEXT_ID_PREFIX}"'
            _LOG.error(msg)
            raise ValidationError(msg)

    @staticmethod
    def _validate_top_k(top_k: int) -> None:
        """
        Validate that top_k is a positive integer.

        Ensures that the top_k parameter is a positive integer.

        Args:
            top_k:
                Number of results to return.

        Raises:
            ValidationError:
                If top_k is not a positive integer.
        """
        if not isinstance(top_k, int) or top_k < 1:
            msg = f'top_k must be a positive integer, got {top_k}'
            _LOG.error(msg)
            raise ValidationError(msg)

    def __del__(self):
        """Destructor to ensure Redis connection is closed."""
        _LOG.debug('Deleting Redis connection')
        self.close()

    def __enter__(self):
        """
        Context manager entry point for Redis store.

        Returns:
            Self instance for use in a with statement.
        """
        _LOG.debug('Entering Redis context manager')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point for Redis store.

        Cleans up the Redis connection when exiting the context.
        """
        _LOG.debug('Exiting Redis context manager')
        self.close()

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Redis store.

        Returns:
            Formatted string with key store information.
        """
        try:
            connection_kwargs = getattr(
                self.redis_client.connection_pool,
                'connection_kwargs',
                {},
            )
            host = connection_kwargs.get('host', 'unknown')
            port = connection_kwargs.get('port', 'unknown')

            try:
                self.redis_client.ping()
                status = 'connected'
            except redis.RedisError:
                status = 'disconnected'

        except AttributeError:
            host = port = 'unknown'
            status = 'unknown'

        return (f"RedisVectorStore(index='{self.index_name}', "
                f"dimensions={self.dimensions}, "
                f"host={host}, "
                f"port={port}, "
                f"status={status})")

    def __repr__(self) -> str:
        """
        Return a detailed string representation for debugging.

        Returns:
            Detailed string representation including all key attributes.
        """
        try:
            connection_pool = getattr(
                self.redis_client,
                'connection_pool',
                None,
            )

            if connection_pool:
                connection_kwargs = getattr(
                    connection_pool,
                    'connection_kwargs',
                    {},
                )
                max_connections = getattr(
                    connection_pool,
                    'max_connections',
                    'unknown',
                )
                host = connection_kwargs.get('host', 'unknown')
                port = connection_kwargs.get('port', 'unknown')
                db = connection_kwargs.get('db', 0)
            else:
                host = port = db = max_connections = 'unknown'

        except (AttributeError, TypeError):
            host = port = db = max_connections = 'unknown'

        return (f"RedisVectorStore("
                f"index_name='{self.index_name}', "
                f"dimensions={self.dimensions}, "
                f"host='{host}', "
                f"port={port}, "
                f"db={db}, "
                f"schema_version={self.SCHEMA_VERSION}, "
                f"max_connections={max_connections})")
