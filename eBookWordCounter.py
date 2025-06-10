# Final Project
# This program will create a local database to display the top most frequent words and their frequencies in an ebook.
# Kevin Diaz
# 11/22/23



from html.parser import HTMLParser
from urllib.request import urlopen
import re
from tkinter import *
import sqlite3



def create_database():
    '''
    create_database() will create a database called 'ebooks.db' and create a table called 'ebooks' with columns called
    'book', 'word', 'frequency' that will store books found on the website along with all the words and word frequencies
    found in each book.
    '''
    try:
        con = sqlite3.connect('ebooks.db')
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS ebooks(book TEXT, word TEXT, frequency INT)""")
        con.commit()
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
    finally:
        con.close()



def search_book(book_name):
    '''
    search_book() will search the table 'ebooks' for the book name that is passed in as a parameter through a SQL query.
    If the book is found, it will call sort_data(book_name) with the same parameter, otherwise it will return empty.
    '''
    try:
        con = sqlite3.connect('ebooks.db')
        cur = con.cursor()

        cur.execute('SELECT * FROM ebooks WHERE book = ?', (book_name,))
        result = cur.fetchall()


        if result:
            # Sort the data by frequency in descending order, return list of tuples
            return sort_data(book_name)
        else:
            return
    except sqlite3.Error as e:
        print(f"Error searching for book: {e}")



def sort_data(book_name):
    '''
    sort_data() will print the book data in the table 'ebooks' that has a frequency greater than or equal to 'n'.
    A SQL query will be used to select the book name and frequency filtered by the words appearing  by the minimum
    frequency 'n' and will ordered by frequency in descending order. The function will return a list of tuples with
    a word and its frequency
    '''
    try:
        con = sqlite3.connect('ebooks.db')
        cur = con.cursor()

        # Minimum word frequency
        n = 1

        cur.execute("""SELECT word, frequency FROM ebooks WHERE book = ? AND frequency >= ? ORDER BY frequency DESC""", (book_name,n))

        # Return a list of tuples
        return cur.fetchall()
    except sqlite3.Error as e:
        print(f"Error sorting data: {e}")



def insert_data(book_name, word_frequency):
    '''
    insert_data() will take in a string parameter 'book' that will be the name of the book and a dictionary parameter
    'word_frequency' that will be a dictionary of words and their frequency. It will then insert the data into the book
    name, word, word frequency into the local database table 'ebooks'.
    '''

    con = sqlite3.connect('ebooks.db')
    cur = con.cursor()

    try:
        for word, freq in word_frequency.items():
            input_tuple = (book_name, word, freq)
            cur.execute('INSERT INTO ebooks VALUES (?, ?, ?)', input_tuple)
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    finally:
        con.commit()
        con.close()



def print_data(book_word_frequencies, x = 10):
    '''
    print_data() will print the top 'x' most frequent words in the book. It will take in a list of tuples 'book' and
    an integer 'x' as parameters. It will then print the top 'x' most frequent words in the book into the output box.
    '''
    for i, word in enumerate(book_word_frequencies):
        if i >= x:
            break
        curr_word = f'{i + 1}) {word[0]}: {word[1]}\n'
        output.insert(END, curr_word)




def drop_table():
    '''
    drop_table() will drop the table 'ebooks' if it exists.
    '''
    try:

        con = sqlite3.connect('ebooks.db')
        cur = con.cursor()

        # Drop the 'ebooks' table if it exists
        cur.execute('DROP TABLE IF EXISTS ebooks')

        con.commit()
        con.close()
    except sqlite3.Error as e:
        print(f"Error dropping table: {e}")







class MyEbookParser(HTMLParser):

    def __init__(self):
        '''
        MyEbookParser() will initialize the HTMLParser class and will create an empty list 'text' that will store all the
        words found in the book.
        '''

        HTMLParser.__init__(self)
        self.text = []


    def handle_data(self, data):
        '''
        handle_data() will take in a string parameter 'data' and will find all the words in 'data' that match the
        pattern and add them to the list 'text'.
        '''
        try:
            words = re.findall(r'\b\w+\b', data)
            self.text.extend(words)
        except Exception as e:
            print(f'Error in handle_data: {e}')



    def frequency(self):
        '''
        frequency() create an empty dictionary 'word_frequency' and will access the member attribute
        list of tuples 'text' and will check each tuple is inside the 'word_frequency' dictionary. If the tuple is not
        inside the dictionary then it will add it to the dictionary with a value of 1. If the tuple is already in the dictionary
        then it will increment the value by 1. The function will return the dictionary 'word_frequency'.

        key: word, value: amount of times appeared
        '''
        word_frequency = {}

        for w in self.text:
            if w in word_frequency:
                word_frequency[w] += 1
            else:
                word_frequency[w] = 1

        return word_frequency



if __name__ == '__main__':
    create_database()



    # Used for Search Database button
    def click_local():
        '''
        click_local() will take the text from the 'local_text_entry' Entry box and will store it inside 'entered_text'
        and will call search_book() with 'entered_text' as a parameter. If the book is found in the local database
        then it will print the top 10 most frequent words in the book, otherwise it will print that the book was not
        found in the database.
        '''

        entered_text = local_text_entry.get().lower()
        output.delete(0.0, END)

        # Sorted dictionary of words and their frequency in descending order
        book_word_frequencies = search_book(entered_text)

        # Top 'x' most frequent words in the book
        x = 10

        # Print the top 'x' most frequent words in the book
        if book_word_frequencies:
            output.insert(END,f'Found in the local database.\nTop {x} most frequent words in "{local_text_entry.get()}":\n')
            print_data(book_word_frequencies, x)
        # If the book is not found in the database
        else:
            output.delete(0.0, END)
            not_found = (f'"{local_text_entry.get()}" not found in the database.\n'
                         f'Enter the url from Project Gutenberg into the url text box to add it to the database.')
            output.insert(END, not_found)



    # Used for Search Database button
    def click_PG():
        '''
        click_PG() will take the url text from the 'PG_text_entry' Entry box and will store it inside 'url', it will also
        take the string number from the 'PG_user_display_number' Entry box and will store it inside 'x'. If 'x' is empty then
        x will be set to the default of 10, otherwise it will be set to what the user entered.

        The function will then call urlopen() with 'url' as a parameter will parse through the Project Gutenberg url
        and will call frequency() to get the word frequency of the book.

        The data will be entered into the local database by calling insert_data() with the book name
        from what the user entered in 'local_text_entry' Entry box when searching locally and the word frequency
        from return of frequency() as parameters.

        The function will then call sort_data() with the book name from what the user entered in 'local_text_entry'
        to sort the data by the top 'x' most frequent words in the book.

        This function can take .html and .txt url links from Project Gutenberg.
        '''

        url = PG_text_entry.get().lower()
        x = PG_user_display_number.get()
        # if x is not an empty string
        if x:
            x = int(x) #Convert string to int
        else:
            x = 10
        output.delete(0.0, END)

        try:
            response = urlopen(url)
            content = response.read()
            html_doc = content.decode().lower()
            parser = MyEbookParser()
            parser.feed(html_doc)
        except Exception as e:
            output.delete(0.0, END)
            output.insert(END, f'Connection error with URL: {e}')

        # Dictionary of words and their frequency
        word_frequency = parser.frequency()
        insert_data(local_text_entry.get().lower(), word_frequency)

        # Sorted dictionary of words and their frequency in descending order
        book_word_frequencies = sort_data(local_text_entry.get().lower())

        # Print the top 'x' most frequent words in the book
        if book_word_frequencies:
            output.insert(END,f'Top {x} most frequent words in "{local_text_entry.get()}":\n')
            print_data(book_word_frequencies, x)



    # Used for Exit button
    def close_window():
        '''
        close_window() will close and exit the program
        '''
        window.destroy()
        exit()



    window = Tk()
    window.title("My eBook Database")

    # 1 Welcome label
    Label(window, text='Welcome to my eBook Database!',
          font='Helvetica 12 bold').grid(row=1, column=0, sticky='w')

    # 2 Directions label (Local)
    Label(window, text='Enter the book title you want to find in the database:',
          font='Helvetica 10 bold').grid(row=2, column=0, sticky='w')

    # 3 Entry box(Local)
    local_text_entry = Entry(window, width=50, bg='pale green1', highlightbackground='black', highlightthickness=1)
    local_text_entry.grid(row=3, column=0, sticky='w')

    # 4 Search button(Local)
    (Button(window, text='SEARCH DATABASE', font='Helvetica 10 bold', bg='lime green', width=16, command=click_local)
     .grid(row=4, column=0, sticky='w'))

    # 5 Directions label (Project Gutenberg URL)
    Label(window, text='Enter the URL below of the book from Project Gutenberg:',
          font='Helvetica 10 bold').grid(row=5, column=0, sticky='w')

    # 6 Entry box (Project Gutenberg URL)
    PG_text_entry = Entry(window, width=70, bg='lightskyblue1', highlightbackground='black', highlightthickness=1)
    PG_text_entry.grid(row=6, column=0, sticky='w')

    # 7 Directions label (Project Gutenberg User Display Number)
    Label(window, text='Enter the number of word frequencies to be displayed (Default: 10):',
          font='Helvetica 10 bold').grid(row=7, column=0, sticky='w')

    # 8 Entry box (Project Gutenberg User Display Number)
    PG_user_display_number = Entry(window, width=5, bg='lightskyblue1', highlightbackground='black', highlightthickness=1)
    PG_user_display_number.grid(row=8, column=0, sticky='w')

    # 9 Search button(Project Gutenberg)
    (Button(window, text='SEARCH PROJECT GUTENBERG', font='Helvetica 10 bold', bg='dodger blue', width=25, command=click_PG)
     .grid(row=9, column=0, sticky='w'))

    # 10 Empty label for spacing
    Label(window, text='', font='Helvetica 10 bold').grid(row=10, column=0, sticky='w')

    # 11 Results label
    Label(window, text='Results:',
          font='Helvetica 12 bold').grid(row=11, column=0, sticky='w')

    # 12 Output box
    output = Text(window, width=40, height=12, wrap=WORD, bg='light grey')
    output.grid(row=12, column=0, sticky='w')

    # 13 Exit Button
    (Button(window, text='EXIT', font='Helvetica 10 bold', bg='red', command=close_window)
     .grid(row=13, column=0, sticky='w'))

    window.mainloop()