from flask import Flask, request,jsonify
import joblib
import jwt
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)
# @app.before_request
# def basic_authentication():
#     if request.method.lower() == 'options':
#         return jsonify({"message": "CORS preflight"}), 200

feature = [
    "Age", "Systolic BP", "Diastolic", "BS", "Body Temp",
    "Previous Complications", "Preexisting Diabetes",
    "Gestational Diabetes", "Mental Health", "Heart Rate",
    "BMI_Normal","BMI_Overweight"
]

@app.route("/")
def home():
    return jsonify({"message": "App with maternal risk model is running!", "columns": feature})


def validateuser(jwttoken):
    try:
        decoded = jwt.decode(jwttoken, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/predict', methods=["POST"])
def maternal_risk():
    try:
        # check for if data for each columns is present or not if not raise exception
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token missing"}), 401

        decoded = validateuser(token)
        if not decoded or not decoded.get("username"):
            return jsonify({"error": "Unauthorized"}), 401
        data = request.get_json()
        for key in feature:
            if key not in data:
                raise ValueError("All features are not present")
        # remove BMI_Overweight column from the model
        model = joblib.load("./maternal_risk_model")
        x = [[data.get(name) for name in feature]]
        predicted = model.predict(x)
        return jsonify({"message":"High risk" if predicted ==1 else "Low risk"}),200
    except Exception as e:
        # print(str(e))
        return jsonify({"Error":"Something went wrong"}),500


if __name__=="__main__":
    app.run(host="0.0.0.0", port=8001)