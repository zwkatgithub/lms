DEFAULT_LENGTH = 255
ISBN_LENGTH = 13
NAME_LENGTH = 20
PAGINATION = 5



ON_THE_SHELF = 1
BORROWED = 2
DAMAGED = 8
LOST = 16
DEALING = 32

TIME_OUT = 3
TIME_IN = 4

choices = [(1,'Title'),(2,'Author'),(3,'ISBN')]
sex_choices = [(1,'Male'),(2,'Female')]
book_choices=[(1,'ISBN'),(2,'Title'),(3,'Author'),(4,'Copy ID')]
login_choices = [(1,'Reader'),(2,'Librarian'),(3,'Admin')]
edit_book_choices = [(1,'On the shelf'),(2,'Borrowed'),(8,'Damaged'),(16,'Lost'),(32,'Arranging')]
income_choices=[(1,'Year'),(2,'Month'),(3,'Week'),(4,'Day')]