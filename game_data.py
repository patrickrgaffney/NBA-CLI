class Game:
    """A single game's attributes and methods."""

    # TODO: add parameter comments in doc_string for each method
    def __init__(self, game_json, away_index, home_index):
        """Create a new Game instance.

        game_json   (json obj) blob of "game-related" data
        away_index  (json obj) blob of "team-related" data for the away team
        home_index  (json obj) blob of "team-related" data for the home team

        id     (int) game id for the day (# of the game)
        time        (string) game time, Eastern Standard Time (EST)
        awayAbbr    (int) away team abbr
        homeAbbr    (int) home team abbr
        tv          (string) nationally televised game, ex: NBATV, defaults to None
        status      (int) 1=before game, 2=during game, 3=game over, defaults to 1
        period      (string) quarter of play, defaults to None (before game starts)
        awayRecord  (string) record of away team
        homeRecord  (string) record of home team
        periodTime  (string) time remaining in current period
        homePts     (list) list of pts by period, ex: [q1, q2, q3, q4, ot1, ot2, ot3, ot4, ot5]
        awayPts     (list) list of pts by period, ex: [q1, q2, q3, q4, ot1, ot2, ot3, ot4, ot5]
        aTotalPts   (int) total number of points by the away team
        hTotalPts   (int) total number of points by the home team

        Values for pts are assigned values from home/away_index if after the game.
        Values for pts are assigned 0 if before the game, they will not be used.
        Values for pts are assigned 0 if during the game, they will be updated later using set_scores() method
        """

        self._id = game_json[2]
        self._status = game_json[3]
        self._time = game_json[4]
        self._homeAbbr = home_index[4]
        self._awayAbbr = away_index[4]
        self._period = game_json[9]
        self._tv = game_json[11]
        self._awayRecord = away_index[6]
        self._homeRecord = home_index[6]
        self._periodTime = 0


        if self._status == 3: # after the game
            # declare lists with q1 totals
            self._homePts = [home_index[7]]
            self._awayPts = [away_index[7]]
            self._hTotalPts = home_index[21]
            self._aTotalPts = away_index[21]

            for period in range(8, 21, 1):
                self._homePts.append(home_index[period])
                self._awayPts.append(away_index[period])
        elif self._status == 1:
            self._homePts = [0 for i in range(0, 14, 1)]
            self._awayPts = [0 for i in range(0, 14, 1)]
            self._hTotalPts = -1
            self._aTotalPts = -1
        else: # during game, will be updated later
            self._homePts = [0 for i in range(0, 14, 1)]
            self._awayPts = [0 for i in range(0, 14, 1)]

    def __len__(self):
        """Define length of Game(s)"""
        return counter

    def __getitem__(self, i):
        """Make Game iterable"""
        if i > len(self):
            raise IndexError
        return i

    def set_scores(self, live_scores):
        """Set the scores for the game's periods and overtimes(s)
           If the game hasn't started, or is over, do nothing.

           live_scores  (json obj) blob of live game data from API
        """

        period_names = ["q1", "q2", "q3", "q4", "ot1", "ot2", "ot3", "ot4", "ot5", "ot6", "ot7", "ot8", "ot9", "ot10"]

        if self._status == 2: # during game
            self._period = live_scores["st"] # update period
            self._periodTime = live_scores["cl"] # update period time remaining
            self._hTotalPts = live_scores["h"]["s"]
            self._aTotalPts = live_scores["v"]["s"]

            for period in range(0, 14, 1):
                self._homePts[period] = live_scores["h"][period_names[period]]
                self._awayPts[period] = live_scores["v"][period_names[period]]

    def __print_periods(self, num_ots):
        """Create a string of team pts per period, or headers of each period."""

        period_names = ["Q1", "Q2", "Q3", "Q4", "OT1", "OT2", "OT3", "OT4", "OT5", "OT6", "OT7", "OT8", "OT9", "OT10"]
        head_string = " " * 5 # space for team abbr
        home_string = self._homeAbbr.rjust(5)
        away_string = self._awayAbbr.rjust(5)

        for period in range(0, 4 + num_ots, 1):
            home_string += str(self._homePts[period]).rjust(5)
            away_string += str(self._awayPts[period]).rjust(5)
            head_string += period_names[period].rjust(5)

        home_string += str(self._hTotalPts).rjust(7)
        away_string += str(self._aTotalPts).rjust(7)
        head_string += "FINAL".rjust(7)

        return head_string + "\n" + home_string + "\n" + away_string

    def __get_num_ots(self):
        """Return the number of overtimes where there is activity."""

        for index, overtime in zip(range(4, 14, 1), range(0, 11, 1)):
            if self._homePts[index] == 0:
                return overtime

        return 0

    def __check_status(self):
        """Check the status of the current game."""

        if (self._status == 1): # before game
            return self._time
        elif (self._status == 2): # during game
            # test for halftime or final
            if (self._period in {"Halftime", "Final"}):
                return self._period
            else: # during a live period
                return str(self._periodTime) + " remaining in " + str(self._period)
        else: # after game
            return "Final"

    def __check_tv(self):
        """Check to see if game is nationally televised."""

        if (self._tv is None):
            return ""
        else: # game is nationally televised
            return " on " + self._tv

    def __str__(self):
        """Prints a header for the game.

        line1 -> HOME_ABBR (HOME_RECORD) at AWAY_ABBR (AWAY_RECORD)
        line2 -> Final/Halftime/End of/x time remaining in/on NATL_TV
        line3 ->           Q1   Q2   Q3   Q4   FINAL/TOTAL
        line4 -> HOME_ABBR q1   q2   q3   q4   pts
        line4 -> AWAY_ABBR q1   q2   q3   q4   pts
        """

        line1 = (self._awayAbbr + " (" + self._awayRecord + ")   at   " + self._homeAbbr + " (" + self._homeRecord + ")").center(34) + "\n"
        line2 = (self.__check_status() + self.__check_tv()).center(34) + "\n"
        lines = self.__print_periods(self.__get_num_ots()) + "\n"

        return line1 + line2 if self._status == 1 else line1 + line2 + lines
