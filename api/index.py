from course_app import create_app
import os

# app = create_app()
# app.secret_key = os.getenv("FLASK_SECRET_KEY")
print("[Vercel] Flask App Created")

# if __name__ == "__main__":
#     app.run(host="0.0.0.0",debug=True)

from pymongo import MongoClient

def handler(request, response):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['db_course_scheduling']
        # db = client.get_database()  # atau db = client['db_course_scheduling']
        return response.json({"status": True, "msg": "MongoDB Connected"})
    except Exception as e:
        return response.json({"status": False, "error": "💥 FAILED " + str(e) })