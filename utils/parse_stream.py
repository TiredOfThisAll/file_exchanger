class MultiPartFormDataParserException(Exception):
    pass


class MultiPartFormDataParser:
    """
    A parser for handling multipart/form-data HTTP requests.

    Attributes:
        boundary (str): The boundary string used to separate parts of the form data.
        content_headers (dict): Dictionary to store headers of the current part being parsed.
    """

    def __init__(self, requestHeaders):
        self.boundary = parse_http_header_parameters(requestHeaders["content-type"])["boundary"]
        if self.boundary is None:
            raise MultiPartFormDataParserException("Boundary string not found in content-type header")
        self.content_headers = {}

    def parse_chunk(self, chunk):
        """
        Parses a chunk of multipart/form-data, returning the start and end indices of the file content.

        Args:
            chunk (bytes): The chunk of data to parse.

        Returns:
            list: A list of byte slices containing the contents of the file.

        Raises:
            MultiPartFormDataParserException: If unexpected data is found after the end-of-data marker.
        """
        self.i = 0
        self.chunk = chunk
        result = []
        current_start = 0
        current_end = current_start

        # Loop through the chunk until all data is processed
        while self.i < len(self.chunk):
            # Check for the end-of-data marker
            if self._expect('\r\n--' + self.boundary + '--\r\n'):
                # Ensure no unexpected data after the end marker
                if self.i != len(self.chunk):
                    raise MultiPartFormDataParserException("Unexpected data found after end-of-data marker")
                break
            # Check for the boundary delimiter indicating a new part
            elif self._expect('--' + self.boundary + '\r\n'):
                # Append the previous part to the result list
                if current_end != 0:
                    result.append(self.chunk[current_start:current_end])
                # Parse content headers until an empty line is found
                while not self._expect('\r\n'):
                    # Parse header name
                    content_header_name = self._parse_until(':')
                    # Assume a space follows the header name
                    self._assume(' ')
                    # Parse header value
                    content_header_value = self._parse_until('\r\n')
                    # Store header
                    self.content_headers[content_header_name] = content_header_value
                # Update start and end indices for the new content part
                current_start = self.i
                current_end = current_start
            else:
                current_end += 1
                self.i += 1

        # Append the last content part to the result list
        if current_end != 0:
            result.append(self.chunk[current_start:current_end])

        return result

    def _assume(self, expected_string):
        """
        Ensures that the next part of the chunk matches the expected string.

        Args:
            expected_string (str): The string to match in the chunk.

        Raises:
            MultiPartFormDataParserException: If the expected string is not found.
        """
        if not self._expect(expected_string):
            raise MultiPartFormDataParserException("Incorrect data format")

    def _expect(self, expected_string):
        """
        Checks if the next part of the chunk matches the expected string and advances the pointer if true.

        Args:
            expected_string (str): The string to match in the chunk.

        Returns:
            bool: True if the expected string is found, otherwise False.
        """
        expected_byte_string = expected_string.encode()
        if self.chunk[self.i:].startswith(expected_byte_string):
            self.i += len(expected_byte_string)
            return True
        return False

    def _parse_until(self, separator):
        """
        Parses the chunk until the specified separator is found.

        Args:
            separator (str): The string to parse until.

        Returns:
            str: The parsed string up to the separator.
        """
        start = self.i
        end = start

        while not self._expect(separator):
            end += 1
            self.i += 1

        return self.chunk[start:end].decode()


def parse_http_header_parameters(source: str):
    """
    Parses HTTP header parameters from a source string.

    Args:
        source (str): The source string containing HTTP header parameters.

    Returns:
        dict: A dictionary containing the parsed key-value pairs.
    """
    result = {}

    for pairString in source.split('; ')[1:]:
        key, value = pairString.split('=')

        if value.startswith('"'):
            value = value[1:]

        if value.endswith('"'):
            value = value[:-1]
        result[key] = value
        
    return result
