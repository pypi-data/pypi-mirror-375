from gitprompter import GitPrompterConfig


class Prompt:
    def __init__(self, config: GitPrompterConfig):
        self.config = config

    def _answer_format(self) -> str:
        return f'Please write your ANSWER in either "code" or "plaintext" format, using the "{self.config.language}" language.'

    def _style_text(self) -> str:
        match self.config.style:
            case "feature":
                text = (
                    "[a brief title summarizing the main idea]\n\n"
                    "[list of changes (each starting with a dash)]\n"
                )
            case "conventional":
                text = (
                    "<type>[optional scope]: <short summary>\n\n"
                    "[optional detailed description]\n\n"
                    "[optional footer(s)]\n\n"
                    "Where:\n"
                    "- type is one of feat, fix, refactor, docs, style, perf, test, build, ci, chore, revert\n"
                    "- scope is optional and indicates the area of code affected\n"
                    "- short summary is a brief imperative description\n"
                    "- detailed description explains the changes and motivations\n"
                    "- footer may contain BREAKING CHANGE notes\n\n"
                )
            case 'custom':
                raise NotImplementedError
            case _:
                raise ValueError('Unknown style')

        return text

    def make(self, command: str, result: str, ) -> str:
        text: list[str] = [
            "Task:",
            "Write a comment following this structure:",
            self._style_text(),
            self._answer_format(),
            f'Result of the "{command}" command:',
            result
        ]

        return '\n'.join(text)