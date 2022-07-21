def print_section_break(title: str, add_leading_line_breaks=True):
    if add_leading_line_breaks:
        print()
        print()
    print('#' * 30)
    print(title.upper())
    print('#' * 30)
    print()


# Defining a main function
def main():
    print_section_break('main function', False)
    print('Hello World')


if __name__ == "__main__":
    main()

# Slices
print_section_break('slices')
number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f'List: {number_list}')
print(f'Slice [1:3]: {number_list[1:3]}')
print(f'Slice [1:4]: {number_list[1:4]}')
print(f'Slice (every second number) [1:5:2]: {number_list[1:5:2]}')
print(f'Slice (reverse) [:-1]: {number_list[:-1]}')
print(f'Slice (reverse) [9:1:-2]: {number_list[9:1:-2]}')
print(f'Slice (reverse) [9::-1]: {number_list[9::-1]}')

saved_slice = slice(4, 0, -1)
print(f'Slice (saved) {saved_slice}: {number_list[saved_slice]}')

saved_slice = slice(4, None, -1)
print(f'Slice (saved) {saved_slice}: {number_list[saved_slice]}')

# Tuples
print_section_break('tuples')
# Reminder: Tuples are immutable and fixed length in comparison to lists
some_tuple = (1, 2)
print(f'Tuple index 0 = {some_tuple[0]} and 1 = {some_tuple[1]}')
tuple_list = [(1, 2), (3, 4)]
print(f'First index of first tuple: {tuple_list[0][0]}')
print(f'Second index of second tuple: {tuple_list[1][1]}')
print(f'Is in list? {(1, 2) in tuple_list}')

tuple_list_unequal = [(1, 2), (3, 4), (5, 6, 'hello')]
print(f'Is (1, 2) in List? {(1, 2) in tuple_list_unequal}')
print(f'Is (5, 6) in List? {(5, 6) in tuple_list_unequal}')
print('Is (5, 6, \'hello\') in List? {0}'.format((5, 6, 'hello') in tuple_list_unequal))

tuple_in_tuple = (1, (2, 3))
print(f'Tuple in tuple: {tuple_in_tuple[1][1]}')

tuple_with_numbers = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
for number in tuple_with_numbers:
    print(f'number is {number}')
print(f'Tuple slice {tuple_with_numbers[5::-1]}')

first_tuple = (1, 2)
second_tuple = (3, 4)
print(f'Tuples added {first_tuple + second_tuple}')
print(f'Tuples doubled {first_tuple * 2}')

print(f'Tuple length: {len(tuple_with_numbers)}')
print(f'Tuple min: {min(tuple_with_numbers)}')
print(f'Tuple min on complex tuples {min(((1, 2), (3, 4)))}')
print(f'Tuple min on complex tuples {min(((4, 1), (3, 4)))}')

# Unpacking
print_section_break('unpacking')
a, b = 1, 2
print(f'Unpacking variable a={a}')
print(f'Unpacking variable b={b}')
# c, d = 1 => TypeError: cannot unpack non-iterable int object
# e, f, g = 1, 2 => ValueError: not enough values to unpack (expected 3, got 2)

(a, b, c) = (1, 2, 3)
print(f'Unpacking a tuple of variables: {a} {b} {c}')

a, b, c = (1, 2, 3)
print(f'Unpacking a tuple to variables: {a} {b} {c}')

# End
print()
print()
