import random
import sqlite3

conn = sqlite3.connect('card.s3db')
c = conn.cursor()
c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='card' ''')
res_table = c.fetchone()
if res_table[0] == 0:
    c.execute('''CREATE TABLE card
    (id INTEGER PRIMARY KEY,
    number TEXT,
    pin TEXT, 
    balance INTEGER DEFAULT 0)''')
    conn.commit()

class Menu:
    def ui_input(self):
        a = input()
        self.make(a)

    def __init__(self):
        self.state = 'action'
        # self.cards = {}
        self.card = ''
        self.transfer_account = ''
        self.ui_input()

    def create_account(self):
        print('\nYour card has been created\nYour card number:')
        # first step, 9 random digits after '400000'
        new_card = '400000' + '{:09d}'.format(random.randint(0, 999999999))
        digits = list(new_card)
        # multiply and subtract 9 step (odd digits by 2)
        for i in range(0, len(digits), 2):
            digits[i] = int(digits[i]) * 2
            if digits[i] > 9:
                digits[i] -= 9
            digits[i] = str(digits[i])
        # adding all 15 digits and finding the 16th digit
        x = sum(map(lambda y: int(y), digits)) % 10
        if x == 0:
            last_digit = 0
        else:
            last_digit = 10 - x
        new_card2 = list(new_card)
        new_card2.append(str(last_digit))
        card_number = ''.join(new_card2)
        # pin
        new_pin = '{:04d}'.format(random.randint(0, 9999))
        c.execute('''INSERT INTO card (number, pin) 
                    VALUES (?, ?)''', (card_number, new_pin))
        conn.commit()
        c.execute('''SELECT
                        number, pin 
                    FROM 
                        card
                    WHERE
                        number = ?
                  ''', (card_number,))
        res_ = c.fetchone()
        print('{}\nYour card PIN:\n{}'.format(res_[0], res_[1]))
        print('\n1. Create an account\n2. Log into account\n0. Exit')
        return self.ui_input()

    def login(self, x):
        c.execute('''SELECT
                        number, pin 
                    FROM 
                        card
                    WHERE
                        number = ?
                  ''', (self.card,))
        res_ = c.fetchone()
        if res_ is not None and res_[1] == x:
            print('\nYou have successfully logged in!\n')
            self.state = 'logged_in'
            print("1. Balance\n2. Log out\n0. Exit")
        else:
            print('\nWrong card number or PIN!\n')
            self.state = 'action'
            print("1. Create an account\n2. Log into account\n0. Exit")
        return self.ui_input()

    def balance(self):
        c.execute('''SELECT
                        number, balance 
                    FROM 
                        card
                    WHERE
                        number = ?
                  ''', (self.card,))
        res_ = c.fetchone()
        print('\nBalance: ', res_[1])
        print('\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
        return self.ui_input()

    def add_income(self, x):
        c.execute('''UPDATE
                        card
                    SET
                        balance = balance + ?
                    WHERE
                        number = ?
                  ''', (x, self.card,))
        conn.commit()
        print('Income was added!')
        print('\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
        self.state = 'logged_in'
        return self.ui_input()

    def close_account(self):
        c.execute('''DELETE FROM
                        card
                    WHERE
                        number = ?
                  ''', (self.card,))
        conn.commit()
        print('\nThe account has been closed!')
        print('\n1. Create an account\n2. Log into account\n0. Exit')
        return self.ui_input()

    def luhn_check(self, x):
        transfer_account = x
        if transfer_account[:6] == '400000':
            digits = list(transfer_account)
            last_digit = digits.pop()
            # multiply and subtract 9 step (odd digits by 2)
            for i in range(0, len(digits), 2):
                digits[i] = int(digits[i]) * 2
                if digits[i] > 9:
                    digits[i] -= 9
                digits[i] = str(digits[i])
            # adding all 15 digits and finding the 16th digit
            y = sum(map(lambda z: int(z), digits)) % 10
            if y == 10 - int(last_digit):
                return self.transfer_check(x)
            else:
                print('Probably you made mistake in the card number. Please try again!')
                print('\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
                self.state = 'logged_in'
                return self.ui_input()
        else:
            print('Such a card does not exist.')
            print('\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            self.state = 'logged_in'
            return self.ui_input()

    def transfer_check(self, x):
        c.execute('''SELECT
                        number, balance 
                    FROM 
                        card
                    WHERE
                        number = ?
                  ''', (x,))
        res_ = c.fetchone()
        if self.card == x:
            self.state = 'logged_in'
            print("You can't transfer money to the same account!")
            print('\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            return self.ui_input()
        elif res_ is None:
            self.state = 'logged_in'
            print('Such a card does not exist.')
            print('\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            return self.ui_input()
        else:
            self.transfer_account = x
            print('Enter how much money you want to transfer:')
            self.state = 'transfer_amount'
            return self.ui_input()

    def make_transfer(self, x):
        c.execute('''SELECT
                        number, balance 
                    FROM 
                        card
                    WHERE
                        number = ?
                  ''', (self.card,))
        res_ = c.fetchone()
        if res_[1] >= int(x):
            c.execute('''UPDATE
                            card
                        SET
                            balance = balance - ?
                        WHERE
                            number = ?
                      ''', (x, self.card,))
            conn.commit()
            c.execute('''UPDATE
                            card
                        SET
                            balance = balance + ?
                        WHERE
                            number = ?
                      ''', (x, self.transfer_account,))
            conn.commit()
            print('Success!')
            print('\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')

        else:
            print('Not enough money!')
            print('\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
        self.state = 'logged_in'
        return self.ui_input()

    def make(self, xxx):
        if self.state == 'action':
            if xxx == '1':
                return self.create_account()
            elif xxx == '2':
                print('\nEnter your card number:')
                self.state = 'card_number'
                return self.ui_input()
            elif xxx == '0':
                print('\nBye!')
                self.state = None
                return None
        elif self.state == 'card_number':
            print('Enter your PIN:')
            self.state = 'pin_number'
            self.card = xxx
            return self.ui_input()
        elif self.state == 'pin_number':
            return self.login(xxx)
        elif self.state == 'logged_in':
            if xxx == '1':
                return self.balance()
            elif xxx == '2':
                print('\nEnter income:')
                self.state = 'add_income'
                return self.ui_input()
            elif xxx == '3':
                print('\nTransfer\nEnter card number:')
                self.state = 'transfer'
                return self.ui_input()
            elif xxx == '4':
                self.state = 'action'
                return self.close_account()
            elif xxx == '5':
                print('\nYou have successfully logged out!')
                print('\n1. Create an account\n2. Log into account\n0. Exit')
                self.state = 'action'
                return self.ui_input()
            elif xxx == '0':
                print('\nBye!')
                self.state = None
                return None
        elif self.state == 'add_income':
            self.state = 'logged-in'
            return self.add_income(xxx)
        elif self.state == 'transfer':
            return self.luhn_check(xxx)
        elif self.state == 'transfer_amount':
            return self.make_transfer(xxx)


print('1. Create an account\n2. Log into account\n0. Exit')

todo = Menu()
