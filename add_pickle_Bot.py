from collections import UserDict
from datetime import datetime, timedelta
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def init(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().init(value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be a 10-digit number.")
        super().__init__(value)

class Record:
    def __init__(self, name, phone):
        self.name = Name(name)
        self.phones = [Phone(phone)]
        self.birthday = None

    def add_birthday(self, birthday):
        try:
            datetime.strptime(birthday, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Phone number must be a 10-digit number.")
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def find_phone(self, phone_number):
        for phone in self.phones:
            if str(phone) == phone_number:
                return phone
        return None

    def edit_phone(self, old_phone, new_phone):
        original_phone = ";".join(str(phone) for phone in self.phones)
        self.delete_phone(old_phone)
        self.add_phone(new_phone)
        new_phone = ";".join(str(phone) for phone in self.phones)
        print (f"Contact updated. Original phone: {original_phone}, New phone {new_phone}")

        return self.__str__()

    def __str__(self):
        phone_numbers = ";".join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name}, phones: {';'.join(map(str, self.phones))}"
    
class AddressBook(UserDict):
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if days_until_birthday <= 7:
                    congratulation_date = birthday_this_year

                    # Check if the birthday falls on a weekend
                    if congratulation_date.weekday() >= 5:  # Saturday (5) or Sunday (6)
                        # If so, move the congratulations to the next Monday
                        days_until_monday = (7 - congratulation_date.weekday()) + 1
                        congratulation_date += timedelta(days=days_until_monday)

                    upcoming_birthdays.append({"Name": record.name.value, "Congratulation_date": congratulation_date.strftime("%d.%m.%Y")})

        return upcoming_birthdays

    def add_record(self, record):
        self.data[record.name.value] = record

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
            return f"Record {name} deleted."
        else:
            return f"No record found for {name}."

    def find_record(self, name):
        return self.data.get(name)

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Name not found."
        except IndexError:
            return "Not enough arguments."

    return inner

@input_error
def add_contact(args, book):
    if len(args) < 2:
        return "Give me name and phone please."
    name = args[0]
    phone = args[1]
    
    record = Record(name, phone)
    book.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find_record(name)
    if record:
        original_phone = str(record.phones[0])
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        return "Error: Name not found."
    
@input_error
def delete_contact(args, book):
    if len(args) < 1:
        return "Give me a name to delete."
    name = args[0]
    return book.delete_record(name)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find_record(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Error: Name not found."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find_record(name)
    if record:
        if record.birthday:
            return f"{name}'s birthday: {record.birthday.value}"
        else:
            return f"No birthday set for {name}."
    else:
        return f"Error: Name not found."

@input_error
def birthdays(args, book: AddressBook):
    return book.get_upcoming_birthdays()

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find_record(name)
    if record:
        return str(record.phones[0])
    else:
        return "Error: Name not found."

@input_error
def show_all(book):
    if book:
        return "\n".join(str(record) for record in book.data.values())
    else:
        return "No contacts saved."

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "delete":
            print(delete_contact(args, book))
        elif command == "find_phone":  # Додана команда для пошуку телефону
            if len(args) != 2:
                print("Invalid command. Please provide a name and a phone number.")
                continue
            name, phone_number = args
            record = book.find_record(name)
            if record:
                found_phone = record.find_phone(phone_number)
                if found_phone:
                    print(f"{record.name}: {found_phone}")
                else:
                    print("Phone number not found.")
            else:
                print(f"No record found for {name}.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()