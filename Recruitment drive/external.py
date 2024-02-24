from flask import request, Flask
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import mysql.connector
import csv

# database connect and configure
connection = mysql.connector.connect(user='root', password='ramar123', host='127.0.0.1')
cursor = connection.cursor(buffered=True)
cursor.execute("CREATE DATABASE IF NOT EXISTS prov")
cursor.close()
connection.close()
application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:ramar123@127.0.0.1/prov"
database = SQLAlchemy(application)
API = Api(application)
application.app_context().push()


#take the database model
class skills(database.Model):
    id = database.Column(database.Integer, primary_key=True, nullable=False)
    name = database.Column(database.String(30), nullable=False)
    skillset = database.Column(database.String(100), default="N/A")


#read the csv file for file
with open("skills.csv") as file:
    content = csv.DictReader(file, delimiter=';')
    for i in content:
        to = skills(id=i['candidateid'], name=i['fullname'], skillset=i['skillset'])
        if not skills.query.filter_by(id=i['candidateid']).all():
            database.session.add(to)
            database.session.commit()

#insert the records to the database
database.create_all()


class FetchAll(Resource):
    def get(self):
        # Retrieve all profiles from the database
        all_profiles = skills.query.all()
        # Convert the profiles to a list of dictionaries
        profiles_list = [{"id": profile.id, "name": profile.name, "skillset": profile.skillset} for profile in
                         all_profiles]
        return profiles_list


#get the skill from API and list candidates having that skill
class Operations(Resource):
    def get(self):
        argument = request.args
        reqskill = argument.get("skills")

        if reqskill:
            # Convert the skill string into a list and make it lowercase
            skills_list = [skill.lower() for skill in
                           reqskill.replace('[', '').replace(']', '').replace(' ', '').split(',')]
            # Query all candidates and filter them based on the specified skills
            all_candidates = skills.query.all()
            matching_candidates = []
            for candidate in all_candidates:
                candidate_skills = [skill.lower() for skill in
                                    candidate.skillset.replace('[', '').replace(']', '').replace(' ', '').split(',')]
                if any(skill in candidate_skills for skill in skills_list):
                    matching_candidates.append(
                        {"id": candidate.id, "name": candidate.name, "skills": candidate.skillset})

            if matching_candidates:
                return matching_candidates
            else:
                return "No candidates found with the given skills"
        else:
            return "Please provide at least one skill in the 'skills' parameter"


class post_operations(Resource):
    def post(self):
        posting = request.get_json()
        post_data = posting['id']
        if skills.query.filter_by(id=post_data).first():
            return "The id already exists. Try adding new Id and details"
        # adding the candidate details
        else:
            posting_to = skills(id=posting['id'], name=posting['name'], skillset=posting['skillset'])
            database.session.add(posting_to)
            database.session.commit()
            return "Details added successfully"


class post_matchRequirements(Resource):
    def post(self):
        posting_s = request.get_json()
        post_data = posting_s['requiredSkillsets']
        # using given skillset to find the candidate
        detailsp = skills.query.filter_by(skillset=post_data).all()
        if detailsp:
            return {"id": detailsp[0].id, "name": detailsp[0].name, "skills": detailsp[0].skillset}
        else:
            return "No profile for the required skills"


class updating(Resource):
    def put(self):
        putting = request.get_json()
        put_id = putting["id"]
        # query to update the candidate using candidate id
        if to_put := skills.query.filter_by(id=put_id).first():
            to_put.id = putting['id']
            to_put.skillset = putting['skillset']
            database.session.add(to_put)
            database.session.commit()
            return "Information changed successfully!"
        else:
            return "The given ID does not exist, try changing the ID to update details"


class deleteProfile(Resource):
    def delete(self):
        delete = request.args
        to_delete = delete.get("id")
        # delete the candidate using candidate id
        if deleting_id := skills.query.filter_by(id=to_delete).first():
            database.session.delete(deleting_id)
            database.session.commit()
            return "The profile removed successfully."
        else:
            return "The ID you are trying to delete is not found in the database"


API.add_resource(FetchAll, '/all-profiles')
API.add_resource(Operations, '/profile-for-skillset')  #?skills=
API.add_resource(post_operations, '/post-requirement')
API.add_resource(post_matchRequirements, '/match-requirement')
API.add_resource(updating, '/update-profile')
API.add_resource(deleteProfile, '/remove-profile')

if __name__ == "__main__":
    application.run(host="127.0.0.1", port=5000, debug=True)
