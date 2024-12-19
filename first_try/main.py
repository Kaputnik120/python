import chess
import lichess.api
from chess.pgn import Game, BaseVisitor
from lichess.format import PYCHESS


class KingsFianchettoVisitor(BaseVisitor):
    white_moves = {(6, 21), (13, 22), (11, 19), (5, 14), (4, 6)}
    black_moves = {(62, 45), (54, 46), (51, 43), (61, 54), (60, 62)}

    def __init__(self, is_white):
        self.is_white = is_white
        self.matching_moves = 0

    def visit_move(self, board: chess.Board, move: chess.Move):
        current_move = (move.from_square.real, move.to_square.real)

        if current_move in (KingsFianchettoVisitor.black_moves, KingsFianchettoVisitor.white_moves)[self.is_white]:
            self.matching_moves += 1

    def result(self) -> bool:
        return self.matching_moves == 5


print("Requesting games...")
games = lichess.api.user_games('Kaputnik120', format=PYCHESS)

total_not_won = 0
total_won = 0
total_elo_sum_won = 0
total_elo_sum_not_won = 0
total_elo_sum = 0
matching_not_won = 0
matching_won = 0
matching_elo_sum_won = 0
matching_elo_sum_not_won = 0
matching_elo_sum = 0

game: Game
for game in games:
    headerItems = game.headers.items()
    headerItem: tuple[str, str]

    skip_game = False
    for headerItem in headerItems:
        if headerItem[0] == 'WhiteElo':
            if not headerItem[1].isnumeric():
                skip_game = True
                break
            white_elo = int(headerItem[1])
        if headerItem[0] == 'BlackElo':
            if not headerItem[1].isnumeric():
                skip_game = True
                break
            black_elo = int(headerItem[1])
        if headerItem[0] == 'Site':
            game_link = headerItem[1]
        if headerItem[0] == 'White':
            is_playing_white = headerItem[1] == 'Kaputnik120'
        if headerItem[0] == 'Result':
            game_result = headerItem[1]
        if headerItem[0] == 'Event':
            is_rated = headerItem[1].startswith('Rated')

    if skip_game:
        continue

    # noinspection PyUnboundLocalVariable
    opponent_elo: int = (white_elo, black_elo)[is_playing_white]

    # noinspection PyUnboundLocalVariable
    is_won = (game_result[0] == '1' and is_playing_white) or (game_result[0] == '0' and not is_playing_white)

    is_matching_game = game.accept(
        visitor=KingsFianchettoVisitor(is_playing_white)
    )

    if is_matching_game:
        if is_won:
            matching_won += 1
            matching_elo_sum_won += opponent_elo
        else:
            matching_not_won += 1
            matching_elo_sum_not_won += opponent_elo
        matching_elo_sum += opponent_elo
    else:
        if is_won:
            total_won += 1
            total_elo_sum_won += opponent_elo
        else:
            total_not_won += 1
            total_elo_sum_not_won += opponent_elo
        total_elo_sum += opponent_elo

total_all = total_won + total_not_won
total_win_rate = total_won / total_all
total_opponent_elo_avg = total_elo_sum / total_all
total_opponent_elo_avg_won = total_elo_sum_won / total_won
total_opponent_elo_avg_not_won = total_elo_sum_not_won / total_not_won

matching_all = matching_won + matching_not_won
matching_win_rate = matching_won / matching_all
matching_opponent_elo_avg = matching_elo_sum / matching_all
matching_opponent_elo_avg_win = matching_elo_sum_won / matching_won
matching_opponent_elo_avg_not_win = matching_elo_sum_not_won / matching_not_won

print('TOTAL')
print(f'Win rate {total_win_rate * 100:.2f}% '
      f'({total_won} won of total {total_all})')
print(f'Average opponent elo average {total_opponent_elo_avg :.2f}\n'
      f'Winning average opponent elo {total_opponent_elo_avg_won :.2f}\n'
      f'Not winning average opponent elo {total_opponent_elo_avg_not_won :.2f}\n')

print('KINGS FIANCHETTO')
print(f'Win rate {matching_win_rate * 100:.2f}% '
      f'({matching_won} won of total {matching_all})')
print(f'Average opponent elo average {matching_opponent_elo_avg :.2f}\n'
      f'Winning average opponent elo {matching_opponent_elo_avg_win :.2f}\n'
      f'Not winning average opponent elo {matching_opponent_elo_avg_not_win :.2f}')
