from flask import jsonify, make_response


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
