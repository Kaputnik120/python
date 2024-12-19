import re


def main():
    file_names = ('../../europace/aws-sso/globals.tf',
                  '/Users/ulbu/OneDrive - EXXETA/Projekte/Europace/Troubleshooting/s3_reparped_bucket_rights.json')

    file_contents = []
    for file_name in file_names:
        with open(file_name) as file:
            file_contents.append(file.read())

    allowed_accounts_definition = file_contents[0]
    pattern = re.compile('([0-9]{12})')
    allowed_account_numbers = set(pattern.findall(allowed_accounts_definition))

    used_account_numbers_policy = file_contents[1]
    used_account_numbers = set(pattern.findall(used_account_numbers_policy))

    print(used_account_numbers - allowed_account_numbers)


if __name__ == '__main__':
    main()
