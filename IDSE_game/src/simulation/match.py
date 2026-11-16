"""A 90-second fictional match with moving players, a ball, and score events."""

from __future__ import annotations

import random
import math


class Match:
    """Simulate a fictional match over 90 real seconds."""

    DURATION = 90.0

    def __init__(self, home_probability: float) -> None:
        self.elapsed = 0.0
        self.home_probability = home_probability
        self.home_goals = 0
        self.away_goals = 0
        self.rng = random.Random(731)
        self.next_event = 5.0
        self.next_pass = 1.2
        self.finished = False
        self.possession_home = True
        self.home_formation = [
            (0.08, .50), (.22, .22), (.22, .50), (.22, .78),
            (.39, .25), (.39, .50), (.39, .75), (.60, .22),
            (.60, .50), (.60, .78), (.79, .50),
        ]
        self.away_formation = [(1 - x, y) for x, y in self.home_formation]
        self.home_players = list(self.home_formation)
        self.away_players = list(self.away_formation)
        self.ball = (.50, .50)
        self.ball_target = (.50, .50)
        self.ball_reset = 0.0

    @property
    def minute(self) -> int:
        """Map ninety real seconds to a ninety-minute match clock."""
        return min(90, int(self.elapsed))

    def update(self, delta: float) -> None:
        """Advance the clock and create a short fictional match event."""
        if self.finished:
            return
        self.elapsed = min(self.DURATION, self.elapsed + delta)
        self._move_players()
        if self.elapsed >= self.next_pass and self.ball_reset <= 0:
            self._pass_ball()
            self.next_pass += self.rng.uniform(1.4, 2.5)
        self._move_ball(delta)
        if self.elapsed >= self.next_event and self.elapsed < self.DURATION:
            self._event()
            self.next_event += self.rng.uniform(6.0, 11.0)
        if self.elapsed >= self.DURATION:
            self.finished = True

    def _move_players(self) -> None:
        """Animate both teams around their formations in normalized pitch space."""
        phase = self.elapsed * 1.7
        for team_index, (formation, positions) in enumerate((
            (self.home_formation, self.home_players),
            (self.away_formation, self.away_players),
        )):
            direction = 1 if team_index == 0 else -1
            for index, (base_x, base_y) in enumerate(formation):
                offset = phase + index * .83 + team_index * 1.3
                positions[index] = (
                    max(.04, min(.96, base_x + direction * .025 * math.sin(offset))),
                    max(.08, min(.92, base_y + .055 * math.sin(offset * .73))),
                )

    def _move_ball(self, delta: float) -> None:
        """Move the ball smoothly toward the next shot or pass target."""
        if self.ball_reset > 0:
            self.ball_reset = max(0.0, self.ball_reset - delta)
            if self.ball_reset == 0:
                self.ball_target = (.50, .50)
        blend = min(1.0, max(0.0, delta) * 1.8)
        x, y = self.ball
        tx, ty = self.ball_target
        self.ball = (x + (tx - x) * blend, y + (ty - y) * blend)

    def _pass_ball(self) -> None:
        """Pass between nearby teammates so the ball keeps moving on screen."""
        players = self.home_players if self.possession_home else self.away_players
        bx, by = self.ball
        nearest = min(
            range(len(players)),
            key=lambda index: (players[index][0] - bx) ** 2 + (players[index][1] - by) ** 2,
        )
        nearby = sorted(
            (index for index in range(len(players)) if index != nearest),
            key=lambda index: (players[index][0] - players[nearest][0]) ** 2
            + (players[index][1] - players[nearest][1]) ** 2,
        )[:5]
        receiver = players[self.rng.choice(nearby)]
        self.ball_target = receiver

    def _event(self) -> None:
        """Create a shot, goal, or possession event using forecast strength."""
        home_attacks = self.rng.random() < self.home_probability
        self.possession_home = home_attacks
        target_x = self.rng.uniform(.62, .91) if home_attacks else self.rng.uniform(.09, .38)
        self.ball_target = (target_x, self.rng.uniform(.22, .78))
        if self.rng.random() < 0.19:
            if home_attacks:
                self.home_goals += 1
            else:
                self.away_goals += 1
            self.ball_reset = .8
