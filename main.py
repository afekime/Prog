from file_manager import PhoneFileManager
from view import PhoneApp

FILENAME = "Lab2.txt"


def main():
    repository = PhoneFileManager()
    objects = repository.load_from_file(FILENAME)

    app = PhoneApp(objects, FILENAME, repository)
    app.run()


if __name__ == "__main__":
    main()