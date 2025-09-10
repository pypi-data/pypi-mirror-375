import typer
import pandas as pd
from pathlib import Path
import logging
import chardet
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
import time

from pyredact.detector import find_pii
from pyredact.anonymizer import anonymize_pii
from pyredact.report_generator import create_summary_report
from pyredact.regex_patterns import REGEX_PATTERNS

console = Console()
logging.basicConfig(level="INFO", format='%(levelname)s: %(message)s', handlers=[])
logger = logging.getLogger(__name__)

app = typer.Typer(rich_markup_mode="markdown", add_completion=False)

ASCII_BANNER = """
ooooooooo.   oooooo   oooo ooooooooo.   oooooooooooo oooooooooo.         .o.         .oooooo.   ooooooooooooo 
`888   `Y88.  `888.   .8'  `888   `Y88. `888'     `8 `888'   `Y8b       .888.       d8P'  `Y8b  8'   888   `8 
 888   .d88'   `888. .8'    888   .d88'  888          888      888     .8"888.     888               888      
 888ooo88P'     `888.8'     888ooo88P'   888oooo8     888      888    .8' `888.    888               888      
 888             `888'      888`88b.     888    "     888      888   .88ooo8888.   888               888      
 888              888       888  `88b.   888       o  888     d88'  .8'     `888.  `88b    ooo       888      
o888o            o888o     o888o  o888o o888ooooood8 o888bood8P'   o88o     o8888o  `Y8bood8P'      o888o     
                                                                                                              
A Tool for PII Detection & De-Identification
"""

def detect_encoding(file_path: Path) -> str:
    with open(file_path, 'rb') as f:
        raw_data = f.read(20000)
    result = chardet.detect(raw_data)
    return result['encoding'] or 'utf-8'

def get_files_from_dir(dir_path: Path) -> list[Path]:
    return list(dir_path.glob("*.csv"))

def calculate_validation_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1_score": f1_score}

@app.command()
def process(
    input_file: Path = typer.Option(None, "--input", "-i", help="Path to a single input CSV file."),
    input_dir: Path = typer.Option(None, "--input-dir", "-d", help="Path to a directory containing CSV files to process."),
    output_dir: Path = typer.Option("output", "--output", "-o", help="Directory to save the output files."),
    types_to_scan: str = typer.Option(None, "--types", "-t", help=f"Comma-separated list of specific PII types to scan for. Available types: {', '.join(REGEX_PATTERNS.keys())}"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output to see line-by-line findings."),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite of existing output files without asking.")
):
    console.print(f"[bold green]{ASCII_BANNER}[/bold green]")
    
    if not input_file and not input_dir:
        console.print("❌ [bold red]Error:[/bold red] You must provide an input using either '--input' for a file or '--input-dir' for a directory.")
        raise typer.Exit(code=1)

    if input_file and input_dir:
        console.print("❌ [bold red]Error:[/bold red] Please provide either '--input' or '--input-dir', not both.")
        raise typer.Exit(code=1)

    files_to_process = [input_file] if input_file else get_files_from_dir(input_dir)
    
    if not files_to_process:
        console.print(f"⚠️ [yellow]Warning:[/yellow] No CSV files found in the specified directory.")
        raise typer.Exit()
    
    console.log(f"Found {len(files_to_process)} file(s) to process.")
    
    types_list = [t.strip().upper() for t in types_to_scan.split(',')] if types_to_scan else None
    
    for file in files_to_process:
        console.rule(f"[bold blue]Processing: {file.name}[/bold blue]")
        process_single_file(file, output_dir, types_list, verbose, force)
        time.sleep(1)

def process_single_file(input_file: Path, output_dir: Path, types_to_scan: list[str] | None, verbose: bool, force: bool):
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        console.print(f"❌ [bold red]Permission Error:[/bold red] Could not create output directory. Aborting.")
        raise typer.Exit(code=1)
        
    output_file = output_dir / f"deidentified_{input_file.name}"
    if output_file.exists() and not force:
        if not typer.confirm(f"⚠️ Output file {output_file} already exists. Overwrite?"):
            console.print("[yellow]Skipping file.[/yellow]")
            return

    try:
        encoding = detect_encoding(input_file)
        if verbose: console.log(f"Detected encoding: [yellow]{encoding}[/yellow]")
        df = pd.read_csv(input_file, dtype=str, encoding=encoding, engine='python').fillna('')
    except Exception as e:
        console.print(f"❌ [bold red]File Read Error:[/bold red] Could not read {input_file.name}. Reason: {e}")
        return
    
    if df.empty:
        console.print(f"⚠️ [yellow]Warning:[/yellow] Input file {input_file.name} is empty.")
        return
        
    all_pii_found = []
    validation_mode = 'pii_type' in df.columns
    tp, fp, fn = 0, 0, 0

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%")) as progress:
        task = progress.add_task("[green]Scanning rows...", total=len(df))
        for index, row in df.iterrows():
            
            if validation_mode:
                row_text_for_validation = ' '.join(row.astype(str))
                detected_pii_in_row = find_pii(row_text_for_validation, types_to_scan)
                detected_types = {p['type'] for p in detected_pii_in_row}
                true_pii_type = row.get('pii_type', '').upper()
                
                if true_pii_type and true_pii_type in detected_types:
                    tp += 1
                    detected_types.remove(true_pii_type)
                elif true_pii_type and true_pii_type not in detected_types:
                    fn += 1
                fp += len(detected_types)

            for col in df.columns:
                if validation_mode and col == 'pii_type':
                    continue
                
                cell_text = str(row[col])
                pii_results = find_pii(cell_text, types_to_scan)
                
                if pii_results:
                    if verbose: console.log(f"Found PII in row {index+2}, column '{col}': {[p['value'] for p in pii_results]}")
                    all_pii_found.extend(pii_results)
                    
                    modified_text = cell_text
                    for pii in pii_results:
                        anonymized_value = anonymize_pii(pii['type'], pii['value'])
                        modified_text = modified_text.replace(pii['value'], anonymized_value)
                    
                    df.loc[index, col] = modified_text

            progress.update(task, advance=1)
    
    df.to_csv(output_file, index=False)
    
    validation_metrics = calculate_validation_metrics(tp, fp, fn) if validation_mode else None
    report_path = create_summary_report(all_pii_found, output_dir, input_file.name, validation_metrics)
    
    console.log(f"✅ [green]Success![/green] De-identified file saved to [cyan]{output_file}[/cyan]")
    console.log(f"✅ [green]Success![/green] Summary report saved to [cyan]{report_path}[/cyan]")

if __name__ == "__main__":
    app()