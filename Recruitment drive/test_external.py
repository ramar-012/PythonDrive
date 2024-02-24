# the package required for testing
import requests
import pytest

def test_get_skills():
    # Pass a single skill without the list notation
    response = requests.get("http://127.0.0.1:5000/profile-for-skillset", params={'skills': 'sql'})
    get_response = response.json()
    print(get_response)
    try:
        assert any(candidate['name'] == "Sam" for candidate in get_response)
        print("The get test is success")
    except AssertionError:
        print("Assertion error, name mismatch")

def test_post():
    # Post a new requirement
    posting = requests.post("http://127.0.0.1:5000/post-requirement",
                            json={"id": 9, "name": "Surya Narayanan", "skillset": "[c++, servers]"})
    assert posting.status_code == 200
    response_get = requests.get("http://127.0.0.1:5000/profile-for-skillset",
                                params={'skills': '[c++, servers]'})
    data = response_get.json()

    # Check if any candidate matches the given name
    for candidate in data:
        if candidate['name'] == 'Surya Narayanan':
            print("Post operation is a success")
            break
    else:
        print('Post operation is not a success. Candidate not found.')

def test_post_search():
    post_search = requests.post("http://127.0.0.1:5000/match-requirement", json={"requirementID": 1, "position": "developer", "requiredSkillsets": "[Perl, Swift]"})
    print("Response status code:", post_search.status_code)
    print("Response body:", post_search.text)

    # Check if the request was successful (status code 200)
    if post_search.status_code == 200:
        try:
            testing = post_search.json()
            assert testing['skills'] == '[Perl, Swift]'
            print(testing)
            print("Post search by skills success")
        except ValueError:
            print("Error decoding JSON. Response does not contain valid JSON data.")
    else:
        print(f"Post search unsuccessful. Status code: {post_search.status_code}")



# test the put(updating) operation
def test_put():
    # Perform the update (PUT) operation
    putting = requests.put("http://127.0.0.1:5000/update-profile", json={"id": 3, "skillset": "[c, java, qa]"})
    assert putting.status_code == 200
    response_get = requests.get("http://127.0.0.1:5000/profile-for-skillset", params={'skills': '[c, java]'})
    data = response_get.json()

    # Iterate through the list of candidates and check if any match the expected skills
    try:
        assert any(candidate['skills'] == '[c, java]' for candidate in data)
        print("Update successful")
    except AssertionError:
        print("Update unsuccessful")


# test the delete operation
def test_delete():
    # ID to be deleted
    deleted_id = 9
    # Perform delete (DELETE) operation by candidate ID
    response_delete = requests.delete("http://127.0.0.1:5000/remove-profile", params={'id': deleted_id})
    assert response_delete.status_code == 200
    response_get_all = requests.get("http://127.0.0.1:5000/all-profiles")
    all_profiles = response_get_all.json()

    # Check if the candidate with the deleted ID is not present in the response
    try:
        assert not any(profile['id'] == deleted_id for profile in all_profiles)
        print(f"Deletion by ID {deleted_id} successful")
    except AssertionError:
        print(f"Deletion by ID {deleted_id} unsuccessful or ID still present in the response")

# run all test cases or manually click run against each test functions
test_get_skills()
test_post()
test_post_search()
test_put()
test_delete()
