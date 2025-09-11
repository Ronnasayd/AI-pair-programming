#!/usr/bin/python3
import os
import re
import sys
import xml.etree.ElementTree as ET
from glob import glob

home_directory = os.path.expanduser("~")


def parse_pytest_coverage(xml_path):
    if not os.path.exists(xml_path):
        print(f"[WARN] coverage.xml não encontrado: {xml_path}")
        return []

    tree = ET.parse(xml_path)
    root = tree.getroot()
    coverage_data = []

    for class_node in root.findall(".//class"):
        filename = class_node.attrib.get("filename")
        lines = class_node.find("lines")
        if not lines:
            continue

        total = 0
        missed = 0
        uncovered_lines = []

        for line in lines.findall("line"):
            total += 1
            if line.attrib.get("hits") == "0":
                missed += 1
                uncovered_lines.append(line.attrib["number"])

        if total == 0:
            continue

        coverage = 100 * (total - missed) / total
        coverage_data.append(
            {
                "tool": "pytest",
                "file": filename,
                "coverage": round(coverage, 2),
                "uncovered_lines": uncovered_lines,
            }
        )

    return coverage_data


def parse_jest_coverage(lcov_path):
    if not os.path.exists(lcov_path):
        print(f"[WARN] lcov.info não encontrado: {lcov_path}")
        return []

    with open(lcov_path, "r") as f:
        content = f.read()

    blocks = content.split("end_of_record\n")
    coverage_data = []

    for block in blocks:
        if "SF:" not in block:
            continue

        filename_match = re.search(r"SF:(.+)", block)
        if not filename_match:
            continue
        filename = filename_match.group(1).strip()

        lines = re.findall(r"(?<!BR)DA:(\d+),(\d+)", block)
        if not lines:
            continue

        total = len(lines)
        uncovered = [line_no for line_no, hits in lines if hits == "0"]
        covered = total - len(uncovered)
        coverage = 100 * covered / total if total > 0 else 0

        coverage_data.append(
            {
                "tool": "jest",
                "file": filename,
                "coverage": round(coverage, 2),
                "uncovered_lines": uncovered,
            }
        )

    return coverage_data


def generate_llm_context(coverage_data, path, threshold=90):
    context = []
    for entry in coverage_data:
        if entry["coverage"] >= threshold:
            continue
        filepath = f'{path}{entry["file"]}'
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                file_lines = f.readlines()
        except FileNotFoundError:
            file_lines = []

        for index, content in enumerate(file_lines):
            file_lines[index] = f"{index+1}: {content}"

        linhas_detalhadas = []
        lines_map = []
        ctx_content = ""
        for line_no in entry["uncovered_lines"]:
            try:
                line_index = int(line_no) - 1
                if line_index not in lines_map:
                    lines_map.append(line_index)
                    content = file_lines[line_index].rstrip()
                    linhas_detalhadas.append(f"{line_no}: {content}")
                    file_lines[line_index] = (
                        f"{content} // Linha não coberta por testes!!!\n"
                    )
            except (IndexError, ValueError):
                linhas_detalhadas.append(f"{line_no}: [linha indisponível]")
        filepath = filepath.replace(home_directory, "~")
        ext = "sh"
        if "." in filepath:
            _, ext = os.path.splitext(filepath)
            ext = ext[1:]

        context.append(
            f"""\
### Arquivo: {filepath}
#### Cobertura: {entry['coverage']}%
#### Linhas não cobertas: {','.join([str(x+1) for x  in lines_map])}
````{ext}\n{''.join(file_lines)}````
"""
        )

    return "\n".join(context)


if __name__ == "__main__":
    path = sys.argv[1]
    jest_files = glob(f"{path}/**/lcov.info")
    pytest_files = glob(f"{path}/**/coverage.xml")
    combined = []
    if len(jest_files):
        jest_coverage = parse_jest_coverage(jest_files[0])
        combined += jest_coverage
    if len(pytest_files):
        pytest_coverage = parse_pytest_coverage(pytest_files[0])
        combined += pytest_coverage

    context_text = generate_llm_context(combined, path)

    print(context_text or "Tudo acima do limite mínimo de cobertura.")
