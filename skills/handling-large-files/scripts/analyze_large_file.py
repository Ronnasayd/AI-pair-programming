#!/usr/bin/env python3
"""
Analyze large files to identify optimal reading strategies.

Usage:
    python analyze_large_file.py largefile.ts
    python analyze_large_file.py largefile.ts --search "pattern"
    python analyze_large_file.py largefile.ts --chunk-size 100
"""

import sys
import re
from pathlib import Path
from typing import Dict


def estimate_tokens(size_bytes: int) -> int:
    """Estimate tokens from bytes."""
    return int(size_bytes * 0.25)


def get_file_structure(file_path: Path) -> Dict:
    """Extract structure of code file (functions, classes, etc.)."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    structure = {
        "total_lines": len(lines),
        "total_size": file_path.stat().st_size,
        "functions": [],
        "classes": [],
        "imports": [],
        "exports": [],
    }
    
    # Language detection
    suffix = file_path.suffix.lower()
    if suffix in [".py"]:
        lang_pattern_func = r"^def\s+(\w+)"
        lang_pattern_class = r"^class\s+(\w+)"
        lang_pattern_import = r"^(import|from)\s+"
    elif suffix in [".ts", ".js", ".tsx", ".jsx"]:
        lang_pattern_func = r"(?:async\s+)?(?:function\s+)?(\w+)\s*(?:\(|=\s*(?:async\s+)?\()"
        lang_pattern_class = r"(?:export\s+)?class\s+(\w+)"
        lang_pattern_import = r"^(?:import|export)\s+"
    elif suffix in [".go"]:
        lang_pattern_func = r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)"
        lang_pattern_class = r"^type\s+(\w+)\s+struct"
        lang_pattern_import = r"^import\s+"
    else:
        # Generic patterns
        lang_pattern_func = r"(?:def|function|async\s+)\s+(\w+)"
        lang_pattern_class = r"(?:class|interface)\s+(\w+)"
        lang_pattern_import = r"^(?:import|from|using)\s+"
    
    for line_num, line in enumerate(lines, 1):
        # Find functions
        if match := re.match(lang_pattern_func, line):
            structure["functions"].append({
                "name": match.group(1),
                "line": line_num,
            })
        
        # Find classes
        if match := re.match(lang_pattern_class, line):
            structure["classes"].append({
                "name": match.group(1),
                "line": line_num,
            })
        
        # Track imports
        if re.match(lang_pattern_import, line):
            structure["imports"].append(line_num)
        
        # Track exports
        if "export" in line:
            structure["exports"].append(line_num)
    
    return structure


def recommend_reading_strategy(
    file_path: Path,
    query: str = None,
) -> Dict:
    """Recommend optimal reading strategy."""
    structure = get_file_structure(file_path)
    total_lines = structure["total_lines"]
    total_size = structure["total_size"]
    total_tokens = estimate_tokens(total_size)
    
    recommendations = {
        "file": str(file_path),
        "total_lines": total_lines,
        "total_size_bytes": total_size,
        "estimated_tokens": total_tokens,
        "structure": structure,
        "strategies": [],
    }
    
    # Strategy 1: Full read
    recommendations["strategies"].append({
        "name": "Full Read",
        "description": "Read entire file",
        "lines": (1, total_lines),
        "estimated_tokens": total_tokens,
        "recommendation": "Use only if necessary" if total_tokens > 15000 else "✅ Safe",
    })
    
    # Strategy 2: Imports + first function
    if structure["functions"]:
        first_func = structure["functions"][0]
        last_import = structure["imports"][-1] if structure["imports"] else 1
        end_line = min(last_import + 10, total_lines)
        
        func_start = first_func["line"]
        func_end = (
            structure["functions"][1]["line"] - 1
            if len(structure["functions"]) > 1
            else min(func_start + 50, total_lines)
        )
        
        lines_needed = (end_line - 1) + (func_end - func_start)
        tokens_needed = int(lines_needed * 4 * 0.25)  # ~4 tokens per line
        
        recommendations["strategies"].append({
            "name": "Structure + First Function",
            "description": "Read imports and first major function",
            "lines": [(1, end_line), (func_start, func_end)],
            "estimated_tokens": tokens_needed,
            "recommendation": "Good for quick overview",
        })
    
    # Strategy 3: Specific function (if query provided)
    if query:
        for func in structure["functions"]:
            if query.lower() in func["name"].lower():
                # Find function's boundaries
                func_idx = structure["functions"].index(func)
                start = func["line"]
                end = (
                    structure["functions"][func_idx + 1]["line"] - 1
                    if func_idx + 1 < len(structure["functions"])
                    else min(start + 100, total_lines)
                )
                
                tokens_needed = int((end - start + 1) * 4 * 0.25)
                
                recommendations["strategies"].append({
                    "name": f"Read '{func['name']}' function",
                    "description": f"Focus on {func['name']} implementation",
                    "lines": (start, end),
                    "estimated_tokens": tokens_needed,
                    "recommendation": "Efficient - targeted read",
                })
    
    # Strategy 4: Divide and conquer
    if total_lines > 500:
        chunk_size = max(100, total_lines // 5)
        recommendations["strategies"].append({
            "name": "Divide and Conquer",
            "description": f"Read in {total_lines // chunk_size} chunks of ~{chunk_size} lines",
            "chunk_size": chunk_size,
            "estimated_tokens": total_tokens,  # Same total, but manageable
            "recommendation": f"Process one chunk at a time, total {total_tokens:,} tokens",
        })
    
    return recommendations


def print_recommendations(recommendations: Dict):
    """Print recommendations in readable format."""
    print(f"\n📊 File Analysis: {recommendations['file']}")
    print(f"   Size: {recommendations['total_size_bytes']:,} bytes")
    print(f"   Lines: {recommendations['total_lines']:,}")
    print(f"   Estimated tokens: {recommendations['estimated_tokens']:,}\n")
    
    # Print structure
    struct = recommendations["structure"]
    print("📐 File Structure:")
    print(f"   Classes: {len(struct['classes'])}")
    for cls in struct["classes"][:5]:
        print(f"     - {cls['name']} (line {cls['line']})")
    
    print(f"   Functions: {len(struct['functions'])}")
    for func in struct["functions"][:5]:
        print(f"     - {func['name']} (line {func['line']})")
    
    if len(struct["functions"]) > 5:
        print(f"     ... and {len(struct['functions']) - 5} more")
    
    # Print strategies
    print(f"\n🎯 Reading Strategies:\n")
    for i, strategy in enumerate(recommendations["strategies"], 1):
        print(f"{i}. {strategy['name']}")
        print(f"   {strategy['description']}")
        print(f"   Tokens: {strategy.get('estimated_tokens', 'N/A')}")
        print(f"   → {strategy['recommendation']}\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_large_file.py <file> [--search pattern]")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    query = None
    if "--search" in sys.argv:
        query_idx = sys.argv.index("--search") + 1
        if query_idx < len(sys.argv):
            query = sys.argv[query_idx]
    
    recommendations = recommend_reading_strategy(file_path, query)
    print_recommendations(recommendations)


if __name__ == "__main__":
    main()
