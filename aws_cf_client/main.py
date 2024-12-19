import getopt
import sys
import time

import boto3
import mypy_boto3_cloudformation

total_stacks = 0
template_fragment = None
cf = None  # type: mypy_boto3_cloudformation.client


def main(argv):
    global template_fragment

    try:
        opts, args = getopt.getopt(argv, "h", ["search-string="])
    except getopt.GetoptError as e:
        print(e)
        print('--search-string=<search string> -h')
        sys.exit(2)

    print(opts)
    print(args)

    for opt, arg in opts:
        if opt == '-h':
            print('--search-string=<search string> -h')
            sys.exit()
        if opt == '--search-string':
            template_fragment = arg

    if template_fragment is None:
        print('Mandatory option --search-string not set')
        sys.exit()

    print(f'Searching for \'{template_fragment}\' in stacks')
    print('Creating client')
    global cf
    cf = boto3.client('cloudformation')

    print('Getting initial CF-stacks')

    stacks = cf.list_stacks()
    check_stacks(stacks)
    next_token: str = stacks['NextToken']

    while next_token != 'null':
        print()
        print('=' * 30)
        print('Getting next CF-stacks')
        stacks = cf.list_stacks(NextToken=next_token)

        if 'NextToken' in stacks:
            next_token = stacks['NextToken']
        else:
            next_token = 'null'

        check_stacks(stacks)

    print(f'Checked {total_stacks} stacks')


def check_stacks(stacks_param):
    print('Checking CF-stacks')

    total = len(stacks_param['StackSummaries'])
    i = 0
    for stack in stacks_param['StackSummaries']:
        i += 1
        global total_stacks
        total_stacks += 1

        stack_id = stack['StackId']
        stack_name = stack['StackName']

        check_template(stack_id, stack_name, 0)

        if i % 10 == 0:
            print(f'Checked {i}/{total} stacks')
    if i % 10 != 0:
        print(f'Checked {total}/{total} stacks')


def check_template(stack_id, stack_name, retries):
    if retries == 0:
        pass
    else:
        sleep_seconds = 2 ** retries * 100 / 1000
        print(f'Waiting for {sleep_seconds}s')
        time.sleep(sleep_seconds)

    # noinspection PyBroadException
    try:
        stack_template: str = str(cf.get_template(StackName=stack_id))
        if template_fragment in stack_template:
            print(f'Found {template_fragment} in template for stack {stack_id}({stack_name})')
            print(f'Template is {stack_template}')
    except Exception as e:
        retries += 1
        check_template(stack_id, stack_name, retries=retries)


if __name__ == "__main__":
    main(sys.argv[1:])
