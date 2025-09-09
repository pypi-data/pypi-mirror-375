import argparse
import asyncio
import atexit
import functools
import inspect
import json
import logging
import logging.config
import logging.handlers
import os
import re
import signal
import sys
from typing import Any
from dotenv import load_dotenv
from mcp import types
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import TextContent, UserMessage
from pydantic import Field
from sqlalchemy.engine import Connection

# Import utilities
from teradata_mcp_server import utils as config, __version__

# Import the tools module with lazy loading support
try:
    from teradata_mcp_server import tools as td
except ImportError:
    import tools as td

load_dotenv()


# Parse command line arguments - if any they will override environment variables
parser = argparse.ArgumentParser(
    prog="teradata-mcp-server",
    description="Teradata MCP Server",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    epilog=(
        "Examples:\n"
        "  teradata-mcp-server --profile all\n"
        "  teradata-mcp-server --mcp_transport sse --mcp_host 127.0.0.1 --mcp_port 8001\n"
        "  DATABASE_URI=teradata://user:pass@host:1025/schema teradata-mcp-server\n"
    ),
)
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
parser.add_argument('-p', '--profile', type=str, required=False, help='Profile name to load from configure_tools.yml')
parser.add_argument('--database_uri', type=str, required=False, help='Database URI to connect to: teradata://username:password@host:1025/schemaname')
parser.add_argument(
    '--mcp_transport',
    type=str,
    choices=['stdio', 'streamable-http', 'sse'],
    required=False,
    help='MCP transport method to use.'
)
parser.add_argument('--mcp_host', type=str, required=False, help='MCP host address')
parser.add_argument('--mcp_port', type=int, required=False, help='MCP port number')
parser.add_argument('--mcp_path', type=str, required=False, help='MCP path for the server')
parser.add_argument('--log-dir', type=str, required=False, help='Directory for log files (overrides LOG_DIR).')
parser.add_argument('--no-file-logs', action='store_true', required=False, help='Disable file logging (same as NO_FILE_LOGS=1).')
parser.add_argument('--logging-level', type=str, choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], required=False, help='Logging level for console/file output.')

# Extract known arguments and load them into the environment if provided
args, unknown = parser.parse_known_args()

# Step 1: Apply CLI arguments (highest priority)
for key, value in vars(args).items():
    if value is not None:
        os.environ[key.upper()] = str(value)

# Step 2: Apply profile defaults (before environment variables)
profile_name = os.getenv("PROFILE")
if profile_name:
    # Import here to avoid circular imports during module loading
    from teradata_mcp_server import utils as config_utils
    config_utils.apply_profile_defaults_to_env(profile_name)

# Set up logging
class CustomJSONFormatter(logging.Formatter):
    """Custom JSON formatter that can handle extra dictionaries in log messages."""

    def format(self, record):
        # Create base log entry
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Check if there are extra fields in the record
        # LogRecord objects can have additional attributes added to them
        reserved_attrs = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
            'thread', 'threadName', 'processName', 'process', 'exc_info', 'exc_text',
            'stack_info', 'getMessage', 'message'
        }

        for key, value in record.__dict__.items():
            if key not in reserved_attrs:
                # Handle dictionary values by merging them
                if isinstance(value, dict):
                    log_entry.update(value)
                else:
                    log_entry[key] = value

        return json.dumps(log_entry, ensure_ascii=False)

#
# --- Lean, CLI‑friendly logging setup ---
# Default: no file writes under stdio (Claude); otherwise use a per‑user log dir.
MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio").lower()

def _default_log_dir():
    if MCP_TRANSPORT == "stdio":
        return None  # avoid file I/O under stdio
    if sys.platform == "darwin":  # macOS
        return os.path.join(os.path.expanduser("~/Library/Logs"), "TeradataMCP")
    if os.name == "nt":  # Windows
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        return os.path.join(base, "TeradataMCP", "Logs")
    # Linux/Unix
    base = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
    return os.path.join(base, "teradata_mcp_server", "logs")

LOG_DIR = os.getenv("LOG_DIR", _default_log_dir() or "")
# Allow explicit disable via NO_FILE_LOGS
if os.getenv('NO_FILE_LOGS', '').lower() in {'1','true','yes'}:
    LOG_DIR = ''
if LOG_DIR:
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except OSError:
        LOG_DIR = ""  # if unwritable, disable file logging silently

# Console logs only when not using stdio to keep the protocol stream clean.
enable_console_logging = (MCP_TRANSPORT != "stdio")
# --- End logging preamble ---

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
        "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
        "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        },
        "json": {
            "()": CustomJSONFormatter,
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        },
    },
    "handlers": {
        **({
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "filename": os.path.join(LOG_DIR, "teradata_mcp_server.jsonl"),
                "formatter": "json",
                "maxBytes": 1000000,
                "backupCount": 3
            }
        } if LOG_DIR else {}),
    },
    "loggers": {
        "teradata_mcp_server": {
            "level": "DEBUG",
            "handlers": (["file"] if LOG_DIR else []),
            "propagate": False
        }
    },
    "root": {
        "level": os.getenv("LOGGING_LEVEL", "WARNING"),
        "handlers": []  # Will be populated conditionally below
    }
}

# Add console handler only if not in stdio mode (to avoid polluting MCP communication)
if enable_console_logging:
    log_config["handlers"]["console"] = {
        "class": "logging.StreamHandler",
        "level": os.getenv("LOGGING_LEVEL", "WARNING"),
        "formatter": "simple",
        "stream": "ext://sys.stdout"
    }
    log_config["loggers"]["teradata_mcp_server"].setdefault("handlers", []).append("console")
    log_config["root"]["handlers"].append("console")

logging.config.dictConfig(log_config)
logger = logging.getLogger("teradata_mcp_server")

# Load tool configuration using new configuration system
# This supports both packaged defaults and working directory overrides
profile_config = config.get_profile_config(profile_name)

logger.info("Starting Teradata MCP server", extra={"server_config": {"profile": profile_name}, "startup_time": "2025-08-09"})

# Check if the EFS or EVS tools are enabled in the profiles
_enableEFS = True if any(re.match(pattern, 'fs_*') for pattern in profile_config.get('tool', [])) else False
_enableEVS = True if any(re.match(pattern, 'evs_*') for pattern in profile_config.get('tool', [])) else False

# Load the tool modules
module_loader = td.initialize_module_loader(profile_config)

# Connect to MCP server
mcp = FastMCP("teradata-mcp-server")

# Initialize global variables
fs_config = None
shutdown_in_progress = False

# Now initialize the TD connection after module loader is ready
_tdconn = td.TDConn()

if _enableEFS:
    try:
        import teradataml as tdml  # import of the teradataml package
        fs_config = td.FeatureStoreConfig()
        try:
            tdml.create_context(tdsqlengine=_tdconn.engine)
        except Exception as e:
            logger.warning(f"Error creating teradataml context: {e}")

    except (AttributeError, ImportError, ModuleNotFoundError) as e:
        logger.warning(f"Feature Store module not available - disabling EFS functionality: {e}")
        _enableEFS = False

# Only attempt to connect to EVS is the system has an EVS installed/configured
if (len(os.getenv("VS_NAME", "").strip()) > 0):
    try:
        _evs    = td.get_evs()
        _enableEVS = True
    except Exception as e:
        logger.error(f"Unable to establish connection to EVS, disabling: {e}")

#afm-defect: moved establish teradataml connection into main TDConn to enable auto-reconnect.
#td.teradataml_connection()



#------------------ Tool utilies  ------------------#
ResponseType = list[types.TextContent | types.ImageContent | types.EmbeddedResource]

def format_text_response(text: Any) -> ResponseType:
    """Format a text response."""
    if isinstance(text, str):
        try:
            # Try to parse as JSON if it's a string
            parsed = json.loads(text)
            return [types.TextContent(
                type="text",
                text=json.dumps(parsed, indent=2, ensure_ascii=False)
            )]
        except json.JSONDecodeError:
            # If not JSON, return as plain text
            return [types.TextContent(type="text", text=str(text))]
    # For non-string types, convert to string
    return [types.TextContent(type="text", text=str(text))]

def format_error_response(error: str) -> ResponseType:
    """Format an error response."""
    return format_text_response(f"Error: {error}")

def execute_db_tool(tool, *args, **kwargs):
    """
    Execute a database tool with the given connection and arguments.
    Currently support both tools expecting DB API or SQLAlchemy engine:
      - If annotated Connection, pass SQLAlchemy engine
      - Otherwise, pass raw DB-API connection
    The second option should be eventually retired as all tools move to SQLAlchemy.
    """
    global _tdconn
    # (Re)initialize if needed
    if not getattr(_tdconn, "engine", None):
        logger.info("Reinitializing TDConn")
        _tdconn = td.TDConn()
        if _enableEFS:
            try:
                global fs_config
                fs_config = td.FeatureStoreConfig()
                import teradataml as tdml  # import of the teradataml package
                try:
                    tdml.create_context(tdsqlengine=_tdconn.engine)
                except Exception as e:
                    logger.warning(f"Error creating teradataml context: {e}")

            except (AttributeError, ImportError, ModuleNotFoundError) as e:
                logger.warning(f"Feature Store module not available during reconnection: {e}")
                # Don't disable _enableEFS here as it might be temporary


    # Check is the first argument of the tool is a SQLAlchemy Connection
    sig = inspect.signature(tool)
    first_param = next(iter(sig.parameters.values()))
    ann = first_param.annotation
    use_sqla = inspect.isclass(ann) and issubclass(ann, Connection)

    try:
        if use_sqla:
            # Use a Connection that has .execute()
            with _tdconn.engine.connect() as conn:
                result = tool(conn, *args, **kwargs)
        else:
            # Raw DB-API path
            raw = _tdconn.engine.raw_connection()
            try:
                result = tool(raw, *args, **kwargs)
            finally:
                raw.close()

        return format_text_response(result)

    except Exception as e:
        logger.error(f"Error in execute_db_tool: {e}", exc_info=True)
        return format_error_response(str(e))

def execute_vs_tool(tool, *args, **kwargs) -> ResponseType:
    global _evs
    global _enableEVS

    if _enableEVS:
        try:
            return format_text_response(tool(_evs, *args, **kwargs))
        except Exception as e:
            if "401" in str(e) or "Session expired" in str(e):
                logger.warning("EVS session expired, refreshing …")
                _evs = td.evs_connect.refresh_evs()
                try:
                    return format_text_response(tool(_evs, *args, **kwargs))
                except Exception as retry_err:
                    logger.error(f"EVS retry failed: {retry_err}")
                    return format_error_response(f"After refresh, still failed: {retry_err}")

            logger.error(f"EVS tool error: {e}")
            return format_error_response(str(e))
    else:
        return format_error_response("Enterprise Vector Store is not available on this server.")



def make_tool_wrapper(func):
    """
    Given a handle_* function, return an async wrapper with:
    - the same signature minus any 'conn' or 'fs_config' params
    - injection of fs_config when declared, while conn injection is handled by execute_db_tool
    """
    sig = inspect.signature(func)

    # Determine which parameters to inject and remove from the exposed signature
    inject_kwargs = {}
    removable = {"conn", "tool_name"}
    if "fs_config" in sig.parameters:
        inject_kwargs["fs_config"] = fs_config
        removable.add("fs_config")

    # Build the new signature without injected params
    params = [
        p for name, p in sig.parameters.items()
        if name not in removable
        and p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    ]
    new_sig = sig.replace(parameters=params)

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        ba = new_sig.bind_partial(*args, **kwargs)
        ba.apply_defaults()
        # execute_db_tool handles injecting `conn`; we add fs_config if needed
        return execute_db_tool(func, **inject_kwargs, **ba.arguments)

    wrapper.__signature__ = new_sig
    return wrapper

#------------------ Register objects defined as code under ./src/teradata_mcp_server/tools/  ------------------#
def register_td_tools(profile_config, module_loader, mcp):
    """Register code-defined tools from loaded modules."""
    patterns = profile_config.get('tool', [])

    if not module_loader:
        logger.warning("No module loader available, skipping code-defined tool registration")
        return

    # Get all functions from the loaded modules
    all_functions = module_loader.get_all_functions()
    for name, func in all_functions.items():
        if not (inspect.isfunction(func) and name.startswith("handle_")):
            continue

        tool_name = name[len("handle_"):]
        if not any(re.match(p, tool_name) for p in patterns):
            continue

        wrapped = make_tool_wrapper(func)
        mcp.tool(name=tool_name, description=wrapped.__doc__)(wrapped)
        logger.info(f"Created tool: {tool_name}")


register_td_tools(profile_config, module_loader, mcp)


#------------------ Register tools, resources and prompts declared in .yml files ------------------#

# Load all objects using new configuration system
# This merges packaged objects with working directory overrides
custom_objects = config.load_all_objects()
custom_glossary = {}


def make_custom_prompt(prompt_name: str, prompt: str, desc: str, parameters: dict | None = None):
    """
    Build and register a FastMCP prompt, supporting optional parameters defined in YAML.
    YAML structure example:
    parameters:
      database_name:
        description: "Database to describe."
        required: true  # optional, defaults to true
        type_hint: str  # optional, defaults to str
        default: "sample_db"  # optional, only used if provided
    """
    if parameters is None or len(parameters) == 0:
        # Original behavior for prompts without parameters
        async def _dynamic_prompt():
            return UserMessage(role="user", content=TextContent(type="text", text=prompt))
        _dynamic_prompt.__name__ = prompt_name
        return mcp.prompt(description=desc)(_dynamic_prompt)
    else:
        # New behavior for prompts with parameters
        param_objects: list[inspect.Parameter] = []
        annotations: dict[str, Any] = {}

        for param_name, meta in parameters.items():
            meta = meta or {}
            type_hint_raw = meta.get("type_hint", str)
            # Convert string type hints to actual Python types
            if isinstance(type_hint_raw, str):
                try:
                    type_hint = eval(type_hint_raw, {"str": str, "int": int, "float": float, "bool": bool})
                except Exception:
                    type_hint = str
            else:
                type_hint = type_hint_raw
            required = meta.get("required", True)
            desc_txt = meta.get("description", "")
            desc_txt += f" (type: {type_hint_raw})"  # Optional enhancement

            if required and "default" not in meta:
                default_value = Field(..., description=desc_txt)
            else:
                default_value = Field(default=meta.get("default", None), description=desc_txt)

            param_objects.append(
                inspect.Parameter(
                    param_name,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=default_value,
                    annotation=type_hint,
                )
            )
            annotations[param_name] = type_hint

        sig = inspect.Signature(param_objects)

        async def _dynamic_prompt(**kwargs):
            missing = [
                name for name, meta in parameters.items()
                if (meta or {}).get("required", True) and name not in kwargs
            ]
            if missing:
                raise ValueError(f"Missing parameters: {missing}")
            formatted_prompt = prompt.format(**kwargs)
            return UserMessage(role="user", content=TextContent(type="text", text=formatted_prompt))

        _dynamic_prompt.__signature__ = sig
        _dynamic_prompt.__annotations__ = annotations
        _dynamic_prompt.__name__ = prompt_name

        return mcp.prompt(description=desc)(_dynamic_prompt)


def make_custom_query_tool(name, tool):
    param_defs = tool.get("parameters", {})
    # 1. Build Parameter objects
    parameters = []
    annotations = {}
    # param_defs is now a dict keyed by name
    for param_name, p in param_defs.items():
        type_hint = p.get("type_hint", str)    # e.g. int, float, str, etc.
        default = inspect.Parameter.empty if p.get("required", True) else p.get("default", None)
        parameters.append(
            inspect.Parameter(
                param_name,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=type_hint
            )
        )
        annotations[param_name] = type_hint

    # 2. Create the new signature
    sig = inspect.Signature(parameters)

    # 3. Define your generic handler
    async def _dynamic_tool(**kwargs):
        """Dynamically generated tool for {name}"""
        missing = [n for n in annotations if n not in kwargs]
        if missing:
            raise ValueError(f"Missing parameters: {missing}")
        return execute_db_tool(td.handle_base_readQuery, tool["sql"], tool_name=name, **kwargs)

    # 4. Inject signature & annotations
    _dynamic_tool.__signature__   = sig
    _dynamic_tool.__annotations__ = annotations

    # 5. Register with FastMCP
    return mcp.tool(
        name=name,
        description=tool.get("description", "")
    )(_dynamic_tool)

def generate_cube_query_tool(name, cube):
    """
    Generate a function to create aggregation SQL from a cube definition.

    :param cube: The cube definition
    :return: A SQL query string generator function taking dimensions and measures as comma-separated strings.
    """
    def _cube_query_tool(dimensions: str, measures: str, dim_filters: str, meas_filters: str, order_by: str, top: int) -> str:
        """
        Generate a SQL query string for the cube using the specified dimensions and measures.

        Args:
            dimensions (str): Comma-separated dimension names (keys in cube['dimensions']).
            measures (str): Comma-separated measure names (keys in cube['measures']).
            dim_filters (str): Filter SQL expressions on dimensions.
            meas_filters (str): Filter SQL expressions on computed measures.
            order_by (str): Order SQL expressions on selected dimensions and measures.
            top (int): Filters the top N results.

        Returns:
            str: The generated SQL query.
        """
        dim_list_raw = [d.strip() for d in dimensions.split(",") if d.strip()]
        mes_list_raw = [m.strip() for m in measures.split(",") if m.strip()]
        # Get dimension expressions from dictionary
        dim_list = ",\n  ".join([
            cube["dimensions"][d]["expression"] if d in cube["dimensions"] else d
            for d in dim_list_raw
        ])
        mes_lines = []
        for measure in mes_list_raw:
            mdef = cube["measures"].get(measure)
            if mdef is None:
                raise ValueError(f"Measure '{measure}' not found in cube '{name}'.")
            expr = mdef["expression"]
            mes_lines.append(f"{expr} AS {measure}")
        met_block = ",\n  ".join(mes_lines)
        sql = (
            f"SELECT {'TOP ' + str(top) if top else ''} * from\n"
            "(SELECT\n"
            f"  {dim_list},\n"
            f"  {met_block}\n"
            "FROM (\n"
            f"{cube['sql'].strip()}\n"
            f"{'WHERE '+dim_filters if dim_filters else ''}"
            ") AS c\n"
            f"GROUP BY {', '.join(dim_list_raw)}"
            ") AS a\n"
            f"{'WHERE '+meas_filters if meas_filters else ''}"
            f"{'ORDER BY '+order_by if order_by else ''}"
            ";"            
        )
        return sql
    return _cube_query_tool

def make_custom_cube_tool(name, cube):
    async def _dynamic_tool(dimensions, measures, dim_filters="", meas_filters="", order_by="", top=None):
        # Accept dimensions and measures as comma-separated strings, parse to lists
        return execute_db_tool(
            td.util_base_dynamicQuery,
            sql_generator=generate_cube_query_tool(name, cube),
            dimensions=dimensions,
            measures=measures,
            dim_filters=dim_filters,
            meas_filters=meas_filters,
            order_by=order_by,
            top=top
        )
    _dynamic_tool.__name__ = 'get_cube_' + name
    # Build allowed values and definitions for dimensions and measures
    dim_lines = []
    for name, d in cube.get('dimensions', {}).items():
        dim_lines.append(f"    - {name}: {d.get('description', '')}")
    measure_lines = []
    for name, m in cube.get('measures', {}).items():
        measure_lines.append(f"    - {name}: {m.get('description', '')}")
    _dynamic_tool.__doc__ = f"""
    Tool to query the cube '{name}'.
    {cube.get('description', '')}

    Expected inputs:
        dimensions (str): Comma-separated dimension names to group by. Allowed values:
{chr(10).join(dim_lines)}

        measures (str): Comma-separated measure names to aggregate. Allowed values:
{chr(10).join(measure_lines)}

        dim_filters (str): Filter expression to apply to dimensions. The dimension used must be in the dimension list, use valid SQL expressions, for example:
{(chr(10)+'AND ').join([f"{d} = 'value'" for d in cube.get('dimensions', {}).keys()])}
        meas_filters (str): Filter expression to apply to computed measures. The measure used must be in the measure list, use valid SQL expressions, for example:
{(chr(10)+'AND ').join([f"{m} > 1000" for m in list(cube.get('measures', {}).keys())])}
        order_by (str): Order expression on any selected dimensions and measures. Use SQL syntax, for example:
{(chr(10)+', ').join([f"{d} ASC" for d in cube.get('dimensions', {}).keys()])}
        top (int): Limit the number of rows returned, use a positive integer.

    Returns:
        Query result as a formatted response.
    """
    return mcp.tool(description=_dynamic_tool.__doc__)(_dynamic_tool)

# Instantiate custom query tools from YAML
custom_terms: list[str] = []
for name, obj in custom_objects.items():
    obj_type = obj.get("type")
    if obj_type == "tool" and any(re.match(pattern, name) for pattern in profile_config.get('tool',[])):
        fn = make_custom_query_tool(name, obj)
        globals()[name] = fn
        logger.info(f"Created tool: {name}")
    elif obj_type == "prompt"  and any(re.match(pattern, name) for pattern in profile_config.get('prompt',[])):
        fn = make_custom_prompt(name, obj["prompt"], obj.get("description", ""), obj.get("parameters", {}))
        globals()[name] = fn
        logger.info(f"Created prompt: {name}")
    elif obj_type == "cube"  and any(re.match(pattern, name) for pattern in profile_config.get('tool',[])):
        fn = make_custom_cube_tool(name, obj)
        globals()[name] = fn
        logger.info(f"Created cube: {name}")
    elif obj_type == "glossary"  and any(re.match(pattern, name) for pattern in profile_config.get('resource',[])):
        # Remove the 'type' key to get just the terms
        custom_glossary = {k: v for k, v in obj.items() if k != "type"}
        logger.info(f"Added custom glossary entries for: {name}.")
    else:
        logger.info(f"Type {obj_type if obj_type else ''} for custom object {name} is {'unknown' if obj_type else 'undefined'}.")

    # Look for additional terms to add to the custom glossary (currently only measures and dimensions in cubes)
    for section in ("measures", "dimensions"):
        if section in obj and  any(re.match(pattern, name) for pattern in profile_config.get('tool',[])):
            custom_terms.extend((term, details, name) for term, details in obj[section].items())

# Enrich glossary with terms from tools and cubes
for term, details, tool in custom_terms:
    term_key = term.strip()

    if term_key not in custom_glossary:
        # New glossary entry
        custom_glossary[term_key] = {
            "definition": details.get("description"),
            "synonyms": [],
            "tools": [tool]
        }
    else:
        # Existing glossary term → preserve definition, just add tool if missing
        if "tools" not in custom_glossary[term_key]:
            custom_glossary[term_key]["tools"] = []
        if tool not in custom_glossary[term_key]["tools"]:
            custom_glossary[term_key]["tools"].append(tool)

if custom_glossary:
    # Resource returning the entire glossary
    @mcp.resource("glossary://all")
    def get_glossary() -> ResponseType:
        """List all glossary terms."""
        return custom_glossary

    # Resource returning the entire glossary
    @mcp.resource("glossary://definitions")
    def get_glossary_definitions() -> ResponseType:
        """Returns all glossary terms with definitions."""
        return {term: details["definition"] for term, details in custom_glossary.items()}

    # Resource returning all information about a specific glossary term
    @mcp.resource("glossary://term/{term_name}")
    def get_glossary_term(term_name: str)  -> dict:
        """Return the definition, synonyms and associated tools of a specific glossary term."""
        term = custom_glossary.get(term_name)
        if term:
            return term
        else:
            return {"error": f"Glossary term not found: {term_name}"}



#------------------ Enterprise Vector Store Tools  ------------------#

# if config['evs']['allmodule']:
#     if config['evs']['tool']['evs_vectorStoreSimilaritySearch']:
#         @mcp.tool(description="Enterprise Vector Store similarity search")
#         async def evs_vectorStoreSimilaritySearch(
#             question: str = Field(description="Natural language question"),
#             top_k: int = Field(1, description="top matches to return"),
#         ) -> ResponseType:

#             return execute_vs_tool(
#                 td.evs_tools.handle_evs_vectorStoreSimilaritySearch,
#                 question=question,
#                 top_k=top_k,
#             )



#--------------- Feature Store Tools ---------------#
# Feature tools leveraging the tdfs4ds package.
# Run only if the EFS tools are defined in the config
if _enableEFS:

    @mcp.tool(description="Set or update the feature store configuration (database and data domain).")
    async def fs_setFeatureStoreConfig(
        data_domain: str | None = None,
        db_name: str | None = None,
        entity: str | None = None,
    ):
        global _tdconn
        with _tdconn.engine.connect() as conn:
            return td.create_response(fs_config.fs_setFeatureStoreConfig(
                conn=conn,
                db_name=db_name,
                data_domain=data_domain,
                entity=entity,
            ))

    @mcp.tool(description="Display the current feature store configuration (database and data domain).")
    async def fs_getFeatureStoreConfig() -> ResponseType:
        return td.create_response(fs_config.model_dump(exclude_none=True), "Current feature store config")

#------------------ Main ------------------#
# Main function to start the MCP server
#     Description: Initializes the MCP server and sets up signal handling for graceful shutdown.
#         It creates a connection to the Teradata database and starts the server to listen for incoming requests.
#         The function uses asyncio to manage asynchronous operations and handle signals for shutdown.
#         If an error occurs during initialization, it logs a warning message.
async def main():
    global _tdconn

    mcp_transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    logger.info(f"MCP_TRANSPORT: {mcp_transport}")

    # Set up proper shutdown handling
    try:
        loop = asyncio.get_running_loop()
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            logger.info(f"Registering signal handler for {s.name}")
            loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s)))
    except NotImplementedError:
        # Windows doesn't support signals properly
        logger.warning("Signal handling not supported on Windows")

    # Start the MCP server
    if mcp_transport == "sse":
        mcp.settings.host = os.getenv("MCP_HOST", "127.0.0.1")
        mcp.settings.port = int(os.getenv("MCP_PORT", "8001"))
        logger.info(f"Starting MCP server on {mcp.settings.host}:{mcp.settings.port}")
        await mcp.run_sse_async()
    elif mcp_transport == "streamable-http":
        mcp.settings.host = os.getenv("MCP_HOST", "127.0.0.1")
        mcp.settings.port = int(os.getenv("MCP_PORT", "8001"))
        mcp.settings.streamable_http_path = os.getenv("MCP_PATH", "/mcp/")
        logger.info(f"Starting MCP server on {mcp.settings.host}:{mcp.settings.port} with path {mcp.settings.streamable_http_path}")
        await mcp.run_streamable_http_async()
    else:
        logger.info("Starting MCP server on stdin/stdout")
        await mcp.run_stdio_async()

#------------------ Shutdown ------------------#
# Shutdown function to handle cleanup and exit
#     Arguments: sig (signal.Signals) - signal received for shutdown
#     Description: Cleans up resources and exits the server gracefully.
#         It sets a flag to indicate that shutdown is in progress and logs the received signal.
#         If the shutdown is already in progress, it forces an immediate exit.
#         The function uses os._exit to terminate the process with a specific exit code.
async def shutdown(sig=None):
    """Clean shutdown of the server."""
    global shutdown_in_progress, _tdconn

    logger.info("Shutting down server")
    if shutdown_in_progress:
        logger.info("Forcing immediate exit")
        os._exit(1)  # Use immediate process termination instead of sys.exit

    _tdconn.close()
    shutdown_in_progress = True
    if sig:
        logger.info(f"Received exit signal {sig.name}")
    os._exit(128 + sig if sig is not None else 0)


#------------------ Entry Point ------------------#
# Entry point for the script
#     Description: This script is designed to be run as a standalone program.
#         It loads environment variables, initializes logging, and starts the MCP server.
#         The main function is called to start the server and handle incoming requests.
#         If an error occurs during execution, it logs the error and exits with a non-zero status code.
if __name__ == "__main__":
    asyncio.run(main())
