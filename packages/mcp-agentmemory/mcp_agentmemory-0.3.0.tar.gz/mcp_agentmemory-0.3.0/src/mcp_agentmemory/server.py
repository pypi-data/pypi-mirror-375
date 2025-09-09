"""
Memory Graph MCP Server for Python Development Insights
A FastMCP server that tracks coding sessions, errors, fixes, and patterns.
"""

from pathlib import Path
from typing import Any, Final

from fastmcp import FastMCP

from .knowledge_graph import KnowledgeGraphManager
from .models import Entity, KnowledgeGraph, ObservationAdd, ObservationKind, Relation

DEFAULT_MEMORY_PATH: Final = Path("~/.mcp/").expanduser()
MEMORY_FILE: Final = "agentmemory.json"
MEMORY_LOG: Final = "agentmemory.log.jsonl"

# FastMCP Server Setup
mcp = FastMCP(name="memory-server")
manager = KnowledgeGraphManager(
    DEFAULT_MEMORY_PATH / MEMORY_FILE,
    DEFAULT_MEMORY_PATH / MEMORY_LOG,
)


# Core CRUD Operations
@mcp.tool(
    name="upsert_entity",
    description="""Create or update a knowledge entity in the graph. This is the
    fundamental building block for storing structured information about your Python
    development work.

Use this to create entities for:
- Features/projects you're working on (entityType="Feature")
- Python modules, classes, or functions (entityType="Module", "Class", "Function")
- Coding patterns or best practices (entityType="Pattern")
- Error types or bug categories (entityType="Error")
- Development concepts or techniques (entityType="Concept")

Parameters:
- name: Unique identifier for the entity (e.g., "user-authentication",
  "FastAPI-middleware", "DatabaseConnection")
- entityType: Category of the entity - helps organize and filter your knowledge
- tags: List of searchable keywords (automatically normalized to lowercase, duplicates
  removed)
- description: Human-readable explanation of what this entity represents

Returns the created/updated entity with normalized tags and assigned type. Use the
returned entity name for creating relations or adding insights.""",
)
def upsert_entity(
    name: str,
    entity_type: str | None = None,
    tags: list[str] | None = None,
    description: str | None = None,
) -> Entity:
    return manager.upsert_entity(name, entity_type, tags, description)


@mcp.tool(
    name="create_relations",
    description="""Establish semantic connections between entities in your knowledge
graph. Relations help you build a web of connected knowledge that reflects how different
parts of your codebase, patterns, and learnings relate to each other.

Common relation types and their uses:
- "implements": A session implements a feature, a class implements a pattern
- "encounters": A feature encounters an error, a session encounters a problem
- "fixed_by": An error is fixed by a pattern or solution
- "depends_on": A module depends on another module, a feature depends on a library
- "related": General connection between similar concepts or techniques
- "contains": A project contains modules, a module contains functions

Parameters:
- relations: List of Relation objects, each with from_, to, and relationType
- Optional confidence (0.0-1.0) and source fields for tracking relation quality

Returns only the newly created relations (idempotent - won't duplicate existing
relations). Use this to build context around your development work and create
navigable knowledge connections.""",
)
def create_relations(relations: list[Relation]) -> list[Relation]:
    return manager.create_relations(relations)


@mcp.tool(
    name="add_insights",
    description="""Add structured observations and insights to entities. This is where
you store the actual knowledge content - code snippets, notes, error details,
commands, and Q&A pairs.

Observation kinds and their purposes:
- "note": General observations, learnings, or documentation
- "snippet": Code examples, implementations, or reusable patterns
- "error": Exception details, stack traces, or problem descriptions
- "command": CLI commands, build scripts, or operational procedures
- "qa": Questions and answers, troubleshooting, or decision rationale

Each observation gets a content hash for automatic deduplication - identical insights
won't be stored twice.

Parameters:
- observations: List of ObservationAdd objects, each containing:
  - entityName: Which entity to attach the insight to
  - contents: List of Observation objects or simple strings (converted to "note" type)

Use tags liberally to make insights searchable. Include source file paths when relevant.
The metadata field can store structured data like line numbers, function names, or
performance metrics.

Returns list of results showing which insights were added (by hash) to each entity.""",
)
def add_insights(observations: list[ObservationAdd]) -> list[dict]:
    return manager.add_insights(observations)


@mcp.tool(
    name="read_graph",
    description="""Retrieve the complete knowledge graph with all entities, their
insights, and relationships. Use this to get a full picture of your accumulated
development knowledge.

Returns a KnowledgeGraph object containing:
- entities: All stored entities with their observations/insights
- relations: All connections between entities

This is useful for:
- Getting an overview of your project structure and learnings
- Exporting your knowledge base
- Analyzing patterns in your development work
- Building custom visualizations or reports

For large graphs, consider using search_insights or open_nodes to get focused
subsets instead.""",
)
def read_graph() -> KnowledgeGraph:
    return manager.read_graph()


@mcp.tool(
    name="search_insights",
    description="""Search through your accumulated insights and knowledge using
flexible filtering criteria. This is your primary tool for retrieving relevant
information from your development history.

Search strategies:
- Text search: Finds insights containing specific words or phrases in text or code
- Tag filtering: Finds insights with specific tags (great for categorizing by
  technology, pattern type, etc.)
- Kind filtering: Focus on specific types of insights (just snippets, just errors, etc.)
- Language filtering: Find insights for specific programming languages

Parameters:
- query: Text to search for in insight content (case-insensitive, searches both text
  and code fields)
- tags: List of tags that insights must have (OR logic - insight needs at least one
  matching tag)
- kinds: List of observation kinds to include ["note", "snippet", "error",
  "command", "qa"]
- language: Filter by programming language (e.g., "python", "javascript", "sql")

Returns a filtered KnowledgeGraph containing only entities with matching insights and
their relationships.

Example usage patterns:
- Find all error-handling patterns: tags=["error", "exception"], kinds=["snippet"]
- Search for specific API usage: query="fastapi", language="python"
- Review recent learnings: tags=["learning", "today"]
- Find troubleshooting commands: kinds=["command"], tags=["debug"]""",
)
def search_insights(
    query: str | None = None,
    tags: list[str] | None = None,
    kinds: list[ObservationKind] | None = None,
    language: str | None = None,
) -> KnowledgeGraph:
    return manager.search_insights(query, tags, kinds, language)


# Error and Solution Tracking
@mcp.tool(
    name="record_error",
    description="""Record a persistent error or exception for long-term tracking
and pattern recognition. Unlike session log_event, this creates a dedicated Error
entity that can be linked to solutions and patterns.

This tool helps you build a knowledge base of problems and their solutions:
- Creates a unique Error entity using a fingerprint of the error details
- Links the error to the feature where it occurred
- Stores detailed error information including stack traces
- Enables tracking of recurring issues and their patterns

The error fingerprint is based on exception type, message, and file location, so
identical errors get deduplicated automatically.

Use this for:
- Exceptions that took significant time to debug
- Recurring errors across different sessions
- Complex bugs that needed specific solutions
- Problems that might help others (or future you)

Parameters:
- feature: Name of the feature where the error occurred
- exception_type: Python exception class name (e.g., "ValueError", "AttributeError",
  "ImportError")
- message: The exception message text
- traceback: Full stack trace for debugging context
- file: Optional source file where error occurred
- line: Optional line number
- code: Optional code snippet that caused the error
- tags: Optional tags for categorization (e.g., ["database", "connection"],
  ["api", "timeout"])

Returns:
- error_entity: Generated entity name (error:{fingerprint}) for linking solutions
- fingerprint: Full fingerprint hash for tracking identical errors

After recording an error, use record_fix to attach solutions and create reusable
patterns.""",
)
def record_error(
    feature: str,
    exception_type: str,
    message: str,
    traceback: str,
    file: str | None = None,
    line: int | None = None,
    code: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, str]:
    return manager.record_error(
        feature,
        exception_type,
        message,
        traceback,
        file=file,
        line=line,
        code=code,
        tags=tags,
    )


@mcp.tool(
    name="record_fix",
    description="""Attach a solution or fix to a previously recorded error, optionally
creating a reusable Pattern entity. This completes the error-solution knowledge cycle.

This tool helps you:
- Document how specific errors were resolved
- Create reusable solution patterns for similar problems
- Build a searchable database of fixes and workarounds
- Track which solutions work for which types of errors

When you provide a pattern_name, the system creates a Pattern entity that can be:
- Searched when encountering similar errors
- Referenced in documentation
- Shared with team members
- Applied to prevent similar issues

Parameters:
- error_entity: The error entity name returned from record_error (e.g.,
  "error:a1b2c3d4e5f6")
- description: Human-readable explanation of the fix or solution approach
- code: The actual fix code, workaround, or corrected implementation
- pattern_name: Optional name for creating a reusable pattern (auto-generated if
  not provided)
- tags: Tags for categorizing the solution (e.g., ["async", "database"],
  ["validation", "input"])

The system automatically:
- Creates the Pattern entity with appropriate tags
- Links the error to the pattern with a "fixed_by" relationship
- Stores the fix code as a "snippet" type insight on the pattern
- Tags the solution appropriately for future search

Returns the pattern entity name for future reference. You can add additional insights
to the pattern entity later if you discover more applications or refinements of the
solution.""",
)
def record_fix(
    error_entity: str,
    description: str | None = None,
    code: str | None = None,
    pattern_name: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, str]:
    return manager.record_fix(error_entity, description, code, pattern_name, tags)


# Export and Maintenance
@mcp.tool(
    name="export_markdown",
    description="""Generate a comprehensive Markdown document of your entire knowledge
graph. This creates a human-readable export of all your accumulated development
knowledge, insights, and relationships.

The generated Markdown includes:
- All entities organized alphabetically with their types and tags
- Complete insight history for each entity (notes, code snippets, errors, etc.)
- Proper syntax highlighting for code blocks
- Structured headings for easy navigation
- Metadata like creation dates and source files

Use this for:
- Creating project documentation from your development history
- Sharing knowledge with team members
- Backing up your insights in a readable format
- Generating reports for retrospectives or knowledge transfer
- Creating a searchable archive of your development learnings

The output is a single Markdown string that you can save to a file, include in
documentation systems, or process further with other tools.

This is particularly valuable for:
- End-of-project knowledge dumps
- Onboarding documentation for new team members
- Personal development journals and learning logs
- Creating searchable knowledge bases from coding sessions""",
)
def export_markdown() -> str:
    return manager.export_markdown()


@mcp.tool(
    name="compact_store",
    description="""Optimize storage by creating a clean snapshot and clearing the
event log. This maintenance operation helps keep your knowledge graph storage efficient.

The system uses an append-only event log for durability, but over time this can grow
large. This tool:
- Writes a complete snapshot of the current graph state
- Clears the event log to save disk space
- Returns statistics about the optimization

Use this periodically to:
- Clean up storage after heavy development sessions
- Prepare for backup or archival
- Optimize for better performance
- Reset the event log while preserving all knowledge

Returns statistics:
- entities: Total number of entities in the graph
- relations: Total number of relationships
- log_bytes_before: Size of event log before compaction
- log_bytes_after: Size after compaction (should be 0)

This operation is safe - all your knowledge and insights are preserved in the snapshot.
The system will continue using the event log for new changes after compaction.""",
)
def compact_store() -> dict[str, Any]:
    return manager.compact_store()
