from ports.stream_source_repository import StreamSourceRepository
from model.StreamSource import StreamSource
from exceptions.domain_exceptions import StreamSourceError
from enums.StreamSourceType import StreamSourceType

MAX_NAME_LENGTH = 200
MAX_URI_LENGTH = 200

class CreateStreamSourceUseCase:
    """
    Use Case to create a new stream source.
    """

    def __init__(self, stream_source_repository: StreamSourceRepository) -> None:
        self._stream_source_repository = stream_source_repository

    def execute(self, name: str, uri: str, is_web: bool, 
                stream_source_type_id: int = 0, enable_fetch: bool = True) -> StreamSource:
        """
        Executes the logic to create a new stream source.

        Returns:
            StreamSource: The newly created stream source object.

        Raises:
            StreamSourceError: If validation fails or creation fails.
        """
        normalized_name = name.strip() if isinstance(name, str) else ""
        if not normalized_name:
            raise StreamSourceError("Stream source name is required.")
        if len(normalized_name) > MAX_NAME_LENGTH:
            raise StreamSourceError(f"Stream source name cannot exceed {MAX_NAME_LENGTH} characters.")

        if uri is not None and not isinstance(uri, str):
            raise StreamSourceError("Stream source URI must be text.")
        normalized_uri = uri.strip() if isinstance(uri, str) else None
        if normalized_uri is not None and len(normalized_uri) > MAX_URI_LENGTH:
            raise StreamSourceError(f"Stream source URI cannot exceed {MAX_URI_LENGTH} characters.")

        if isinstance(stream_source_type_id, bool) or not isinstance(stream_source_type_id, (int, str)):
            raise StreamSourceError("Stream source type ID must be a valid type number.")
        try:
            normalized_type_id = int(stream_source_type_id)
        except ValueError as error:
            raise StreamSourceError("Stream source type ID must be a valid type number.") from error

        valid_type_ids = {0, *(source_type.value for source_type in StreamSourceType)}
        if normalized_type_id not in valid_type_ids:
            raise StreamSourceError(f"Stream source type ID {normalized_type_id} is not supported.")

        new_source = StreamSource(
            name=normalized_name,
            uri=normalized_uri,
            isWeb=is_web,
            streamSourceTypeId=normalized_type_id,
            enableFetch=enable_fetch
        )
        
        self._stream_source_repository.save(new_source)
        return new_source
