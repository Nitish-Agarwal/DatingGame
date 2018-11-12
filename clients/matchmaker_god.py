import json
from random import random
import numpy as np

from clients.client import Player


class MatchMaker(Player):
    def __init__(self, name):
        super(MatchMaker, self).__init__(name=name, is_player=False)
        game_info = json.loads(self.client.receive_data(size=32368*2))
        print('Matchmaker', game_info)
        self.random_candidates_and_scores = game_info['randomCandidateAndScores']
        self.n = game_info['n']
        self.prev_candidate = {'candidate': [], 'score': 0, 'iter': -1}
        self.time_left = 120

    def play_game(self):

        while True:
            candidate = self.my_candidate()
            self.client.send_data(json.dumps(candidate))
            response = json.loads(self.client.receive_data())
            if 'game_over' in response:
                if response['match_found']:
                    print("Perfect Candidate Found")
                    print("Total candidates used = ", response['num_iterations'])
                else:
                    print("Perfect candidate not found - you have failed the player")
                    print("Total candidates used = ", response['total_candidates'])
                exit(0)
            else:
                self.prev_candidate = response['prev_candidate']
                self.time_left = response['time_left']

    def my_candidate(self):

        """
        PLACE YOUR CANDIDATE GENERATION ALGORITHM HERE
        As the matchmaker, you have access to the number of attributes (self.n),
        initial random candidates and their scores (self.random_candidates_and_scores),
        your clock time left (self.time_left)
        and a dictionary of the previous candidate sent (self.prev_candidate) consisting of
            'candidate' = previous candidate attributes
            'score' = previous candidate score
            'iter' = iteration num of previous candidate
        For this function, you must return an array of values that lie between 0 and 1 inclusive and must have four or
        fewer digits of precision. The length of the array should be equal to the number of attributes (self.n)
        """
        if self.prev_candidate['iter'] == -1:
            return self.__first_candidate__()
        else:
            return self.__subsequent_candidates__()

    def __first_candidate__(self):
        n = self.n
        candidates = np.array([self.random_candidates_and_scores[str(i)]['Attributes'] for i in range(40)])
        scores = np.array([self.random_candidates_and_scores[str(i)]['Score'] for i in range(40)])
        if np.linalg.matrix_rank(candidates) == n:
            self.estimated_preferences = np.inner(np.linalg.pinv(candidates), scores)
            suggested_candidate = [0.0] * n
            for i in range(n):
                if self.estimated_preferences[i] > 0.0:
                    suggested_candidate[i] = 1.0
            return suggested_candidate
        else:
            return [round(random(), 4) for i in range(n)]

    def __subsequent_candidates__(self):
        return [round(random(), 4) for i in range(self.n)]
