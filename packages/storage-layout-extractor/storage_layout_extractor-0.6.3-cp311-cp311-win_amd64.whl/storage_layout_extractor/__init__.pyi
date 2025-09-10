"""
Type stubs for storage_layout_extractor - Python bindings for EVM storage layout analysis.

This module provides functionality to analyze EVM bytecode and extract
the storage layout of smart contracts.
"""

from typing import List, Dict, Any

class PyStorageSlot:
    """Represents a storage slot in a contract's storage layout."""
    index: str
    offset: int
    typ: str
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the storage slot to a dictionary representation.
        
        Returns:
            Dictionary containing index, offset, and type information
        """
        ...

def extract_storage(bytecode_str: str, timeout_secs: int = 10) -> List[PyStorageSlot]:
    """
    Extract storage layout from EVM bytecode
    
    Args:
        bytecode_str: Hex-encoded bytecode string (with or without 0x prefix)
        timeout_secs: Analysis timeout in seconds (default: 10)
        
    Returns:
        List of PyStorageSlot objects representing the storage layout
        
    Raises:
        RuntimeError: If bytecode is invalid, analysis fails, or times out
        
    Example:
        >>> bytecode = "0x60806040..."
        >>> slots = extract_storage(bytecode)
        >>> for slot in slots:
        ...     print(f"Slot {slot.index} at offset {slot.offset}: {slot.typ}")
    """
    ...