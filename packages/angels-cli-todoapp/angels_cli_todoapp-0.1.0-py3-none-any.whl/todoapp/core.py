import string

# Init list
todo_list = []

def add_list_item(item):
    todo_list.append(item)

def delete_list_item(item):
    del todo_list[item]

def view_list_item():
    for index, item in enumerate(todo_list):
        print(f"{index + 1}. {item}")

def update_list_item(item, updated_item): 
    todo_list[item - 1] = updated_item

def help_menu(): 
    print('''
This todo app has the following capabilities/commands:
    - Add: Add items to your todo list
    - Delete: Delete an item by its number
    - View: View your current list
    - Update: Update an item by number
    - Help: Show this menu
    - Exit: Exit the program
    ''')
