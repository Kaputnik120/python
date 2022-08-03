class DatabaseInterface:
    QUERY_TYPE_FIRST_NAME = 'f'
    QUERY_TYPE_LAST_NAME = 'l'
    QUERY_TYPE_AGE = 'a'
    QUERY_TYPES = (QUERY_TYPE_FIRST_NAME, QUERY_TYPE_LAST_NAME, QUERY_TYPE_AGE)

    def __init__(self):
        self._database = (('Max', 'Mustermann', 30), ('Harald', 'der Haarige', 70), ('Test', 'McTest', 12))

    @staticmethod
    def _raise_error():
        raise SomeTechnicalError('Database deleted by admin')

    def query_first_name(self, first_name: str) -> tuple[tuple[str, str, int]]:
        query_result = tuple(filter(lambda database_entry: first_name in database_entry[0], self._database))
        return query_result

    def query_last_name(self, last_name: str) -> tuple[tuple[str, str, int]]:
        try:
            DatabaseInterface._raise_error()
        except SomeTechnicalError as ste:
            raise EnvError(ste)

        query_result = tuple(filter(lambda database_entry: last_name in database_entry[1], self._database))
        return query_result

    def query_age(self, age: int) -> tuple[tuple[str, str, int]]:
        query_result = tuple(filter(lambda database_entry: age == database_entry[2], self._database))
        return query_result


class UserError(Exception):
    pass


class EnvError(Exception):
    pass


class SomeTechnicalError(Exception):
    pass


class CodeLogicError(Exception):
    pass


class UserInputValidator:
    ERROR_MSG_INVALID_QUERY_TYPE = 'Invalid query type'
    ERROR_MSG_INVALID_QUERY = 'Query is not matching requirements'

    @staticmethod
    def validate_query_type(user_input: str):
        if not isinstance(user_input, str) or len(
                user_input) != 1 or user_input not in DatabaseInterface.QUERY_TYPES:
            raise UserError(UserInputValidator.ERROR_MSG_INVALID_QUERY_TYPE, user_input)

    @staticmethod
    def validate_query(user_input: str, query_type):
        match query_type:
            case DatabaseInterface.QUERY_TYPE_FIRST_NAME | DatabaseInterface.QUERY_TYPE_LAST_NAME:
                if not isinstance(user_input, str) or len(user_input) < 1 or len(user_input) > 10:
                    raise UserError(UserInputValidator.ERROR_MSG_INVALID_QUERY, user_input)
            case DatabaseInterface.QUERY_TYPE_AGE:
                try:
                    int(user_input)
                except Exception:
                    raise UserError(UserInputValidator.ERROR_MSG_INVALID_QUERY, user_input)


def main():
    while True:
        print('Which kind of query do you want to execute (f=firstname, l=lastname, a=age)')
        query_type = input()
        try:
            UserInputValidator.validate_query_type(query_type)
        except UserError as ue:
            print(ue)
            continue

        print('Please provide query string (max 10 digits for firstname and lastname queries)')
        query = input()
        try:
            UserInputValidator.validate_query(query, query_type)
        except UserError as ue:
            print(ue)
            continue

        try:
            database_interface = DatabaseInterface()
            query_result: tuple[tuple[str, str, int]]
            match query_type:
                case DatabaseInterface.QUERY_TYPE_FIRST_NAME:
                    query_result = database_interface.query_first_name(query)
                case DatabaseInterface.QUERY_TYPE_LAST_NAME:
                    query_result = database_interface.query_last_name(query)
                case DatabaseInterface.QUERY_TYPE_AGE:
                    query_result = database_interface.query_age(int(query))
                case _:
                    raise CodeLogicError(f'Invalid query type: \'{query_type}\'')

            print(query_result)
            print('Query successful')
        except EnvError:
            print(f'We had some technical difficulties. Please try again later.')
        except CodeLogicError as cle:
            print(f'Sorry, there\'s an unknown problem. Please file a bug with the following content: {cle}')

        print()
        continue


if __name__ == '__main__':
    main()
