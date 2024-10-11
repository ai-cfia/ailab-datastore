"""
Metadata exceptions hierarchy:

    Exception
    |__MetadataError
       |__BuildInspectionImportError
       |__BuildInspectionExportError
       |__NPKError
"""


class MetadataError(Exception):
    """Base exception for metadata errors"""

    pass


class BuildInspectionImportError(MetadataError):
    """Error raised when building the inspection import fails"""

    pass


class BuildInspectionExportError(MetadataError):
    """Error raised when building the inspection export fails"""

    pass


class NPKError(MetadataError):
    pass
