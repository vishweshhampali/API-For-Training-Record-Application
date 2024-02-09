#!/usr/bin/env python
"""
This is a simple web server for a training record application.
This backend has functionality to support recording training in an SQL database. 
It also supports user access/session control.
"""

# import the various libraries needed
import http.cookies as Cookie  # some cookie handling support
from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer,
)  # the heavy lifting of the web server
import urllib  # some url parsing support
import json  # support for json encoding
import sys  # needed for agument handling
import time  # time support
import sqlite3  # sql database
import random  # generate random numbers
import datetime
import calendar


def random_digits(n):
    """This function provides a random integer with the specfied number of digits and no leading zeros."""
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return random.randint(range_start, range_end)


# The following three functions issue SQL queries to the database.


def do_database_execute(op):
    """Execute an sqlite3 SQL query to database.db that does not expect a response."""
    print(op)
    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()
        cursor.execute(op)
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()


def do_database_fetchone(op):
    """Execute an sqlite3 SQL query to database.db that expects to extract a single row result. Note, it may be a null result."""
    print(op)
    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()
        cursor.execute(op)
        result = cursor.fetchone()
        print(result)
        db.close()
        return result
    except Exception as e:
        print(e)
        return None


def do_database_fetchall(op):
    """Execute an sqlite3 SQL query to database.db that expects to extract a multi-row result. Note, it may be a null result."""
    print(op)
    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()
        cursor.execute(op)
        result = cursor.fetchall()
        print(result)
        db.close()
        return result
    except Exception as e:
        print(e)
        return None


def do_database_execute_parameterised(op, variables):
    """Execute an sqlite3 SQL query to database.db that does not expect a response."""
    print(op)
    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()
        cursor.execute(op, variables)
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()


def do_database_fetchone_parameterised(op, variables):
    """Execute an sqlite3 SQL query to database.db that expects to extract a single row result. Note, it may be a null result."""
    print(op)
    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()
        cursor.execute(op, variables)
        result = cursor.fetchone()
        print(result)
        db.close()
        return result
    except Exception as e:
        print(e)
        return None


def do_database_fetchall_parameterised(op, variables):
    """Execute an sqlite3 SQL query to database.db that expects to extract a multi-row result. Note, it may be a null result."""
    print(op)
    try:
        db = sqlite3.connect("database.db")
        cursor = db.cursor()
        cursor.execute(op, variables)
        result = cursor.fetchall()
        print(result)
        db.close()
        return result
    except Exception as e:
        print(e)
        return None


# The following build_ functions return the responses that the front end client understands.
# You can return a list of these.


def build_response_message(code, text):
    """This function builds a message response that displays a message
    to the user on the web page. It also returns an error code."""
    return {"type": "message", "code": code, "text": text}


def build_response_skill(id, name, gained, trainer, state):
    """This function builds a summary response that contains one summary table entry."""
    return {
        "type": "skill",
        "id": id,
        "name": name,
        "gained": gained,
        "trainer": trainer,
        "state": state,
    }


def build_response_class(id, name, trainer, when, notes, size, max, action):
    """This function builds an activity response that contains the id and name of an activity type,"""
    return {
        "type": "class",
        "id": id,
        "name": name,
        "trainer": trainer,
        "when": when,
        "notes": notes,
        "size": size,
        "max": max,
        "action": action,
    }


def build_response_attendee(id, name, action):
    """This function builds an activity response that contains the id and name of an activity type,"""
    return {"type": "attendee", "id": id, "name": name, "action": action}


def build_response_redirect(where):
    """This function builds the page redirection response
    It indicates which page the client should fetch.
    If this action is used, it should be the only response provided."""
    return {"type": "redirect", "where": where}


# The following handle_..._request functions are invoked by the corresponding /action?command=.. request


def handle_login_request(iuser, imagic, content):
    """A user has supplied a username and password. Check if these are
    valid and if so, create a suitable session record in the database
    with a random magic identifier that is returned.
    Return the username, magic identifier and the response action set."""

    # 1. Check For valid inputs -- Pending

    response = []
    username = content["username"]
    password = content["password"]

    if not username or not password:
        # RETURNING RESPONSES
        response.append(build_response_message(101, "Please Enter Valid Credentials"))
        return [iuser, imagic, response]

    credentials_check_query = "SELECT userid, fullname, username, password  FROM users where username = ? and password = ?;"
    variable_values = (username, password)
    credentials_check_query_result = do_database_fetchone_parameterised(
        credentials_check_query, variable_values
    )

    if credentials_check_query_result:

        session_id = random_digits(5)
        user_id = credentials_check_query_result[0]
        magic_id = random_digits(10)

        iuser = user_id
        imagic = magic_id

        variable_values = (iuser,)
        # DELETING EXISTING SESSIONS
        session_delete_query = 'DELETE FROM "session" WHERE userid = ?;'
        do_database_execute_parameterised(session_delete_query, variable_values)

        variable_values = (session_id, iuser, imagic)
        # INSERTING NEW SESSION
        session_create_query = (
            'INSERT INTO "session" (sessionid, userid, magic) VALUES(?,?,?);'
        )
        do_database_execute_parameterised(session_create_query, variable_values)

        # SENDING RESPONSES
        response.append(build_response_message(0, "Login Successful"))
        response.append(build_response_redirect("/index.html"))

    else:
        response.append(
            build_response_message(201, "Invalid Credentials, Failed Login Attempt !!")
        )

    return [iuser, imagic, response]


def handle_logout_request(iuser, imagic, parameters):
    """This code handles the selection of the logout button.
    You will need to ensure the end of the session is recorded in the database
    And that the session magic is revoked."""

    response = []

    ## Add code here
    session_select_query = 'SELECT * FROM "session" WHERE userid = ? and magic = ?;'
    session_select_query_result = do_database_fetchall_parameterised(
        session_select_query, (iuser, imagic)
    )

    # DELETING USER AND SESSION
    if session_select_query_result:
        session_delete_query = 'DELETE FROM "session" WHERE userid = ? and magic = ?;'
        do_database_execute_parameterised(session_delete_query, (iuser, imagic))
        iuser = "!"

        # SENDING RESPONSES
        response.append(build_response_message(0, "Logout Succesfull"))
        response.append(build_response_redirect("/logout.html"))
    else:

        # SENDING RESPONSES
        response.append(build_response_message(102, "User Needs To Be Logged In !!"))
        response.append(build_response_redirect("/login.html"))

    return [iuser, imagic, response]


def handle_get_my_skills_request(iuser, imagic):
    """This code handles a request for a list of a users skills.
    You must return a value for all vehicle types, even when it's zero."""

    # 1. User in attendee tables , with date-time passed should be marked 'passed', 'pending' or 'failed' in same order -- [DONE]
    # 2. Entries where class is cancelled or user is removed should not be shown here -- [DONE]
    # 3. If user is the trainer for that skill, then response should say 'trainer' --[DONE]

    response = []

    ## Add code here

    # CHECKING IF USER IS LOGGED IN
    if iuser and imagic:
        check_session_query = 'SELECT sessionid, userid, magic FROM "session" WHERE userid = ? and magic = ?;'
        check_session_query_result = do_database_fetchone_parameterised(
            check_session_query, (iuser, imagic)
        )

        # FETCHING USER'S SKILLS
        if check_session_query_result:
            query = (
                "SELECT t.skillid, s.name, u.fullname, (SELECT y.start FROM attendee x LEFT JOIN class y ON x.classid = y.classid WHERE x.userid = "
                + str(iuser)
                + " AND x.status = 1 AND y.skillid = t.skillid) 'start', 'trainer' AS 'status' FROM trainer t LEFT JOIN class c ON c.trainerid = t.trainerid LEFT JOIN skill s ON t.skillid = s.skillid LEFT JOIN users u ON t.trainerid = u.userid WHERE t.trainerid = "
                + str(iuser)
                + " GROUP BY 1,2,3,4,5 UNION ALL SELECT * FROM (SELECT skillid, name, fullname, start, status FROM ( SELECT d.skillid, d.name, e.fullname, b.start, CASE WHEN (a.status = 0 and b.start < unixepoch('now'))  THEN 'pending' WHEN (a.status = 0 and b.start >= unixepoch('now')) THEN 'scheduled' WHEN (a.status = 1) THEN 'passed' WHEN (a.status = 2) THEN 'failed' END 'status', CASE  WHEN a.status = 1 THEN 1 WHEN (a.status = 0 and b.start < unixepoch('now')) THEN 2 WHEN (a.status = 0 and b.start >= unixepoch('now')) THEN 3 WHEN (a.status = 2) THEN 4 END 'sorting_order',RANK() OVER(PARTITION BY name ORDER BY b.start DESC)rank FROM attendee a LEFT JOIN class b ON a.classid = b.classid LEFT JOIN skill d ON b.skillid = d.skillid LEFT JOIN trainer c ON d.skillid = c.trainerid LEFT JOIN users e ON c.trainerid = e.userid WHERE a.status != 3 and a.status != 4 and a.userid = "
                + str(iuser)
                + " and d.skillid not in (SELECT skillid FROM trainer WHERE trainerid = "
                + str(iuser)
                + ")) Z WHERE z.rank = 1 ORDER BY sorting_order) i ;"
            )
            query_result = do_database_fetchall(query)
            for row in query_result:
                skill_id = row[0]
                skill_name = row[1]
                skill_trainer = row[2]
                skill_time = row[3]
                skill_status = row[4]

                # SENDING RESPONSES
                response.append(
                    build_response_skill(
                        skill_id, skill_name, skill_time, skill_trainer, skill_status
                    )
                )
            response.append(build_response_message(0, "Skills Fetched, Success!!"))

        else:

            # SENDING RESPONSES
            response.append(build_response_message("200", "Please, Login!"))
            response.append(build_response_redirect("/login.html"))
    else:

        # SENDING RESPONSES
        response.append(build_response_message("200", "Please, Login!"))
        response.append(build_response_redirect("/login.html"))

    return [iuser, imagic, response]


def handle_get_upcoming_request(iuser, imagic):
    """This code handles a request for the details of a class."""

    # 1. Only the classes in future -- [DONE]
    # 2. Ordered as per earliest class -- [DONE]
    # 3. If user is trainer for the class then 'edit' -- [DONE]
    # 4. If class is in future and user has enrolled 'leave' -- [DONE]
    # 5. User not enrolled and not removed 'join' -- [DONE]
    # 6. If user is already signed up to another class with same skill, cant join other class with same skill 'unavailable' -- [MAYBE DONE]

    response = []

    ## Add code here

    # CHECKING IF USER LOGGED IN
    if iuser and imagic:
        check_session_query = 'SELECT sessionid, userid, magic FROM "session" WHERE userid = ? and magic = ?;'
        check_session_query_result = do_database_fetchone_parameterised(
            check_session_query, (iuser, imagic)
        )

        # FETCHING CLASS DETAILS
        if check_session_query_result:
            query = (
                "SELECT a.classid, c.name, b.fullname, a.start, a.note, (SELECT COUNT(attendeeid) FROM attendee x WHERE x.classid = a.classid AND x.status in (0)) AS 'class_size', a.max, CASE WHEN a.max = 0 OR ("
                + str(iuser)
                + " IN (SELECT x.userid FROM attendee x WHERE x.classid = a.classid AND status = 4)) THEN 'cancelled' WHEN "
                + str(iuser)
                + " = (SELECT p.trainerid FROM class p WHERE p.classid = a.classid) THEN 'edit' WHEN ("
                + str(iuser)
                + " IN (SELECT userid FROM attendee p WHERE p.classid = a.classid and p.status = 0)) AND (a.start >= unixepoch('now')) THEN 'leave' WHEN ((SELECT q.skillid FROM class p LEFT JOIN skill q ON q.skillid = p.skillid WHERE p.classid = a.classid) IN (SELECT r.skillid FROM attendee p LEFT JOIN class q ON p.classid = q.classid LEFT JOIN skill r ON r.skillid = q.skillid WHERE p.userid = "
                + str(iuser)
                + " AND p.status = 0 UNION ALL SELECT skillid FROM trainer t WHERE trainerid = "
                + str(iuser)
                + ")) THEN 'unavailable' WHEN ("
                + str(iuser)
                + " NOT IN (SELECT userid FROM attendee p WHERE p.classid = a.classid AND p.status IN (1,4) UNION ALL SELECT t2.trainerid FROM trainer t2 LEFT JOIN class c2 ON t2.skillid = c2.skillid WHERE c2.classid = a.classid )) THEN 'join' END 'action' FROM class a LEFT JOIN users b on a.trainerid = b.userid LEFT JOIN skill c on a.skillid = c.skillid LEFT JOIN trainer d on c.skillid = d.skillid WHERE a.start > unixepoch('now') GROUP BY 1,2,3,4,5,6,7,8 ORDER BY a.start ;"
            )
            query_result = do_database_fetchall(query)

            for row in query_result:
                class_id = row[0]
                class_name = row[1]
                class_trainer = row[2]
                class_start = row[3]
                class_note = row[4]
                class_size = row[5]
                class_max = row[6]
                class_action = row[7]

                # SENDING RESPONSES

                response.append(
                    build_response_class(
                        class_id,
                        class_name,
                        class_trainer,
                        class_start,
                        class_note,
                        class_size,
                        class_max,
                        class_action,
                    )
                )
            response.append(
                build_response_message(0, "Upcoming Class Fetched, Success!!")
            )
        else:

            # SENDING RESPONSES
            response.append(build_response_message("200", "Please, Login!"))
            response.append(build_response_redirect("/login.html"))
    else:

        # SENDING RESPONSES
        response.append(build_response_message("200", "Please, Login!"))
        response.append(build_response_redirect("/login.html"))

    return [iuser, imagic, response]


def handle_get_class_detail_request(iuser, imagic, content):
    """This code handles a request for a list of upcoming classes."""

    # 1. User is not trainer then error -- [DONE]
    # 2. User is trainer then send attendee and class response -- [DONE]

    response = []

    ## Add code here

    # INITIALISING VARIABLE TO STORE PARAMETER

    class_id = int(content["id"])

    # CHECKING IF USER IS LOGGED IN
    if iuser and imagic:
        check_session_query = 'SELECT sessionid, userid, magic FROM "session" WHERE userid = ? and magic = ?;'
        check_session_query_result = do_database_fetchone_parameterised(
            check_session_query, (iuser, imagic)
        )

        # FETCHING CLASS DETAILS
        if check_session_query_result:

            # check_class_exists = "SELECT classid FROM class c WHERE classid = ?"
            # check_class_exists_result = do_database_fetchone_parameterised(check_class_exists, (class_id,))
            # check_class_exists_flag = False

            # if check_class_exists_result and int(class_id) == check_class_exists_result[0]:
            # check_class_exists_flag = True
            # response.append(build_response_message(199, 'Class Doesn\'t Exist, Bad Parameter'))

            class_trainer_query = (
                "SELECT c.trainerid FROM class c WHERE classid = " + str(class_id) + ";"
            )
            class_trainer_query_result = do_database_fetchone(class_trainer_query)

            if (class_trainer_query_result) and (
                int(class_trainer_query_result[0]) == int(iuser)
            ):

                class_response_query = (
                    "SELECT * FROM (SELECT a.classid, c.name, b.fullname, a.start, a.note,(SELECT COUNT(attendeeid) FROM attendee x WHERE x.classid = a.classid AND x.status in (0)) AS 'class_size', a.max, CASE WHEN a.max = 0 OR ("
                    + str(iuser)
                    + " IN (SELECT x.userid FROM attendee x WHERE x.classid = a.classid AND status = 4)) THEN 'cancelled' WHEN "
                    + str(iuser)
                    + " = d.trainerid THEN 'cancel' WHEN ("
                    + str(iuser)
                    + " IN (SELECT userid FROM attendee p WHERE p.classid = a.classid)) AND (a.start >= unixepoch('now')) THEN 'leave' WHEN (("
                    + str(iuser)
                    + " NOT IN (SELECT userid FROM attendee p WHERE p.classid = a.classid)) AND ("
                    + str(iuser)
                    + " NOT IN (SELECT p.trainerid FROM trainer p WHERE p.skillid = a.skillid))) THEN 'join' END 'action' FROM class a LEFT JOIN users b on a.trainerid = b.userid LEFT JOIN skill c on a.skillid = c.skillid LEFT JOIN trainer d on c.skillid = d.skillid WHERE classid = "
                    + str(class_id)
                    + " AND userid = "
                    + str(iuser)
                    + ") z WHERE action IS NOT NULL;"
                )
                class_response_query_result = do_database_fetchone(class_response_query)

                class_id = class_response_query_result[0]
                class_name = class_response_query_result[1]
                class_trainer = class_response_query_result[2]
                class_when = class_response_query_result[3]
                class_notes = class_response_query_result[4]
                class_size = class_response_query_result[5]
                class_max = class_response_query_result[6]
                class_action = class_response_query_result[7]

                # SENDING RESPONSES
                response.append(
                    build_response_class(
                        class_id,
                        class_name,
                        class_trainer,
                        class_when,
                        class_notes,
                        class_size,
                        class_max,
                        class_action,
                    )
                )

                attendee_response_query = (
                    "SELECT a.attendeeid, u.fullname, CASE WHEN ((a.status = 0) AND (c.start >= unixepoch('now'))) THEN 'remove' WHEN a.status = 0 AND (c.start < unixepoch('now')) THEN 'update' WHEN a.status = 1 THEN 'passed' WHEN a.status = 2 THEN 'failed' WHEN ((a.status = 3) OR (a.status = 4)) THEN 'cancelled' END 'state' FROM attendee a LEFT JOIN users u ON a.userid = u.userid LEFT JOIN class c ON a.classid = c.classid WHERE a.classid = "
                    + str(class_id)
                    + ";"
                )
                attendee_response_query_result = do_database_fetchall(
                    attendee_response_query
                )

                for row in attendee_response_query_result:
                    attendee_id = row[0]
                    attendee_name = row[1]
                    attendee_state = row[2]

                    # SENDING RESPONSES
                    response.append(
                        build_response_attendee(
                            attendee_id, attendee_name, attendee_state
                        )
                    )

                # SENDING RESPONSES
                response.append(build_response_message(0, "Class Fetched, Success!"))
            else:

                # SENDING RESPONSES
                response.append(
                    build_response_message(203, "You're Not A Trainer For This Class")
                )
        else:

            # SENDING RESPONSES
            response.append(build_response_message(200, "Please, Login!"))
            response.append(build_response_redirect("/login.html"))
    else:

        # SENDING RESPONSES
        response.append(build_response_message(200, "Please, Login!"))
        response.append(build_response_redirect("/login.html"))

    return [iuser, imagic, response]


def handle_join_class_request(iuser, imagic, content):
    """This code handles a request by a user to join a class."""

    # 1. Class has space and isnt unavailable, then user can join -- [PENDING]
    # 2. If joins class size will increased by one in class response
    # 3. Can't join the class only if they are enrolled already to same skill, (passed and enrolled not allowed) -- [DONE]
    # 4. If removed they can't join the specific class -- [DONE]
    # 5. Can join another class though

    response = []

    ## Add code here

    # INTIALISING VARIABLE FOR PARAMETER
    try:
        class_id = content["id"]
    except:
        class_id = None

    # CHECKING IF THE USER IS LOGGED IN
    if iuser and imagic:
        check_session_query = 'SELECT sessionid, userid, magic FROM "session" WHERE userid = ? and magic = ?;'
        check_session_query_result = do_database_fetchone_parameterised(
            check_session_query, (iuser, imagic)
        )

        # INSERTING (JOINING) THE CLASS
        if check_session_query_result:
            if class_id is not None:
                # CHANGES TO BE MADE TO HAVE RANDOM NUMBER FOR ATTENDEE ID
                max_attendee_id_query = (
                    "SELECT attendeeid FROM attendee ORDER BY 1 DESC LIMIT 1;"
                )
                max_attendee_id_query_result = do_database_fetchone(
                    max_attendee_id_query
                )
                if max_attendee_id_query_result and 1 < max_attendee_id_query_result[0]:
                    max_attendee_id = max_attendee_id_query_result[0]
                else:
                    max_attendee_id = 1

                # CALCULATING REMAINING SPOTS IN CLASS
                check_class_space_query = (
                    "SELECT c.max - COUNT(a.attendeeid) FROM class c LEFT JOIN attendee a ON a.classid = c.classid WHERE c.classid = "
                    + str(class_id)
                    + " GROUP BY a.classid"
                )
                check_class_space_query_result = do_database_fetchone(
                    check_class_space_query
                )

                # CHECKING IF USER IS ALREADY ENROLLED TO THE SAME SKILL OR PASSED
                check_user_enrolled_passed_query = (
                    "SELECT a.userid FROM attendee a LEFT JOIN class c ON c.classid = a.classid WHERE userid = "
                    + str(iuser)
                    + " AND (a.status = 0 OR a.status = 1) AND c.skillid IN (SELECT c.skillid FROM class c WHERE c.classid = "
                    + str(class_id)
                    + " );"
                )
                check_user_enrolled_passed_query_result = do_database_fetchall(
                    check_user_enrolled_passed_query
                )
                check_user_enrolled_passed_flag = False

                if check_user_enrolled_passed_query_result and (
                    int(iuser)
                    in [i[0] for i in check_user_enrolled_passed_query_result]
                ):
                    check_user_enrolled_passed_flag = True
                    response.append(
                        build_response_message(
                            103, "You've Joined Similar Skill Already!"
                        )
                    )
                    print("here")

                # CHECKING IF USER IS ALREADY REMOVED FROM THIS CLASS
                check_user_removed_query = (
                    "SELECT userid FROM attendee WHERE classid = "
                    + str(class_id)
                    + " AND status = 4 AND userid = "
                    + str(iuser)
                    + ";"
                )
                check_user_removed_query_result = do_database_fetchone(
                    check_user_removed_query
                )
                check_user_removed_flag = False

                if check_user_removed_query_result and (
                    int(iuser) == check_user_removed_query_result[0]
                ):
                    check_user_removed_flag = True
                    response.append(
                        build_response_message(
                            103, "You've Been Removed From This Class!"
                        )
                    )
                    print("first here")

                # CHECKING IF CLASS EXISTS AND IT IS AN UPCOMING CLASS
                check_upcoming_class = (
                    "SELECT classid FROM class WHERE classid = "
                    + str(class_id)
                    + " AND start > unixepoch('now')"
                )
                check_upcoming_class_result = do_database_fetchone(check_upcoming_class)
                check_upcoming_class_flag = False

                if check_upcoming_class_result is None:
                    check_upcoming_class_flag = True

                if (
                    check_class_space_query_result
                    and (check_class_space_query_result[0] > 0)
                    and (not check_user_removed_flag)
                    and (not check_user_enrolled_passed_flag)
                    and (not check_upcoming_class_flag)
                ):
                    join_class_query = (
                        "INSERT INTO attendee (attendeeid, userid, classid, status) VALUES("
                        + str(max_attendee_id + 1)
                        + ","
                        + str(iuser)
                        + ","
                        + str(class_id)
                        + ",0);"
                    )
                    do_database_execute(join_class_query)

                    query = (
                        "SELECT a.classid, c.name, b.fullname, a.start, a.note, (SELECT COUNT(attendeeid) FROM attendee x WHERE x.classid = a.classid AND x.status in (0)) AS 'class_size',a.max, CASE WHEN a.max = 0 OR ("
                        + str(iuser)
                        + " IN (SELECT x.userid FROM attendee x WHERE x.classid = a.classid AND status = 4)) THEN 'cancelled' WHEN "
                        + str(iuser)
                        + " = d.trainerid THEN 'edit' WHEN ("
                        + str(iuser)
                        + " IN (SELECT userid FROM attendee p WHERE p.classid = a.classid and p.status = 0)) AND (a.start >= unixepoch('now')) THEN 'leave' WHEN ((SELECT q.skillid FROM class p LEFT JOIN skill q ON q.skillid = p.skillid WHERE p.classid = a.classid) IN (SELECT r.skillid FROM attendee p LEFT JOIN class q ON p.classid = q.classid LEFT JOIN skill r ON r.skillid = q.skillid WHERE p.userid = "
                        + str(iuser)
                        + " AND p.status = 0)) THEN 'unavailable' WHEN ("
                        + str(iuser)
                        + " NOT IN (SELECT userid FROM attendee p WHERE p.classid = a.classid and p.status = 4 or p.status = 1 )) THEN 'join'  END 'action' FROM class a LEFT JOIN users b on a.trainerid = b.userid LEFT JOIN skill c on a.skillid = c.skillid LEFT JOIN trainer d on c.skillid = d.skillid WHERE a.classid = "
                        + str(class_id)
                        + " ORDER BY a.start ;"
                    )
                    query_result = do_database_fetchall(query)

                    for row in query_result:
                        class_id = row[0]
                        class_name = row[1]
                        class_trainer = row[2]
                        class_start = row[3]
                        class_note = row[4]
                        class_size = row[5]
                        class_max = row[6]
                        class_action = row[7]

                        response.append(
                            build_response_class(
                                class_id,
                                class_name,
                                class_trainer,
                                class_start,
                                class_note,
                                class_size,
                                class_max,
                                class_action,
                            )
                        )

                    # SENDING RESPONSES
                    response.append(
                        build_response_message(0, "Joined Class Successfully")
                    )
                    # response.append(build_response_class(class_id, class_name, class_trainer, class_when, class_notes, class_size, class_max, class_action))
                    # response.append(build_response_redirect('////index.html'))
                else:
                    response.append(
                        build_response_message(203, "Sorry, Invalid Class Details")
                    )
            else:
                response.append(
                    build_response_message(101, "Missing class id parameter!")
                )
        else:

            # SENDING RESPONSES
            response.append(build_response_message(200, "Please, Login!"))
            response.append(build_response_redirect("/login.html"))
    else:

        # SENDING RESPONSES
        response.append(build_response_message(200, "Please, Login!"))
        response.append(build_response_redirect("/login.html"))

    return [iuser, imagic, response]


def handle_leave_class_request(iuser, imagic, content):
    """This code handles a request by a user to leave a class."""

    # 1. Leave a class if they are enrolled -- [DONE]
    # 2. If date/time is not passed -- [DONE]
    # 3. Send an updated class response -- [DONE]

    response = []

    ## Add code here

    # INITIALISING THE PARAMETER
    try:
        class_id = content["id"]
    except:
        class_id = None

    # CHECKING IF THE USER IS LOGGED IN
    if iuser and imagic:
        check_session_query = 'SELECT sessionid, userid, magic FROM "session" WHERE userid = ? and magic = ?;'
        check_session_query_result = do_database_fetchone_parameterised(
            check_session_query, (iuser, imagic)
        )

        if check_session_query_result:
            if class_id is not None:
                # CHECKING IF USER IS ENROLLED AND CLASS IS IN FUTURE
                check_user_enrolled_query = (
                    "SELECT a.userid FROM attendee a LEFT JOIN class c ON a.classid = c.classid WHERE a.userid = "
                    + str(iuser)
                    + " AND a.classid = "
                    + str(class_id)
                    + " AND c.start > unixepoch('now') ;"
                )
                check_user_enrolled_query_result = do_database_fetchone(
                    check_user_enrolled_query
                )

                # DELETING THE ATTENDEE
                if check_user_enrolled_query_result and (
                    int(iuser) == int(check_user_enrolled_query_result[0])
                ):

                    leave_class_query = (
                        "DELETE FROM attendee WHERE userid = "
                        + str(iuser)
                        + " AND classid = "
                        + str(class_id)
                        + ";"
                    )
                    do_database_execute(leave_class_query)

                    query = (
                        "SELECT a.classid, c.name, b.fullname, a.start, a.note, (SELECT COUNT(attendeeid) FROM attendee x WHERE x.classid = a.classid AND x.status in (0)) AS 'class_size', a.max, CASE WHEN a.max = 0 OR ("
                        + str(iuser)
                        + " IN (SELECT x.userid FROM attendee x WHERE x.classid = a.classid AND status = 4)) THEN 'cancelled' WHEN "
                        + str(iuser)
                        + " = (SELECT p.trainerid FROM class p WHERE p.classid = a.classid) THEN 'edit' WHEN ("
                        + str(iuser)
                        + " IN (SELECT userid FROM attendee p WHERE p.classid = a.classid and p.status = 0)) AND (a.start >= unixepoch('now')) THEN 'leave' WHEN ((SELECT q.skillid FROM class p LEFT JOIN skill q ON q.skillid = p.skillid WHERE p.classid = a.classid) IN (SELECT r.skillid FROM attendee p LEFT JOIN class q ON p.classid = q.classid LEFT JOIN skill r ON r.skillid = q.skillid WHERE p.userid = "
                        + str(iuser)
                        + " AND p.status = 0 UNION ALL SELECT skillid FROM trainer t WHERE trainerid = "
                        + str(iuser)
                        + ")) THEN 'unavailable' WHEN ("
                        + str(iuser)
                        + " NOT IN (SELECT userid FROM attendee p WHERE p.classid = a.classid AND p.status IN (1,4) UNION ALL SELECT t2.trainerid FROM trainer t2 LEFT JOIN class c2 ON t2.skillid = c2.skillid WHERE c2.classid = a.classid )) THEN 'join' END 'action' FROM class a LEFT JOIN users b on a.trainerid = b.userid LEFT JOIN skill c on a.skillid = c.skillid LEFT JOIN trainer d on c.skillid = d.skillid WHERE a.classid = "
                        + str(class_id)
                        + " ORDER BY a.start ;"
                    )
                    query_result = do_database_fetchall(query)

                    for row in query_result:
                        class_id = row[0]
                        class_name = row[1]
                        class_trainer = row[2]
                        class_start = row[3]
                        class_note = row[4]
                        class_size = row[5]
                        class_max = row[6]
                        class_action = row[7]

                        response.append(
                            build_response_class(
                                class_id,
                                class_name,
                                class_trainer,
                                class_start,
                                class_note,
                                class_size,
                                class_max,
                                class_action,
                            )
                        )

                    # SENDING RESPONSES
                    response.append(
                        build_response_message(0, "Leaving class, Success!")
                    )
                    # response.append(build_response_redirect('////index.html'))

                else:
                    # SENDING RESPONSES
                    response.append(
                        build_response_message(
                            103, "You're Not Enrolled To Such Class!"
                        )
                    )
            else:
                response.append(build_response_message(101, "Missing class id!"))
        else:
            # SENDING RESPONSES
            response.append(build_response_message(200, "Please, Login!"))
            response.append(build_response_redirect("/login.html"))
    else:
        # SENDING RESPONSES
        response.append(build_response_message(200, "Please, Login!"))
        response.append(build_response_redirect("/login.html"))

    return [iuser, imagic, response]


def handle_cancel_class_request(iuser, imagic, content):
    """This code handles a request to cancel an entire class."""

    response = []

    # 1. User should be trainer for the class -- [DONE]
    # 2. Class should be in future -- [DONE]
    # 3. Class should be marked cancelled, by setting max to 0 -- [DONE]
    # 4. All attendees should be marked cancelled -- [DONE]
    # 5. Updated class and attendee response, with attendees whose status changed --[DONE]

    ## Add code here
    try:
        class_id = content["id"]
    except:
        class_id = None

    if iuser and imagic:
        check_session_query = 'SELECT sessionid, userid, magic FROM "session" WHERE userid = ? and magic = ?;'
        check_session_query_result = do_database_fetchone_parameterised(
            check_session_query, (iuser, imagic)
        )

        # CHECKING IF USER IS LOGGED IN
        if check_session_query_result:
            if class_id is not None:

                # CHECKING IF USER IS THE TRAINER
                check_user_query = (
                    "SELECT c.trainerid FROM class c LEFT JOIN trainer t ON c.skillid = t.skillid WHERE classid = "
                    + str(class_id)
                    + " AND c.start > unixepoch('now');"
                )
                check_user_query_result = do_database_fetchone(check_user_query)

                if check_user_query_result and (
                    int(iuser) == int(check_user_query_result[0])
                ):

                    # UPDATING CLASS TABLE AND SETTING MAX AS '0'
                    update_class_query = (
                        "UPDATE class SET max = 0 WHERE classid = "
                        + str(class_id)
                        + ";"
                    )
                    do_database_execute(update_class_query)

                    # UPDATING ATTENDEES TO CANCELLED
                    update_attendee_query = (
                        "UPDATE attendee SET status = 3 WHERE classid = "
                        + str(class_id)
                        + " AND status = 0;"
                    )
                    do_database_execute(update_attendee_query)

                    # BUILDING CLASS RESPONSE
                    class_response_query = (
                        "SELECT a.classid, c.name, b.fullname, a.start, a.note,(SELECT COUNT(attendeeid) FROM attendee x WHERE x.classid = a.classid AND x.status in (0)) AS 'class_size', a.max FROM class a LEFT JOIN users b on a.trainerid = b.userid LEFT JOIN skill c on a.skillid = c.skillid LEFT JOIN trainer d on c.skillid = d.skillid WHERE classid = "
                        + str(class_id)
                        + " AND userid = "
                        + str(iuser)
                        + ";"
                    )
                    class_response_query_result = do_database_fetchone(
                        class_response_query
                    )

                    class_id = class_response_query_result[0]
                    class_name = class_response_query_result[1]
                    class_trainer = class_response_query_result[2]
                    class_when = class_response_query_result[3]
                    class_notes = class_response_query_result[4]
                    class_size = class_response_query_result[5]
                    class_max = class_response_query_result[6]
                    class_action = "cancelled"

                    # SENDING RESPONSE
                    response.append(
                        build_response_class(
                            class_id,
                            class_name,
                            class_trainer,
                            class_when,
                            class_notes,
                            class_size,
                            class_max,
                            class_action,
                        )
                    )

                    # BUILDING ATTENDEE RESPOSNE
                    attendee_response_query = (
                        "SELECT a.attendeeid, u.fullname, CASE WHEN ((a.status = 0) AND (c.start >= unixepoch('now'))) THEN 'remove' WHEN a.status = 0 AND (c.start < unixepoch('now')) THEN 'update' WHEN a.status = 1 THEN 'passed' WHEN a.status = 2 THEN 'failed' WHEN ((a.status = 3) OR (a.status = 4)) THEN 'cancelled' END 'state' FROM attendee a LEFT JOIN users u ON a.userid = u.userid LEFT JOIN class c ON a.classid = c.classid WHERE a.status = 4 AND a.classid = "
                        + str(class_id)
                        + ";"
                    )
                    attendee_response_query_result = do_database_fetchall(
                        attendee_response_query
                    )

                    for row in attendee_response_query_result:
                        attendee_id = row[0]
                        attendee_name = row[1]
                        attendee_state = row[2]

                        # SENDING RESPONSE
                        response.append(
                            build_response_attendee(
                                attendee_id, attendee_name, attendee_state
                            )
                        )

                    # SENDING RESPONSE
                    response.append(
                        build_response_message(0, "Cancel Class, Successfull")
                    )

                else:
                    # SENDING RESPONSE
                    response.append(build_response_message(211, "Class Cancel Failed"))
            else:
                response.append(
                    build_response_message(103, "Missing classid parameter!")
                )
        else:
            # SENDING RESPONSE
            response.append(build_response_message(200, "Please Login"))
            response.append(build_response_redirect("/login.html"))
    else:
        # SENDING RESPONSE
        response.append(build_response_message(200, "Please Login"))
        response.append(build_response_redirect("/login.html"))

    return [iuser, imagic, response]


def handle_update_attendee_request(iuser, imagic, content):
    """This code handles a request to cancel a user attendance at a class by a trainer"""

    # 1. Check if user is trainer -- [DONE]
    # 2. If time passed, update to 'passed' or 'failed' and send attendee response -- [DONE]
    # 3. If time not passed, update to 'remove' and send attendee response -- [DONE]

    response = []

    ## Add code here
    attendee_id = content["id"]
    attendee_state = content["state"]
    updated = False
    if iuser and imagic:
        check_session_query = 'SELECT sessionid, userid, magic FROM "session" WHERE userid = ? and magic = ?;'
        check_session_query_result = do_database_fetchone_parameterised(
            check_session_query, (iuser, imagic)
        )

        if check_session_query_result:

            check_user_query = (
                "SELECT t.trainerid FROM attendee a LEFT JOIN class c ON a.classid = c.classid LEFT JOIN trainer t ON c.skillid = t.skillid WHERE attendeeid = "
                + str(attendee_id)
                + " AND c.start < unixepoch('now');"
            )
            check_user_query_result = do_database_fetchone(check_user_query)

            if check_user_query_result:
                if int(iuser) == int(check_user_query_result[0]):
                    if attendee_state == "pass":
                        attendee_state_update_query = (
                            "UPDATE attendee SET status = 1 WHERE attendeeid = "
                            + str(attendee_id)
                            + ";"
                        )
                        do_database_execute(attendee_state_update_query)
                        updated = True
                    if attendee_state == "fail":
                        attendee_state_update_query = (
                            "UPDATE attendee SET status = 2 WHERE attendeeid = "
                            + str(attendee_id)
                            + ";"
                        )
                        do_database_execute(attendee_state_update_query)
                        updated = True

            check_user_query = (
                "SELECT t.trainerid FROM attendee a LEFT JOIN class c ON a.classid = c.classid LEFT JOIN trainer t ON c.skillid = t.skillid WHERE attendeeid = "
                + str(attendee_id)
                + " AND c.start > unixepoch('now');"
            )
            check_user_query_result = do_database_fetchone(check_user_query)

            if check_user_query_result:
                if int(iuser) == int(check_user_query_result[0]):
                    if attendee_state == "remove":
                        attendee_state_update_query = (
                            "UPDATE attendee SET status = 4 WHERE attendeeid = "
                            + str(attendee_id)
                            + ";"
                        )
                        do_database_execute(attendee_state_update_query)
                        updated = True

            if updated:

                attendee_response_query = (
                    "SELECT a.attendeeid, u.fullname, CASE WHEN ((a.status = 0) AND (c.start >= unixepoch('now'))) THEN 'remove' WHEN a.status = 0 AND (c.start < unixepoch('now')) THEN 'update' WHEN a.status = 1 THEN 'passed' WHEN a.status = 2 THEN 'failed' WHEN ((a.status = 3) OR (a.status = 4)) THEN 'cancelled' END 'state' FROM attendee a LEFT JOIN users u ON a.userid = u.userid LEFT JOIN class c ON a.classid = c.classid WHERE a.attendeeid = "
                    + str(attendee_id)
                    + ";"
                )
                attendee_response_query_result = do_database_fetchall(
                    attendee_response_query
                )

                for row in attendee_response_query_result:
                    attendee_id = row[0]
                    attendee_name = row[1]
                    attendee_state = row[2]
                    response.append(
                        build_response_attendee(
                            attendee_id, attendee_name, attendee_state
                        )
                    )

                response.append(build_response_message(0, "Update Attendee, Success"))

            else:
                response.append(
                    build_response_message(203, "Update Attendee, UnSuccessfull")
                )

        else:
            response.append(build_response_message(200, "Please, Login!"))
            response.append(build_response_redirect("/login.html"))
    else:
        response.append(build_response_message(200, "Please, Login!"))
        response.append(build_response_redirect("/login.html"))

    return [iuser, imagic, response]


def handle_create_class_request(iuser, imagic, content):
    """This code handles a request to create a class."""

    response = []

    # 1. Check User is trainer -- [DONE]
    # 2. date and time validity -- [DONE]
    # 3. Only classed in future -- [DONE]
    # 4. Class size range 1 to 10 -- [DONE]
    # 5. Class for valid skill -- [DONE]
    # 6. Redirect to class details -- [DONE]
    # 7. Randomly Generated Class ID -- [PENDING]

    ## Add code here
    try:
        skill_id = content["id"]
        note = content["note"]
        max = content["max"]
        day = content["day"]
        month = content["month"]
        year = content["year"]
        hour = content["hour"]
        minute = content["minute"]
    except:
        skill_id = None
        note = None
        max = None
        day = None
        month = None
        year = None
        hour = None
        minute = None

    input_check_flag = True

    if iuser and imagic:
        check_session_query = 'SELECT sessionid, userid, magic FROM "session" WHERE userid = ? and magic = ?;'
        check_session_query_result = do_database_fetchone_parameterised(
            check_session_query, (iuser, imagic)
        )

        if check_session_query_result:
            if (
                skill_id is not None
                and note is not None
                and max is not None
                and day is not None
                and month is not None
                and year is not None
                and hour is not None
                and minute is not None
            ):
                check_user_trainer_query = (
                    "SELECT trainerid, skillid FROM trainer WHERE skillid = "
                    + str(skill_id)
                    + " AND trainerid = "
                    + str(iuser)
                    + ";"
                )
                check_user_trainer_query_result = do_database_fetchone(
                    check_user_trainer_query
                )

                max_class_id_query = (
                    "SELECT classid FROM class ORDER BY 1 DESC LIMIT 1;"
                )
                max_class_id_query_result = do_database_fetchone(max_class_id_query)

                if max_class_id_query_result and (
                    1 < int(max_class_id_query_result[0])
                ):
                    new_class_id = int(max_class_id_query_result[0]) + 1
                else:
                    new_class_id = 1

                if check_user_trainer_query_result and (
                    int(iuser) == int(check_user_trainer_query_result[0])
                ):

                    if not (1 <= max <= 10):
                        input_check_flag = False
                        response.append(build_response_message(203, "Invalid Max Size"))

                    check_valid_skill_query = (
                        "SELECT skillid FROM skill WHERE skillid = "
                        + str(skill_id)
                        + ";"
                    )
                    check_valid_skill_query_result = do_database_fetchone(
                        check_valid_skill_query
                    )
                    if int(skill_id) != int(check_valid_skill_query_result[0]):
                        input_check_flag = False
                        response.append(build_response_message(203, "Invalid Skill"))

                    if not (0 <= hour < 24 and 0 <= minute < 60):
                        input_check_flag = False
                        response.append(
                            build_response_message(203, "Invalid Time Input")
                        )

                    if month not in range(1, 13):
                        input_check_flag = False
                        response.append(build_response_message(203, "Invalid Month"))
                    else:
                        max_days_in_month = calendar.monthrange(year, month)[1]
                        if not (1 <= day <= max_days_in_month):
                            input_check_flag = False
                            response.append(build_response_message(203, "Invalid Day"))

                    if input_check_flag:
                        date_time = datetime.datetime(year, month, day, hour, minute)
                        current_datetime = datetime.datetime.now()

                        if date_time > current_datetime:
                            start_time = time.mktime(date_time.timetuple())
                            insert_class_query = (
                                "INSERT INTO class (classid, trainerid, skillid, start, max, note) VALUES("
                                + str(new_class_id)
                                + ", "
                                + str(iuser)
                                + ", "
                                + str(skill_id)
                                + ", "
                                + str(int(start_time))
                                + ", "
                                + str(max)
                                + ", '"
                                + str(note)
                                + "');"
                            )
                            do_database_execute(insert_class_query)
                            response.append(
                                build_response_redirect("/class/" + str(new_class_id))
                            )
                        else:
                            response.append(
                                build_response_message(203, "Invalid Date & Time")
                            )
                else:
                    response.append(
                        build_response_message(
                            203, "You're not a trainer for this class!"
                        )
                    )
            else:
                response.append(
                    build_response_message(103, "Missing class parameters!")
                )
        else:
            response.append(build_response_message(200, "Please Login"))
            response.append(build_response_redirect("/login.html"))
    else:
        response.append(build_response_message(200, "Please Login"))
        response.append(build_response_redirect("/login.html"))

    return [iuser, imagic, response]


# HTTPRequestHandler class
class myHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # POST This function responds to GET requests to the web server.
    def do_POST(self):
        """
        Responds to HTTP POST requests.
        """ 
        # The set_cookies function adds/updates two cookies returned with a webpage.
        # These identify the user who is logged in. The first parameter identifies the user
        # and the second should be used to verify the login session.
        def set_cookies(x, user, magic):
            ucookie = Cookie.SimpleCookie()
            ucookie["u_cookie"] = user
            x.send_header("Set-Cookie", ucookie.output(header="", sep=""))
            mcookie = Cookie.SimpleCookie()
            mcookie["m_cookie"] = magic
            x.send_header("Set-Cookie", mcookie.output(header="", sep=""))

        # The get_cookies function returns the values of the user and magic cookies if they exist
        # it returns empty strings if they do not.
        def get_cookies(source):
            rcookies = Cookie.SimpleCookie(source.headers.get("Cookie"))
            user = ""
            magic = ""
            for keyc, valuec in rcookies.items():
                if keyc == "u_cookie":
                    user = valuec.value
                if keyc == "m_cookie":
                    magic = valuec.value
            return [user, magic]

        # Fetch the cookies that arrived with the GET request
        # The identify the user session.
        user_magic = get_cookies(self)

        print(user_magic)

        # Parse the GET request to identify the file requested and the parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # The special file 'action' is not a real file, it indicates an action
        # we wish the server to execute.
        if parsed_path.path == "/action":
            self.send_response(200)  # respond that this is a valid page request

            # extract the content from the POST request.
            # This are passed to the handlers.
            length = int(self.headers.get("Content-Length"))
            scontent = self.rfile.read(length).decode("ascii")
            print(scontent)
            if length > 0:
                content = json.loads(scontent)
            else:
                content = []

            # deal with get parameters
            parameters = urllib.parse.parse_qs(parsed_path.query)

            if "command" in parameters:
                # check if one of the parameters was 'command'
                # If it is, identify which command and call the appropriate handler function.
                # You should not need to change this code.
                if parameters["command"][0] == "login":
                    [user, magic, response] = handle_login_request(
                        user_magic[0], user_magic[1], content
                    )
                    # The result of a login attempt will be to set the cookies to identify the session.
                    set_cookies(self, user, magic)
                elif parameters["command"][0] == "logout":
                    [user, magic, response] = handle_logout_request(
                        user_magic[0], user_magic[1], parameters
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")
                elif parameters["command"][0] == "get_my_skills":
                    [user, magic, response] = handle_get_my_skills_request(
                        user_magic[0], user_magic[1]
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")

                elif parameters["command"][0] == "get_upcoming":
                    [user, magic, response] = handle_get_upcoming_request(
                        user_magic[0], user_magic[1]
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")
                elif parameters["command"][0] == "join_class":
                    [user, magic, response] = handle_join_class_request(
                        user_magic[0], user_magic[1], content
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")
                elif parameters["command"][0] == "leave_class":
                    [user, magic, response] = handle_leave_class_request(
                        user_magic[0], user_magic[1], content
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")

                elif parameters["command"][0] == "get_class":
                    [user, magic, response] = handle_get_class_detail_request(
                        user_magic[0], user_magic[1], content
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")

                elif parameters["command"][0] == "update_attendee":
                    [user, magic, response] = handle_update_attendee_request(
                        user_magic[0], user_magic[1], content
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")

                elif parameters["command"][0] == "cancel_class":
                    [user, magic, response] = handle_cancel_class_request(
                        user_magic[0], user_magic[1], content
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")

                elif parameters["command"][0] == "create_class":
                    [user, magic, response] = handle_create_class_request(
                        user_magic[0], user_magic[1], content
                    )
                    if (
                        user == "!"
                    ):  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, "", "")
                else:
                    # The command was not recognised, report that to the user. This uses a special error code that is not part of the codes you will use.
                    response = []
                    response.append(
                        build_response_message(
                            901, "Internal Error: Command not recognised."
                        )
                    )

            else:
                # There was no command present, report that to the user. This uses a special error code that is not part of the codes you will use.
                response = []
                response.append(
                    build_response_message(902, "Internal Error: Command not found.")
                )

            text = json.dumps(response)
            print(text)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(text, "utf-8"))

        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404)  # a file not found html response
            self.end_headers()
        return

    # GET This function responds to GET requests to the web server.
    # You should not need to change this function.
    def do_GET(self):

        # Parse the GET request to identify the file requested and the parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # Return a CSS (Cascading Style Sheet) file.
        # These tell the web client how the page should appear.
        if self.path.startswith("/css"):
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open("." + self.path, "rb") as file:
                self.wfile.write(file.read())

        # Return a Javascript file.
        # These contain code that the web client can execute.
        elif self.path.startswith("/js"):
            self.send_response(200)
            self.send_header("Content-type", "text/js")
            self.end_headers()
            with open("." + self.path, "rb") as file:
                self.wfile.write(file.read())

        # A special case of '/' means return the ////index.html (homepage)
        # of a website
        elif parsed_path.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("./pages/////index.html", "rb") as file:
                self.wfile.write(file.read())

        # Pages of the form /create/... will return the file create.html as content
        # The ... will be a class id
        elif parsed_path.path.startswith("/class/"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("./pages/class.html", "rb") as file:
                self.wfile.write(file.read())

        # Pages of the form /create/... will return the file create.html as content
        # The ... will be a skill id
        elif parsed_path.path.startswith("/create/"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("./pages/create.html", "rb") as file:
                self.wfile.write(file.read())

        # Return html pages.
        elif parsed_path.path.endswith(".html"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("./pages" + parsed_path.path, "rb") as file:
                self.wfile.write(file.read())
        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404)
            self.end_headers()

        return


def run():
    """This is the entry point function to this code."""
    print("starting server...")
    ## You can add any extra start up code here
    # Server settings
    # When testing you should supply a command line argument in the 8081+ range

    # Changing code below this line may break the test environment. There is no good reason to do so.
    if len(sys.argv) < 2:  # Check we were given both the script name and a port number
        print("Port argument not provided.")
        return
    server_address = ("127.0.0.1", int(sys.argv[1]))
    httpd = HTTPServer(server_address, myHTTPServer_RequestHandler)
    print("running server on port =", sys.argv[1], "...")
    httpd.serve_forever()  # This function will not return till the server is aborted.


run()
