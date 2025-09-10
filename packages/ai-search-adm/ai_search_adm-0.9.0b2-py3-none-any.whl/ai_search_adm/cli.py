from __future__ import annotations

import os

import typer
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    add_completion=False,
    help=(
        "[bold cyan]Administration tool for Azure AI Search indexes.[/bold cyan]\n\n"
        "[yellow]⚠️  PRERELEASE: This is beta software - use with caution.[/yellow]"
    ),
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
console = Console()


def _show_auth_info(endpoint: str, api_key: str | None, label: str = "") -> None:
    """Display authentication information."""
    service_name = endpoint.split("//")[1].split(".")[0] if "//" in endpoint else endpoint

    auth_table = Table(show_header=False, box=None, title=f"Authentication Info{' - ' + label if label else ''}")
    auth_table.add_column("Property", style="dim")
    auth_table.add_column("Value")

    if api_key:
        min_key_length_for_masking = 12
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > min_key_length_for_masking else "***"
        auth_table.add_row("Method", "[yellow]API Key[/yellow]")
        auth_table.add_row("Key", f"[dim]{masked_key}[/dim]")
    else:
        auth_table.add_row("Method", "[cyan]DefaultAzureCredential[/cyan]")

        # Check for environment variables that indicate auth method
        if os.environ.get("AZURE_CLIENT_ID"):
            auth_table.add_row("Type", "[dim]Service Principal[/dim]")
            client_id = os.environ.get("AZURE_CLIENT_ID", "")
            if len(client_id) > 8:
                auth_table.add_row("Client ID", f"[dim]{client_id[:8]}...[/dim]")
        elif os.environ.get("MSI_ENDPOINT"):
            auth_table.add_row("Type", "[dim]Managed Identity[/dim]")
        else:
            auth_table.add_row("Type", "[dim]Azure CLI/Interactive[/dim]")

    auth_table.add_row("Service", f"[cyan]{service_name}[/cyan]")
    console.print(auth_table)
    console.print()


def _mk_client(endpoint: str, api_key: str | None) -> SearchIndexClient:
    """Create a SearchIndexClient with either API key or DefaultAzureCredential authentication."""
    if api_key:
        return SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))
    cred = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    return SearchIndexClient(endpoint=endpoint, credential=cred)


def _index_exists(client: SearchIndexClient, name: str) -> bool:
    """Check if an index exists on the search service."""
    try:
        client.get_index(name)
        return True
    except ResourceNotFoundError:
        return False


def _sanitize_for_create(idx: SearchIndex, new_name: str) -> SearchIndex:
    """Sanitize an index definition for creation by setting a new name and removing etag."""
    idx.name = new_name
    if hasattr(idx, "etag"):
        try:
            idx.etag = None
        except Exception:
            pass
    return idx


def _validate_duplicate_params(endpoint: str, source: str, target: str) -> None:
    """Validate required parameters and show all missing ones at once."""
    missing = []
    if not endpoint.strip():
        missing.append("--endpoint")
    if not source.strip():
        missing.append("--source")
    if not target.strip():
        missing.append("--target")

    if missing:
        console.print(f"[red]Error:[/red] Missing required options: {', '.join(missing)}")
        console.print("\n[bold cyan]Usage:[/bold cyan]")
        console.print("ai-search-adm duplicate --endpoint <endpoint> --source <index> --target <index>")
        console.print("\n[bold cyan]Example:[/bold cyan]")
        console.print("ai-search-adm duplicate \\")
        console.print("  --endpoint https://myservice.search.windows.net \\")
        console.print("  --source my-source-index \\")
        console.print("  --target my-target-index")
        console.print("\n[dim]Use --help for more options[/dim]")
        raise typer.Exit(1)


@app.command("duplicate")
def duplicate_index(
    endpoint: str = typer.Option("", help="Target service endpoint, e.g. https://<service>.search.windows.net"),
    source: str = typer.Option("", help="Source index name"),
    target: str = typer.Option("", help="Target index name"),
    from_endpoint: str | None = typer.Option(
        None, help="Optional: source service endpoint if different (cross-service clone)"
    ),
    api_key: str | None = typer.Option(None, help="Admin API key (otherwise uses DefaultAzureCredential)"),
    source_api_key: str | None = typer.Option(None, help="Admin API key for the source service, if different"),
    overwrite: bool = typer.Option(False, help="If target exists, delete it first (DANGEROUS)"),
) -> None:
    """[bold]Duplicate an index definition[/bold] (schema only, no documents).

    This command copies the index structure including fields, analyzers,
    suggesters, and scoring profiles from source to target.
    """

    # Validate required parameters
    _validate_duplicate_params(endpoint, source, target)

    src_ep = from_endpoint or endpoint

    console.rule("[bold]ai-search-adm • duplicate index definition")

    # Show authentication info
    if from_endpoint:
        _show_auth_info(src_ep, source_api_key or api_key, "Source Service")
        _show_auth_info(endpoint, api_key, "Target Service")
    else:
        _show_auth_info(endpoint, api_key)

    table = Table(show_header=False, box=None, title="Operation Details")
    table.add_column("Property", style="dim")
    table.add_column("Value")
    table.add_row("Source endpoint", f"[cyan]{src_ep}[/cyan]")
    table.add_row("Target endpoint", f"[cyan]{endpoint}[/cyan]")
    table.add_row("Source index", f"[magenta]{source}[/magenta]")
    table.add_row("Target index", f"[magenta]{target}[/magenta]")
    console.print(table)
    console.print()

    src_client = _mk_client(src_ep, source_api_key or api_key)
    dst_client = _mk_client(endpoint, api_key)

    try:
        src_index = src_client.get_index(source)
    except ResourceNotFoundError:
        console.print(f"[red]Error:[/red] Source index '{source}' not found on {src_ep}")
        raise typer.Exit(2) from None
    except HttpResponseError as e:
        console.print(f"[red]Error fetching source index:[/red] {e.message}")
        raise typer.Exit(2) from e

    if _index_exists(dst_client, target):
        if not overwrite:
            console.print(f"[yellow]Target index '{target}' exists.[/yellow] Use --overwrite to replace it.")
            raise typer.Exit(3)
        console.print(f"[yellow]Deleting existing target index '{target}' ...[/yellow]")
        try:
            dst_client.delete_index(target)
        except HttpResponseError as e:
            console.print(f"[red]Error deleting target index:[/red] {e.message}")
            raise typer.Exit(4) from e

    new_index = _sanitize_for_create(src_index, target)

    try:
        created = dst_client.create_index(new_index)
    except HttpResponseError as e:
        console.print(f"[red]Create failed:[/red] {e.message}")
        raise typer.Exit(5) from e

    console.print("[green]Success![/green] Created '", target, "'. Summary:")
    summary = Table(show_header=True, header_style="bold", box=None)
    summary.add_column("Property")
    summary.add_column("Count")
    summary.add_row("Fields", str(len(created.fields or [])))
    summary.add_row("Suggesters", str(len(created.suggesters or [])))
    summary.add_row("Scoring Profiles", str(len(created.scoring_profiles or [])))
    summary.add_row("Analyzers", str(len(created.analyzers or [])))
    summary.add_row("Tokenizers", str(len(getattr(created, "tokenizers", []) or [])))
    summary.add_row("Token Filters", str(len(getattr(created, "token_filters", []) or [])))
    summary.add_row("Char Filters", str(len(getattr(created, "char_filters", []) or [])))
    console.print(summary)
    console.print("[dim]Note: documents are not copied.[/dim]")


@app.command("list")
def list_indexes(
    endpoint: str = typer.Option("", help="Service endpoint, e.g. https://<service>.search.windows.net"),
    api_key: str | None = typer.Option(None, help="Admin API key (otherwise uses DefaultAzureCredential)"),
) -> None:
    """[bold]List all indexes[/bold] in the search service.

    Shows index names and field counts for quick overview.
    """

    # Validate required parameters
    if not endpoint.strip():
        console.print("[red]Error:[/red] Missing required option: --endpoint")
        console.print("\n[bold cyan]Usage:[/bold cyan]")
        console.print("ai-search-adm list --endpoint <endpoint>")
        console.print("\n[bold cyan]Example:[/bold cyan]")
        console.print("ai-search-adm list --endpoint https://myservice.search.windows.net")
        console.print("\n[dim]Use --help for more options[/dim]")
        raise typer.Exit(1)
    console.rule("[bold]ai-search-adm • list indexes")

    # Show authentication info
    _show_auth_info(endpoint, api_key)

    client = _mk_client(endpoint, api_key)

    try:
        indexes = client.list_indexes()

        table = Table(show_header=True, header_style="bold")
        table.add_column("Name")
        table.add_column("Fields")

        for index in indexes:
            table.add_row(index.name, str(len(index.fields or [])))

        console.print(table)
    except HttpResponseError as e:
        console.print(f"[red]Error listing indexes:[/red] {e.message}")
        raise typer.Exit(1) from e


def _validate_clear_params(endpoint: str, index: str) -> None:
    """Validate required parameters for clear command."""
    missing = []
    if not endpoint.strip():
        missing.append("--endpoint")
    if not index.strip():
        missing.append("--index")

    if missing:
        console.print(f"[red]Error:[/red] Missing required options: {', '.join(missing)}")
        console.print("\n[bold cyan]Usage:[/bold cyan]")
        console.print("ai-search-adm clear --endpoint <endpoint> --index <index>")
        console.print("\n[bold cyan]Example:[/bold cyan]")
        console.print("ai-search-adm clear --endpoint https://myservice.search.windows.net --index my-index")
        console.print("\n[dim]Use --help for more options[/dim]")
        raise typer.Exit(1)


def _confirm_destructive_operation(index_name: str) -> None:
    """Ask user to confirm a destructive operation by typing 'DELETE'."""
    console.print("\n[bold red]⚠️  DESTRUCTIVE OPERATION WARNING ⚠️[/bold red]")
    console.print(f"This will [bold red]DELETE ALL DATA[/bold red] in index '[magenta]{index_name}[/magenta]'")
    console.print("The index structure will be preserved, but all documents will be lost.")
    console.print("\nThis action [bold]CANNOT BE UNDONE[/bold]!")

    console.print("\nTo confirm, type [bold cyan]DELETE[/bold cyan] and press Enter:")

    try:
        confirmation = input().strip()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
        raise typer.Exit(0) from None

    if confirmation != "DELETE":
        console.print(f"[yellow]Confirmation failed.[/yellow] You typed '{confirmation}' but 'DELETE' was required.")
        console.print("Operation cancelled for safety.")
        raise typer.Exit(0)


@app.command("clear")
def clear_index(
    endpoint: str = typer.Option("", help="Service endpoint, e.g. https://<service>.search.windows.net"),
    index: str = typer.Option("", help="Index name to clear (remove all documents)"),
    api_key: str | None = typer.Option(None, help="Admin API key (otherwise uses DefaultAzureCredential)"),
) -> None:
    """[bold red]Clear all data from an index[/bold red] (DESTRUCTIVE).

    This completely removes all documents from the index by dropping and
    recreating it with the same schema. The index structure is preserved.

    [red]⚠️  WARNING: This operation cannot be undone![/red]
    """

    # Validate required parameters
    _validate_clear_params(endpoint, index)

    console.rule("[bold]ai-search-adm • clear index data")

    # Show authentication info
    _show_auth_info(endpoint, api_key)

    table = Table(show_header=False, box=None, title="Operation Details")
    table.add_column("Property", style="dim")
    table.add_column("Value")
    table.add_row("Endpoint", f"[cyan]{endpoint}[/cyan]")
    table.add_row("Index", f"[magenta]{index}[/magenta]")
    table.add_row("Operation", "[red]Clear all documents[/red]")
    console.print(table)

    client = _mk_client(endpoint, api_key)

    # Check if index exists
    try:
        original_index = client.get_index(index)
    except ResourceNotFoundError:
        console.print(f"[red]Error:[/red] Index '{index}' not found on {endpoint}")
        raise typer.Exit(2) from None
    except HttpResponseError as e:
        console.print(f"[red]Error fetching index:[/red] {e.message}")
        raise typer.Exit(2) from e

    # Get confirmation from user
    _confirm_destructive_operation(index)

    console.print("\n[yellow]Step 1/3:[/yellow] Saving index schema...")
    # Schema is already fetched in original_index

    console.print(f"[yellow]Step 2/3:[/yellow] Deleting index '{index}'...")
    try:
        client.delete_index(index)
    except HttpResponseError as e:
        console.print(f"[red]Error deleting index:[/red] {e.message}")
        raise typer.Exit(3) from e

    console.print("[yellow]Step 3/3:[/yellow] Recreating index with original schema...")
    # Sanitize the index for recreation
    recreated_index = _sanitize_for_create(original_index, index)

    try:
        client.create_index(recreated_index)
    except HttpResponseError as e:
        console.print(f"[red]Error recreating index:[/red] {e.message}")
        console.print(f"[red]CRITICAL:[/red] Index '{index}' was deleted but could not be recreated!")
        console.print("You may need to manually recreate the index from a backup.")
        raise typer.Exit(4) from e

    console.print(f"[green]✅ Success![/green] Index '[magenta]{index}[/magenta]' has been cleared.")
    console.print("[dim]All documents have been removed, but the index structure is preserved.[/dim]")


@app.command("stats")
def show_stats(
    endpoint: str = typer.Option("", help="Service endpoint, e.g. https://<service>.search.windows.net"),
    index: str = typer.Option("", help="Index name to get statistics for"),
    api_key: str | None = typer.Option(None, help="Admin API key (otherwise uses DefaultAzureCredential)"),
) -> None:
    """[bold]Show index statistics[/bold] including document count and storage usage.

    Displays detailed statistics about an index from Azure AI Search.
    """

    # Validate required parameters
    missing = []
    if not endpoint.strip():
        missing.append("--endpoint")
    if not index.strip():
        missing.append("--index")

    if missing:
        console.print(f"[red]Error:[/red] Missing required options: {', '.join(missing)}")
        console.print("\n[bold cyan]Usage:[/bold cyan]")
        console.print("ai-search-adm stats --endpoint <endpoint> --index <index>")
        console.print("\n[bold cyan]Example:[/bold cyan]")
        console.print("ai-search-adm stats --endpoint https://myservice.search.windows.net --index my-index")
        console.print("\n[dim]Use --help for more options[/dim]")
        raise typer.Exit(1)

    console.rule("[bold]ai-search-adm • index statistics")

    # Show authentication info
    _show_auth_info(endpoint, api_key)

    client = _mk_client(endpoint, api_key)

    try:
        # Get index statistics
        stats = client.get_index_statistics(index)

        # Display statistics in a nice table
        table = Table(show_header=False, box=None, title=f"Statistics for '[magenta]{index}[/magenta]'")
        table.add_column("Property", style="dim")
        table.add_column("Value", style="cyan")

        # Document count
        doc_count = stats.get("document_count", 0)
        table.add_row("Documents", f"{doc_count:,}")

        # Storage size (in bytes)
        storage_size = stats.get("storage_size", 0)
        # Convert to human-readable format
        if storage_size < 1024:
            size_str = f"{storage_size} bytes"
        elif storage_size < 1024 * 1024:
            size_str = f"{storage_size / 1024:.2f} KB"
        elif storage_size < 1024 * 1024 * 1024:
            size_str = f"{storage_size / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{storage_size / (1024 * 1024 * 1024):.2f} GB"

        table.add_row("Storage Size", size_str)
        table.add_row("Storage (bytes)", f"{storage_size:,}")

        # Vector index size if present
        if "vector_index_size" in stats:
            vector_size = stats["vector_index_size"]
            if vector_size < 1024 * 1024:
                vector_str = f"{vector_size / 1024:.2f} KB"
            elif vector_size < 1024 * 1024 * 1024:
                vector_str = f"{vector_size / (1024 * 1024):.2f} MB"
            else:
                vector_str = f"{vector_size / (1024 * 1024 * 1024):.2f} GB"
            table.add_row("Vector Index Size", vector_str)

        console.print(table)

    except ResourceNotFoundError:
        console.print(f"[red]Error:[/red] Index '{index}' not found on {endpoint}")
        raise typer.Exit(2) from None
    except HttpResponseError as e:
        console.print(f"[red]Error fetching statistics:[/red] {e.message}")
        raise typer.Exit(2) from e


if __name__ == "__main__":
    app()
