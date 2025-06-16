"""
Command-line interface for alletaal-lint.

This module provides a CLI for the LiNT readability assessment tool.
"""

import sys
from pathlib import Path
from typing import Optional, List
import json

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import Document, Sentence


app = typer.Typer(
    name="alletaal-lint",
    help="Dutch Text Readability Assessment using LiNT methodology. "
         "Note: Scores may differ from original T-Scan due to modern NLP implementation.",
    no_args_is_help=True,
)

console = Console()


def get_difficulty_description(level: int) -> str:
    """Get human-readable description of difficulty level."""
    descriptions = {
        1: "Very Difficult",
        2: "Difficult", 
        3: "Moderate",
        4: "Easy"
    }
    return descriptions.get(level, "Unknown")


def get_difficulty_color(level: int) -> str:
    """Get color for difficulty level display."""
    colors = {
        1: "red",
        2: "orange", 
        3: "yellow",
        4: "green"
    }
    return colors.get(level, "white")


@app.command()
def score(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Text to analyze"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File to analyze"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for results"),
    format: str = typer.Option("table", "--format", help="Output format (table, json, csv)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed analysis"),
) -> None:
    """Score text or file for readability."""
    
    # Get input text
    if text:
        input_text = text
    elif file:
        if not file.exists():
            console.print(f"[red]Error: File {file} not found[/red]")
            raise typer.Exit(1)
        try:
            input_text = file.read_text(encoding='utf-8')
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[red]Error: Either --text or --file must be provided[/red]")
        raise typer.Exit(1)

    # Analyze text
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing text...", total=None)
        
        try:
            document = Document(input_text)
            analysis = document.get_detailed_analysis()
        except Exception as e:
            console.print(f"[red]Error analyzing text: {e}[/red]")
            raise typer.Exit(1)

    # Format and display results
    if format == "json":
        output_data = {
            "document_score": analysis['document_score'],
            "document_level": analysis['document_level'],
            "document_level_description": get_difficulty_description(analysis['document_level']),
            "sentence_count": analysis['sentence_count'],
            "average_sentence_length": analysis['average_sentence_length'],
        }
        
        if detailed:
            output_data["sentences"] = [
                {
                    "text": sent[0],
                    "score": sent[1], 
                    "level": sent[2],
                    "level_description": get_difficulty_description(sent[2])
                }
                for sent in analysis['sentence_scores']
            ]
        
        json_output = json.dumps(output_data, indent=2, ensure_ascii=False)
        
        if output:
            output.write_text(json_output, encoding='utf-8')
            console.print(f"[green]Results saved to {output}[/green]")
        else:
            console.print(json_output)
    
    elif format == "csv":
        import csv
        import io
        
        csv_output = io.StringIO()
        writer = csv.writer(csv_output)
        
        if detailed:
            writer.writerow(["sentence", "score", "level", "level_description"])
            for sent in analysis['sentence_scores']:
                writer.writerow([sent[0], sent[1], sent[2], get_difficulty_description(sent[2])])
        else:
            writer.writerow(["document_score", "document_level", "document_level_description", 
                           "sentence_count", "average_sentence_length"])
            writer.writerow([
                analysis['document_score'], 
                analysis['document_level'],
                get_difficulty_description(analysis['document_level']),
                analysis['sentence_count'],
                analysis['average_sentence_length']
            ])
        
        csv_content = csv_output.getvalue()
        
        if output:
            output.write_text(csv_content, encoding='utf-8')
            console.print(f"[green]Results saved to {output}[/green]")
        else:
            console.print(csv_content)
    
    else:  # table format
        # Document summary
        level_color = get_difficulty_color(analysis['document_level'])
        level_desc = get_difficulty_description(analysis['document_level'])
        
        summary_table = Table(title="Document Readability Summary")
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Value")
        
        summary_table.add_row("LiNT Score", f"{analysis['document_score']}")
        summary_table.add_row("Difficulty Level", f"[{level_color}]{analysis['document_level']} - {level_desc}[/{level_color}]")
        summary_table.add_row("Sentences", str(analysis['sentence_count']))
        summary_table.add_row("Avg. Sentence Length", f"{analysis['average_sentence_length']:.1f} words")
        
        console.print(summary_table)
        
        # Detailed sentence analysis if requested
        if detailed:
            console.print()
            sentence_table = Table(title="Sentence Analysis")
            sentence_table.add_column("Sentence", max_width=60)
            sentence_table.add_column("Score", justify="center")
            sentence_table.add_column("Level", justify="center")
            
            for sent_text, sent_score, sent_level in analysis['sentence_scores']:
                color = get_difficulty_color(sent_level)
                level_text = f"[{color}]{sent_level}[/{color}]"
                
                # Truncate long sentences for display
                display_text = sent_text if len(sent_text) <= 60 else sent_text[:57] + "..."
                
                sentence_table.add_row(display_text, str(sent_score), level_text)
            
            console.print(sentence_table)


@app.command()
def sentence(
    text: str = typer.Argument(..., help="Sentence to analyze"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed metrics"),
) -> None:
    """Score a single sentence for readability."""
    
    try:
        sentence = Sentence(text)
        score = sentence.calculate_lint_score()
        level = sentence.get_difficulty_level()
        
        color = get_difficulty_color(level)
        level_desc = get_difficulty_description(level)
        
        console.print(Panel(
            f"[bold]Sentence:[/bold] {text}\n\n"
            f"[bold]LiNT Score:[/bold] {score}\n"
            f"[bold]Difficulty Level:[/bold] [{color}]{level} - {level_desc}[/{color}]",
            title="Sentence Readability Analysis"
        ))
        
        if detailed:
            console.print()
            metrics_table = Table(title="Detailed Metrics")
            metrics_table.add_column("Metric", style="bold")
            metrics_table.add_column("Value")
            
            metrics_table.add_row("Word Frequency (log)", f"{sentence.get_word_frequency_log():.3f}")
            metrics_table.add_row("Max Dependency Length", str(sentence.get_max_dependency_length()))
            metrics_table.add_row("Content Words Proportion", f"{sentence.get_proportion_of_content_words_excluding_adverbs():.3f}")
            metrics_table.add_row("Concrete Nouns Proportion", f"{sentence.get_proportion_of_broadly_concrete_nouns():.3f}")
            
            console.print(metrics_table)
    
    except Exception as e:
        console.print(f"[red]Error analyzing sentence: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def server(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
) -> None:
    """Start the FastAPI server."""
    try:
        import uvicorn
        from .api import app as fastapi_app
        
        console.print(f"[green]Starting server on {host}:{port}[/green]")
        console.print(f"[blue]API documentation available at http://{host}:{port}/docs[/blue]")
        
        uvicorn.run(
            "alletaal_lint.api:app",
            host=host,
            port=port,
            reload=reload,
        )
    except ImportError:
        console.print("[red]Error: uvicorn is required to run the server[/red]")
        console.print("Install with: pip install uvicorn[standard]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def install_model() -> None:
    """Install the required Dutch spaCy model."""
    import subprocess
    
    console.print("[yellow]Installing Dutch spaCy model (nl_core_news_sm)...[/yellow]")
    
    try:
        subprocess.run([
            sys.executable, "-m", "spacy", "download", "nl_core_news_sm"
        ], check=True)
        console.print("[green]Successfully installed nl_core_news_sm[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error installing model: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__
    console.print(f"alletaal-lint version {__version__}")


if __name__ == "__main__":
    app()