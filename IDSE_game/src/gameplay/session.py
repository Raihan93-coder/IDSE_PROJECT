"""State for the first data-cleaning mini-game."""

from src.data_processing.dataset import clean_history, generate_history


class Session:
    """Keep challenge answer state and the cleaned dataset."""

    def __init__(self) -> None:
        self.records = generate_history()
        self.answer_index: int | None = None
        self.answered = False
        self.cleaned = []

    def answer(self, index: int) -> None:
        """Submit one of three data-cleaning strategies."""
        self.answer_index = index
        self.answered = True
        if index == 1:
            self.cleaned = clean_history(self.records)

    @property
    def correct(self) -> bool:
        """Whether the learner selected the robust cleaning workflow."""
        return self.answer_index == 1
