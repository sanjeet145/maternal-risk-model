from flask import Flask, request,jsonify
import joblib
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# keys={
#   "Preexisting_Diabetes":1,
#   "Mental_Health":1,
#   "Previous_Complications":1,
#   "Diastolic":-1.2,
#   "Gestational_Diabetes":0,
#   "Systolic_BP":-1.4,
#   "BS":0.57,
#   "BMI_Normal":0,
#   "Age":-0.6,
#   "Body_Temp":1.46,
#   "Heart_Rate":0.57
# }

# {
#       "Age": 25,
#       "Systolic_BP": 120,
#       "Diastolic": 80,
#       "BS": 90,
#       "Body_Temp": 98.6,
#       "Previous_Complications": 1,
#       "Preexisting_Diabetes": 0,
#       "Gestational_Diabetes": 0,
#       "Mental_Health": 0,
#       "Heart_Rate": 72,
#       "BMI_Normal": 1
# }

# {
#     "Preexisting_Diabetes": 0,
#     "Mental_Health": 0,
#     "Previous_Complications": 0,
#     "Diastolic": 78,
#     "Gestational_Diabetes": 0,
#     "Systolic_BP": 120,
#     "BS": 90,
#     "BMI_Normal": 1,
#     "Age": 28,
#     "Body_Temp": 98.6,
#     "Heart_Rate": 72
# }



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
        return "High risk" if predicted ==1 else "Low risk"
    except Exception as e:
        print(str(e))
        return jsonify({"Error":"Something went wrong"}),500


if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=8001)