
# **Plan**

# 1. Create django project:

- Adjust settings
- Define dirs/urls
- Set database connection
- Create WR app
- Register app at settings.py

# 2. Create models

## User:
- username
- email
- password
- full_name

## Subscription:
- city: ForeignKey(Location)
- user: ForeignKey(User)
- period: ForeignKey(Period)

## Location:
- city: String
- country: String

## Period:
- period: int _`# 1/2/6/12 hours`_


# 3. Create data requesting functionality (Maybe Context-processor)
- Make 4 groups for each period (1, 2, 6, 12)
- Every group is filtering needed location to request data
- Request weather data to undefined service

# 4. Create Notificator:
- Receive weather data
- Send data to defined Users

# 5. Create API:
- API views using rest-framework classes
- Routes

# 6. Modify app with social auth
- Github/Google oauth
