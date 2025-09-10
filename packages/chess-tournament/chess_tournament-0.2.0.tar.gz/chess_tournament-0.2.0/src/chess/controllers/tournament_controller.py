"""Controller for tournament-related operations."""

import json
import os
import logging
import random
from datetime import date
from jinja2 import Environment, FileSystemLoader
from chess.models.tournament import Tournament
from chess.models.round import Round
from chess.models.match import Match

logger = logging.getLogger(__name__)


def get_valid_result_input():
    """
    Prompts the user for a match result and returns a valid score list.
    Keeps prompting until a valid input is received.
    """
    result_map = {"1": [1, 0], "2": [0, 1], "0": [0.5, 0.5]}

    user_input = ""

    while user_input not in result_map:
        user_input = input("Enter result (1 for win, 2 for loss, 0 for draw): ").strip()
        if user_input not in result_map:
            print("Invalid input. Please use '1', '2', or '0'.")

    return result_map[user_input]


class TournamentController:
    """Handles tournament-related operations.

    Such as creation, loading, and saving tournaments.
    """

    FILE_PATH = "data/tournaments.json"

    def __init__(self, player_controller):
        """Initialize the tournaments file if it doesn't exist."""
        self.player_controller = player_controller
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        if not os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                f.write("[]")

    def load_tournaments(self) -> list[Tournament]:
        """Load tournaments from JSON file."""
        try:
            with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:
                    return []
                return [Tournament.from_dict(t) for t in json.loads(data)]
        except FileNotFoundError:
            return []

    def save_tournaments(self, tournaments: list[Tournament]) -> None:
        """Save tournaments to JSON file."""
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tournaments], f, indent=4)

    def create_tournament(self):
        """Prompt user and create a new tournament."""
        name = input("Tournament name: ").strip()
        location = input("Location: ").strip()
        start_date = input("Start date (YYYY-MM-DD): ").strip()
        end_date = input("End date (YYYY-MM-DD): ").strip()
        description = input("Description (optional): ").strip()

        tournament = Tournament(
            name=name,
            location=location,
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
            current_round=0,  # Start at round 0
            rounds=[],
            players=[],
            description=description,
        )

        tournaments = self.load_tournaments()
        tournaments.append(tournament)
        self.save_tournaments(tournaments)

        print(f" Tournament '{name}' created successfully.")

    def list_tournaments(self):
        """Show list of tournaments."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print("No tournaments available.")
            return
        print("Tournaments:")
        for t in tournaments:
            print(f"- {t.name} ({t.location}), {t.start_date} → {t.end_date}")

    def add_players(self):
        """Adds players to the last created tournament."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print("No tournament exists. Please create one first.")
            return

        tournament = tournaments[-1]
        print(f"Adding players to tournament: {tournament.name}")

        nb_to_add_input = input("How many players do you want to add? ").strip()
        if not nb_to_add_input.isdigit() or int(nb_to_add_input) <= 0:
            print("Invalid number.")
            return

        nb_to_add = int(nb_to_add_input)

        # Create a set of IDs for quick lookups
        existing_player_ids = {player.id_national for player in tournament.players}

        for i in range(nb_to_add):
            player_id = input(f"Enter player's national ID {i+1}: ").strip()

            # Validate the national ID
            if not player_id:
                print("The national ID cannot be empty.")
                continue

            # Check if the player is already in the tournament
            if player_id in existing_player_ids:
                print("This player is already registered in the tournament.")
                continue

            player = self.player_controller.find_player_by_id(player_id)

            if player:
                tournament.players.append(player)
                existing_player_ids.add(player.id_national)
                print(f"Added {player.first_name} {player.last_name}.")
            else:
                print("Player not found.")

        self.save_tournaments(tournaments)

        print(
            f"{len(tournament.players)} players are now registered in tournament "
            f"{tournament.name}."
        )

    def start_round(self):
        """Starts the next round of the most recent tournament.
        after checking if the previous round's results have been entered."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print(" No tournaments exist. Create one first.")
            return

        tournament = tournaments[-1]

        if tournament.current_round >= tournament.number_of_rounds:
            print(" All rounds have been played. The tournament is finished.")
            return

        if tournament.current_round > 0:
            previous_round = tournament.rounds[tournament.current_round - 1]
            if previous_round.end_time is None:
                print(" Unable to start a new round.")
                print(" Please enter the results of the previous round first.")
                return

        print(
            f"Starting round {tournament.current_round + 1} for '{tournament.name}'..."
        )

        if not tournament.players:
            print(" Cannot start a round. No players are registered.")
            return

        if len(tournament.players) % 2 != 0:
            print(" Cannot start a round. An even number of players is required.")
            print(" Please add or remove a player.")
            return

        players = tournament.players

        if tournament.current_round == 0:
            random.shuffle(players)
        else:
            random.shuffle(players)
            players = sorted(players, key=lambda p: p.score, reverse=True)
        new_round_matches = []
        # Use a list of players to be paired and remove them as they are matched
        players_to_pair = players[:]

        while players_to_pair:
            player_white = players_to_pair.pop(0)

            # Find the first available opponent
            for i, player_black in enumerate(players_to_pair):
                already_played = False
                for r in tournament.rounds:
                    for match in r.matches:
                        ids = {
                            match.player_white.id_national,
                            match.player_black.id_national,
                        }
                        if (
                            player_white.id_national in ids
                            and player_black.id_national in ids
                        ):
                            already_played = True
                            break
                    if already_played:
                        break

                if not already_played:
                    new_match = Match(player_white, player_black, [0, 0])
                    new_round_matches.append(new_match)
                    players_to_pair.pop(i)  # Remove the opponent from the list
                    break

        # Create a new Round and add matches
        new_round = Round(tournament.current_round + 1)
        new_round.matches = new_round_matches
        tournament.rounds.append(new_round)

        # Update the tournament's current round number
        tournament.current_round += 1

        self.save_tournaments(tournaments)

        print(f" Round {tournament.current_round} started successfully.")
        print(" Pairings:")
        for match in new_round_matches:
            print(
                f"  - {match.player_white.first_name} {match.player_white.last_name} "
                f"vs {match.player_black.first_name} {match.player_black.last_name}"
            )

    def enter_results(self):
        """Allows the user to enter results for the current round.
        Updates match scores."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print("No tournaments exist. Create one first.")
            return

        tournament = tournaments[-1]

        if not tournament.rounds:
            print("No rounds have been started yet.")
            return

        current_round = tournament.rounds[-1]

        if current_round.end_time is not None:
            print("Results have already been entered for this round.")
            return

        print(f"Entering results for Round {current_round.round_no}...")

        if not current_round.matches:
            print("No matches to enter results for.")
            return

        for match in current_round.matches:
            player_white = match.player_white
            player_black = match.player_black

            print(f"\nMatch: {player_white.last_name} vs {player_black.last_name}")
            score = get_valid_result_input()

            match.score = score

            if score == [1, 0]:
                player_white.score += 1
            elif score == [0, 1]:
                player_black.score += 1
            else:  # score == [0.5, 0.5]
                player_white.score += 0.5
                player_black.score += 0.5

        current_round.close()

        self.save_tournaments(tournaments)
        print("Round results saved successfully.")

        if tournament.current_round >= tournament.number_of_rounds:
            print("\nAll rounds have been played. The tournament is finished.")
        else:

            print("\nReady for the next round. Choose '4. Start round' from the menu.")

    def show_standings(self):
        """Display tournament details, players,
        rounds with matches, and current standings."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print(" No tournaments exist. Create one first.")
            return

        tournament = tournaments[-1]

        # --- Tournament details ---
        print("\n--- Tournament Details ---")
        print(f" Name: {tournament.name}")
        print(f" Location: {tournament.location}")
        print(f" Start Date: {tournament.start_date}")
        print(f" End Date: {tournament.end_date}")
        print(f" Number of rounds: {tournament.number_of_rounds}")
        print(f" Current round: {tournament.current_round}")
        print(f" Description: {tournament.description}")

        # --- Registered players (alphabetical) ---
        if tournament.players:
            print("\n--- Registered Players (Alphabetical) ---")
            sorted_players = sorted(
                tournament.players,
                key=lambda p: (p.last_name.lower(), p.first_name.lower()),
            )
            for player in sorted_players:
                print(
                    f"  - {player.first_name} {player.last_name}"
                    f"  - (ID: {player.id_national})"
                )
        else:
            print("\n No players are registered for this tournament.")
            return

        # --- Rounds and matches ---
        print("\n--- Round Information ---")
        if not tournament.rounds:
            print(" No round has been started yet.")
        else:
            for round_obj in tournament.rounds:
                start_time = round_obj.start_time
                end_time = round_obj.end_time if round_obj.end_time else "In progress"
                print(f"\nRound {round_obj.round_no}:")
                print(f"  - Start: {start_time}")
                print(f"  - End: {end_time}")

                if not round_obj.matches:
                    print("  No matches in this round yet.")
                    continue

                print("  Matches:")
                for match in round_obj.matches:
                    player_white = match.player_white
                    player_black = match.player_black
                    score = match.score

                    if score == [0, 0]:
                        score_str = "Not played"
                    elif score == [1, 0]:
                        score_str = "1 - 0"
                    elif score == [0, 1]:
                        score_str = "0 - 1"
                    else:  # [0.5, 0.5]
                        score_str = "0.5 - 0.5"

                    print(
                        f"    {player_white.first_name} {player_white.last_name} vs "
                        f"{player_black.first_name} {player_black.last_name}"
                        f"| Result: {score_str}"
                    )

        # --- Calculate current standings ---
        scores = {player.id_national: 0.0 for player in tournament.players}
        for round_obj in tournament.rounds:
            for match in round_obj.matches:
                scores[match.player_white.id_national] += match.score[0]
                scores[match.player_black.id_national] += match.score[1]

        sorted_standings = sorted(
            tournament.players,
            key=lambda p: scores.get(p.id_national, 0.0),
            reverse=True,
        )

        print("\n--- Current Standings ---")
        if not any(score > 0 for score in scores.values()):
            print(" No results have been entered yet.")

        for rank, player in enumerate(sorted_standings, 1):
            player_score = scores.get(player.id_national, 0.0)
            print(
                f" {rank}. {player.first_name} {player.last_name}:"
                f" {player_score} points"
            )

    def export_full_tournament_report_html(
        self, tournament, filename="tournament_report.html"
    ):
        """Export a full tournament report to HTML,
        including all rounds, matches, and standings."""

        # Alphabetical sort of players
        sorted_players = sorted(
            tournament.players,
            key=lambda p: (p.last_name.lower(), p.first_name.lower()),
        )

        # Calculate scores
        scores = {player.id_national: 0.0 for player in tournament.players}
        for round_obj in tournament.rounds:
            for match in round_obj.matches:
                scores[match.player_white.id_national] += match.score[0]
                scores[match.player_black.id_national] += match.score[1]
        sorted_standings = sorted(
            tournament.players,
            key=lambda p: scores.get(p.id_national, 0.0),
            reverse=True,
        )

        env = Environment(loader=FileSystemLoader("src/chess/templates"))
        template = env.get_template("tournament_report.html.j2")

        html_content = template.render(
            tournament=tournament,
            sorted_players=sorted_players,
            scores=scores,
            sorted_standings=sorted_standings,
        )

        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f" Full tournament HTML report exported successfully: {filepath}")

    def export_report(self):
        """Export the last created tournament to HTML."""
        tournaments = self.load_tournaments()
        if not tournaments:
            print("No tournaments exist. Create one first.")
            return

        tournament = tournaments[-1]  # export the last tournament
        filename = f"{tournament.name.replace(' ', '_')}_report.html"
        self.export_full_tournament_report_html(tournament, filename)
