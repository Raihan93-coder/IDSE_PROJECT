"""Reusable shapes, typography, and screen layouts for Touchline Data."""

from __future__ import annotations

import pygame

BG = (13, 23, 39)
SURFACE = (23, 37, 56)
SURFACE_2 = (31, 49, 69)
WHITE = (241, 246, 249)
MUTED = (158, 177, 191)
GREEN = (92, 210, 143)
GOLD = (255, 196, 82)
RED = (239, 118, 111)
BLUE = (99, 175, 255)


def font(size: int, bold: bool = False) -> pygame.font.Font:
    """Return a system font with consistent weight."""
    return pygame.font.SysFont("dejavusans", size, bold=bold)


def text(surface: pygame.Surface, value: str, x: int, y: int, size: int = 20,
         color: tuple[int, int, int] = WHITE, bold: bool = False) -> None:
    """Draw one line of interface text."""
    surface.blit(font(size, bold).render(value, True, color), (x, y))


def panel(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int] = SURFACE,
          radius: int = 18, border: tuple[int, int, int] | None = None) -> None:
    """Draw a rounded card with an optional quiet border."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, width=1, border_radius=radius)


def button(surface: pygame.Surface, rect: pygame.Rect, label: str, primary: bool = False,
           disabled: bool = False) -> None:
    """Draw a button with a high contrast label."""
    color = (48, 69, 86) if disabled else ((GREEN if primary else SURFACE_2))
    label_color = BG if primary and not disabled else WHITE
    pygame.draw.rect(surface, color, rect, border_radius=12)
    size = 15 if len(label) > 46 else 18
    text(surface, label, rect.x + 18, rect.y + (rect.height - size - 8) // 2, size, label_color, True)


def wrapped(surface: pygame.Surface, value: str, x: int, y: int, width: int,
            size: int = 18, color: tuple[int, int, int] = MUTED, line_gap: int = 8) -> int:
    """Draw wrapped body copy and return its final vertical position."""
    words = value.split()
    line = ""
    line_y = y
    for word in words:
        candidate = f"{line} {word}".strip()
        if font(size).size(candidate)[0] > width and line:
            text(surface, line, x, line_y, size, color)
            line_y += size + line_gap
            line = word
        else:
            line = candidate
    if line:
        text(surface, line, x, line_y, size, color)
        line_y += size + line_gap
    return line_y


def button_rect(w: int, h: int, index: int) -> pygame.Rect:
    """Return a menu button rectangle."""
    return pygame.Rect(w // 2 - 135, int(h * .53) + index * 58, 270, 46)


def primary_rect(w: int, h: int) -> pygame.Rect:
    """Return the primary action button rectangle."""
    return pygame.Rect(w - 280, h - 94, 220, 50)


def back_rect(w: int, h: int) -> pygame.Rect:
    """Return the persistent back button rectangle."""
    return pygame.Rect(42, h - 94, 160, 50)


def answer_rect(w: int, h: int, index: int) -> pygame.Rect:
    """Return one multiple-choice answer rectangle."""
    return pygame.Rect(w // 2 - 350, int(h * .65) + index * 58, 700, 48)


def bet_team_rect(w: int, h: int, index: int) -> pygame.Rect:
    """Return a team selection rectangle on the betting screen."""
    return pygame.Rect(w // 2 - 330 + index * 345, int(h * .47), 320, 70)


def stake_rect(w: int, h: int, direction: int) -> pygame.Rect:
    """Return a stake adjustment button rectangle."""
    return pygame.Rect(w // 2 - 135 + (direction > 0) * 205, int(h * .65), 62, 50)


def header(surface: pygame.Surface, balance: int, label: str) -> None:
    """Draw persistent game branding and player balance."""
    w, _ = surface.get_size()
    pygame.draw.rect(surface, (17, 30, 47), (0, 0, w, 72))
    pygame.draw.rect(surface, GREEN, (0, 70, w, 2))
    text(surface, "TOUCHLINE", 38, 18, 22, WHITE, True)
    text(surface, "DATA", 158, 18, 22, GREEN, True)
    text(surface, label, 245, 24, 13, MUTED, True)
    text(surface, f"₹ {balance:,}", w - 190, 21, 20, GOLD, True)


def footer(surface: pygame.Surface, label: str) -> None:
    """Draw a concise keyboard hint."""
    w, h = surface.get_size()
    text(surface, label, 42, h - 34, 13, MUTED, True)


def title(surface: pygame.Surface, eyebrow: str, heading: str, subtitle: str) -> None:
    """Draw the standard screen title block."""
    w, _ = surface.get_size()
    text(surface, eyebrow.upper(), 60, 105, 13, GREEN, True)
    text(surface, heading, 60, 132, 34, WHITE, True)
    text(surface, subtitle, 60, 180, 17, MUTED)


def draw_menu(surface: pygame.Surface, profile) -> None:
    """Draw the game's launch screen."""
    w, h = surface.get_size()
    kicker = font(18, True).render("THE DATA-DRIVEN", True, GREEN)
    surface.blit(kicker, (w // 2 - kicker.get_width() // 2, int(h * .19)))
    heading = font(56, True).render("MATCHDAY", True, WHITE)
    surface.blit(heading, (w // 2 - heading.get_width() // 2, int(h * .25)))
    sub = font(19).render("Learn data science. Read the game. Lead your club.", True, MUTED)
    surface.blit(sub, (w // 2 - sub.get_width() // 2, int(h * .39)))
    pygame.draw.line(surface, (51, 83, 91), (w // 2 - 250, int(h * .47)), (w // 2 + 250, int(h * .47)), 2)
    for idx, label in enumerate(("CAREER", "HOW TO PLAY", "SETTINGS", "EXIT")):
        button(surface, button_rect(w, h, idx), label, idx == 0)
    text(surface, f"LEVELS CLEARED  {profile.levels_completed}/7     MATCHES  {profile.matches_played}",
         w // 2 - 190, h - 44, 13, MUTED, True)


def draw_career(surface: pygame.Surface, profile) -> None:
    """Show the seven learning milestones and the available first level."""
    w, h = surface.get_size()
    title(surface, "CAREER / SEASON 01", "Build your matchday edge", "Clear each data-science level to unlock the next league.")
    names = ["Cleaning", "EDA", "Statistics", "Visualization", "Regression", "Classification", "Clustering"]
    descriptions = ["Repair a messy match log", "Explore patterns in club form", "Compare mean and spread",
                    "Read a matchday chart", "Estimate expected goals", "Classify match outcomes", "Group similar clubs"]
    for i, (name, desc) in enumerate(zip(names, descriptions)):
        x = 60 + (i % 4) * (w - 120) // 4
        y = 240 + (i // 4) * 145
        rect = pygame.Rect(x, y, (w - 160) // 4, 118)
        is_open = i == 0 or i < profile.levels_completed
        panel(surface, rect, SURFACE if is_open else (19, 30, 44), border=GREEN if i == 0 else None)
        text(surface, f"0{i + 1}", x + 17, y + 15, 14, GREEN if is_open else MUTED, True)
        text(surface, name.upper() if is_open else "LOCKED", x + 17, y + 40, 18, WHITE if is_open else MUTED, True)
        text(surface, desc if is_open else "Clear the level before this one.", x + 17, y + 75, 13, MUTED)
    button(surface, button_rect(w, h, 0), "START CLEANING", True)
    button(surface, back_rect(w, h), "BACK")


def draw_tutorial_info(surface: pygame.Surface) -> None:
    """Explain the offline learning and matchday loop."""
    w, h = surface.get_size()
    title(surface, "FIELD GUIDE", "How to play", "Every match starts with evidence, then asks you to make a call.")
    steps = [("01", "LEARN", "Get a short lesson on a data-science idea."),
             ("02", "INVESTIGATE", "Clean or inspect fictional match records."),
             ("03", "PREDICT", "Review a fixed offline model and its inputs."),
             ("04", "MATCHDAY", "Choose a fictional outcome and watch a 90-second match.")]
    for i, (num, label, desc) in enumerate(steps):
        y = 240 + i * 82
        panel(surface, pygame.Rect(120, y, w - 240, 66))
        text(surface, num, 145, y + 19, 16, GREEN, True)
        text(surface, label, 205, y + 12, 16, WHITE, True)
        text(surface, desc, 205, y + 36, 14, MUTED)
    button(surface, back_rect(w, h), "BACK")


def draw_settings(surface: pygame.Surface) -> None:
    """Explain the intentionally small offline settings screen."""
    w, h = surface.get_size()
    title(surface, "PREFERENCES", "Settings", "The first build keeps the matchday experience simple.")
    panel(surface, pygame.Rect(80, 245, w - 160, 125))
    text(surface, "DISPLAY", 110, 270, 17, WHITE, True)
    text(surface, "Resizable window  •  Keyboard and mouse input  •  60 FPS cap", 110, 312, 16, MUTED)
    text(surface, "All club, match and save data stays on this device.", 110, 347, 14, GREEN)
    button(surface, back_rect(w, h), "BACK")


def draw_lesson(surface: pygame.Surface) -> None:
    """Introduce missing values, duplicates, invalid entries and medians."""
    w, h = surface.get_size()
    title(surface, "LEVEL 01 / CLEANING", "A clean sheet starts with clean data", "Match logs are collected by people. Real datasets need a quick audit.")
    panel(surface, pygame.Rect(70, 245, w - 140, 210))
    text(surface, "TODAY'S TOOLKIT", 100, 270, 14, GREEN, True)
    items = [("MISSING", "Fill shots with the median instead of guessing."),
             ("DUPLICATE", "Keep one copy of a repeated match record."),
             ("INVALID", "Reject impossible values, such as −3 goals.")]
    for i, (tag, desc) in enumerate(items):
        x = 105 + i * ((w - 260) // 3)
        text(surface, tag, x, 315, 13, GOLD, True)
        wrapped(surface, desc, x, 341, (w - 300) // 3, 16)
    panel(surface, pygame.Rect(70, 474, w - 140, 74), (32, 55, 64))
    text(surface, "THE GOAL", 95, 490, 12, GREEN, True)
    text(surface, "Keep useful rows, make missing values explicit, and document each choice.", 95, 514, 17, WHITE)
    button(surface, back_rect(w, h), "BACK")
    button(surface, primary_rect(w, h), "START CHALLENGE", True)


def draw_cleaning(surface: pygame.Surface, session, rows: list[dict[str, object]]) -> None:
    """Present the dirty table and cleaning strategy choices."""
    w, h = surface.get_size()
    title(surface, "LEVEL 01 / MINI-GAME", "Audit the match log", "This generated dataset has a blank, a duplicate, an odd label and an impossible score.")
    x, y = 70, 235
    panel(surface, pygame.Rect(x, y, w - 140, 190))
    headers = ("CLUB", "SHOTS", "GOALS", "DATA CHECK")
    col_x = [x + 24, x + 310, x + 490, x + 650]
    for label, cx in zip(headers, col_x):
        text(surface, label, cx, y + 17, 12, MUTED, True)
    for i, row in enumerate(rows[:5]):
        ry = y + 48 + i * 27
        club = str(row["club"])
        shots, goals = row["shots"], row["goals"]
        issue = "MISSING SHOTS" if shots is None else ("CHECK LABEL" if club != club.strip().title() else "—")
        color = GOLD if issue != "—" else MUTED
        text(surface, club[:22], col_x[0], ry, 14, WHITE)
        text(surface, "—" if shots is None else str(shots), col_x[1], ry, 14, GOLD if shots is None else WHITE)
        text(surface, str(goals), col_x[2], ry, 14, RED if int(goals) < 0 else WHITE)
        text(surface, issue, col_x[3], ry, 12, color)
        pygame.draw.line(surface, SURFACE_2, (x + 18, ry + 24), (w - 88, ry + 24), 1)
    text(surface, "A duplicate row and a negative goal count are also in the full file.", x + 22, y + 166, 12, MUTED)
    text(surface, "Which workflow gives you a trustworthy table?", 70, 450, 18, WHITE, True)
    choices = ["Replace every blank with zero and keep all rows",
               "Median-fill shots; standardize labels; remove duplicates and invalid goals",
               "Drop every row that is not already perfectly formatted"]
    for index, label in enumerate(choices):
        rect = answer_rect(w, h, index)
        button(surface, rect, f"{index + 1}    {label}", index == 1)
    button(surface, back_rect(w, h), "BACK")


def draw_forecast(surface: pygame.Surface, prediction, session) -> None:
    """Show the fixed pretrained prediction and explain its inputs."""
    w, h = surface.get_size()
    title(surface, "MODEL ROOM / OFFLINE", "What does the model expect?", "A preset logistic model estimates a home win from fictional historical features.")
    panel(surface, pygame.Rect(70, 245, w - 140, 205))
    probability = prediction.home_probability * 100
    text(surface, f"{probability:.0f}%", 105, 274, 54, GREEN, True)
    text(surface, "HOME WIN ESTIMATE", 108, 338, 14, MUTED, True)
    bx, by, bw, bh = 400, 300, w - 540, 28
    pygame.draw.rect(surface, SURFACE_2, (bx, by, bw, bh), border_radius=14)
    pygame.draw.rect(surface, GREEN, (bx, by, int(bw * prediction.home_probability), bh), border_radius=14)
    text(surface, "HOME FORM", bx, 259, 12, MUTED, True)
    text(surface, f"{prediction.home_form:.2f}", bx, 344, 17, WHITE, True)
    text(surface, "AWAY FORM", bx + 145, 259, 12, MUTED, True)
    text(surface, f"{prediction.away_form:.2f}", bx + 145, 344, 17, WHITE, True)
    text(surface, "HOME SHOT RATE", bx + 290, 259, 12, MUTED, True)
    text(surface, f"{prediction.home_shot_rate:.2f}", bx + 290, 344, 17, WHITE, True)
    wrapped(surface, "This is a probability estimate, not a promise. Features are scaled between 0 and 1; the fixed model is provided for inspection and is never trained in-game.",
            75, 482, w - 150, 16)
    feedback = "Cleaning workflow complete: missing shots were median-filled and invalid or repeated rows removed." if session.correct else "Before analysis, use median imputation, label normalization, deduplication and an invalid-value check."
    wrapped(surface, feedback, 75, 548, w - 150, 15, GREEN if session.correct else GOLD)
    button(surface, back_rect(w, h), "BACK")
    button(surface, primary_rect(w, h), "MATCHDAY", True)


def draw_betting(surface: pygame.Surface, prediction, stake: int, selected: str, balance: int) -> None:
    """Let the player choose a fictional match outcome and stake."""
    w, h = surface.get_size()
    title(surface, "MATCHDAY / YOUR CALL", "Choose your forecast", "This is a fictional classroom simulation. Your stake is deducted before kick-off.")
    teams = [("Harbor FC", "HOME", prediction.home_probability), ("Cedar Town", "AWAY", 1 - prediction.home_probability)]
    for index, (club, side, probability) in enumerate(teams):
        rect = bet_team_rect(w, h, index)
        chosen = selected == ("home" if index == 0 else "away")
        panel(surface, rect, (37, 66, 70) if chosen else SURFACE, border=GREEN if chosen else None)
        text(surface, side, rect.x + 20, rect.y + 12, 12, GREEN if chosen else MUTED, True)
        text(surface, club, rect.x + 20, rect.y + 32, 21, WHITE, True)
        text(surface, f"{probability * 100:.0f}% model estimate", rect.x + 20, rect.y + 55, 12, MUTED)
    text(surface, "STAKE", w // 2 - 105, int(h * .65) + 14, 13, MUTED, True)
    button(surface, stake_rect(w, h, -1), "−")
    text(surface, f"₹ {stake:,}", w // 2 - 45, int(h * .65) + 13, 20, GOLD, True)
    button(surface, stake_rect(w, h, 1), "+")
    text(surface, f"AVAILABLE  ₹ {balance:,}     WIN PAYOUT  ₹ {stake * 2:,}", w // 2 - 185, int(h * .65) + 68, 13, MUTED)
    button(surface, back_rect(w, h), "BACK")
    button(surface, primary_rect(w, h), "KICK OFF", True, balance < stake)


def draw_match(surface: pygame.Surface, match) -> None:
    """Render a full-screen animated match with player dots and a moving ball."""
    w, h = surface.get_size()
    pitch = pygame.Rect(30, 118, w - 60, h - 192)
    grass_a, grass_b = (33, 115, 76), (37, 124, 81)
    pygame.draw.rect(surface, grass_a, pitch)
    stripe_width = pitch.width // 10
    for stripe in range(10):
        if stripe % 2:
            pygame.draw.rect(
                surface, grass_b,
                (pitch.x + stripe * stripe_width, pitch.y, stripe_width, pitch.height),
            )

    line_color = (190, 224, 190)
    pygame.draw.rect(surface, line_color, pitch, 3)
    pygame.draw.line(surface, line_color, pitch.midtop, pitch.midbottom, 3)
    pygame.draw.circle(surface, line_color, pitch.center, min(92, pitch.height // 7), 3)
    box_h = int(pitch.height * .42)
    box_w = int(pitch.width * .14)
    small_h = int(pitch.height * .22)
    small_w = int(pitch.width * .055)
    pygame.draw.rect(surface, line_color, (pitch.left, pitch.centery - box_h // 2, box_w, box_h), 3)
    pygame.draw.rect(surface, line_color, (pitch.right - box_w, pitch.centery - box_h // 2, box_w, box_h), 3)
    pygame.draw.rect(surface, line_color, (pitch.left, pitch.centery - small_h // 2, small_w, small_h), 3)
    pygame.draw.rect(surface, line_color, (pitch.right - small_w, pitch.centery - small_h // 2, small_w, small_h), 3)

    def screen_point(position: tuple[float, float]) -> tuple[int, int]:
        """Map normalized simulation coordinates onto the pitch with a margin."""
        px, py = position
        return (
            int(pitch.x + 38 + px * (pitch.width - 76)),
            int(pitch.y + 30 + py * (pitch.height - 60)),
        )

    for team, color in ((match.home_players, (83, 178, 255)), (match.away_players, (255, 157, 101))):
        for jersey, position in enumerate(team, start=1):
            center = screen_point(position)
            pygame.draw.circle(surface, (16, 35, 32), center, 15)
            pygame.draw.circle(surface, color, center, 12)
            pygame.draw.circle(surface, (232, 245, 246), center, 12, 2)
            number = font(9, True).render(str(jersey), True, (11, 25, 36))
            surface.blit(number, (center[0] - number.get_width() // 2, center[1] - number.get_height() // 2))

    ball_x, ball_y = screen_point(match.ball)
    pygame.draw.circle(surface, (15, 37, 29), (ball_x + 2, ball_y + 3), 10)
    pygame.draw.circle(surface, (250, 250, 235), (ball_x, ball_y), 9)
    pygame.draw.polygon(surface, (35, 44, 43), [
        (ball_x, ball_y - 4), (ball_x + 4, ball_y - 1), (ball_x + 2, ball_y + 4),
        (ball_x - 3, ball_y + 3), (ball_x - 4, ball_y - 1),
    ])

    board = pygame.Rect(w // 2 - 250, 20, 500, 82)
    panel(surface, board, (13, 23, 39), radius=16, border=(69, 93, 94))
    text(surface, "HARBOR FC", board.x + 20, board.y + 29, 15, (106, 190, 255), True)
    score = font(30, True).render(f"{match.home_goals}  —  {match.away_goals}", True, WHITE)
    surface.blit(score, (w // 2 - score.get_width() // 2, board.y + 20))
    text(surface, "CEDAR TOWN", board.right - 132, board.y + 29, 15, (255, 174, 119), True)
    clock_label = f"{match.minute:02d}'" if match.minute < 90 else "90'"
    clock_surface = font(26, True).render(clock_label, True, GOLD)
    surface.blit(clock_surface, (board.x - 76, board.y + 25))
    text(surface, "90 MIN", board.x - 75, board.y + 51, 11, MUTED, True)

    remaining = max(0, 1 - match.elapsed / match.DURATION)
    pygame.draw.rect(surface, (21, 42, 48), (pitch.x + 16, pitch.bottom + 14, pitch.width - 32, 7), border_radius=4)
    pygame.draw.rect(surface, GOLD,
                     (pitch.x + 16, pitch.bottom + 14, int((pitch.width - 32) * (1 - remaining)), 7),
                     border_radius=4)
    if match.finished:
        panel(surface, pygame.Rect(w // 2 - 190, h // 2 - 62, 380, 112), (13, 23, 39), border=GOLD)
        label = font(24, True).render("FULL TIME", True, GOLD)
        surface.blit(label, (w // 2 - label.get_width() // 2, h // 2 - 46))
        button(surface, primary_rect(w, h), "FULL TIME / RESULTS", True)


def draw_results(surface: pygame.Surface, match, result: dict, profile) -> None:
    """Show score, settlement and learning takeaway."""
    w, h = surface.get_size()
    title(surface, "FINAL WHISTLE", "Match report", "A model estimate helps you reason about uncertainty; it cannot guarantee an outcome.")
    panel(surface, pygame.Rect(100, 245, w - 200, 220))
    score = f"HARBOR FC   {match.home_goals}  —  {match.away_goals}   CEDAR TOWN"
    score_surf = font(26, True).render(score, True, WHITE)
    surface.blit(score_surf, (w // 2 - score_surf.get_width() // 2, 280))
    status = "CALL CORRECT" if result["won"] else "CALL MISSED"
    status_color = GREEN if result["won"] else GOLD
    status_surf = font(20, True).render(status, True, status_color)
    surface.blit(status_surf, (w // 2 - status_surf.get_width() // 2, 343))
    text(surface, f"NET RESULT  ₹ {result['profit']:+,}       NEW BALANCE  ₹ {profile.balance:,}",
         w // 2 - 220, 392, 16, WHITE, True)
    wrapped(surface, "You practiced removing duplicate and impossible records. This fixed model forecast is based on historical features; probability is never certainty.",
            110, 505, w - 220, 16)
    button(surface, back_rect(w, h), "MAIN MENU")
    button(surface, primary_rect(w, h), "CAREER", True)


def draw_toast(surface: pygame.Surface, message: str) -> None:
    """Show temporary inline feedback at the bottom of the screen."""
    w, h = surface.get_size()
    panel(surface, pygame.Rect(w // 2 - 230, h - 155, 460, 45), (75, 48, 47), radius=10)
    text(surface, message, w // 2 - 210, h - 142, 13, WHITE)
