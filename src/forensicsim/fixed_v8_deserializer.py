"""Fixed V8 deserializer that properly handles one-byte strings with Latin-1 encoding."""

import ccl_chromium_reader.serialization_formats.ccl_v8_value_deserializer as v8_orig
import typing


class FixedDeserializer(v8_orig.Deserializer):
    """Fixed V8 deserializer that properly decodes one-byte strings."""
    
    def _read_one_byte_string(self) -> str:
        """Read a one-byte string, properly handling Latin-1 encoding.
        
        The original implementation tried ASCII first and returned raw bytes on failure.
        This causes Swedish characters like å (0xE5) to be corrupted.
        
        This fixed version tries UTF-8 first (for modern data), then Latin-1 (ISO-8859-1)
        which properly handles Western European characters.
        """
        length = self._read_le_varint()[0]
        raw = self._read_raw(length)
        
        # Try UTF-8 first (most modern data)
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            pass
        
        # Fall back to Latin-1 (ISO-8859-1) which handles all byte values
        # This properly decodes Swedish characters like å (0xE5)
        return raw.decode("latin-1")


# Monkey-patch the original module to use our fixed version
def patch_ccl_chromium_reader():
    """Patch the ccl_chromium_reader to use our fixed deserializer."""
    import ccl_chromium_reader.serialization_formats.ccl_v8_value_deserializer
    ccl_chromium_reader.serialization_formats.ccl_v8_value_deserializer.Deserializer = FixedDeserializer
    
    # Also patch any already-imported references
    import ccl_chromium_reader.ccl_chromium_indexeddb
    if hasattr(ccl_chromium_reader.ccl_chromium_indexeddb, 'ccl_v8_value_deserializer'):
        ccl_chromium_reader.ccl_chromium_indexeddb.ccl_v8_value_deserializer.Deserializer = FixedDeserializer