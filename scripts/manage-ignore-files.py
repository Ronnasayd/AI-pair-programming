#!/usr/bin/env python3
"""Script interativo com checkboxes para habilitar e desabilitar skills, agents.

Também gerencia instructions no ~/.claude/aipp-settings.json do projeto atual.
"""

import contextlib
import curses
from pathlib import Path
import sys

import aipp_settings


class IgnoreFileManager:
    """Manages skill/agent/instruction enablement for one project via aipp_settings."""

    def __init__(self, workspace_root: str | Path = ".") -> None:
        """Resolve workspace_root to an absolute path string (the JSON project key)."""
        self.workspace_root = str(Path(workspace_root).resolve())

    def interactive_checkbox_menu(  # noqa: C901 -- unchanged UI loop, kept verbatim
        self, stdscr: "curses.window", file_type: str
    ) -> None:
        # why: unchanged UI loop kept verbatim; splitting it would risk the render logic
        # pylint: disable=too-many-locals,too-many-statements,too-many-nested-blocks
        """Menu interativo com checkboxes usando curses.

        Args:
            stdscr: Curses window passed in by curses.wrapper.
            file_type: Category to edit -- "skills", "agents", or "instructions".
        """
        curses.curs_set(0)  # Esconde o cursor
        stdscr.timeout(100)  # Timeout de 100ms para input

        # Cores
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Selecionado
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Normal
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Header
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Instrução
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Filtro

        category = file_type  # "skills" | "agents" | "instructions"
        titles = {
            "skills": "📋 GERENCIADOR DE SKILLS",
            "agents": "🤖 GERENCIADOR DE AGENTS",
            "instructions": "📏 GERENCIADOR DE RULES",
        }
        title = titles.get(category, "📋 GERENCIADOR")

        entry = aipp_settings.get_project(self.workspace_root)
        items_dict = entry.get(category, {})

        if not items_dict:
            stdscr.addstr("❌ Nenhum item encontrado\n")
            stdscr.refresh()
            stdscr.getch()
            return

        # Constrói lista flat (JSON não tem seções)
        all_items = [
            {"pattern": name, "is_enabled": enabled}
            for name, enabled in items_dict.items()
        ]

        cursor_pos = 0
        scroll_offset = 0
        changes: dict = {}  # pattern -> novo estado
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
                pattern = item["pattern"]
                is_enabled = changes.get(pattern, item["is_enabled"])

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

                # Trunca se necessário
                available = width - len(prefix) - len(checkbox) - len(status) - 5
                display_pattern = pattern
                if len(display_pattern) > available:
                    display_pattern = display_pattern[: available - 3] + "..."

                line_text = f"{prefix}{checkbox} {display_pattern} {status}"

                with contextlib.suppress(curses.error):
                    stdscr.addstr(y, 0, line_text, color)

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
                summary = (
                    f"📊 Mudanças: {total_changes} | ✅ {enabled_changes} | "
                    f"❌ {disabled_changes} {scroll_info}"
                )
            else:
                summary = (
                    f"Items: {len(filtered_items_indices)}/{len(all_items)} "
                    f"{scroll_info}"
                )

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
                        pattern = item["pattern"]

                        if pattern in changes:
                            del changes[pattern]
                        else:
                            changes[pattern] = not item["is_enabled"]
                elif key == ord("s") or key == ord("S"):
                    # Salvar
                    if changes:
                        self._apply_changes(category, changes)
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
                            "ℹ️  Nenhuma mudança para salvar",  # noqa: RUF001
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

    def _apply_changes(self, category: str, changes: dict) -> None:
        """Persiste as mudanças no aipp-settings.json via aipp_settings.set_item."""
        for pattern, enabled in changes.items():
            aipp_settings.set_item(self.workspace_root, category, pattern, enabled)

    def main_menu(self, stdscr: "curses.window") -> None:
        """Menu principal.

        Args:
            stdscr: Curses window passed in by curses.wrapper.
        """
        curses.curs_set(0)
        stdscr.timeout(-1)  # Entrada bloqueante

        # Cores
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        while True:
            stdscr.clear()
            _height, width = stdscr.getmaxyx()

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

            for menu_key, text in menu_items:
                y += 1
                stdscr.addstr(y, 2, f"[{menu_key}] {text}", curses.color_pair(2))

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
                    self.interactive_checkbox_menu(stdscr, "instructions")
                elif key == ord("q") or key == ord("Q"):
                    stdscr.clear()
                    stdscr.addstr(0, 0, "👋 Até logo!", curses.color_pair(3))
                    stdscr.refresh()
                    stdscr.getch()
                    break
            except KeyboardInterrupt:
                break


def main() -> None:
    """CLI entry point: launch the curses menu for the current directory's project."""
    # Usa o diretório de trabalho atual (CWD) em vez de tentar resolver do script
    workspace_root = Path.cwd()
    manager = IgnoreFileManager(workspace_root)

    try:
        curses.wrapper(manager.main_menu)
    except Exception as e:  # pylint: disable=broad-exception-caught
        # why: top-level CLI guard must not crash raw on any curses/runtime error
        print(f"❌ Erro: {e}")  # noqa: T201 -- CLI stderr-equivalent output
        sys.exit(1)


if __name__ == "__main__":
    main()
