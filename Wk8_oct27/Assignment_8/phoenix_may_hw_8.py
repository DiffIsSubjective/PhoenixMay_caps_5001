"""
This is the code for assignment 8. It uses several classes of employees (and robots)
inside a restaurant.
"""

# QUESTION 1

class Person:
    """
    Person class takes name, job, and pay.
    Job defaults to None, pay to 0.
    """
    def __init__(self, name, job=None, pay = 0):
        self.name = name
        self.job = job
        self.pay = pay

    def applyRaise(self, percent):
        """
        Updates the pay attribute to increase by the input percentage.
        """
        self.percent = percent
        self.pay = self.pay * (1 + percent)

# Testing the applyRaise method by giving Ted here a 10% raise, $17 to $18.70 per hour
rec1 = Person("Ted", "Clerk", 17)

print(f"Before applying the raise, {rec1.name} is paid ${rec1.pay:.2f} per hour.")

rec1.applyRaise(0.1)

print(f"After applying the raise, {rec1.name} is now paid ${rec1.pay:.2f} per hour.")

# QUESTION 2

# All of these are pretty similar. Set up class, define attributes, set work method.
class Employee:
    """
    Employee class is made for other classes to inherit from.
    Takes name and salary. Salary defaults to None.
    """
    def __init__(self, name, salary=None):
        self.name = name
        self.salary = salary

    def work(self):
        return f"{self.name} does stuff."

class Chef(Employee):
    """
    Chef class inherits from employee.
    Chef takes name, salary is set to 50,000.
    """
    def __init__(self, name):
        self.name = name
        Employee.__init__(self, name, salary=50000)

    def work(self):
        return f"{self.name} makes food."

class PizzaRobot(Chef):
    """
    PizzaRobot inherits from Chef class.
    PizzaRobot takes name, salary is set to None.
    """
    def __init__(self, name):
        self.name = name
        Chef.__init__(self, name)
        self.salary = None

    def work(self):
        return f"{self.name} makes pizza."

class Server(Employee):
    """
    Server inherits from employee class.
    Server takes name, salary is set to 40,000.
    """
    def __init__(self, name):
        self.name = name
        Employee.__init__(self, name, salary=40000)

    def work(self):
        return f"{self.name} takes orders."

# This part tests the classes by making an instance of each, testing the salaries are correct for
# each class, and calling the work method to make sure it works right for each class.

rec2 = Employee("Eddie")
print(f"\nQuestions 2 and 3:\n\nEmployee class: {rec2.name}")
print(rec2.work())
if rec2.salary == None:
    print(f"With no salary set, Employee salary defaults to {rec2.salary} as instructed.")
else:
    raise ValueError("Base Employee salary should be negative for this default example!")

rec3 = Chef("Chuck")
print(f"\nChef class: {rec3.name}")
print(f"{rec3.work()}")
if rec3.salary == 50000:
    print(f"{rec3.name}'s salary is set to {rec3.salary}, since all chefs make $50,000 per year.")
else:
    raise ValueError("Salary for the chef was not $50,000!")

rec4 = PizzaRobot("Johnny-5")
print(f"\nPizzaRobot class: {rec4.name}")
print(f"{rec4.work()}")
if rec4.salary == None:
    print(f"{rec4.name}'s salary is set to {rec4.salary}, since robots do NOT get paid!")
else:
    raise ValueError("Salary for the robot wasn't None! Robots can't have money!")

rec5 = Server("Sullivan")
print(f"\nServer class: {rec5.name}")
print(f"{rec5.work()}")
if rec5.salary == 40000:
    print(f"{rec5.name}'s salary is set to {rec5.salary}, since all servers make $40,000 per year.")
else:
    raise ValueError("Salary for the server was not $40,000!")
