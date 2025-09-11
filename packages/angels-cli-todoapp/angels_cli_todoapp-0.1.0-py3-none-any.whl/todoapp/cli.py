import string
from .core import add_list_item, delete_list_item, view_list_item, update_list_item, help_menu, todo_list

def main():
    print("Type 'help' if you want to learn how to get around the todo app: ")

    running = True
    while running:
        user_selection = input("What would you like to do? ")

        user_selection = user_selection.lower().strip()
        user_selection = user_selection.translate(str.maketrans('', '', string.punctuation))

        if user_selection == "add":
            item = input("Enter your todo item: ")
            add_list_item(item)

        elif user_selection == "delete":
            item = int(input("Which item would you like to delete? Please enter the item number: ")) - 1
            if item >= len(todo_list):
                print("The item number you selected is greater than the list length.")
            else:
                delete_list_item(item)

        elif user_selection == "update":
            item = int(input("Enter the number of the item you want to update: "))
            updated_item = input("What would you like to replace this item with? ")
            update_list_item(item, updated_item)

        elif user_selection == "view":
            view_list_item()
            if len(todo_list) == 0:
                print("The list is empty!")

        elif user_selection == "exit":
            running = False

        elif user_selection == "help":
            help_menu()
