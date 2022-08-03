class Parent:
    some_static_variable: str  # Names can collide with instance variables

    def __init__(self):
        self.some_class_variable = 'Parent class variable'

    def run(self):
        # class variables should be declared in class body, but can be created in functions
        # noinspection PyAttributeOutsideInit
        self.some_other_class_variable = 'Parent other class variable'
        print(
            f'parent run with class variable {self.some_class_variable} and '
            f'other class variable {self.some_other_class_variable}')

        # Fails at runtime
        # def func_without_self():
        #   print('I have no self')


class Child1(Parent):

    def __init__(self):
        print('Child1 constructor called')

    def run(self):
        self.some_class_variable = 'Child1 overwritten class variable'
        print(f'child1 run with class variable {self.some_class_variable}')


class Child2(Parent):
    def __init__(self):
        print('Child2 constructor called')
        # Super-Constructor must be called to initialize Parent variables
        super(Child2, self).__init__()

    def run(self):
        print(f'child2 run with class variable from parent {self.some_class_variable}')
        self._private_func()

    def _private_func(self):
        print('I want to be used privately: ' + self.some_class_variable)

    # Never created functions like this, namings with __ are automatically prefixed and reserved for the Python runtime
    # noinspection PyMethodMayBeStatic
    def __never_do_this(self):
        print('Please kill me')

    def __del__(self):
        print('Delete called')

    @staticmethod
    def static_func():
        print('Hello, I\'m static')


class DiamondChild(Child1, Child2):

    def __init__(self):
        print('Who you gonna call? Constructor')
        super(DiamondChild, self).__init__()

    def run(self):
        print('Who you gonna call? Run')
        super(DiamondChild, self).run()


def main():
    parent = Parent()
    parent.run()

    child1 = Child1()
    child1.run()

    child2 = Child2()
    child2.run()
    del child2
    Child2.static_func()

    diamond_child = DiamondChild()
    diamond_child.run()


if __name__ == '__main__':
    main()
