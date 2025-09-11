
from aiebash.script_executor import run_bash_block
from rich.console import Console

def run_code_selection(console: Console, code_blocks: list):
    """
    Интерактивный выбор и запуск bash-блоков.
    Вводите номер блока для выполнения, 0/q/exit — выход.
    """
    while True:
        try:
            choice = console.input("[blue]\nВведите номер блока для запуска (0 — выход): [/blue]").strip()
            if choice.lower() in ("0", "q", "exit"):
                break
            if not choice.isdigit():
                console.print("[red]Введите номер блока или 0 для выхода.[/red]")
                continue
            idx = int(choice)
            if not (1 <= idx <= len(code_blocks)):
                console.print(f"[red]Нет такого блока. Всего: {len(code_blocks)}.[/red]")
                continue
            run_bash_block(console, code_blocks[idx - 1], idx)
        except (EOFError, KeyboardInterrupt):
            break