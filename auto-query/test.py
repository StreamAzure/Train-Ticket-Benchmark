import logging
from queries import Query
from scenarios import query_and_preserve

# login train-ticket and store the cookies
url = 'http://localhost:8080'
q = Query(url)
if not q.login():
    print('login failed')

print("login success")

# execute scenario on current user
query_and_preserve(q)

# or execute query directly
# q.query_high_speed_ticket()