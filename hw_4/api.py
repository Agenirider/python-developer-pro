#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import abc
import json

# import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import datetime
import traceback

from scoring import get_score, get_interests

from config import DEBUG

import redis

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
BAD_GATEWAY = 502
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
    BAD_GATEWAY: "Bad Gateway",
}

UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class CharField(object):
    def __init__(self, name, required, nullable):
        self.name = "_" + name
        self.default = None
        self.required = required
        self.nullable = nullable

    def __get__(self, instance, cls):
        return getattr(instance, self.name)

    def __set__(self, instance, value):

        value = value or self.default

        if value is not None:
            if isinstance(value, str):
                setattr(instance, self.name, value)
            else:
                setattr(instance, self.name, "")
        else:
            setattr(instance, self.name, None)

    def __delete__(self, instance):
        raise AttributeError("Can't delete attribute")


class EmailField(CharField):
    def __init__(self, name, required=False, nullable=True):
        super().__init__(name, required, nullable)
        self.name = "_" + name
        self.required = required
        self.nullable = nullable
        self.default = None

    def __get__(self, instance, cls):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if not hasattr(self, self.name):

            # check - value is email with @

            if value is not None and len(re.findall("@", value)) == 1:
                setattr(instance, self.name, value)
            else:
                setattr(instance, self.name, self.default)

    def __delete__(self, instance):
        raise AttributeError("Can't delete attribute")


class PhoneField(object):
    def __init__(self, name, required=False, nullable=True):
        self.name = "_" + name
        self.required = required
        self.nullable = nullable
        self.default = None

    def __get__(self, instance, cls):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if not hasattr(self, self.name):
            if value is not None:
                str_val = str(value)
                first_digit = str_val[0]
                if len(str_val) == 11 and first_digit == "7":
                    setattr(instance, self.name, value)

                else:
                    setattr(instance, self.name, self.default)

            else:
                setattr(instance, self.name, value)

    def __delete__(self, instance):
        raise AttributeError("Can't delete attribute")


class BirthDayField(object):
    def __init__(self, name, required=False, nullable=True):
        self.name = "_" + name
        self.required = required
        self.nullable = nullable
        self.default = None

    def __get__(self, instance, cls):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if not hasattr(self, self.name):

            value = value or self.default

            if value is not None:
                try:
                    date_sign = re.match(r"\d{2}.\d{2}.\d{4}", value).group(0)
                    birthday_day, birthday_month, birthday_year = date_sign.split(".")

                    now = datetime.datetime.now()

                    current_year = now.year

                    if (current_year - int(birthday_year)) < 70:

                        setattr(
                            instance,
                            self.name,
                            "".join([birthday_day, birthday_month, birthday_year]),
                        )

                    else:
                        # User too old :( for this scoring API
                        setattr(instance, self.name, "")

                except (AttributeError, TypeError):
                    setattr(instance, self.name, "")

            else:
                setattr(instance, self.name, None)

    def __delete__(self, instance):
        raise AttributeError("Can't delete attribute")


class GenderField(object):
    def __init__(self, name, required=False, nullable=True):
        self.name = "_" + name
        self.required = required
        self.nullable = nullable
        self.default = ""

    def __get__(self, instance, cls):
        return getattr(instance, self.name)

    def __set__(self, instance, value):

        if not hasattr(self, self.name):
            if value is not None:

                if value in [0, 1, 2]:
                    setattr(instance, self.name, value)
                else:
                    setattr(instance, self.name, self.default)
            else:
                setattr(instance, self.name, None)

    def __delete__(self, instance):
        raise AttributeError("Can't delete attribute")


class ClientIDsField(object):
    def __init__(self, name, required):
        self.name = "_" + name
        self.default = None
        self.required = required

    def __get__(self, instance, cls):
        return getattr(instance, self.name)

    def __set__(self, instance, values):

        values = values or self.default

        if isinstance(values, list):
            if self.required:
                if values is not None:
                    is_digits = list(
                        {True if isinstance(d, int) else False for d in values}
                    )
                    if len(is_digits) == 1 and True in is_digits:
                        setattr(instance, self.name, values)
                    else:
                        setattr(instance, self.name, self.default)
                else:
                    setattr(instance, self.name, values)
            else:
                setattr(instance, self.name, self.default)
        else:
            setattr(instance, self.name, self.default)

    def __delete__(self, instance):
        raise AttributeError("Can't delete attribute")


def date_checker(date_string):
    try:
        date_sign = re.match(r"\d{2}.\d{2}.\d{4}", date_string).group(0)

        parsed_date = re.findall(r"\d+", date_sign)

        date_parts_checked_set = set()
        day, month, year = map(int, parsed_date)

        if 0 < day < 31:
            date_parts_checked_set.add(True)
        else:
            date_parts_checked_set.add(False)

        if 0 < month < 13:
            date_parts_checked_set.add(True)
        else:
            date_parts_checked_set.add(False)

        if year > 2015:
            date_parts_checked_set.add(True)
        else:
            date_parts_checked_set.add(False)

        if True in list(date_parts_checked_set) and len(date_parts_checked_set) == 1:
            return True
        else:
            return False

    except AttributeError:
        return False


class DateField(object):
    def __init__(self, name, required=False, nullable=True):
        self.name = "_" + name
        self.required = required
        self.nullable = nullable
        self.default = None

    def __get__(self, instance, cls):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if not hasattr(self, self.name):
            if self.required:
                if value is not None and date_checker(value):
                    setattr(instance, self.name, value)

                elif value is None:
                    setattr(instance, self.name, None)

            else:
                if value is not None:
                    if date_checker(value):
                        setattr(instance, self.name, value)
                    else:
                        setattr(instance, self.name, "")

                elif value is None:
                    setattr(instance, self.name, self.default)

    def __delete__(self, instance):
        raise AttributeError("Can't delete attribute")


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField("client_ids", required=True)
    date = DateField("date", required=False, nullable=True)

    def __init__(self, client_ids, date):
        self.client_ids = client_ids
        self.date = date

    def __get__(self, instance, cls):
        return getattr(instance, self.name)

    def hasCorrectDate(self):
        if self.date is not None and self.date != "":
            return True

    def hasClientsIds(self):
        if hasattr(self, "client_ids"):
            if self.client_ids is not None and len(self.client_ids) > 0:
                return True
            else:
                return False
        else:
            return False

    def getInterests(self, store, client_ids):

        if self.hasClientsIds():
            if self.hasCorrectDate() and self.date:
                return get_interests(store, client_ids), 200

            elif self.date is None:
                return get_interests(store, client_ids), 200

            else:
                return {"error": ERRORS[INVALID_REQUEST]}, 422
        else:
            return {"error": ERRORS[INVALID_REQUEST]}, 422


class OnlineScoreRequest(object):
    first_name = CharField("first_name", required=False, nullable=True)
    last_name = CharField("last_name", required=False, nullable=True)
    email = EmailField("email", required=False, nullable=True)
    phone = PhoneField("phone", required=False, nullable=True)
    birthday = BirthDayField("birthday", required=False, nullable=True)
    gender = GenderField("gender", required=False, nullable=True)

    def __init__(self, phone, email, first_name, last_name, birthday, gender):
        self.phone = phone
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender

    def hasPhoneEmailFields(self):
        return True if self.phone is not None and self.email is not None else False

    def hasFirstLastNameFields(self):
        return (
            True
            if self.last_name is not None and self.first_name is not None
            else False
        )

    def hasGenderBirthdayFields(self):
        return True if self.gender is not None and self.birthday != "" else False

    def getScore(self, store):

        # Check we have correct arguments != ''
        is_correct_values = {
            False if self.__dict__[key] in [""] else True for key in [*self.__dict__]
        }

        if len(is_correct_values) == 1 and True in is_correct_values:

            if self.hasPhoneEmailFields():
                return {"score": get_score(store, self.phone, self.email)}, 200

            if self.hasFirstLastNameFields():
                return {
                    "score": get_score(
                        store,
                        None,
                        None,
                        last_name=self.last_name,
                        first_name=self.first_name,
                    )
                }, 200

            if self.hasGenderBirthdayFields():
                return {
                    "score": get_score(
                        store, None, None, gender=self.gender, birthday=self.birthday
                    )
                }, 200

            else:
                return {"error": ERRORS[INVALID_REQUEST]}, 422

        else:
            return {"error": ERRORS[INVALID_REQUEST]}, 422


class MethodRequest(object):
    account = CharField("account", required=False, nullable=True)
    login = CharField("login", required=True, nullable=True)
    token = CharField("token", required=True, nullable=True)
    method = CharField("method", required=True, nullable=False)

    def __init__(self, account, login, token, method):
        self.account = account
        self.login = login
        self.token = token
        self.method = method

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def hash_encoder(arr):
    return b"".join([x.encode("utf-8") for x in arr])


def check_auth(account_request):
    user_is_admin = account_request.is_admin

    # UTF-8 ENCODE REQUIRED
    if user_is_admin:
        hash_admin_parts = [datetime.datetime.now().strftime("%Y%m%d%H"), ADMIN_SALT]
        digest = hashlib.sha512(hash_encoder(hash_admin_parts)).hexdigest()

    elif not user_is_admin:

        hash_parts = [account_request.account, account_request.login, SALT]
        digest = hashlib.sha512(hash_encoder(hash_parts)).hexdigest()

    if digest == account_request.token:
        return True

    return False


def method_handler(request, ctx, store):
    params = request["body"]

    try:
        request_args = request["body"]["arguments"]
    except KeyError:
        return {"error": ERRORS[INVALID_REQUEST]}, 422

    requires_fields = ["account", "login", "token", "method"]

    for field in requires_fields:
        if field not in [*params]:
            return {"error": ERRORS[INVALID_REQUEST]}, 422

    account_request = MethodRequest(
        params["account"], params["login"], params["token"], params["method"]
    )

    check_auth_result = check_auth(account_request)

    if not check_auth_result:
        return {"error": ERRORS[FORBIDDEN]}, FORBIDDEN

    elif check_auth_result and account_request.login == "admin":
        return {"score": 42}, OK

    elif not check_auth_result and account_request.login == "admin":
        return {"error": ERRORS[FORBIDDEN]}, FORBIDDEN

    else:

        if (
            account_request.method == "online_score"
            and account_request.login != "admin"
        ):
            requires_fields = [
                "phone",
                "email",
                "first_name",
                "last_name",
                "birthday",
                "gender",
            ]
            attrs = [
                request_args[x] if x in [*request_args] else None
                for x in requires_fields
            ]
            score = OnlineScoreRequest(*attrs)

            # UPDATE CONTEXT HAS
            ctx.update(
                {"has": [attr for attr in requires_fields if attr in [*request_args]]}
            )

            result = score.getScore(store)

            return result

        elif (
            account_request.method == "online_score"
            and account_request.login == "admin"
        ):
            return {"score": 42}, OK

        elif account_request.method == "clients_interests":
            requires_fields = ["client_ids", "date"]
            attrs = [
                request_args[x] if x in [*request_args] else None
                for x in requires_fields
            ]
            interests = ClientsInterestsRequest(*attrs)

            # UPDATE CONTEXT nclients
            ctx.update(
                {
                    "nclients": len(interests.client_ids)
                    if interests.client_ids is not None
                    else 0
                }
            )

            interests_result = interests.getInterests(store, interests.client_ids)

            return interests_result

        else:
            # Unknown method
            raise AttributeError("Unknown method")


def get_request_id(headers):
    return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)


def is_redis_available(redis_connection):
    try:
        redis_connection.ping()
        return True
    except (
        redis.exceptions.ConnectionError,
        ConnectionRefusedError,
        redis.exceptions.TimeoutError,
    ):
        return False
    return False


class MainHTTPHandler(BaseHTTPRequestHandler):
    """ Method -> this is an URL like in http://localhost:8080/method """

    router = {"method": method_handler}

    store = redis.Redis("127.0.0.1", socket_connect_timeout=1, port=6379, db=0)
    redis_available_status = is_redis_available(store)

    def do_POST(self):

        response, code = {}, OK
        context = {"request_id": get_request_id(self.headers)}
        request = None

        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")

            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))

            if path in self.router:
                try:
                    if not self.redis_available_status:
                        response, code = {}, BAD_GATEWAY
                    else:
                        response, code = self.router[path](
                            {"body": request, "headers": self.headers},
                            context,
                            self.store,
                        )

                except AttributeError:
                    logging.error("Unexpected error - Invalid request")
                    code = INVALID_REQUEST

                except Exception as e:
                    logging.error(
                        f"Unexpected error -> {traceback.format_exc()}"
                    ) if DEBUG else logging.error(f"Unexpected error -> {e}")
                    code = INTERNAL_ERROR

            else:
                code = NOT_FOUND

        # ADD RESP CODE
        self.send_response(code)
        # ADD HEADER
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}

        # ADD CONTAINS
        context.update(r)
        logging.info(context)

        byte_resp = bytes(json.dumps(r), "utf-8")
        self.wfile.write(byte_resp)

        return


if __name__ == "__main__":

    print("START SERVER") if DEBUG else None

    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename="./opts.log",
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        pass

    server.server_close()
