from datetime import datetime

class SoccerMatch():
    def __init__(self):
        self.start = None
        self.end = None
        self.team1 = ""
        self.team2 = ""
        self.team1_odds = ""
        self.team2_odds = ""
        self.draw_odds = ""
        self.outcome = ""

    def set_start(self, start_time_str):
        self.start = datetime.strptime(start_time_str, "%d %b %Y %H:%M")
        # TODO set end automatically (start_time + 90 mins)

    def set_teams(self, participants):
        self.team1 = participants[0]
        self.team2 = participants[1]

    def set_outcome_from_scores(self, scores):
        if scores == None or len(scores) == 0:
            self.outcome = "NONE"
        elif scores[0] == -1 and scores[1] == -1:
            self.outcome = "NONE"
        elif scores[0] > scores[1]:
            self.outcome = "TEAM1"
        elif scores[0] < scores[1]:
            self.outcome = "TEAM2"
        else:
            self.outcome = "DRAW"

    def set_odds(self, odds):
        self.team1_odds = odds[0]
        self.draw_odds = odds[1]
        self.team2_odds = odds[2]

    def get_start_time_string(self):
        if self.start is None:
            return "NULL"
        return self.start.ctime()

    def get_end_time_string(self):
        if self.end is None:
            return "NULL"
        return self.end.ctime()

    def get_team1_string(self):
        return self.team1

    def get_team2_string(self):
        return self.team2

    def get_team1_odds(self):
        return self.team1_odds

    def get_team2_odds(self):
        return self.team2_odds

    def get_draw_odds(self):
        return self.draw_odds

    def get_outcome_string(self):
        return self.outcome