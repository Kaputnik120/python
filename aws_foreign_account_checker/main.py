import json
import re
import time

import boto3
import mypy_boto3_iam

total_roles = 0
total_policies = 0
account_numbers_found = set()
account_numbers_allowed = {'736815776541', '831269439992', '349546234265', '944132310209', '972874111695',
                           '301497165819'}  # known customer accounts
iam_client = boto3.client('iam')  # type mypy_boto3_iam.client
account_pattern = re.compile('([0-9]{12})')
account_pattern_arn = re.compile('arn.*:([0-9]{12}):')


def main():
    print('Listing allowed account numbers')
    with open('../../europace/aws-sso/globals.tf') as file:
        file_content = (file.read())
    allowed_accounts_definition = file_content

    global account_numbers_allowed
    account_numbers_allowed = account_numbers_allowed | set(account_pattern.findall(allowed_accounts_definition))

    print('Getting initial iam roles')
    roles = iam_client.list_roles()

    iterate_roles_with_policies(roles)
    marker: str = roles['Marker']

    while marker != 'null':
        roles = iam_client.list_roles(Marker=marker)

        if 'Marker' in roles:
            marker = roles['Marker']
        else:
            marker = 'null'

        iterate_roles_with_policies(roles)

    print(f'Checked {total_roles} roles')
    print(f'Checked {total_policies} policies')
    print(f'Allowed account numbers: {account_numbers_allowed}')
    print(f'Found account numbers: {account_numbers_found}')
    print(f'Suspicious account numbers: {account_numbers_found - account_numbers_allowed}')


def iterate_roles_with_policies(roles):
    global total_roles
    total_roles += len(roles['Roles'])
    total_loop_roles = len(roles['Roles'])
    current_loop_roles = 0

    for role in roles['Roles']:
        current_loop_roles += 1
        role_name = role['RoleName']
        global total_policies

        print(f'\n{role_name}:')

        marker = None
        while marker != 'null':

            inline_policies: dict
            if marker is None:
                inline_policies = iam_client.list_role_policies(RoleName=role_name)
            else:
                inline_policies = iam_client.list_role_policies(RoleName=role_name, Marker=marker)

            if 'Marker' in inline_policies:
                marker = inline_policies['Marker']
            else:
                marker = 'null'

            total_policies += len(inline_policies['PolicyNames'])

            for inline_policy_name in inline_policies['PolicyNames']:
                print(f'[inline] {inline_policy_name}')
                get_and_check_policy(role_name=role_name, policy_name=inline_policy_name, retries=0, is_named=False)

        marker = None
        while marker != 'null':

            named_policies: dict
            if marker is None:
                named_policies = iam_client.list_attached_role_policies(RoleName=role_name)
            else:
                named_policies = iam_client.list_attached_role_policies(RoleName=role_name)

            if 'Marker' in named_policies:
                marker = named_policies['Marker']
            else:
                marker = 'null'

            total_policies += len(named_policies['AttachedPolicies'])

            for named_policy in named_policies['AttachedPolicies']:
                print('[attached] {0}'.format(named_policy['PolicyName']))
                get_and_check_policy(policy_arn=named_policy['PolicyArn'], retries=0, is_named=True)

    if current_loop_roles % 10 != 0:
        print(f'Checked {total_loop_roles}/{total_loop_roles} roles')


def get_and_check_policy(retries: int, is_named: bool, role_name='', policy_name='', policy_arn=''):
    if retries == 0:
        pass
    else:
        sleep_seconds = 2 ** retries * 100 / 1000
        print(f'Waiting for {sleep_seconds}s')
        time.sleep(sleep_seconds)

    # noinspection PyBroadException
    try:
        if is_named:
            if len(policy_arn) < 20:
                raise ValueError(f'Policy arn \'{policy_arn}\' is shorter than 20 characters')

            policy_versions_paginator = iam_client.get_paginator(
                'list_policy_versions')  # type: mypy_boto3_iam.ListPolicyVersionsPaginator
            policy_versions_for_arn = policy_versions_paginator.paginate(PolicyArn=policy_arn)
            version: str
            for policy_versions_page in policy_versions_for_arn:
                for policy_version in policy_versions_page['Versions']:
                    if policy_version['IsDefaultVersion']:
                        version = policy_version['VersionId']
                        break

            # noinspection PyUnboundLocalVariable
            default_policy_version = iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=version)
            policy_document = json.dumps(default_policy_version['PolicyVersion']['Document'])
        else:
            policy = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
            policy_document = json.dumps(policy['PolicyDocument'])

        policy_account_numbers = set(account_pattern_arn.findall(policy_document))
        if policy_account_numbers:
            print(f'Account numbers: {policy_account_numbers}')
            global account_numbers_found
            account_numbers_found = account_numbers_found | policy_account_numbers
            policy_account_numbers_suspicious = policy_account_numbers - account_numbers_allowed
            if policy_account_numbers_suspicious:
                print(f'Suspicious account numbers: {policy_account_numbers_suspicious}')
    except ValueError as e:
        raise e
    except Exception as e:
        print(e)
        retries += 1
        if is_named:
            get_and_check_policy(policy_name=policy_name, role_name=role_name, retries=retries, is_named=is_named)
        else:
            get_and_check_policy(policy_arn=policy_arn, retries=retries, is_named=is_named)


if __name__ == '__main__':
    main()
