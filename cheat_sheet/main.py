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

print()
print()
