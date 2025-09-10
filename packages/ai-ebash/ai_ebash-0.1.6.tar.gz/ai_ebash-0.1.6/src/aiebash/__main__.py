#!/usr/bin/env python3
import sys
import threading
import time
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

# sys.path, как раньше
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aiebash.llm_factory import create_llm_client
from aiebash.formatter_text import annotate_bash_blocks
from aiebash.block_runner import run_code_selection
from aiebash.settings import settings

# Получаем настройки для конкретного бэкенда, например 'openai_over_proxy'
BACKEND = "openai_over_proxy"

MODEL = settings.get(BACKEND, "MODEL")
API_URL = settings.get(BACKEND, "API_URL")
API_KEY = settings.get(BACKEND, "API_KEY")

# Глобальные настройки
DEBUG = settings.get_bool("global", "DEBUG")
CONTEXT = settings.get("global", "CONTEXT")

# Клиент
llm_client = create_llm_client(
    backend=BACKEND,
    model=MODEL,
    api_url=API_URL,
    api_key=API_KEY,
)

# Управление прогрессом
stop_event = threading.Event()
def run_progress():
    console = Console()
    with console.status("[bold green]Ai печатает...[/bold green]", spinner="dots"):
        while not stop_event.is_set():
            time.sleep(0.1)


def main():
    if len(sys.argv) < 2:
        print("Использование: ai [-run] [-chat] ваш запрос к ИИ без кавычек")
        sys.exit(0)

    console = Console()

    # Режимы
    run_mode = "-run" in sys.argv
    chat_mode = "-chat" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("-run", "-chat")]

    prompt = " ".join(args)

    try:
        if chat_mode:
            # Диалоговый режим
            console.print(Rule(" Вход в чатовый режим ", style="cyan"))
            messages = []
            if CONTEXT:
                messages.append({"role": "system", "content": CONTEXT})

            while True:
                user_input = console.input("[bold green]Вы:[/bold green] ")
                if user_input.strip().lower() in ("exit", "quit", "выход"):
                    break

                messages.append({"role": "user", "content": user_input})

                stop_event.clear()
                progress_thread = threading.Thread(target=run_progress)
                progress_thread.start()

                answer = llm_client.send_chat(messages)

                stop_event.set()
                progress_thread.join()

                messages.append({"role": "assistant", "content": answer})
                console.print(Markdown(answer))
                console.print(Rule("", style="green"))

        else:
            # Обычный режим (один вопрос → один ответ)
            stop_event.clear()
            progress_thread = threading.Thread(target=run_progress)
            progress_thread.start()

            answer = llm_client.send_prompt(prompt, system_context=CONTEXT)

            stop_event.set()
            progress_thread.join()

            if DEBUG:
                print("=== RAW RESPONSE ===")
                print(answer)
                print("=== /RAW RESPONSE ===")

            annotated_answer, code_blocks = annotate_bash_blocks(answer)

            if run_mode and code_blocks:
                console.print(Markdown(annotated_answer))
                run_code_selection(console, code_blocks)
            else:
                console.print(Markdown(answer))

            console.print(Rule("", style="green"))

    except Exception as e:
        print("Ошибка:", e)


if __name__ == "__main__":
    main()
