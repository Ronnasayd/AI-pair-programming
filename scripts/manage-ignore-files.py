#!/usr/bin/env python3
"""
Script interativo com checkboxes para habilitar e desabilitar skills e agents
nos arquivos .skillsignore e .agentsignore
"""

import sys
import curses
from pathlib import Path
from typing import List, Dict, Tuple


class IgnoreFileManager:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.skillsignore_path = self.workspace_root / ".skillsignore"
        self.agentsignore_path = self.workspace_root / ".agentsignore"
        self.rulesignore_path = self.workspace_root / ".rulesignore"

    def read_file(self, file_path: Path) -> List[str]:
        """Lê o arquivo mantendo as linhas originais"""
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {file_path}")
            return []
        with open(file_path, "r") as f:
            return f.readlines()

    def write_file(self, file_path: Path, lines: List[str]) -> bool:
        """Escreve as linhas no arquivo"""
        try:
            with open(file_path, "w") as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"❌ Erro ao escrever arquivo: {e}")
            return False

    def parse_ignore_file(
        self, lines: List[str]
    ) -> Dict[str, List[Tuple[int, str, bool]]]:
        """
        Parseia o arquivo e retorna um dicionário com:
        - chave: categoria/seção
        - valor: lista de (line_index, pattern, is_enabled)
        """
        sections = {}
        current_section = "Geral"

        for idx, line in enumerate(lines):
            # Detecta seções (linhas com #####)
            if "####" in line:
                current_section = line.replace("#", "").strip()
                if not current_section:
                    current_section = "Geral"
                continue

            # Ignora linhas vazias e comentários de seção
            if (
                not line.strip()
                or line.strip().startswith("#")
                and len(line.strip()) > 1
                and line.strip()[1] == "#"
            ):
                continue

            # Processa linhas de comentário e padrões
            # Em .ignore: sem # = DESABILITADO
            #            # = HABILITADO
            if line.strip().startswith("#") and not line.strip().startswith("##"):
                # É um comentário de padrão = HABILITADO
                pattern = line.lstrip("#").strip()
                if pattern and not pattern.startswith("#"):
                    if current_section not in sections:
                        sections[current_section] = []
                    sections[current_section].append((idx, pattern, True))
            elif line.strip() and not line.strip().startswith("##"):
                # É um padrão sem comentário = DESABILITADO
                pattern = line.strip()
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append((idx, pattern, False))

        return sections

    def interactive_checkbox_menu(self, stdscr, file_type: str):
        """Menu interativo com checkboxes usando curses"""
        curses.curs_set(0)  # Esconde o cursor
        stdscr.timeout(100)  # Timeout de 100ms para input

        # Cores
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Selecionado
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Normal
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Header
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Instrução
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Filtro

        if file_type == "skills":
            file_path = self.skillsignore_path
            lines = self.read_file(file_path)
            title = "📋 GERENCIADOR DE SKILLS"
        elif file_type == "agents":
            file_path = self.agentsignore_path
            lines = self.read_file(file_path)
            title = "🤖 GERENCIADOR DE AGENTS"
        else:
            file_path = self.rulesignore_path
            lines = self.read_file(file_path)
            title = "📏 GERENCIADOR DE RULES"

        sections = self.parse_ignore_file(lines)

        if not sections:
            stdscr.addstr("❌ Nenhum item encontrado\n")
            stdscr.refresh()
            stdscr.getch()
            return

        # Constrói lista flat com info de seção
        all_items = []
        for section, items in sections.items():
            for line_idx, pattern, is_enabled in items:
                all_items.append(
                    {
                        "section": section,
                        "line_idx": line_idx,
                        "pattern": pattern,
                        "is_enabled": is_enabled,
                    }
                )

        cursor_pos = 0
        scroll_offset = 0
        changes: Dict[int, bool] = {}  # line_idx -> novo estado
        search_term = ""  # Termo de busca
        search_active = False  # Modo de busca ativo
        filtered_items_indices = list(
            range(len(all_items))
        )  # Índices dos items filtrados

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Filtra items baseado no termo de busca
            if search_term:
                filtered_items_indices = [
                    idx
                    for idx in range(len(all_items))
                    if search_term.lower() in all_items[idx]["pattern"].lower()
                ]
            else:
                filtered_items_indices = list(range(len(all_items)))

            # Ajusta cursor se necessário
            if cursor_pos >= len(filtered_items_indices):
                cursor_pos = max(0, len(filtered_items_indices) - 1)

            # Garante que o cursor está visível na tela
            visible_items = height - 7  # espaço para header + footer + search
            if cursor_pos < scroll_offset:
                scroll_offset = cursor_pos
            elif cursor_pos >= scroll_offset + visible_items:
                scroll_offset = cursor_pos - visible_items + 1

            # Header
            stdscr.addstr(0, 0, title, curses.color_pair(3) | curses.A_BOLD)
            stdscr.addstr(1, 0, "=" * width, curses.color_pair(3))

            # Search bar
            if search_active:
                search_display = f"🔍 Filtro (ATIVO): {search_term}_"
            elif search_term:
                search_display = f"🔍 Filtro: {search_term}"
            else:
                search_display = "🔍 Filtro (pressione / para buscar)"
            stdscr.addstr(
                2, 0, search_display[:width], curses.color_pair(5) | curses.A_BOLD
            )

            # Instruções
            if search_active:
                instr = (
                    "Modo FILTRO: digite para buscar | Backspace: deletar | ESC: sair"
                )
            else:
                instr = (
                    "↑/↓: navegar | /: filtrar | ESPAÇO: alternar | S: salvar | Q: sair"
                )
            stdscr.addstr(3, 0, instr[:width], curses.color_pair(4))
            stdscr.addstr(4, 0, "-" * width)

            # Items com checkboxes
            y = 5
            rendered_items = 0

            for pos, idx in enumerate(filtered_items_indices):
                # Pula items acima do scroll offset
                if pos < scroll_offset:
                    continue

                if y >= height - 2:
                    break

                item = all_items[idx]

                # Estado do item (considerando mudanças)
                line_idx = item["line_idx"]
                if line_idx in changes:
                    is_enabled = changes[line_idx]
                else:
                    is_enabled = item["is_enabled"]

                # Checkbox
                if pos == cursor_pos:
                    checkbox = "☑️ " if is_enabled else "☐ "
                    prefix = "➜ "
                    color = curses.color_pair(1) | curses.A_BOLD
                else:
                    checkbox = "☑️ " if is_enabled else "☐ "
                    prefix = "  "
                    color = curses.color_pair(2)

                # Status badge
                status = "[✅ ATIVO]" if is_enabled else "[❌ INATIVO]"
                pattern = item["pattern"]

                # Trunca se necessário
                available = width - len(prefix) - len(checkbox) - len(status) - 5
                if len(pattern) > available:
                    pattern = pattern[: available - 3] + "..."

                line_text = f"{prefix}{checkbox} {pattern} {status}"

                try:
                    stdscr.addstr(y, 0, line_text, color)
                except curses.error:
                    pass

                y += 1
                rendered_items += 1

            # Footer com resumo e indicador de scroll
            stdscr.addstr(height - 2, 0, "-" * width)

            # Conta mudanças
            enabled_changes = sum(1 for v in changes.values() if v)
            disabled_changes = sum(1 for v in changes.values() if not v)
            total_changes = len(changes)

            # Mostra posição no scroll
            if filtered_items_indices:
                scroll_info = f"[{cursor_pos + 1}/{len(filtered_items_indices)}]"
            else:
                scroll_info = "[0/0]"

            if total_changes > 0:
                summary = f"📊 Mudanças: {total_changes} | ✅ {enabled_changes} | ❌ {disabled_changes} {scroll_info}"
            else:
                summary = f"Items: {len(filtered_items_indices)}/{len(all_items)} {scroll_info}"

            stdscr.addstr(height - 1, 0, summary[:width], curses.color_pair(3))

            stdscr.refresh()

            # Entrada com timeout
            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                return

            # Se não há input (-1), continua o loop sem fazer nada
            if key == -1:
                continue

            # Modo de busca ativo
            if search_active:
                if key == 27:  # ESC - sair do modo de busca
                    search_active = False
                elif key == curses.KEY_BACKSPACE or key == 8 or key == 127:  # Backspace
                    search_term = search_term[:-1]
                    cursor_pos = 0
                    scroll_offset = 0
                elif 32 <= key <= 126:  # Caracteres imprimíveis
                    search_term += chr(key)
                    cursor_pos = 0
                    scroll_offset = 0
            # Modo normal (sem busca)
            else:
                if key == ord("/"):  # Ativar modo de busca
                    search_active = True
                    search_term = ""
                    cursor_pos = 0
                    scroll_offset = 0
                elif key == curses.KEY_UP:
                    cursor_pos = max(0, cursor_pos - 1)
                elif key == curses.KEY_DOWN:
                    cursor_pos = min(len(filtered_items_indices) - 1, cursor_pos + 1)
                elif key == curses.KEY_PPAGE:  # Page Up
                    cursor_pos = max(0, cursor_pos - 5)
                elif key == curses.KEY_NPAGE:  # Page Down
                    cursor_pos = min(len(filtered_items_indices) - 1, cursor_pos + 5)
                elif key == ord(" "):  # Espaço para alternar
                    if filtered_items_indices:
                        actual_idx = filtered_items_indices[cursor_pos]
                        item = all_items[actual_idx]
                        line_idx = item["line_idx"]

                        if line_idx in changes:
                            del changes[line_idx]
                        else:
                            changes[line_idx] = not item["is_enabled"]
                elif key == ord("s") or key == ord("S"):
                    # Salvar
                    if changes:
                        self._apply_changes(file_path, lines, changes)
                        stdscr.clear()
                        stdscr.addstr(
                            0,
                            0,
                            f"✅ Arquivo salvo com {len(changes)} mudança(s)!",
                            curses.color_pair(1),
                        )
                        stdscr.refresh()
                        stdscr.getch()
                        return
                    else:
                        stdscr.clear()
                        stdscr.addstr(
                            0,
                            0,
                            "ℹ️  Nenhuma mudança para salvar",
                            curses.color_pair(3),
                        )
                        stdscr.refresh()
                        stdscr.getch()
                elif key == ord("q") or key == ord("Q"):
                    if changes:
                        stdscr.clear()
                        confirm = "⚠️  Há mudanças não salvas. Descartar? (s/n): "
                        stdscr.addstr(0, 0, confirm, curses.color_pair(3))
                        stdscr.refresh()
                        if stdscr.getch() == ord("s"):
                            return
                    else:
                        return

    def _apply_changes(
        self, file_path: Path, lines: List[str], changes: Dict[int, bool]
    ):
        """Aplica as mudanças e reordena o arquivo

        Em .ignore:
        - True (habilitado) = com # = comentado (ativo)
        - False (desabilitado) = sem # = descomentuário (inativo)

        Ordena: ativos primeiro (alfabético), depois inativos (alfabético)
        """
        # Aplica as mudanças
        for line_idx, should_be_enabled in changes.items():
            current_line = lines[line_idx]

            if should_be_enabled:
                if not current_line.strip().startswith("#"):
                    lines[line_idx] = f"# {current_line.lstrip()}"
            else:
                lines[line_idx] = current_line.lstrip("#").lstrip()
                if not lines[line_idx].endswith("\n"):
                    lines[line_idx] += "\n"

        # Separa seções, comments e padrões
        sections = {}
        current_section = "Geral"
        active_items = []
        inactive_items = []

        for line in lines:
            # Detecta seções
            if "####" in line:
                current_section = line.replace("#", "").strip()
                if not current_section:
                    current_section = "Geral"
                if current_section not in sections:
                    sections[current_section] = line
                continue

            # Ignora linhas vazias e comments de seção
            if (
                not line.strip()
                or line.strip().startswith("#")
                and len(line.strip()) > 1
                and line.strip()[1] == "#"
            ):
                continue

            # Processa padrões
            if line.strip().startswith("#") and not line.strip().startswith("##"):
                pattern = line.lstrip("#").strip()
                if pattern:
                    active_items.append(pattern)
            elif line.strip() and not line.strip().startswith("##"):
                pattern = line.strip()
                inactive_items.append(pattern)

        # Ordena alfabeticamente
        active_items.sort()
        inactive_items.sort()

        # Reconstrói o arquivo
        new_lines = []

        # Adiciona seção principal se houver
        if "Geral" in sections:
            new_lines.append(sections["Geral"])

        # Adiciona ativos primeiro
        for pattern in active_items:
            new_lines.append(f"# {pattern}\n")

        # Depois inativos
        for pattern in inactive_items:
            new_lines.append(f"{pattern}\n")

        # Adiciona outras seções
        for section, section_line in sections.items():
            if section != "Geral":
                new_lines.append(section_line)

        self.write_file(file_path, new_lines)

    def main_menu(self, stdscr):
        """Menu principal"""
        curses.curs_set(0)
        stdscr.timeout(-1)  # Entrada bloqueante

        # Cores
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Title
            title = "🎮 GERENCIADOR DE SKILLS, AGENTS E RULES"
            stdscr.addstr(
                0,
                (width - len(title)) // 2,
                title,
                curses.color_pair(3) | curses.A_BOLD,
            )
            stdscr.addstr(1, 0, "=" * width)

            y = 3
            menu_items = [
                ("1", "📋 Gerenciar Skills"),
                ("2", "🤖 Gerenciar Agents"),
                ("3", "📏 Gerenciar Rules"),
                ("Q", "❌ Sair"),
            ]

            for key, text in menu_items:
                y += 1
                stdscr.addstr(y, 2, f"[{key}] {text}", curses.color_pair(2))

            y += 2
            stdscr.addstr(y, 2, "👉 Digite sua opção: ", curses.color_pair(3))
            stdscr.refresh()

            try:
                key = stdscr.getch()

                if key == ord("1"):
                    self.interactive_checkbox_menu(stdscr, "skills")
                elif key == ord("2"):
                    self.interactive_checkbox_menu(stdscr, "agents")
                elif key == ord("3"):
                    self.interactive_checkbox_menu(stdscr, "rules")
                elif key == ord("q") or key == ord("Q"):
                    stdscr.clear()
                    stdscr.addstr(0, 0, "👋 Até logo!", curses.color_pair(3))
                    stdscr.refresh()
                    stdscr.getch()
                    break
            except KeyboardInterrupt:
                break


def main():
    # Usa o diretório de trabalho atual (CWD) em vez de tentar resolver do script
    workspace_root = Path.cwd()
    manager = IgnoreFileManager(workspace_root)

    # Verifica se os arquivos existem
    if not manager.skillsignore_path.exists():
        print(f"❌ Arquivo não encontrado: {manager.skillsignore_path}")
        sys.exit(1)

    if not manager.agentsignore_path.exists():
        print(f"❌ Arquivo não encontrado: {manager.agentsignore_path}")
        sys.exit(1)

    if not manager.rulesignore_path.exists():
        print(f"❌ Arquivo não encontrado: {manager.rulesignore_path}")
        sys.exit(1)

    try:
        curses.wrapper(manager.main_menu)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
