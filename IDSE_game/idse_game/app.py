"""Pygame interface for the educational round flow."""
from __future__ import annotations
import random
import pygame
import pygame_gui
from .world import make_match, make_dataset
from .learning import clean_rows, summary, predict_home_win
from .betting import ODDS, settle
from .save_system import load, save

W, H = 1120, 720
PHASES = ["Match", "Cleaning", "EDA", "Statistics", "Visualisation", "Prediction", "Betting", "Simulation", "Result"]

class Game:
    """Own the round state and render educational screens through pygame_gui."""
    def __init__(self):
        pygame.init(); pygame.display.set_caption("IDSE Football Betting Simulator")
        self.screen = pygame.display.set_mode((W,H)); self.clock = pygame.time.Clock(); self.manager = pygame_gui.UIManager((W,H))
        self.save_data = load(); self.money = int(self.save_data["money"]); self.round = int(self.save_data["round"])
        self.phase = 0; self.match = None; self.rows = []; self.raw = []; self.quality = .5; self.chart_kind = None
        self.home_p = .5; self.bet = "Home win"; self.stake = 500; self.score = [0,0]; self.elapsed = 0
        self.message = "Welcome. Inspect the data before placing your wager."; self.buttons=[]; self.make_round()

    def make_round(self):
        self.match = make_match(self.round); self.raw = make_dataset(self.match); self.rows = list(self.raw)
        self.quality=.5; self.phase=0; self.message="Choose Start Round to receive the match dataset."; self.build()

    def build(self):
        self.manager.clear_and_reset(); self.buttons=[]
        self.title = pygame_gui.elements.UILabel(pygame.Rect(32,20,1056,52), "IDSE FOOTBALL LAB   •   ROUND %02d" % self.round, self.manager, object_id="#title")
        self.status = pygame_gui.elements.UILabel(pygame.Rect(32,76,1056,38), f"Balance  ₹{self.money:,}     |     Learning first, betting second", self.manager)
        self.panel = pygame_gui.elements.UITextBox("", pygame.Rect(48,145,1024,390), self.manager, object_id="#copy")
        labels = self.options()
        for i,label in enumerate(labels):
            x=48+(i%3)*345; y=570+(i//3)*58
            b=pygame_gui.elements.UIButton(pygame.Rect(x,y,325,46), label, self.manager)
            self.buttons.append((b,label))
        self.refresh()

    def options(self):
        return [["Start Round"],["Clean dataset","Skip cleaning"],["Possession predicts shots","Goals are random","Skip EDA"],
          ["Review measures"],["Histogram: goals","Scatter: shots vs goals","Skip chart"],
          ["Use prediction","Guess home win","Skip prediction"],
          ["Home win","Draw","Away win","Over 2.5 goals","Correct score 1-0","Stake −₹100","Stake +₹100","Place bet"],
          ["Simulate match"],["Next round"]][self.phase]

    def panel_text(self):
        if self.phase == 0:
            return f"<b>SELECT MATCH  ·  {self.match.stadium}</b><br>{self.match.home} vs {self.match.away}<br><br>Fictional clubs. Form indicators: {self.match.home} {self.match.home_strength:.0%}  ·  {self.match.away} {self.match.away_strength:.0%}.<br>You'll inspect and prepare a synthetic match-history dataset before betting."
        if self.phase == 1:
            missing=sum(v is None for row in self.raw for v in row.values()); duplicates=len(self.raw)-len({tuple(sorted(r.items())) for r in self.raw})
            return f"<b>DATA CLEANING MINI TASK</b><br>Dataset: {len(self.raw)} rows · {len(self.raw[0])} columns<br>Detected: {missing} missing values, {duplicates} duplicate row, and one implausible goals outlier.<br><br>Choose Clean dataset to remove exact duplicates, fill missing numeric fields with their column mean, and cap the outlier. Skipping lowers prediction quality."
        if self.phase == 2:
            p=sum(float(r['possession']) for r in self.rows)/len(self.rows); s=sum(float(r['shots']) for r in self.rows)/len(self.rows)
            return f"<b>EXPLORATORY DATA ANALYSIS</b><br>Rows after preparation: {len(self.rows)}<br>Average possession: {p:.1f}%  ·  Average shots: {s:.1f}<br><br>Look for relationships before modelling: teams with more possession often create more shots, but that does not guarantee goals. Identify a useful trend."
        if self.phase == 3:
            vals=[float(r['goals']) for r in self.rows]; st=summary(vals)
            return "<b>STATISTICAL MEASURES</b><br>Goals per match · n = %d<br>Mean %.2f   Median %.2f   Mode %.0f<br>Variance %.2f   Standard deviation %.2f<br>Range %.0f   IQR %.0f<br><br>Mean is sensitive to extreme values; median and IQR are more robust."%(len(vals),st['mean'],st['median'],st['mode'],st['variance'],st['std_dev'],st['range'],st['iqr'])
        if self.phase == 4:
            return "<b>VISUALISATION MINI TASK</b><br>Pick a chart that fits the question. A histogram shows the distribution of one numeric variable; a scatter plot shows a relationship between two numeric variables.<br><br>Choose a chart to inspect."
        if self.phase == 5:
            return f"<b>PREMATCH MODEL CARD</b><br>Frozen logistic-style predictor · no training during play<br>Home win probability: <b>{self.home_p:.0%}</b>  ·  Draw: {max(8, int((1-self.home_p)*34))}%  ·  Away: {1-self.home_p:.0%}<br><br>Prediction quality reflects data preparation ({self.quality:.0%}). This is a probability, not a promise."
        if self.phase == 6:
            return f"<b>PLACE A WAGER</b><br>Selected: {self.bet}  ·  illustrative decimal odds {ODDS[self.bet]:.1f}×<br>Stake: ₹{self.stake:,} / Balance: ₹{self.money:,}<br><br>Odds show reward versus risk. Every learning step above is required before a wager is enabled."
        if self.phase == 7:
            return f"<b>{self.match.home}  {self.score[0]} — {self.score[1]}  {self.match.away}</b><br>{self.match.stadium}<br><br>Simulated 90-minute fixture · minute {min(90,int(self.elapsed))}'"
        return self.message

    def refresh(self):
        self.panel.set_text(self.panel_text()); self.status.set_text(f"Balance  ₹{self.money:,}     |     {PHASES[self.phase]}     |     Learning first, betting second")
        for button,label in self.buttons:
            if self.phase == 6 and label == self.bet: button.disable()

    def advance(self, label):
        if self.phase==0: self.phase=1
        elif self.phase==1:
            if label=="Clean dataset": self.rows,dups,filled=clean_rows(self.raw); self.quality=1.; self.message=f"Removed {dups} duplicate and filled {filled} missing values."
            else: self.quality=.45
            self.phase=2
        elif self.phase==2:
            self.quality=min(1,self.quality+.08) if label=="Possession predicts shots" else self.quality
            self.phase=3
        elif self.phase==3: self.phase=4
        elif self.phase==4:
            if label=="Histogram: goals": self.chart_kind="hist"
            elif label=="Scatter: shots vs goals": self.chart_kind="scatter"
            self.phase=5; self.home_p=predict_home_win(self.rows,self.match.home_strength,self.match.away_strength,self.quality)
        elif self.phase==5:
            if label=="Guess home win": self.quality=max(.3,self.quality-.2)
            elif label=="Skip prediction": self.quality=max(.2,self.quality-.25)
            self.phase=6
        elif self.phase==6:
            if label in ODDS: self.bet=label
            elif label=="Stake −₹100": self.stake=max(100,self.stake-100)
            elif label=="Stake +₹100": self.stake=min(max(100,self.money),self.stake+100)
            elif label=="Place bet": self.money-=min(self.stake,self.money); self.score=[0,0]; self.elapsed=0; self.phase=7
        elif self.phase==7 and label=="Simulate match": self.elapsed=90; self.score=self.simulate_score(); self.set_result_message(); self.phase=8
        elif self.phase==8 and label=="Next round":
            self.round+=1; self.save_data.update(money=self.money,round=self.round,wins=self.save_data.get("wins",0),losses=self.save_data.get("losses",0))
            # Money at this point already includes the stake deduction; settle restores stake on a win.
            self.money,self.change=settle(self.money+self.stake,self.stake,self.bet,*self.score)
            self.save_data["money"]=self.money
            if self.money<=0: self.money=1000; self.message="Bankrupt fund restored to ₹1,000 for learning."
            self.save_data["unlocks"]=["Cleaning","EDA","Statistics","Visualisation","Regression","Classification","Clustering"]
            save(self.save_data); self.make_round(); return
        self.build()

    def set_result_message(self):
        tentative, delta = settle(self.money + self.stake, self.stake, self.bet, *self.score)
        won = delta > 0
        self.message = (f"Full time: {self.match.home} {self.score[0]}–{self.score[1]} {self.match.away}. "
                        f"Your {self.bet} bet {'won' if won else 'lost'}; net change ₹{delta:+,}. "
                        f"Next balance: ₹{tentative:,}. Review the result, then continue.")

    def simulate_score(self):
        rng=random.Random(self.round*101)
        # Results depend on team strength, with deterministic reproducibility.
        return [min(5,rng.choices([0,1,2,3],[30,42,22,6])[0] if self.match.home_strength>self.match.away_strength else rng.choices([0,1,2,3],[43,37,16,4])[0]),
                min(5,rng.choices([0,1,2,3],[30,42,22,6])[0] if self.match.away_strength>self.match.home_strength else rng.choices([0,1,2,3],[43,37,16,4])[0])]

    def draw_chart(self, kind):
        # Tiny native pygame chart keeps chart exploration fully offline.
        chart=pygame.Surface((780,200)); chart.fill((245,248,246)); pygame.draw.line(chart,(50,70,70),(45,170),(750,170),2); pygame.draw.line(chart,(50,70,70),(45,20),(45,170),2)
        if kind=="hist":
            bins=[0]*6
            for row in self.rows: bins[min(5,int(row['goals']))]+=1
            for i,n in enumerate(bins): pygame.draw.rect(chart,(27,142,106),(75+i*105,170-n*15,65,n*15))
        else:
            for row in self.rows:
                x=55+int(float(row['shots'])*35); y=165-int(float(row['goals'])*35); pygame.draw.circle(chart,(224,140,60),(min(740,x),max(25,y)),5)
        self.screen.blit(chart,(170,335))

    def run(self):
        running=True
        while running:
            dt=self.clock.tick(60)/1000
            for event in pygame.event.get():
                if event.type==pygame.QUIT: running=False
                self.manager.process_events(event)
                if event.type==pygame_gui.UI_BUTTON_PRESSED:
                    for button,label in self.buttons:
                        if event.ui_element==button and button.is_enabled: self.advance(label); break
            if self.phase==7:
                self.elapsed=min(90,self.elapsed+dt)
                if self.elapsed>=90: self.score=self.simulate_score(); self.set_result_message(); self.phase=8; self.build()
            self.manager.update(dt); self.screen.fill((15,35,32)); self.manager.draw_ui(self.screen)
            if self.chart_kind and self.phase >= 5: self.draw_chart(self.chart_kind)
            pygame.display.flip()
        save({**self.save_data,"money":self.money,"round":self.round}); pygame.quit()
