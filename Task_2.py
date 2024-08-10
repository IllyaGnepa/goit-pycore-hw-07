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

def input_error(func):
    # Decorator to handle input errors.
    def wrapper(args, book):
        try:
            return func(args, book)
        except ValueError as e:
            return str(e)
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    # Add a new contact or update an existing contact with a phone number.
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    # Change a phone number for an existing contact.
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone number updated for contact {name}."
    else:
        return f"Contact {name} not found."

@input_error
def show_phone(args, book: AddressBook):
    # Show all phone numbers for a contact.
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s phones: {', '.join(p.value for p in record.phones)}"
    else:
        return f"Contact {name} not found."

@input_error
def list_contacts(args, book: AddressBook):
    # List all contacts in the address book.
    if not book.data:
        return "Address book is empty."
    result = ["Contacts in address book:"]
    for name, record in book.data.items():
        result.append(str(record))
    return "\n".join(result)

@input_error
def add_birthday(args, book: AddressBook):
    # Add a birthday to a contact.
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for contact {name}."
    else:
        return f"Contact {name} not found."

@input_error
def show_birthday(args, book: AddressBook):
    # Show the birthday of a contact.
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
        else:
            return f"Birthday not set for contact {name}."
    else:
        return f"Contact {name} not found."

@input_error
def birthdays(args, book: AddressBook):
    # Show upcoming birthdays within the next week.
    days = int(args[0]) if args else 7
    upcoming_birthdays = book.get_upcoming_birthdays(days)
    if not upcoming_birthdays:
        return "No upcoming birthdays within the next week."
    result = ["Upcoming birthdays:"]
    for record in upcoming_birthdays:
        result.append(f"{record.name.value} on {record.birthday.value.strftime('%d.%m.%Y')}")
    return "\n".join(result)

def parse_input(user_input):
    # Parse user input into command and arguments.
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(list_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
