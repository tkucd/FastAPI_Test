from controllers import *

app.add_api_route('/', index)

app.add_api_route('/admin', admin)

app.add_api_route('/register', register, methods=['GET', 'POST'])

app.add_api_route('/todo/{username}/{year}/{month}/{day}', detail)