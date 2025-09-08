import subprocess
import sys
from typing import Optional

import click

from gitprompter import utils, GitPrompterConfig
from gitprompter.prompts import Prompt


class GitDiffProcessor:
    """
    Класс для обработки git diff и создания промптов на основе изменений.

    Обеспечивает унифицированный интерфейс для работы с git diff, git diff --cached,
    и сравнения между ветками с обработкой ошибок и логированием.

    """

    BASE_PARAMS = {
        'capture_output': True,
        'text': True,
        'encoding': 'utf-8',
        'errors': 'replace',  # Обработка проблем с кодировкой
        'shell': sys.platform == 'win32',  # Используем shell=True только на Windows
    }

    def __init__(self, config: GitPrompterConfig, prompt: Prompt):
        self.config = config
        self.prompt = prompt

    def _run_git_command(self, commands: list[str]) -> Optional[str]:
        """
        Выполняет git команду и обрабатывает ошибки.

        Args:
            commands: Список аргументов команды git

        Returns:
            Стандартный вывод команды или None в случае ошибки
        """
        result = subprocess.run(commands, **self.BASE_PARAMS)

        if result.returncode != 0:
            command_text = ' '.join(commands)
            click.secho(f"Ошибка при выполнении '{command_text}':", fg="red")
            click.secho(result.stderr, fg="red")
            return None

        return result.stdout

    def _get_branch_range(self, since: str) -> str:
        current_branch = self._run_git_command(
            ['git', 'symbolic-ref', '--short', 'HEAD']
        )

        if current_branch is None:
            raise ValueError('No current branch found.')

        current_branch_name = current_branch.strip()
        if since == current_branch_name:
            return since
        else:
            return f"{since}..{current_branch_name}"

    def _process_prompt(self, diff_text: str, command: str) -> None:
        """
        Создает промпт на основе diff текста и копирует в буфер.

        Args:
            diff_text: Текст diff для обработки
            command: Описание для логирования
        """
        cleaned_text = utils.clean_git_diff(diff_text)
        utils.log_text_info(cleaned_text, command)
        prompt = self.prompt.make(command, cleaned_text)
        click.secho() # empty line
        if self.config.to_file:
            utils.write_to_txt(prompt)
        else:
            utils.copy_to_buffer(prompt)

    def create_diff_prompt(self) -> None:
        """
        Создает промпт на основе git diff и git diff --cached.

        Объединяет изменения в рабочей директории и индексированные изменения
        в единый промпт для коммита.
        """
        result = self._run_git_command(['git', 'diff'])
        result_cached = self._run_git_command(['git', 'diff', '--cached'])

        if result is None or result_cached is None:
            return

        self._process_prompt(result + result_cached, 'git diff + git diff --cached')

    def create_branch_comments_prompt(self, since: str) -> None:
        """
        Создает промпт на основе истории коммитов между ветками.

        Args:
            since: Имя ветки/тега/коммита для сравнения истории
        """

        command = ['git', 'log', self._get_branch_range(since)]

        result = self._run_git_command(
            command
        )

        if result is not None:
            self._process_prompt(
                result,
                ' '.join(command),
            )