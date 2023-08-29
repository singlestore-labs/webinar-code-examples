import segment.analytics as analytics
from dotenv import load_dotenv
from faker import Faker
from datetime import datetime
import random
import os
import time


fake = Faker()
load_dotenv()

analytics.write_key = os.getenv('SEGMENT_WRITE_KEY')

customers = []
signup_actions = ['sign_up', 'log_in', 'confirm_email', 'completed_setup', 'added_payment_info', 'start_subscription', 'end_subscription']
app_actions = ['opened_app', 'viewed_dashboard', 'viewed_todo', 'add_todo', 'complete_todo', 'delete_todo', 'edit_todo']

# a function that uses faker to fake a user with first/last name, email, and phone number. also add a way to generate a 16 character alphanumeric id

def fake_user():
    return {
        "userId": fake.uuid4(),
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": fake.email(),
        "phone": fake.phone_number()
    }

# a function that appends a fake user to the customers list

def add_fake_user():
    customers.append(fake_user())

# a function that outputs a random number between 0 and 6

def random_action():
    return random.randint(0, 6)

# a function that selects the indexed item using an argument integer and the list name as argument

def select_action(index, list_name):
    return list_name[index]

# a function that records a user action using the segment analytics library. the function should take a user id, action name, and a dictionary of properties as arguments

def record_action(user_id, action_name, properties):
    analytics.track(user_id, action_name, properties)

# the signup_actions list contains all the actions that a user can take when signing up for the app and going through the setup steps. they should be considered successive and completed in order. end_subscription should be rare.
# a function that loops through the users in the customers list and creates records for each of the signup actions for each user. the users should not all complete all of the signup actions, but they should be completed in order.
# the function should output each user and their signup actions to the console in a dictionary format

def signup():
    for customer in customers:
        action_counter = 0
        action_count = random_action()
        analytics.identify(customer['userId'], {
            "firstName": customer['firstName'],
            "lastName": customer['lastName'],
            "email": customer['email'],
            "phone": customer['phone'],
            'created_at': '{}'.format(datetime.now())
        })
        time.sleep(3)
        customer['signup_actions'] = []
        while action_counter <= action_count:
            action = select_action(action_counter, signup_actions)
            record_action(customer['userId'], action, {
                'time': datetime.now()
            })
            time.sleep(1.1)
            action_counter += 1
            customer['signup_actions'].append(action)
        # add a small delay
        time.sleep(1.1)
    print(customers)

# a function that loops through each customer in the customers list and then creates a random number of app actions for each user. Each app action should be recorded with a timestamp. Only generate app actions for users that have signed up and logged in.

def taking_actions(customer):
    if 'signup_actions' in customer and 'log_in' in customer['signup_actions']:
        action_counter = 0
        action_count = random_action()
        customer['app_actions'] = []
        while action_counter <= action_count:
            action = select_action(action_counter, app_actions)
            record_action(customer['userId'], action, {
                'time': datetime.now()
            })
            customer['app_actions'].append(action)
            action_counter += 1
            # add a small delay
            time.sleep(random.randint(1, 9))

# a function that generates n number of fake users

def generate_users(n):
    for i in range(n):
        add_fake_user()

def fake_actions_loop(customers):
    while True:
        for customer in customers:
                taking_actions(customer)

# a function that generates n number of fake users and then runs the signup and app actions functions

def generate_data(n):
    generate_users(n)
    signup()
    fake_actions_loop(customers)

generate_data(100)