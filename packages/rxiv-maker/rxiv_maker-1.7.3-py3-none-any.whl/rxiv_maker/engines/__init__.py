"""Unified engines package for rxiv-maker.

This package provides both container engines (Docker, Podman) and core operations
for manuscript processing, creating a unified interface for all execution functionality.
"""

# Container engines - execution infrastructure (deprecated)
from .core import (
    ContainerEngineError,
    get_container_engine,
)

# Optional imports for backward compatibility
try:
    from .core import AbstractContainerEngine, ContainerSession
except ImportError:
    AbstractContainerEngine = None  # type: ignore
    ContainerSession = None  # type: ignore

# Core operations - manuscript processing functionality
from .operations import (
    # Bibliography
    BibliographyAdder,
    BibliographyFixer,
    BuildManager,
    CleanupManager,
    EnvironmentSetup,
    # Core generation
    FigureGenerator,
    PDFValidator,
    TrackChangesManager,
    analyze_manuscript_word_count,
    # Utilities
    copy_pdf_with_custom_filename,
    generate_api_docs,
    generate_preprint,
    # Publishing
    prepare_arxiv_package,
    # Validation
    validate_manuscript,
)

__all__ = [
    # Container engines (deprecated)
    "get_container_engine",
    "ContainerEngineError",
    # Core operations
    "FigureGenerator",
    "generate_preprint",
    "BuildManager",
    "BibliographyAdder",
    "BibliographyFixer",
    "validate_manuscript",
    "PDFValidator",
    "analyze_manuscript_word_count",
    "prepare_arxiv_package",
    "TrackChangesManager",
    "copy_pdf_with_custom_filename",
    "CleanupManager",
    "EnvironmentSetup",
    "generate_api_docs",
]
