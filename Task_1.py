from collections import UserDict
import re
from datetime import datetime, timedelta

# Base class for record fields
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Class for storing the name of a contact
class Name(Field):
    pass

# Class for storing a phone number with validation for format (10 digits)
class Phone(Field):
    def __init__(self, value):
        if self._validate(value):
            super().__init__(value)
        else:
            raise ValueError("Invalid phone number format. It should be 10 digits.")

    def _validate(self, value):
        return re.fullmatch(r"\d{10}", value) is not None

# Class for storing a birthday with validation for date format (DD.MM.YYYY)
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Class for storing information about a contact
class Record:
    def __init__(self, name):
        self.name = Name(name)  
        self.phones = []  
        self.birthday = None  

    def add_phone(self, phone):
        # Add a new phone number to the contact.
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        # Remove a phone number from the contact.
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone):
        # Edit a phone number in the contact.
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            self.phones.remove(phone_to_edit)
            self.add_phone(new_phone)

    def find_phone(self, phone):
        # Find a phone number in the list.
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        # Add a birthday to the contact. 
        self.birthday = Birthday(birthday)

    def __str__(self):
        # Return a string representation of the contact in a readable format. 
        phones = '; '.join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"

# Class for managing and storing address book records
class AddressBook(UserDict):
    def add_record(self, record):
        # Add a record to the address book. 
        self.data[record.name.value] = record

    def find(self, name):
        # Find a record by name.
        return self.data.get(name)

    def delete(self, name):
        # Delete a record by name.
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        # Return a list of contacts with upcoming birthdays within the next few days.
        today = datetime.now()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if today <= next_birthday <= (today + timedelta(days=days)):
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

# Command handling functions
def handle_add_contact(book, name, phone, email, favorite, birthday=None):
    # Handle the command to add a contact.
    try:
        record = Record(name)
        record.add_phone(phone)
        if birthday:
            record.add_birthday(birthday)
        book.add_record(record)
        return f"Contact {name} added successfully."
    except ValueError as e:
        return str(e)

def handle_list_contacts(book):
    # Handle the command to list all contacts. 
    if not book.data:
        return "Address book is empty."
    result = ["Contacts in address book:"]
    for name, record in book.data.items():
        result.append(str(record))
    return "\n".join(result)

def handle_get_contact(book, name):
    # Handle the command to get a contact by name.
    record = book.find(name)
    if record:
        return str(record)
    else:
        return f"Contact {name} not found."

def handle_remove_contact(book, name):
    # Handle the command to remove a contact by name.
    record = book.find(name)
    if record:
        book.delete(name)
        return f"Contact {name} removed successfully."
    else:
        return f"Contact {name} not found."

def handle_edit_contact_phone(book, name, old_phone, new_phone):
    # Handle the command to edit a phone number in a contact.
    record = book.find(name)
    if record:
        try:
            record.edit_phone(old_phone, new_phone)
            return f"Phone number updated for contact {name}."
        except ValueError as e:
            return str(e)
    else:
        return f"Contact {name} not found."

def handle_upcoming_birthdays(book, days=7):
    # Handle the command to get upcoming birthdays within the next few days.
    upcoming_birthdays = book.get_upcoming_birthdays(days)
    if not upcoming_birthdays:
        return "No upcoming birthdays within the next week."
    result = ["Upcoming birthdays:"]
    for record in upcoming_birthdays:
        result.append(f"{record.name.value} on {record.birthday.value.strftime('%d.%m.%Y')}")
    return "\n".join(result)

def main():
    book = AddressBook()
    commands = {
        "add": handle_add_contact,
        "list": handle_list_contacts,
        "get": handle_get_contact,
        "remove": handle_remove_contact,
        "edit": handle_edit_contact_phone,
        "birthdays": handle_upcoming_birthdays,
        "exit": lambda book: "Exiting the program...",
        "close": lambda book: "Closing the program..."
    }

    print("Welcome to the Address Book!")
    while True:
        command = input("Enter command (add, list, get, remove, edit, birthdays, exit, close): ").strip().lower()
        if command in ["exit", "close"]:
            print(commands[command](book))
            break
        elif command in commands:
            if command == "add":
                name = input("Enter name: ").strip()
                phone = input("Enter phone: ").strip()
                email = input("Enter email: ").strip()  
                favorite = input("Is favorite (True/False): ").strip().lower() == 'true'
                birthday = input("Enter birthday (DD.MM.YYYY) or leave empty: ").strip()
                birthday = birthday if birthday else None
                print(commands[command](book, name, phone, email, favorite, birthday))
            elif command == "list":
                print(commands[command](book))
            elif command == "get":
                name = input("Enter name: ").strip()
                print(commands[command](book, name))
            elif command == "remove":
                name = input("Enter name: ").strip()
                print(commands[command](book, name))
            elif command == "edit":
                name = input("Enter name: ").strip()
                old_phone = input("Enter old phone: ").strip()
                new_phone = input("Enter new phone: ").strip()
                print(commands[command](book, name, old_phone, new_phone))
            elif command == "birthdays":
                days = input("Enter number of days (default 7): ").strip()
                days = int(days) if days else 7
                print(commands[command](book, days))
        else:
            print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()
