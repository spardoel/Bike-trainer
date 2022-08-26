import time


class UserInterface:
    def __init__(self, database):
        self.database = database

    def display_welcome_message(self):

        print(
            "Welcome to my TrainerRoad clone! \nPlease choose one of the following options: \n\nTo display the available workouts, press '1' \nTo exit, press '2'"
        )

        # then wait for the user's input
        user_input = input()

        if user_input == "1":
            self.display_available_workouts()
            return self.selected_workout

        elif user_input == "2":
            self.display_end_message()

        else:
            print("Invalid input. Try again.\n")
            time.sleep(2)
            self.display_welcome_message()

    def display_end_message(self):
        print("Program terminated. See you next time!")
        exit()

    def display_available_workouts(self):

        # get the available workouts from the database
        valid_ids = self.database.print_available_workouts()

        print("Enter the workout id number to select it.\n To exit, press 'E'")

        user_input = input()

        if user_input in valid_ids:
            self.selected_workout = int(user_input)

        elif user_input == "e" or user_input == "E":
            self.display_end_message()

        else:
            print("Invalid input. Please try again.")
            self.display_available_workouts()
