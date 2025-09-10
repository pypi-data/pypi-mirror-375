"""
MCP KQL Server - Simplified and Efficient Implementation
Clean server with 2 main tools and single authentication

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, Optional, List, Any

import pandas as pd
from fastmcp import FastMCP

from .constants import (
    SERVER_NAME
)
from .execute_kql import kql_execute_tool
from .memory import get_memory_manager
from .utils import bracket_if_needed, SchemaManager, ErrorHandler, QueryProcessor
from .kql_auth import authenticate_kusto

logger = logging.getLogger(__name__)

mcp = FastMCP(name=SERVER_NAME)

# Global manager instances
memory_manager = get_memory_manager()
schema_manager = SchemaManager(memory_manager)
query_processor = QueryProcessor(memory_manager)

# Global kusto manager - will be set at startup
kusto_manager_global = None


@mcp.tool()
async def execute_kql_query(
    query: str,
    cluster_url: str,
    database: str,
    auth_method: str = "device",
    output_format: str = "json",
    generate_query: bool = False,
    table_name: Optional[str] = None,
    use_live_schema: bool = True
) -> str:
    """
    Execute a KQL query with optional query generation from natural language.

    Args:
        query: KQL query to execute, or natural language description if generate_query=True.
        cluster_url: Kusto cluster URL.
        database: Database name.
        auth_method: Authentication method (ignored, uses startup auth).
        output_format: Output format (json, csv, table).
        generate_query: If True, treat 'query' as natural language and generate KQL.
        table_name: Target table name for query generation (optional).
        use_live_schema: Whether to use live schema discovery for query generation.

    Returns:
        JSON string with query results or generated query.
    """
    try:
        global kusto_manager_global
        if not kusto_manager_global or not kusto_manager_global.get("authenticated"):
            return json.dumps({
                "success": False,
                "error": "Authentication required",
                "suggestions": [
                    "Ensure Azure CLI is installed and authenticated",
                    "Run 'az login' to authenticate",
                    "Check your Azure permissions"
                ]
            })

        # Generate KQL query if requested
        if generate_query:
            generated_result = await ErrorHandler.safe_execute(
                lambda: _generate_kql_from_natural_language(
                    query, cluster_url, database, table_name, use_live_schema
                ),
                default={
                    "success": False,
                    "error": "Query generation failed",
                    "suggestions": ["Try providing a more specific query description", "Specify the table name explicitly"]
                },
                error_msg="Query generation failed"
            )
            
            if not generated_result["success"]:
                return ErrorHandler.safe_json_dumps(generated_result, indent=2)
            
            # Use the generated query for execution
            query = generated_result["query"]
            
            # Return generation info if output format is specifically for generation
            if output_format == "generation_only":
                return ErrorHandler.safe_json_dumps(generated_result, indent=2)

        # Execute query
        df = kql_execute_tool(kql_query=query, cluster_uri=cluster_url, database=database)

        if df is None or df.empty:
            logger.warning(f"Query returned empty result for: {query[:100]}...")
            result = {
                "success": False,
                "error": "Query returned no results",
                "row_count": 0,
                "suggestions": ["Check your query syntax and logic", "Verify table names and filters"]
            }
            return json.dumps(result, indent=2)

        # Check if validation info was attached during execution
        validation_info = {}
        if hasattr(df, '_validation_result'):
            validation_info = {
                "warnings": getattr(df._validation_result, 'warnings', []),
                "suggestions": getattr(df._validation_result, 'suggestions', []),
                "tables_used": list(getattr(df._validation_result, 'tables_used', set())),
                "columns_used": {
                    table: list(cols)
                    for table, cols in getattr(df._validation_result, 'columns_used', {}).items()
                }
            }

        # Return results
        if output_format == "csv":
            return df.to_csv(index=False)
        elif output_format == "table":
            return df.to_string(index=False)
        else:
            # Convert DataFrame to serializable format with proper type handling
            def convert_dataframe_to_serializable(df):
                """Convert DataFrame to JSON-serializable format."""
                try:
                    # Convert to records and handle timestamps/types properly
                    records = []
                    for _, row in df.iterrows():
                        record = {}
                        for col, value in row.items():
                            if pd.isna(value):
                                record[col] = None
                            elif hasattr(value, 'isoformat'):  # Timestamp objects
                                record[col] = value.isoformat()
                            elif hasattr(value, 'strftime'):  # datetime objects
                                record[col] = value.strftime('%Y-%m-%d %H:%M:%S')
                            elif isinstance(value, type):  # type objects
                                record[col] = value.__name__
                            elif hasattr(value, 'item'):  # numpy types
                                record[col] = value.item()
                            else:
                                record[col] = value
                        records.append(record)
                    return records
                except Exception as e:
                    logger.warning(f"DataFrame conversion failed: {e}")
                    # Fallback: convert to string representation
                    return df.astype(str).to_dict("records")
            
            result = {
                "success": True,
                "row_count": len(df),
                "columns": df.columns.tolist(),
                "data": convert_dataframe_to_serializable(df),
            }
            
            # Add validation info if available
            if validation_info and any(validation_info.values()):
                result["validation"] = validation_info
            
            return ErrorHandler.safe_json_dumps(result, indent=2)

    except Exception as e:
        # Use the enhanced ErrorHandler for consistent Kusto error handling
        error_result = ErrorHandler.handle_kusto_error(e)
        return ErrorHandler.safe_json_dumps(error_result, indent=2)

async def _generate_kql_from_natural_language(
    natural_language_query: str,
    cluster_url: str,
    database: str,
    table_name: Optional[str] = None,
    use_live_schema: bool = True
) -> Dict[str, Any]:
    """
    Enhanced KQL generation with pre-validation of columns to ensure accuracy.
    """
    try:
        # 1. Determine target table
        entities = query_processor.parse(natural_language_query)
        target_table = table_name or (entities.get("tables")[0] if entities.get("tables") else None)

        if not target_table:
            return {"success": False, "error": "Could not determine a target table from the query.", "query": ""}

        # 2. Get the actual schema for the table
        schema_info = await schema_manager.get_table_schema(cluster_url, database, target_table, force_refresh=use_live_schema)
        if not schema_info or not schema_info.get("columns"):
            return {"success": False, "error": f"Failed to retrieve a valid schema for table '{target_table}'.", "query": ""}
        
        actual_columns = schema_info["columns"].keys()
        # Create a case-insensitive map for matching
        actual_columns_lower = {col.lower(): col for col in actual_columns}

        # 3. Extract potential column mentions from the natural language query
        potential_columns = set(re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', natural_language_query))

        # 4. Filter the potential columns against the actual schema
        valid_columns = []
        for p_col in potential_columns:
            if p_col.lower() in actual_columns_lower:
                # Use the correct casing from the schema
                valid_columns.append(actual_columns_lower[p_col.lower()])

        # 5. Build the query ONLY with validated columns
        if not valid_columns:
            # If no valid columns are mentioned, create a safe default query
            final_query = f"{bracket_if_needed(target_table)} | take 10"
            generation_method = "safe_fallback_no_columns_found"
        else:
            # Build a project query with only valid columns
            project_clause = ", ".join([bracket_if_needed(c) for c in valid_columns])
            final_query = f"{bracket_if_needed(target_table)} | project {project_clause} | take 10"
            generation_method = "schema_validated_generation"

        return {
            "success": True,
            "query": final_query,
            "generation_method": generation_method,
            "target_table": target_table,
            "schema_validated": True,
            "columns_used": valid_columns
        }

    except Exception as e:
        logger.error(f"Error in enhanced KQL generation: {e}", exc_info=True)
        return {"success": False, "error": str(e), "query": ""}


@mcp.tool()
async def schema_memory(
    operation: str,
    cluster_url: str = None,
    database: str = None,
    table_name: str = None,
    natural_language_query: str = None,
    session_id: str = "default",
    include_visualizations: bool = True
) -> str:
    """
    Comprehensive schema memory and analysis operations.
    
    Operations:
    - "discover": Discover and cache schema for a table
    - "list_tables": List all tables in a database
    - "get_context": Get AI context for tables
    - "generate_report": Generate analysis report with visualizations
    - "clear_cache": Clear schema cache
    - "get_stats": Get memory statistics
    - "refresh_schema": Proactively refresh schema for a database
    
    Args:
        operation: The operation to perform
        cluster_url: Kusto cluster URL (required for most operations)
        database: Database name (required for most operations)
        table_name: Table name (required for some operations)
        natural_language_query: Natural language query for context operations
        session_id: Session ID for report generation
        include_visualizations: Include visualizations in reports
    
    Returns:
        JSON string with operation results
    """
    try:
        global kusto_manager_global
        if not kusto_manager_global or not kusto_manager_global.get("authenticated"):
            return json.dumps({
                "success": False,
                "error": "Authentication required",
                "suggestions": [
                    "Ensure Azure CLI is installed and authenticated",
                    "Run 'az login' to authenticate",
                    "Check your Azure permissions"
                ]
            })

        if operation == "discover":
            return await _schema_discover_operation(cluster_url, database, table_name)
        elif operation == "list_tables":
            return await _schema_list_tables_operation(cluster_url, database)
        elif operation == "get_context":
            return await _schema_get_context_operation(cluster_url, database, natural_language_query)
        elif operation == "generate_report":
            return await _schema_generate_report_operation(session_id, include_visualizations)
        elif operation == "clear_cache":
            return await _schema_clear_cache_operation()
        elif operation == "get_stats":
            return await _schema_get_stats_operation()
        elif operation == "refresh_schema":
            return await _schema_refresh_operation(cluster_url, database)
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown operation: {operation}",
                "available_operations": ["discover", "list_tables", "get_context", "generate_report", "clear_cache", "get_stats", "refresh_schema"]
            })

    except Exception as e:
        logger.error(f"Schema memory operation failed: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


def _get_session_queries(session_id: str, memory) -> List[Dict]:
    """Get queries for a session (simplified implementation)."""
    # For now, get recent queries from all clusters
    try:
        all_queries = []
        for cluster_data in memory.corpus.get("clusters", {}).values():
            learning_results = cluster_data.get("learning_results", [])
            all_queries.extend(learning_results[-10:])  # Last 10 results
        return all_queries
    except Exception:
        return []


def _generate_executive_summary(session_queries: List[Dict]) -> str:
    """Generate executive summary of the analysis session."""
    if not session_queries:
        return "No queries executed in this session."
    
    total_queries = len(session_queries)
    successful_queries = sum(1 for q in session_queries if q.get("result_metadata", {}).get("success", True))
    total_rows = sum(q.get("result_metadata", {}).get("row_count", 0) for q in session_queries)
    
    return f"""
## Executive Summary

- **Total Queries Executed**: {total_queries}
- **Successful Queries**: {successful_queries} ({successful_queries/total_queries*100:.1f}% success rate)
- **Total Data Rows Analyzed**: {total_rows:,}
- **Session Duration**: Active session
- **Key Insights**: Data exploration and analysis completed successfully
"""


def _perform_data_analysis(session_queries: List[Dict]) -> str:
    """Perform analysis of query patterns and results."""
    if not session_queries:
        return "No data available for analysis."
    
    # Analyze query complexity
    complex_queries = sum(1 for q in session_queries if q.get("learning_insights", {}).get("query_complexity", 0) > 3)
    temporal_queries = sum(1 for q in session_queries if q.get("learning_insights", {}).get("has_time_reference", False))
    aggregation_queries = sum(1 for q in session_queries if q.get("learning_insights", {}).get("has_aggregation", False))
    
    return f"""
## Data Analysis

### Query Pattern Analysis
- **Complex Queries** (>3 operations): {complex_queries}
- **Temporal Queries**: {temporal_queries}
- **Aggregation Queries**: {aggregation_queries}

### Data Coverage
- Queries successfully returned data in {sum(1 for q in session_queries if q.get("learning_insights", {}).get("data_found", False))} cases
- Average result size: {sum(q.get("result_metadata", {}).get("row_count", 0) for q in session_queries) / len(session_queries):.1f} rows per query
"""


def _generate_data_flow_diagram(session_queries: List[Dict]) -> str:
    """Generate Mermaid data flow diagram."""
    return """
### Data Flow Architecture

```mermaid
graph TD
    A[User Query] --> B[Query Parser]
    B --> C[Schema Discovery]
    C --> D[Query Validation]
    D --> E[Kusto Execution]
    E --> F[Result Processing]
    F --> G[Learning & Context Update]
    G --> H[Response Generation]
    
    C --> I[Memory Manager]
    I --> J[Schema Cache]
    G --> I
    
    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style I fill:#e8f5e8
```
"""


def _generate_schema_relationship_diagram(session_queries: List[Dict]) -> str:
    """Generate Mermaid schema relationship diagram."""
    return """
### Schema Relationship Model

```mermaid
erDiagram
    CLUSTER {
        string cluster_uri
        string description
        datetime last_accessed
    }
    
    DATABASE {
        string database_name
        int table_count
        datetime discovered_at
    }
    
    TABLE {
        string table_name
        int column_count
        string schema_type
        datetime last_updated
    }
    
    COLUMN {
        string column_name
        string data_type
        string description
        list sample_values
    }
    
    CLUSTER ||--o{ DATABASE : contains
    DATABASE ||--o{ TABLE : contains
    TABLE ||--o{ COLUMN : has
```
"""


def _generate_timeline_diagram(session_queries: List[Dict]) -> str:
    """Generate Mermaid timeline diagram."""
    return """
### Query Execution Timeline

```mermaid
timeline
    title Query Execution Timeline
    
    section Discovery Phase
        Schema Discovery    : Auto-triggered on query execution
        Table Analysis      : Column types and patterns identified
        
    section Execution Phase
        Query Validation    : Syntax and schema validation
        Kusto Execution     : Query sent to cluster
        Result Processing   : Data transformation and formatting
        
    section Learning Phase
        Pattern Recognition : Query patterns stored
        Context Building    : Schema context enhanced
        Memory Update       : Knowledge base updated
```
"""


def _generate_recommendations(session_queries: List[Dict]) -> List[str]:
    """Generate actionable recommendations based on query analysis."""
    recommendations = []
    
    if not session_queries:
        recommendations.append("Start executing queries to get personalized recommendations")
        return recommendations
    
    # Analyze query patterns to generate recommendations
    has_complex_queries = any(q.get("learning_insights", {}).get("query_complexity", 0) > 5 for q in session_queries)
    has_failed_queries = any(not q.get("result_metadata", {}).get("success", True) for q in session_queries)
    low_data_queries = sum(1 for q in session_queries if q.get("result_metadata", {}).get("row_count", 0) < 10)
    
    if has_complex_queries:
        recommendations.append("Consider breaking down complex queries into simpler steps for better performance")
    
    if has_failed_queries:
        recommendations.append("Review failed queries and use schema discovery to ensure correct column names")
    
    if low_data_queries > len(session_queries) * 0.5:
        recommendations.append("Many queries returned small datasets - consider adjusting filters or time ranges")
    
    recommendations.append("Use execute_kql_query with generate_query=True for assistance with query construction")
    recommendations.append("Leverage schema discovery to explore available tables and columns")
    
    return recommendations



def _format_report_markdown(report: Dict) -> str:
    """Format the complete report as markdown."""
    markdown = f"""# KQL Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{report['summary']}

{report['analysis']}

## Visualizations

{''.join(report['visualizations'])}

## Recommendations

"""
    
    for i, rec in enumerate(report['recommendations'], 1):
        markdown += f"{i}. {rec}\n"
    
    markdown += """
## Next Steps

1. Continue exploring your data with the insights gained
2. Use the schema discovery features to find new tables and columns
3. Leverage the query generation tools for complex analysis
4. Monitor query performance and optimize as needed

---
*Report generated by MCP KQL Server with AI-enhanced analytics*
"""
    
    return markdown


async def _schema_discover_operation(cluster_url: str, database: str, table_name: str) -> str:
    """Discover and cache schema for a table."""
    try:
        schema_info = await schema_manager.get_table_schema(cluster_url, database, table_name, force_refresh=True)
        
        if schema_info and not schema_info.get("error"):
            return json.dumps({
                "success": True,
                "message": f"Schema discovered and cached for {table_name}",
                "schema": schema_info
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": f"Failed to discover schema for {table_name}: {schema_info.get('error', 'Unknown error')}"
            })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _schema_list_tables_operation(cluster_url: str, database: str) -> str:
    """List all tables in a database."""
    try:
        from .utils import discover_tables_in_database
        tables = await discover_tables_in_database(cluster_url, database)
        return json.dumps({
            "success": True,
            "tables": tables,
            "count": len(tables)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _schema_get_context_operation(cluster_url: str, database: str, natural_language_query: str) -> str:
    """Get AI context for tables."""
    try:
        context = memory_manager.get_ai_context_for_tables(
            cluster_url=cluster_url,
            database=database,
            natural_language_query=natural_language_query
        )
        return json.dumps({
            "success": True,
            "context": context
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _schema_generate_report_operation(session_id: str, include_visualizations: bool) -> str:
    """Generate analysis report with visualizations."""
    try:
        # Gather session data
        session_queries = _get_session_queries(session_id, memory_manager)
        
        report = {
            "summary": _generate_executive_summary(session_queries),
            "analysis": _perform_data_analysis(session_queries),
            "visualizations": [],
            "recommendations": []
        }
        
        if include_visualizations:
            report["visualizations"] = [
                _generate_data_flow_diagram(session_queries),
                _generate_schema_relationship_diagram(session_queries),
                _generate_timeline_diagram(session_queries)
            ]
        
        report["recommendations"] = _generate_recommendations(session_queries)
        markdown_report = _format_report_markdown(report)
        
        return json.dumps({
            "success": True,
            "report": markdown_report,
            "session_id": session_id,
            "generated_at": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _schema_clear_cache_operation() -> str:
    """Clear schema cache."""
    try:
        memory_manager.clear_schema_cache()
        return json.dumps({
            "success": True,
            "message": "Schema cache cleared successfully"
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _schema_get_stats_operation() -> str:
    """Get memory statistics."""
    try:
        stats = memory_manager.get_memory_stats()
        return json.dumps({
            "success": True,
            "stats": stats
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _schema_refresh_operation(cluster_url: str, database: str) -> str:
    """Proactively refresh schema for a database."""
    try:
        if not cluster_url or not database:
            return json.dumps({
                "success": False,
                "error": "cluster_url and database are required for refresh_schema operation"
            })
        
        # Step 1: List all tables in the database
        from .utils import discover_tables_in_database
        tables = await discover_tables_in_database(cluster_url, database)
        
        if not tables:
            return json.dumps({
                "success": False,
                "error": f"No tables found in database {database}"
            })
        
        # Step 2: Refresh schema for each table
        refreshed_tables = []
        failed_tables = []
        
        for table_name in tables:
            try:
                logger.info(f"Refreshing schema for {database}.{table_name}")
                schema_info = await schema_manager.get_table_schema(
                    cluster_url, database, table_name, force_refresh=True
                )
                
                if schema_info and not schema_info.get("error"):
                    refreshed_tables.append({
                        "table": table_name,
                        "columns": len(schema_info.get("columns", {})),
                        "last_updated": schema_info.get("last_updated", "unknown")
                    })
                    logger.debug(f"Successfully refreshed schema for {table_name}")
                else:
                    failed_tables.append({
                        "table": table_name,
                        "error": schema_info.get("error", "Unknown error")
                    })
                    logger.warning(f"Failed to refresh schema for {table_name}: {schema_info.get('error')}")
                    
            except Exception as table_error:
                failed_tables.append({
                    "table": table_name,
                    "error": str(table_error)
                })
                logger.error(f"Exception refreshing schema for {table_name}: {table_error}")
        
        # Step 3: Update memory with discovery timestamp
        try:
            from .utils import normalize_name
            cluster_key = normalize_name(cluster_url)
            
            # Update the discovery metadata
            if cluster_key in memory_manager.memories:
                if database in memory_manager.memories[cluster_key].get("databases", {}):
                    memory_manager.memories[cluster_key]["databases"][database]["last_schema_refresh"] = datetime.now().isoformat()
                    memory_manager.memories[cluster_key]["databases"][database]["total_tables"] = len(refreshed_tables)
            
            # Save the updated memory
            memory_manager.save_memory()
            logger.info(f"Updated memory with refresh metadata for {database}")
            
        except Exception as memory_error:
            logger.warning(f"Failed to update memory metadata: {memory_error}")
        
        # Step 4: Return comprehensive results
        return json.dumps({
            "success": True,
            "message": f"Schema refresh completed for database {database}",
            "summary": {
                "total_tables": len(tables),
                "successfully_refreshed": len(refreshed_tables),
                "failed_tables": len(failed_tables),
                "refresh_timestamp": datetime.now().isoformat()
            },
            "refreshed_tables": refreshed_tables,
            "failed_tables": failed_tables if failed_tables else None
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Schema refresh operation failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Schema refresh failed: {str(e)}"
        })


def main():
    """Start the simplified MCP KQL server."""
    global kusto_manager_global
    logger.info("Starting simplified MCP KQL server...")
    
    try:
        # Single authentication at startup
        kusto_manager_global = authenticate_kusto()
        
        if kusto_manager_global["authenticated"]:
            logger.info("🚀 MCP KQL Server ready - authenticated and initialized")
        else:
            logger.warning("🚀 MCP KQL Server starting - authentication failed, some operations may not work")
        
        # Log available tools
        logger.info("Available tools: execute_kql_query (with query generation), schema_memory (comprehensive schema operations)")
        
        # Use FastMCP's built-in stdio transport
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")

if __name__ == "__main__":
    main()
