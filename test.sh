BaseURL="http://127.0.0.1:8000/"
BaseUserURL="${BaseURL}users/"
BaseRecommendationURL="${BaseURL}recommendation/"

all_users=`curl ${BaseUserURL} -s`
user_count_1=$(echo "${all_users}" | jq '. | length')

email=$(echo "akash$(shuf -i 1-1000000 -n 1)-$(date +%s)"@gmail.com)
user='{"name": "Akash Chattopadhyay", "age": 24, "gender": "male", "email": "'"${email}"'", "city": "Gurgaon", "interests": ["sports"]}'
new_user=`curl -s -H 'Content-Type: application/json' -d "${user}" -X POST ${BaseUserURL}`
all_users=`curl ${BaseUserURL} -s`
user_count_2=$(echo "${all_users}" | jq '. | length')

if [[ $user_count_1 != $((user_count_2 - 1)) ]]
then
    echo "Things went wrong in testing positive for creation"
    exit 0
fi

new_user_1=`curl -s -H 'Content-Type: application/json' -d "${user}" -X POST ${BaseUserURL}`
all_users=`curl ${BaseUserURL} -s`
user_count_2=$(echo "${all_users}" | jq '. | length')
if [[ $user_count_1 == $((user_count_2 - 2)) ]]
then
    echo "Things went wrong in testing negative for creation"
    exit 0
fi

id=$(echo "${new_user}" | jq '.id')
final_user_url="${BaseUserURL}${id}"
user_test=`curl -s -H 'Content-Type: application/json' -X GET ${final_user_url}`

if [[ "${user_test}" != "${new_user}" ]]
then
    echo "Things went wrong in testing positive for reading one"
    exit 0
fi

user_test=`curl -s -H 'Content-Type: application/json' -X GET ${BaseUserURL}/-1`
if [[ "${user_test}" == "${new_user}" ]]
then
    echo "Things went wrong in testing negative for reading one"
    exit 0
fi

user='{"name": "John Doe", "age": 24, "gender": "male", "email": "'"${email}"'", "city": "Gurgaon", "interests": ["reading"]}'
user_test_2=`curl -s -H 'Content-Type: application/json' -d "${user}" -X PATCH ${final_user_url}`
user_test=`curl -s -H 'Content-Type: application/json' -X GET ${final_user_url}`

if [[ "$(echo "${user_test}" | jq '.name')" != "$(echo "${user}" | jq '.name')" ]]
then
    echo "Things went wrong in testing positive for updating"
    exit 0
fi

id=$(echo "${user_test}" | jq '.id')
recommendations=`curl -s -H 'Content-Type: application/json' -X GET ${BaseRecommendationURL}${id}`
user_count_1=$(echo "${recommendations}" | jq '. | length')
echo $user_count_1

user_test=`curl -s -H 'Content-Type: application/json' -X DELETE ${final_user_url}`
user_test_2=`curl -s -H 'Content-Type: application/json' -X GET ${final_user_url}`
if [[ "${user_test_2}" == "${user_test}" ]]
then
    echo "Things went wrong in testing positive for deleting"
    exit 0
fi
