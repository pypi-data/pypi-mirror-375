
# --- Top-level imports ---
from typing import List, Dict, Optional
import threading
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule
from aiebash.formatter_text import annotate_bash_blocks
from aiebash.progress import run_progress
from aiebash.script_executor import run_bash_block

def _render_answer(console: Console, answer: str, run_mode: bool) -> List[str]:
    """Отрисовать ответ AI. При run_mode=True нумеруем bash-блоки, иначе просто показываем текст.
    Возвращает список bash-блоков (только при run_mode=True), иначе пустой список.
    """
    console.print("[bold blue]AI:[/bold blue]")
    if run_mode:
        annotated_answer, code_blocks = annotate_bash_blocks(answer)
        console.print(Markdown(annotated_answer))
        return code_blocks
    else:
        console.print(Markdown(answer))
        return []

def chat_loop(console: Console, llm_client, context: str, run_mode: bool, first_prompt: Optional[str]) -> None:
    """Простой чат с ИИ.
    - run_mode=False: просто переписка, блоки не нумеруются, запуск не возможен.
    - run_mode=True: блоки нумеруются; если вводится число N, выполняется блок N;
      при неверном номере выводится предупреждение; далее снова ожидается ввод.
    """
    messages: List[Dict[str, str]] = []
    if context:
        messages.append({"role": "system", "content": context})

    stop_event = threading.Event()
    code_blocks: List[str] = []

    # Первый вопрос
    if first_prompt:
        messages.append({"role": "user", "content": first_prompt})
        stop_event.clear()
        progress_thread = threading.Thread(target=run_progress, args=(stop_event,))
        progress_thread.start()
        answer: str = llm_client.send_chat(messages)
        stop_event.set()
        progress_thread.join()
        messages.append({"role": "assistant", "content": answer})
        code_blocks = _render_answer(console, answer, run_mode)

    # Основной цикл
    while True:
        try:
            user_input: str = console.input("[bold green]Вы:[/bold green] ")
            stripped = user_input.strip()
            if stripped.lower() in ("exit", "quit", "выход"):
                break

            # Если режим запуска включен и введено число — попытка запуска блока
            if run_mode and stripped.isdigit():
                idx = int(stripped)
                if 1 <= idx <= len(code_blocks):
                    run_bash_block(console, code_blocks, idx)
                else:
                    console.print("[yellow]Нет такого блока. Введите номер из списка или текстовый запрос.[/yellow]")
                continue  # Возвращаемся к вводу промпта

            # Обычное сообщение пользователя
            messages.append({"role": "user", "content": user_input})
            stop_event.clear()
            progress_thread = threading.Thread(target=run_progress, args=(stop_event,))
            progress_thread.start()
            try:
                answer = llm_client.send_chat(messages)
            except Exception as e:
                stop_event.set()
                progress_thread.join()
                msg = str(e)
                if "HTTPSConnectionPool" in msg:
                    console.print("[yellow]Нет соединения с интернетом или сервером API. Проверьте сеть и настройки.[/yellow]")
                elif "403 Client Error: Forbidden" in msg:
                    console.print("[yellow]Попробуйте через некоторе время. Если ошибка повторяется - проверьте ключ API, права или лимиты.[/yellow]")
                elif "429 Client Error: Too Many Requests" in msg:
                    console.print("[yellow]Слишком много запросов. Попробуйте позже.[/yellow]")
                else:
                    console.print(f"[yellow]Ошибка: {e}[/yellow]")
                break
            stop_event.set()
            progress_thread.join()
            messages.append({"role": "assistant", "content": answer})
            code_blocks = _render_answer(console, answer, run_mode)

        except KeyboardInterrupt:
            stop_event.set()
            progress_thread.join()
            console.print("\n")
            break
