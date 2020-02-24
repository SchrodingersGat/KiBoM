# -*- coding: utf-8 -*-

try:
    import mysql.connector
    from mysql.connector import errorcode
except:
    pass


def DBConnect(prefs):
    """
    Connect to a mysql database. Database data is stored in prefs.
    """
    db_config = {
        'user': prefs.db_user,
        'password': prefs.db_pass,
        'host': prefs.db_host,
        'database': prefs.db_db,
        'raise_on_warnings': True,
        'use_pure': False,
    }

    if prefs.mysql_available:
        if "".__ne__(prefs.db_user) and "".__ne__(prefs.db_pass) and "".__ne__(prefs.db_host) and "".__ne__(prefs.db_db):
            try:
                print("Connecting to database...")
                prefs.db_cnx = mysql.connector.connect(**db_config)
                print("Connected!")
                prefs.db_cursor = prefs.db_cnx.cursor(buffered=True)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Database connection error: something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)


def DBDisconnect(prefs):
    """
    Disconnect from a mysql database.
    """
    if prefs.mysql_available:
        if prefs.db_cnx is not None:
            prefs.db_cnx.commit()
        if prefs.db_cursor is not None:
            prefs.db_cursor.close()
        if prefs.db_cnx is not None:
            prefs.db_cnx.close()


def DBQuery(q, c, prefs):
    query = ""
    params = None
    param_name = None
    param_value = None
    args = None
    for q_elem in q:
        if q_elem == '{':  # '{' is the mark for parameter value
            params = {}
            continue
        if q_elem == '}':  # '}' is the mark for end parameter name-value tuple, so this query ends.
            break
        if query.startswith('CALL ') and q_elem == '(':  # '{' is the mark for args
            args = []
            continue
        if args is not None and q_elem == ')':  # '}' is the mark for end parameter name-value tuple, so this query ends.
            break

        if params or args is None:
            query = query + q_elem + ' '
        elif args is None:
            if param_name is None:
                param_name = q_elem
            else:
                if q_elem.startswith('$'):  # Then evaluate this value
                    param_value = eval(q_elem[1:], {'__builtins__': None}, {'component': c})
                else:
                    param_value = q_elem
            if param_name is not None and param_value is not None:
                params.update({param_name: param_value})
                param_name = None
                param_value = None
        elif args is not None:
            if q_elem.startswith('$'):  # Then evaluate this value
                q_elem = eval(q_elem[1:], {'__builtins__': None}, {'component': c})
            args.append(q_elem)

    if prefs.mysql_available:
        if prefs.db_cursor is not None:
            if 'call '.__eq__(query[0:5].lower()):
                query = query[5:].strip()
                if prefs.verbose:
                    print("Calling database stored procedure: " + query)
                    print("with arguments: ")
                    print(args)
                try:
                    return_tuple = prefs.db_cursor.callproc(query, args)
                except mysql.connector.Error as err:
                    print("Database access error: " + str(err))
                    return ""
                return_value = ""
                for result in prefs.db_cursor.stored_results():
                    for item in result.fetchall():
                        if "".__eq__(return_value):
                            return_value = ' '.join(item)
                        else:
                            return_value = return_value + ',' + ' '.join(item)
                if prefs.verbose:
                    print("Procedure returned: " + return_value)
                return(return_value)
            else:
                if prefs.verbose:
                    print("Executing database query: " + query)
                    print("with arguments: ")
                    print(params)
                try:
                    prefs.db_cursor.execute(query, params, multi=True)
                except mysql.connector.Error as err:
                    print("Database access error: " + str(err))
                    return ""
                return_tuple = prefs.db_cursor.fetchone()
                if return_tuple is not None:
                    return return_tuple[0]
                else:
                    return ""
