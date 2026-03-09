#!/usr/bin/env python3
"""
Token estimation tool for files and directories.

Usage:
    python estimate_tokens.py file.txt              # Single file
    python estimate_tokens.py /path/to/directory    # All files in directory
    python estimate_tokens.py . --extensions py,ts,js  # Filter by type
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple


def estimate_tokens(size_bytes: int, language: str = "text") -> int:
    """
    Estimate tokens for given byte size.
    
    Args:
        size_bytes: File size in bytes
        language: Programming language (for accuracy adjustment)
        
    Returns:
        Estimated token count
    """
    multipliers = {
        "python": 1.3,
        "javascript": 1.4,
        "typescript": 1.4,
        "go": 1.3,
        "java": 1.5,
        "sql": 1.2,
        "html": 1.2,
        "markdown": 1.1,
        "text": 1.0,
    }
    
    base_tokens = size_bytes * 0.25  # 1 token ≈ 4 bytes
    multiplier = multipliers.get(language.lower(), 1.0)
    
    return int(base_tokens * multiplier)


def get_language_from_extension(extension: str) -> str:
    """Infer language from file extension."""
    extension_map = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "go": "go",
        "java": "java",
        "sql": "sql",
        "html": "html",
        "md": "markdown",
        "txt": "text",
    }
    return extension_map.get(extension.lstrip("."), "text")


def format_bytes(size_bytes: int) -> str:
    """Format bytes to human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def analyze_file(file_path: Path) -> Dict:
    """Analyze a single file."""
    try:
        size = file_path.stat().st_size
        ext = file_path.suffix.lstrip(".")
        language = get_language_from_extension(ext)
        tokens = estimate_tokens(size, language)
        
        return {
            "path": str(file_path),
            "size": size,
            "size_human": format_bytes(size),
            "language": language,
            "tokens": tokens,
            "tokens_human": f"{tokens:,}",
        }
    except Exception as e:
        return {"path": str(file_path), "error": str(e)}


def analyze_directory(
    directory: Path,
    extensions: List[str] = None,
    recursive: bool = True,
) -> Tuple[List[Dict], Dict]:
    """
    Analyze all files in directory.
    
    Args:
        directory: Directory path
        extensions: Filter by extensions (e.g., ["py", "ts"])
        recursive: Search recursively
        
    Returns:
        (list of file analysis, summary statistics)
    """
    files = []
    total_size = 0
    total_tokens = 0
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    for file_path in directory.glob(pattern):
        if not file_path.is_file():
            continue
        
        ext = file_path.suffix.lstrip(".")
        
        # Filter by extensions if specified
        if extensions and ext not in extensions:
            continue
        
        analysis = analyze_file(file_path)
        
        if "error" not in analysis:
            files.append(analysis)
            total_size += analysis["size"]
            total_tokens += analysis["tokens"]
    
    summary = {
        "file_count": len(files),
        "total_size": total_size,
        "total_size_human": format_bytes(total_size),
        "total_tokens": total_tokens,
        "total_tokens_human": f"{total_tokens:,}",
    }
    
    return files, summary


def print_file_analysis(file_analysis: Dict):
    """Print analysis for single file."""
    if "error" in file_analysis:
        print(f"❌ {file_analysis['path']}: {file_analysis['error']}")
        return
    
    get_risk_indicator = lambda t: (
        "✅" if t < 15000 else
        "⚠️ " if t < 50000 else
        "🔴"
    )
    
    indicator = get_risk_indicator(file_analysis["tokens"])
    print(
        f"{indicator} {file_analysis['path']:<60} "
        f"{file_analysis['size_human']:>8} "
        f"({file_analysis['tokens_human']:>8} tokens) "
        f"[{file_analysis['language']}]"
    )


def get_recommendation(tokens: int) -> str:
    """Get recommendation based on token count."""
    if tokens < 5000:
        return "✅ Safe - Read fully"
    elif tokens < 15000:
        return "⚠️  Consider using range reading"
    elif tokens < 50000:
        return "🔴 Large - Use search + range reading"
    else:
        return "❌ Huge - Use divide and conquer strategy"


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python estimate_tokens.py <file_or_directory> [--extensions py,ts,js]")
        print("\nExamples:")
        print("  python estimate_tokens.py myfile.ts")
        print("  python estimate_tokens.py /path/to/src")
        print("  python estimate_tokens.py . --extensions py,ts,js")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    # Parse extensions filter
    extensions = None
    if "--extensions" in sys.argv:
        ext_index = sys.argv.index("--extensions") + 1
        if ext_index < len(sys.argv):
            extensions = sys.argv[ext_index].split(",")
    
    if not path.exists():
        print(f"❌ Path not found: {path}")
        sys.exit(1)
    
    if path.is_file():
        # Single file analysis
        analysis = analyze_file(path)
        print_file_analysis(analysis)
        
        if "error" not in analysis:
            print(f"\nRecommendation: {get_recommendation(analysis['tokens'])}")
    
    elif path.is_dir():
        # Directory analysis
        print(f"\n📁 Analyzing directory: {path}\n")
        
        files, summary = analyze_directory(path, extensions=extensions)
        
        if not files:
            print("No files found.")
            return
        
        # Print files sorted by size (largest first)
        print("Files by size:\n")
        for analysis in sorted(files, key=lambda x: x["size"], reverse=True):
            print_file_analysis(analysis)
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"Total files: {summary['file_count']}")
        print(f"Total size: {summary['total_size_human']} ({summary['total_size']:,} bytes)")
        print(f"Total tokens: {summary['total_tokens_human']}")
        print(f"{'='*80}\n")
        
        print(f"Overall recommendation: {get_recommendation(summary['total_tokens'])}")
        
        # Token budget analysis
        print("\nToken budget scenarios:")
        budgets = [5000, 15000, 30000, 50000, 100000]
        for budget in budgets:
            if summary["total_tokens"] <= budget:
                status = "✅ Within"
                remaining = budget - summary["total_tokens"]
                print(f"  {status} {budget:,} tokens (remaining: {remaining:,})")
            else:
                status = "❌ Exceeds"
                overage = summary["total_tokens"] - budget
                print(f"  {status} {budget:,} tokens (overage: {overage:,})")


if __name__ == "__main__":
    main()
