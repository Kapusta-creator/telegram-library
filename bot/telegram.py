import telebot
from app import download
from pprint import pprint
from database import dbapi

db = dbapi.DatabaseConnector()


class TelegramBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.book = {}
        self.keyboard1 = telebot.types.ReplyKeyboardMarkup(True)

    def run(self):
        def interact_with_book(user_id, param):
            msg1 = self.bot.send_message(user_id, "Введите название книги")
            book = {}

            @self.bot.message_handler(content_types=["text"])
            def add_title(message):
                book["name"] = message.text
                msg2 = self.bot.send_message(user_id, "Введите автора")
                print(message.text, "title")

                @self.bot.message_handler(content_types=["text"])
                def add_author(message):
                    book["author"] = message.text
                    msg3 = self.bot.send_message(user_id, "Введите год издания")
                    print(message.text, "author")

                    @self.bot.message_handler(content_types=["text"])
                    def add_year(message):
                        book["year"] = message.text
                        if param == "add":
                            try:
                                add_book(book["name"], book["author"], book["year"], message.from_user.id)
                            except Exception as e:
                                self.bot.send_message(message.from_user.id, "Ошибка.")
                                print(e)
                        elif param == "delete":
                            try:
                                ask_for_delete_book(book["name"], book["author"], book["year"], message.from_user.id)
                            except Exception as e:
                                self.bot.send_message(message.from_user.id, "Ошибка.")
                                print(e)
                        elif param == "find":
                            try:
                                find_book(book["name"], book["author"], book["year"], message.from_user.id)
                            except Exception as e:
                                self.bot.send_message(message.from_user.id, "Ошибка.")
                                print(e)
                        elif param == "borrow":
                            try:
                                ask_for_borrow_book(book["name"], book["author"], book["year"], message.from_user.id)
                            except Exception as e:
                                self.bot.send_message(message.from_user.id, "Ошибка.")
                        elif param == "stats":
                            try:
                                get_stats(book["name"], book["author"], book["year"], message.from_user.id)
                            except Exception as e:
                                self.bot.send_message(message.from_user.id, "Ошибка.")
                                print(e)
                        # try:
                        #    dbapi.add()
                        print(message.text, "year")

                    self.bot.register_next_step_handler(msg3, add_year)

                self.bot.register_next_step_handler(msg2, add_author)

            self.bot.register_next_step_handler(msg1, add_title)

        def get_stats(title, author, year, user_id):
            book_id = db.get_book(title, author)
            if book_id is not None:
                try:
                    #download(book_id)
                    self.bot.send_message(user_id, f"Статистика доступна по адресу http://127.0.0.1:8080/download/{book_id}")
                except Exception as e:
                    self.bot.send_message(user_id, "Ошибка.")
                    print(e)
            else:
                self.bot.send_message(user_id, f"Нет такой книги")

        @self.bot.message_handler(content_types=["text"])
        def handle_text_message(message):
            if message.text == "/start":
                self.bot.send_message(message.from_user.id, "Салам Алейкум! Мир вашему дому.")
            elif message.text == "/add":
                interact_with_book(message.from_user.id, "add")
            elif message.text == "/delete":
                interact_with_book(message.from_user.id, "delete")
            elif message.text == "/list":
                books = db.list_books()
                if books is not None:
                    answer = []
                    for book in books:
                        answer.append(" ".join(str(p) for p in book[:len(book) - 1]) + (" (Удалена)" if not book[-1] else "") + ";")
                    answer = "\n".join(answer)
                    self.bot.send_message(message.from_user.id, answer)
                else:
                    self.bot.send_message(message.from_user.id, "Книг нет")
            elif message.text == "/find":
                interact_with_book(message.from_user.id, "find")
            elif message.text == "/borrow":
                interact_with_book(message.from_user.id, "borrow")
            elif message.text == "/retrieve":
                try:
                    book = db.retrieve(message.from_user.id)
                    if book:
                        self.bot.send_message(message.from_user.id, f"Вы вернули книгу {' '.join(book)}")
                    else:
                        self.bot.send_message(message.from_user.id, "Вам нечего возвращать")
                except Exception as e:
                    self.bot.send_message(message.from_user.id, "Ошибка.")
                    print(e)
            elif message.text == "/stats":
                interact_with_book(message.from_user.id, "stats")

        def ask_for_borrow_book(title, author, year, user_id):
            try:
                book_id = db.get_book(title, author)
                print(book_id)
                if book_id is not None:
                    msg = self.bot.send_message(user_id, f"Найдена книга: {title} {author} {year}. Берем?")
                    self.bot.register_next_step_handler(msg, borrow_book,
                                                        book_id=book_id, user_id=user_id)
                else:
                    self.bot.send_message(user_id, f"Книгу сейчас невозможно взять")
            except Exception as e:
                print(e)

        def borrow_book(message, book_id, user_id):
            if message.text.lower() == "да":
                try:
                    borrow_id = db.borrow(book_id, user_id)
                    if borrow_id is not False:
                        self.bot.send_message(user_id, f"Вы взяли книгу, borrow_id: {borrow_id}")
                    else:
                        self.bot.send_message(user_id, f"Книгу сейчас невозможно взять")
                except Exception as e:
                    print(e)
            else:
                self.bot.send_message(user_id, f"Вы не взяли книгу")

        def add_book(title, author, year, user_id):
            try:
                id = db.add(title, author, int(year))
                if id:
                    self.bot.send_message(user_id, f"Книга добавлена {id}")
                else:
                    self.bot.send_message(user_id, "Ошибка при добавлении книги")
            except Exception as e:
                self.bot.send_message(user_id, f"Ошибка")
                print(e)

        def find_book(title, author, year, user_id):
            try:
                if db.get_book(title, author) is not None:
                    self.bot.send_message(user_id, f"Найдена книга: {title} {author} {year}.")
                else:
                    self.bot.send_message(user_id, f"Такой книги у нас нет.")
            except Exception as e:
                print(e)

        def ask_for_delete_book(title, author, year, user_id):
            try:
                book_id = db.get_book(title, author)
                if book_id is not None:
                    msg = self.bot.send_message(user_id, f"Найдена книга: {title} {author} {year}. Удаляем?")
                    self.bot.register_next_step_handler(msg, delete_book,
                                                        book_id=book_id, user_id=user_id)
                else:
                    self.bot.send_message(user_id, f"Невозможно удалить книгу")
            except Exception as e:
                print(e)

        def delete_book(message, book_id, user_id):
            if message.text.lower() == "да":
                try:
                    if db.delete(book_id):
                        self.bot.send_message(user_id, f"Книга удалена")
                    else:
                        self.bot.send_message(user_id, f"Невозможно удалить книгу")
                except Exception as e:
                    print(e)

        @self.bot.message_handler(commands=["start"])
        def handle_start(message):
            self.bot.reply_to(message, "Салам Алейкум! Мир вашему дому.")

        self.bot.infinity_polling()


bot = TelegramBot("6120547477:AAH44arJlB5DBX6U_dyk3tEa1HVj5sj86Lk")
