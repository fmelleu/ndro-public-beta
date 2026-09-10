"""Exceptions raised when a snapshot directory does not satisfy the data
contract. Every exception carries a short, user-safe ``diagnostic`` message
with no file paths, stack traces, or internal implementation detail -- it is
meant to be shown directly in the Streamlit UI.
"""


class ContractError(Exception):
    """Base class for any snapshot-contract violation."""

    def __init__(self, diagnostic: str):
        self.diagnostic = diagnostic
        super().__init__(diagnostic)


class ContractVersionError(ContractError):
    """The snapshot declares a contract_version this app does not support."""


class MissingFileError(ContractError):
    """A required snapshot file is absent."""


class SchemaValidationError(ContractError):
    """A required column is missing from a snapshot file."""


class RequiredValueError(ContractError):
    """A required-non-null field contains a null/blank value."""


class DuplicateKeyError(ContractError):
    """A file that must be unique per association_id has duplicates."""


class SnapshotConsistencyError(ContractError):
    """snapshot_version/cutoff_date disagree across files."""
