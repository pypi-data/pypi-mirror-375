import subprocess
from rich.console import Console

def run_bash_block(console: Console, code: str, idx: int) -> None:
    """
    Печатает номер и содержимое блока, выполняет его и выводит результат.
    """
    console.print(f"\n>>> Выполняем блок #{idx}:", style="blue")
    console.print(code)
    try:
        result = subprocess.run(code, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            console.print(f"[green]Out:[/green]\n{result.stdout}")
        if result.stderr:
            console.print(f"[red]Error:[/red]\n{result.stderr}")
    except Exception as e:
        console.print(f"[red]Ошибка выполнения скрипта: {e}[/red]")