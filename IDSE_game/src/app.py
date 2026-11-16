"""Pygame application and first playable career level."""

from __future__ import annotations

import pygame

from src.data_processing.dataset import sample_rows
from src.gameplay.session import Session
from src.ml.predictor import forecast
from src.save.profile import Profile
from src.simulation.match import Match
from src.ui import components as ui


class Game:
    """Own the game state and route input between the career screens."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Touchline Data | Football & Data Science")
        self.fullscreen = True
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.profile = Profile.load()
        self.session = Session()
        self.page = "menu"
        self.running = True
        self.match: Match | None = None
        self.prediction = None
        self.result: dict | None = None
        self.selected_bet = "home"
        self.stake = 500
        self.toast = ""

    def start_level(self) -> None:
        """Start the Cleaning lesson with a fresh fictional match."""
        self.session = Session()
        self.prediction = None
        self.match = None
        self.result = None
        self.page = "tutorial"

    def toggle_fullscreen(self) -> None:
        """Switch between full-screen play and a resizable desktop window."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

    def handle_click(self, pos: tuple[int, int]) -> None:
        """Apply a mouse click to the active screen."""
        w, h = self.screen.get_size()
        if self.page == "menu":
            if ui.button_rect(w, h, 0).collidepoint(pos):
                self.page = "career"
            elif ui.button_rect(w, h, 1).collidepoint(pos):
                self.page = "tutorial_info"
            elif ui.button_rect(w, h, 2).collidepoint(pos):
                self.page = "settings"
            elif ui.button_rect(w, h, 3).collidepoint(pos):
                self.running = False
        elif self.page in ("career", "tutorial_info", "settings"):
            if ui.back_rect(w, h).collidepoint(pos):
                self.page = "menu"
            elif self.page == "career" and ui.button_rect(w, h, 0).collidepoint(pos):
                self.start_level()
        elif self.page == "tutorial":
            if ui.back_rect(w, h).collidepoint(pos):
                self.page = "career"
            elif ui.primary_rect(w, h).collidepoint(pos):
                self.page = "cleaning"
        elif self.page == "cleaning":
            if ui.back_rect(w, h).collidepoint(pos):
                self.page = "tutorial"
            else:
                for index in range(3):
                    if ui.answer_rect(w, h, index).collidepoint(pos):
                        self.session.answer(index)
                        if self.session.answered:
                            self.prediction = forecast()
                            self.page = "forecast"
                        break
        elif self.page == "forecast":
            if ui.back_rect(w, h).collidepoint(pos):
                self.page = "cleaning"
            elif ui.primary_rect(w, h).collidepoint(pos):
                self.page = "betting"
        elif self.page == "betting":
            if ui.back_rect(w, h).collidepoint(pos):
                self.page = "forecast"
            elif ui.bet_team_rect(w, h, 0).collidepoint(pos):
                self.selected_bet = "home"
            elif ui.bet_team_rect(w, h, 1).collidepoint(pos):
                self.selected_bet = "away"
            elif ui.stake_rect(w, h, -1).collidepoint(pos):
                self.stake = max(100, self.stake - 500)
            elif ui.stake_rect(w, h, 1).collidepoint(pos):
                self.stake = min(2000, self.stake + 500, self.profile.balance)
            elif ui.primary_rect(w, h).collidepoint(pos) and self.profile.balance >= self.stake:
                self.profile.balance -= self.stake
                self.profile.save()
                self.match = Match(self.prediction.home_probability)
                self.page = "match"
            elif ui.primary_rect(w, h).collidepoint(pos):
                self.toast = "Choose a stake within your available balance."
        elif self.page == "match":
            if ui.primary_rect(w, h).collidepoint(pos) and self.match and self.match.finished:
                self.finish_match()
        elif self.page == "results":
            if ui.primary_rect(w, h).collidepoint(pos):
                self.page = "career"
            elif ui.back_rect(w, h).collidepoint(pos):
                self.page = "menu"

    def finish_match(self) -> None:
        """Settle the fictional match and persist career progress."""
        assert self.match is not None
        won = (self.selected_bet == "home" and self.match.home_goals > self.match.away_goals) or (
            self.selected_bet == "away" and self.match.away_goals > self.match.home_goals
        )
        payout = self.stake * 2 if won else 0
        self.profile.balance += payout
        self.profile.levels_completed = max(self.profile.levels_completed, 1)
        self.profile.matches_played += 1
        self.profile.save()
        self.result = {"won": won, "payout": payout, "profit": payout - self.stake}
        self.page = "results"

    def handle_key(self, key: int) -> None:
        """Offer keyboard navigation for every primary action and back route."""
        if key == pygame.K_F11:
            self.toggle_fullscreen()
        elif key == pygame.K_ESCAPE and self.page == "match" and self.fullscreen:
            self.toggle_fullscreen()
        elif key == pygame.K_ESCAPE:
            self.page = {
                "career": "menu",
                "tutorial_info": "menu",
                "settings": "menu",
                "tutorial": "career",
                "cleaning": "tutorial",
                "forecast": "cleaning",
                "betting": "forecast",
                "results": "menu",
            }.get(self.page, self.page)
        elif self.page == "cleaning" and key in (pygame.K_1, pygame.K_2, pygame.K_3):
            w, h = self.screen.get_size()
            self.handle_click(ui.answer_rect(w, h, key - pygame.K_1).center)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            next_page = {
                "menu": "career",
                "career": "tutorial",
                "tutorial": "cleaning",
                "forecast": "betting",
                "results": "career",
                "tutorial_info": "menu",
                "settings": "menu",
            }.get(self.page)
            if next_page == "tutorial":
                self.start_level()
            elif next_page:
                self.page = next_page
            elif self.page == "betting":
                w, h = self.screen.get_size()
                self.handle_click(ui.primary_rect(w, h).center)
            elif self.page == "match" and self.match and self.match.finished:
                self.finish_match()

    def draw(self) -> None:
        """Render the active screen at the current window size."""
        w, h = self.screen.get_size()
        self.screen.fill(ui.BG)
        if self.page == "match" and self.match:
            self.match.update(self.clock.get_time() / 1000)
            ui.draw_match(self.screen, self.match)
            ui.footer(self.screen, "F11 / ESC  WINDOWED" if self.fullscreen else "F11  FULL SCREEN")
        else:
            ui.header(self.screen, self.profile.balance, "CAREER MODE" if self.page != "menu" else "OFFLINE SEASON")
        if self.page == "match":
            pass
        elif self.page == "menu":
            ui.draw_menu(self.screen, self.profile)
        elif self.page == "career":
            ui.draw_career(self.screen, self.profile)
        elif self.page == "tutorial_info":
            ui.draw_tutorial_info(self.screen)
        elif self.page == "settings":
            ui.draw_settings(self.screen)
        elif self.page == "tutorial":
            ui.draw_lesson(self.screen)
        elif self.page == "cleaning":
            ui.draw_cleaning(self.screen, self.session, sample_rows())
        elif self.page == "forecast":
            ui.draw_forecast(self.screen, self.prediction, self.session)
        elif self.page == "betting":
            ui.draw_betting(self.screen, self.prediction, self.stake, self.selected_bet, self.profile.balance)
        elif self.page == "results":
            ui.draw_results(self.screen, self.match, self.result, self.profile)
        if self.page != "match" and self.page not in ("menu", "career", "tutorial_info", "settings"):
            ui.footer(self.screen, "ESC  BACK   •   ENTER  CONTINUE")
        if self.toast:
            ui.draw_toast(self.screen, self.toast)
            self.toast = ""

    def run(self) -> None:
        """Run the event loop until the player exits."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


def run() -> None:
    """Create and run the game."""
    Game().run()
