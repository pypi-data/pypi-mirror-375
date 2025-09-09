import logging
import pathlib
import sys
from datetime import datetime
from typing import Any, Union

import typer
from jinja2 import Environment, PackageLoader, select_autoescape
from rich import print as rprint

app = typer.Typer()

# Global state for quiet mode
_QUIET_MODE = False


def _quiet_print(*args: Any, **kwargs: Any) -> None:
    """Print only if not in quiet mode."""
    if not _QUIET_MODE:
        rprint(*args, **kwargs)


# Initialize Jinja2 environment
def _get_jinja_env() -> Environment:
    """Get Jinja2 environment with custom filters."""
    env = Environment(
        loader=PackageLoader("reerelease", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Add custom filter for date formatting
    def strftime_filter(date_obj: Union[str, datetime], format_str: str) -> str:
        if date_obj == "now":
            return datetime.now().strftime(format_str)
        if isinstance(date_obj, str):
            # If it's a string and not "now", return it as-is or handle as needed
            return date_obj
        return date_obj.strftime(format_str)

    env.filters["strftime"] = strftime_filter
    return env


def _get_template_files() -> list[tuple[str, str]]:
    """Get list of template files and their expected output names."""
    # Get the templates directory from the package
    package_path = pathlib.Path(__file__).parent
    templates_dir = package_path / "templates"

    if not templates_dir.exists():
        return []

    template_files = []
    for template_file in templates_dir.glob("*.j2"):
        # Remove .j2 extension to get output filename
        output_name = template_file.stem
        template_files.append((template_file.name, output_name))

    return template_files


def _extract_context_name_from_path(context_path: pathlib.Path, required_files: list[str]) -> str:
    """Extract context name from a context directory, defaulting to directory name."""
    context_name = context_path.name  # Default to directory name

    # Look for a readme file to extract the context name
    for file in required_files:
        if "readme" in file.lower():
            readme_path = context_path / file
            try:
                content = readme_path.read_text(encoding="utf-8")
                # Simple extraction: look for first # heading
                for line in content.split("\n"):
                    if line.startswith("#") and len(line) > 1 and line[1].isspace():
                        # Extract everything after '# ' and strip whitespace
                        context_name = line[1:].strip()
                        break
            except Exception as e:
                logger = logging.getLogger("reerelease")
                logger.debug("Could not read context name from %s: %s", readme_path, e)
            break

    return context_name


# ---- commands ----
@app.command()
def new(
    name: str,
    path: pathlib.Path,
) -> None:
    """Create a new context"""
    _quiet_print(f"➕ Creating files for context: [red]{name}[/red] at [yellow]{path}[/yellow]")
    logger = logging.getLogger("reerelease")
    logger.debug("new command called with name=%s path=%s", name, path)

    # Ensure the target directory exists
    path.mkdir(parents=True, exist_ok=True)

    # Get template files dynamically
    templates = _get_template_files()

    if not templates:
        logger.error("No template files found in templates directory")
        raise typer.Exit(1)

    # Check for existing files
    existing_files = []
    for _template_name, output_name in templates:
        output_path = path / output_name
        if output_path.exists():
            existing_files.append(output_name)

    # If any files exist, show graceful message and exit
    if existing_files:
        _quiet_print(f"📁 Context already exists at [yellow]{path}[/yellow]")
        _quiet_print("Found existing files:")
        for filename in existing_files:
            _quiet_print(f"  • [cyan]{filename}[/cyan]")
        logger.warning(
            "Context already exists at %s with files: %s", path, ", ".join(existing_files)
        )
        return  # Exit gracefully without error

    # Get Jinja2 environment
    env = _get_jinja_env()

    # Context for template rendering
    context = {
        "context_name": name,
        "creation_date": datetime.now().strftime("%Y-%m-%d"),
    }

    # Create files from templates
    for template_name, output_name in templates:
        try:
            template = env.get_template(template_name)
            content = template.render(**context)

            output_path = path / output_name
            output_path.write_text(content, encoding="utf-8")

            _quiet_print(f"  ✅ Created [green]{output_name}[/green]")
            logger.debug("Created file: %s", output_path)

        except Exception as e:
            _quiet_print(f"  ❌ Failed to create [red]{output_name}[/red]: {e}")
            logger.error("Failed to create file %s: %s", output_name, e)
            raise

    logger.info("Successfully created context %s at %s", name, path)
    _quiet_print(
        f"🎉 Successfully created context [green]{name}[/green] at [yellow]{path}[/yellow]"
    )


@app.command(hidden=True)
def emit_test_logs() -> None:
    """(test-only) Emit log messages at all levels for testing verbosity."""
    logger = logging.getLogger("reerelease")
    logger.debug("test-DEBUG: emit-test-logs called")
    logger.info("test-INFO: emit-test-logs called")
    logger.warning("test-WARNING: emit-test-logs called")
    logger.error("test-ERROR: emit-test-logs called")
    logger.critical("test-CRITICAL: emit-test-logs called")


@app.command()
def contexts(
    path: str = typer.Argument(
        ".", help="Path to scan for contexts (defaults to current directory)"
    ),
) -> None:
    """List all detected contexts"""
    # Convert string path to Path object
    path_obj = pathlib.Path(path)

    _quiet_print(f"🔍 Scanning for contexts in {path_obj}...")
    logger = logging.getLogger("reerelease")
    logger.debug("contexts command called with path=%s", path_obj)

    # Ensure the path exists
    if not path_obj.exists():
        _quiet_print(f"❌ Path does not exist: {path_obj}")
        logger.error("Path does not exist: %s", path_obj)
        raise typer.Exit(1)

    if not path_obj.is_dir():
        _quiet_print(f"❌ Path is not a directory: {path_obj}")
        logger.error("Path is not a directory: %s", path_obj)
        raise typer.Exit(1)

    # Get required files from templates
    template_files = _get_template_files()
    if not template_files:
        logger.warning("No template files found - cannot detect contexts")
        _quiet_print("❌ No template files found for context detection")
        return

    required_files = [output_name for _, output_name in template_files]
    logger.debug("Looking for contexts with files: %s", required_files)

    # Scan directory and subdirectories for contexts
    detected_contexts = []

    # Look for directories containing all required context files
    for search_path in [path_obj] + list(path_obj.rglob("*")):  # Include the root path itself
        if search_path.is_dir():
            # Check if this directory has all required files
            if all((search_path / file).exists() for file in required_files):
                # Extract context name using helper function
                context_name = _extract_context_name_from_path(search_path, required_files)

                detected_contexts.append((context_name, search_path.resolve()))
                logger.debug("Found context: %s at %s", context_name, search_path)

    # Display results in tree format
    if detected_contexts:
        from rich.console import Console
        from rich.tree import Tree

        console = Console()
        tree = Tree(f"📂 Found {len(detected_contexts)} context(s) in [yellow]{path_obj}[/yellow]")

        # Sort contexts by path depth to show hierarchy naturally
        detected_contexts.sort(key=lambda x: (len(x[1].parts), str(x[1])))

        # Build a simple hierarchical structure
        nodes = {}  # path -> tree_node

        for context_name, context_path in detected_contexts:
            try:
                rel_path = context_path.relative_to(path_obj.resolve())

                if str(rel_path) == ".":
                    # Root level context
                    nodes[str(context_path)] = tree.add(
                        f"[green]{context_name}[/green] [dim](.)[/dim]"
                    )
                else:
                    # Find the deepest ancestor that is also a context
                    parent_node = None
                    current_parent = context_path.parent

                    while current_parent != path_obj.resolve():
                        # Check if this ancestor is a context
                        for _other_name, other_path in detected_contexts:
                            if other_path == current_parent:
                                parent_node = nodes.get(str(current_parent))
                                break

                        if parent_node is not None:
                            break  # Found a context ancestor

                        current_parent = current_parent.parent

                    if parent_node is None:
                        # No context ancestor, add to root
                        current_node = tree.add(
                            f"[green]{context_name}[/green] [dim]({rel_path})[/dim]"
                        )
                    else:
                        # Add to the context ancestor
                        current_node = parent_node.add(
                            f"[green]{context_name}[/green] [dim]({rel_path})[/dim]"
                        )

                    nodes[str(context_path)] = current_node

            except ValueError:
                # Fallback to absolute path if relative calculation fails
                tree.add(f"[green]{context_name}[/green] [dim]({context_path})[/dim]")

        console.print(tree)
        logger.info("Found %d contexts", len(detected_contexts))
    else:
        _quiet_print("📭 No contexts found.")
        logger.info("No contexts found")


# ---- Simplified Logging Support ----
def configure_logging(*, level: int = logging.WARNING, quiet: bool = False) -> None:
    """Configure a simple, blocking console logger."""
    global _QUIET_MODE
    _QUIET_MODE = quiet

    log = logging.getLogger("reerelease")

    # Clear any handlers configured by previous tests
    if log.hasHandlers():
        log.handlers.clear()

    if quiet:
        log.addHandler(logging.NullHandler())
        return

    log.setLevel(level)
    handler: logging.Handler
    try:
        from rich.logging import RichHandler

        # Send logs to stderr (default for RichHandler)
        handler = RichHandler(rich_tracebacks=True, show_path=False, level=level)
        handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
    except ImportError:
        # Explicitly send logs to stderr
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        handler.setLevel(level)

    log.addHandler(handler)
    log.propagate = False  # Prevent passing messages to the root logger


# Typer callback to configure logging before running commands
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Disable all logging and console output."
    ),
    verbosity: str = typer.Option(
        "WARNING", "--verbosity", "-V", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    ),
) -> None:
    """
    Global options for the reerelease tool.
    """
    level_name = verbosity.upper()
    level = getattr(logging, level_name, logging.WARNING)
    configure_logging(level=level, quiet=quiet)


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
