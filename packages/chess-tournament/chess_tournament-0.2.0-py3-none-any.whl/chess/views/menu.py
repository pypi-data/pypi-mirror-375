"""View for displaying the main menu and handling user interactions."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MenuView:
    """Handles the main menu and interactive submenus for the Chess Tournament."""

    def __init__(self, player_controller, match_controller, tournament_controller):
        """Initialize MenuView with controllers."""
        self.player_controller = player_controller
        self.match_controller = match_controller
        self.tournament_controller = tournament_controller
        self.running = True

        self.menu_options = [
            ("1", "Manage players", self.manage_players),
            ("2", "Manage matches", self.manage_matches),
            ("3", "Manage tournaments", self.manage_tournaments),
            ("0", "Exit", self.exit_app),
        ]

    def display_menu(self):
        """Display main menu and handle choices until exit."""
        while self.running:
            print("\n=== Chess Tournament Menu ===")
            for key, desc, _ in self.menu_options:
                print(f"{key}. {desc}")
            choice = input("Enter your choice: ").strip()
            self.handle_choice(choice)

    def handle_choice(self, choice):
        """Execute the selected action from the main menu."""
        for key, _, action in self.menu_options:
            if choice == key:
                action()
                return
        print(" Invalid choice, try again.")

    def add_player(self):
        """Interactively add a player."""
        player_id = input("National ID (2 capital letters and 5 digits): ").strip()
        if not player_id or not player_id.isalnum() or len(player_id) != 7:
            print(" Invalid ID format (ex: AB12345).")
            return
        if self.player_controller.player_exists(player_id):
            print(" Player with this ID already exists.")
            return

        last_name = input("Enter last name: ").strip()
        first_name = input("Enter first name: ").strip()
        birth_date_str = input("Enter birth date (YYYY-MM-DD): ").strip()

        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except ValueError:
                print(" Invalid date format.")
                return

        self.player_controller.add_player(
            id_national=player_id,
            last_name=last_name,
            first_name=first_name,
            birthdate=birth_date,
        )
        print(f" Player {first_name} {last_name} added.")

    def list_players(self):
        """Display all registered players."""
        players = self.player_controller.list_players()
        if not players:
            print("No players.")
            return
        print("=== Registered Players ===")
        for p in players:
            print(
                f"- {p.last_name} {p.first_name} | ID: {p.id_national} | "
                f"Birthdate: {p.birth_date}"
            )

    def list_matches(self):
        """Display all matches."""
        matches = self.match_controller.list_matches()

        if not matches:
            print("No matches recorded.")
            return

        print("=== Recorded Matches ===")
        for i, match in enumerate(matches, start=1):
            player_white = match.player_white
            player_black = match.player_black
            score = match.score

            if score == [1, 0]:
                score_str = "1-0"
            elif score == [0, 1]:
                score_str = "0-1"
            else:
                score_str = "0.5-0.5"

            print(
                f"Match {i}: {player_white.first_name} {player_white.last_name} "
                f"vs {player_black.first_name} {player_black.last_name} | "
                f"Result: {score_str}"
            )

    def create_tournament(self):
        """Interactively create a tournament."""
        self.tournament_controller.create_tournament()

    def list_tournaments(self):
        """Display all tournaments."""
        self.tournament_controller.list_tournaments()

    def add_players_to_tournament(self):
        """Add players to a tournament."""
        self.tournament_controller.add_players()

    def start_round(self):
        """Start the next round in a tournament."""
        self.tournament_controller.start_round()

    def show_standings(self):
        """Show tournament standings."""
        self.tournament_controller.show_standings()

    def manage_players(self):
        """Player submenu active until 'Back' is selected."""
        submenu = {
            "1": ("Add a player", self.add_player),
            "2": ("List players", self.list_players),
            "0": ("Back", None),
        }
        self._interactive_submenu("Player Menu", submenu)

    def manage_matches(self):
        """Match submenu active until 'Back' is selected."""
        submenu = {
            "1": ("Create a match", self.match_controller.interactive_create_match),
            "2": ("List matches", self.list_matches),
            "0": ("Back", None),
        }
        self._interactive_submenu("Match Menu", submenu)

    def manage_tournaments(self):
        """Tournament submenu active until 'Back' is selected."""
        submenu = {
            "1": ("Create a tournament", self.tournament_controller.create_tournament),
            "2": ("List tournaments", self.tournament_controller.list_tournaments),
            "3": ("Add players", self.tournament_controller.add_players),
            "4": ("Start round", self.tournament_controller.start_round),
            "5": ("Enter results", self.tournament_controller.enter_results),
            "6": ("Show standings", self.tournament_controller.show_standings),
            "7": ("Export tournament report", self.tournament_controller.export_report),
            "0": ("Back", None),
        }
        self._interactive_submenu("Tournament Menu", submenu)

    def _interactive_submenu(self, title, submenu):
        """
        Run a submenu in a controlled loop until the user selects 'Back'.

        Args:
            title (str): Submenu title.
            submenu (list): List of (key, description, action) tuples.
        """
        choice = None
        while choice != "0":
            print(f"\n=== {title} ===")
            for key, (description, _) in submenu.items():
                print(f"{key}. {description}")
            choice = input("Enter your choice: ").strip()
            if choice in submenu:
                action = submenu[choice][1]
                if action:
                    action()
            elif choice != "0":
                print("Invalid choice, try again.")

    def exit_app(self):
        """Exit the program."""
        print(" Goodbye!")
        self.running = False
