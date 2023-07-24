# flask dependencies
from flask import Blueprint, jsonify, request, current_app
from .schema import DeviceLocations
# db session
from api import db_session


import json
import os
import pandas as pd
import datetime
from api import redis_cache

try:
    apis_blueprint = Blueprint("apis", __name__, url_prefix="/api")
    main_blueprint = Blueprint("main_apis", __name__, url_prefix="/")
except Exception as e:
    apis_blueprint = Blueprint("apis", __name__, url_prefix="/api")
    main_blueprint = Blueprint("main_apis", __name__, url_prefix="/")


def set_cache(key, val):
    try:
        res = redis_cache.set(
            key,
            json.dumps(val)
        )
        redis_cache.expire(key, 10000)
        print("Key stored in cache", res)	
    except Exception as e:
        print("Exception in setting data in cache", e)	


def get_cache(key):
    try:
        cache_data = redis_cache.get(key)
        if cache_data:
            print("Cache hit for", key)
            return json.loads(cache_data)
        else:
            print("Cache miss", key)
    except Exception as e:
        print("Exception in cache", e)


@main_blueprint.route("/", methods=["GET"])
def api():
    try:
        return jsonify(
            {
                "success": True,
                "message": "Successfully received request"
            })
    except Exception as e:
        print("error", e)
        return jsonify({
            "success": False,
            "message": "Error while performing operation"
            }), 404


@apis_blueprint.route("/add_csv_data", methods=["GET"])
def load_csv_to_database():
    try:
        current_directory = str(os.getcwd() + '/api/raw_data.csv')
        print(current_directory)
        df = pd.read_csv(current_directory)
        df.sort_values(by=["sts"], inplace = True)
        all_data = []
        for index, row in df.iterrows():
            all_data.append(DeviceLocations(
                device_fk_id = int(row['device_fk_id']),
                latitude = row['latitude'],
                longitude = row['longitude'],
                timestamp = row['time_stamp'],
                sts = row['sts'],
                speed = row['speed']
            ))
        
        db_session.add_all(all_data)
        db_session.commit()
        return jsonify(
            {
                "success": True,
                "message": "Successfully loaded data to table"
            })
    except Exception as e:
        print("error", e)
        return jsonify({
            "success": False,
            "message": "Error while performing operation"
            }), 404


@apis_blueprint.route("/delete_csv_data", methods=["DELETE"])
def clear_csv_from_database():
    try:
        db_session.query(DeviceLocations).delete()
        db_session.commit()
        redis_cache.flushall()
        return jsonify(
            {
                "success": True,
                "message": "Successfully cleared database"
            })
    except Exception as e:
        print("error", e)
        return jsonify({
            "success": False,
            "message": "Error while performing operation"
            }), 404
    

@apis_blueprint.route("/device", methods=["GET"])
def device_data_get():
    try:
        id = int(request.args.get('id'))

        cache_data = get_cache(f'device_data_{id}')
        if cache_data:
            return jsonify(
                {
                    "success": True,
                    "data": cache_data
                })
        
        device_data = db_session.query(DeviceLocations).filter(DeviceLocations.device_fk_id == id).order_by(DeviceLocations.sts.desc()).first()
        if not device_data:
            return jsonify({
                "success": True,
                "message": "Device not found"
            }), 400

        result_data = [{
                    "device_id": device_data.device_fk_id,
                    "latitude": device_data.latitude,
                    "longitude": device_data.longitude,
                    "time_stamp": str(device_data.time_stamp),
                    "sts": str(device_data.sts),
                    "speed": device_data.speed
                }]
        
        set_cache(f'device_data_{id}', result_data)

        return jsonify(
            {
                "success": True,
                "data": result_data
            })
    except Exception as e:
        print("error", e)
        return jsonify({
            "success": False,
            "message": "Error while performing operation"
            }), 404


@apis_blueprint.route("/get_location", methods=["GET"])
def device_data_get_location():
    try:
        id = int(request.args.get('id'))

        cache_data = get_cache(f'location_data_{id}')
        if cache_data:
            return jsonify(
                {
                    "success": True,
                    "data": cache_data
                })
        
        device_data = db_session.query(DeviceLocations).filter(DeviceLocations.device_fk_id == id).order_by(DeviceLocations.sts.asc())
        if not device_data or device_data.count() == 0:
            return jsonify({
                "success": True,
                "message": "Device not found"
            }), 400
        
        count = device_data.count()
        print(count)
        result_data =[]
        result_data.append({
                "start": [device_data[0].latitude, device_data[0].longitude]
            })	
        result_data.append({
                "end": [device_data[count - 1].latitude, device_data[count - 1].longitude]
            })	
        
        set_cache(f'location_data_{id}', result_data)
        
        return jsonify(
            {
                "success": True,
                "data": result_data
            })
    except Exception as e:
        print("error", e)
        return jsonify({
            "success": False,
            "message": "Error while performing operation"
            }), 404


@apis_blueprint.route("/get_all_location", methods=["GET"])
def device_data_get_all_location():
    try:
        id = int(request.args.get('id'))
        start_time = datetime.datetime.strptime(request.args.get('start_time'), "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.datetime.strptime(request.args.get('end_time'), "%Y-%m-%dT%H:%M:%S")
        
        cache_data = get_cache(f'location_data_{id}_start{start_time}_end_{end_time}')
        if cache_data:
            return jsonify(
                {
                    "success": True,
                    "data": cache_data
                })
        
        device_data = db_session.query(DeviceLocations).filter(
            DeviceLocations.device_fk_id == id,
            DeviceLocations.time_stamp >= start_time,
            DeviceLocations.time_stamp <= end_time
            ).order_by(DeviceLocations.sts.asc())
        if not device_data or device_data.count() == 0:
            return jsonify({
                "success": True,
                "message": "Device not found"
            }), 400
        
        count = device_data.count()
        
        result_data =[{
            "device_id": ele.device_fk_id,
            "latitude": ele.latitude,
            "longitude": ele.longitude,
            "time_stamp": str(ele.time_stamp),
            "sts": str(ele.sts),
            "speed": ele.speed
        }
            for ele in device_data
        ]

        set_cache(f'location_data_{id}_start{start_time}_end_{end_time}', result_data)

        return jsonify(
            {
                "success": True,
                "data": result_data,
                "count": count
            })
    except Exception as e:
        print("error", e)
        return jsonify({
            "success": False,
            "message": "Error while performing operation"
            }), 404

@apis_blueprint.app_errorhandler(400)
def bad_request(e):
    """
    Bad request error handler
    """
    return jsonify({"error": "bad Request."}), 400


@apis_blueprint.app_errorhandler(401)
def unauthorized_request(e):
    """
    Unauthorized request error handler
    """
    return jsonify({"error": "unauthorized access."}), 401


@apis_blueprint.app_errorhandler(403)
def forbidden_request(e):
    """
    Forbidden request error handler
    """
    return jsonify({"error": "forbidden access."}), 403


@apis_blueprint.app_errorhandler(404)
def not_found_error(e):
    """
    Resource not found error handler
    """
    return jsonify({"error": "resource not found."}), 404


@apis_blueprint.app_errorhandler(405)
def method_not_allowed_error(e):
    """
    Method not allowed error handler
    """
    return jsonify({"error": "method not allowed."}), 405


@apis_blueprint.app_errorhandler(429)
def method_not_allowed_error(e):
    """
    Method not allowed error handler
    """
    return jsonify({"error": "Too many requests check the rate limit."}), 405


@apis_blueprint.app_errorhandler(500)
def server_error(e):
    """
    Internal server error handler
    """
    return jsonify({"error": "internal server error."}), 500


@apis_blueprint.app_errorhandler(502)
def bad_gateway(e):
    """
    Bad gateway error handler
    """
    return jsonify({"error": "bad gateway error."}), 502


@apis_blueprint.app_errorhandler(503)
def service_unavailable(e):
    """
    Service unavailable error handler
    """
    return jsonify({"error": "service unavailable."}), 503


@apis_blueprint.app_errorhandler(504)
def timeout_error(e):
    """
    Timeout error handler
    """
    return jsonify({"error": "gateway timeout."}), 504
