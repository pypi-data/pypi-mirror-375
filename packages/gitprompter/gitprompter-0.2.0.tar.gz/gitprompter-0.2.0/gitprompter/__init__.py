"""gitprompter"""
from gitprompter.config import GitPrompterConfig
from gitprompter.core import GitDiffProcessor
from gitprompter.prompts import Prompt

config = GitPrompterConfig()
processor = GitDiffProcessor(
    config=config,
    prompt=Prompt(config)
)