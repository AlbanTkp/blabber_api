from flask import jsonify, make_response, request


def sendResponse(message, result=None, code=200):
    response = {
        'success': True,
        'data': result or {},
        'message': message
    }
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    return make_response(jsonify(response), code, headers)


def sendError(error, data=None, code=200):
    response = {
        'success': False,
        'data': data or {},
        'message': error
    }
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    return make_response(jsonify(response), code, headers)


import time


def renameFile(filename):
    current_time_millis = int(time.time() * 1000)
    extension = filename.split('.')[-1].lower()
    new_filename = f"{current_time_millis}.{extension}"
    return new_filename
