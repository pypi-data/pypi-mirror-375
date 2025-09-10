from collections import Counter
from datetime import datetime
from pathlib import Path

def create_summary_report(
    pii_results: list, 
    output_dir: Path,
    filename: str,
    validation_metrics: dict = None
):
    report_path = output_dir / f"summary_report_{Path(filename).stem}.txt"
    pii_counts = Counter(item['type'] for item in pii_results)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("--- PyRedact Scan Report ---\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source File: {filename}\n")
        f.write("---------------------------------\n\n")
        
        f.write(f"Total PII Instances Found: {len(pii_results)}\n")
        f.write("PII Breakdown:\n")
        if not pii_counts:
            f.write("  - No PII detected.\n")
        else:
            for pii_type, count in sorted(pii_counts.items()):
                f.write(f"  - {pii_type}: {count}\n")
        
        if validation_metrics:
            f.write("\n--- Validation Metrics ---\n")
            f.write(f"True Positives: {validation_metrics['tp']}\n")
            f.write(f"False Positives: {validation_metrics['fp']}\n")
            f.write(f"False Negatives: {validation_metrics['fn']}\n\n")
            f.write(f"Precision: {validation_metrics['precision']:.2f}\n")
            f.write(f"Recall: {validation_metrics['recall']:.2f}\n")
            f.write(f"F1-Score: {validation_metrics['f1_score']:.2f}\n")
        
        f.write("\n--- End of Report ---\n")

    return report_path