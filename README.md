#url management

application generates a unique short code for each URL created by the user.
all urls created by a user are associated with that user, allowing for easy management and retrieval of URLs.

Project have been implemented using Django REST Framework for building the API endpoints and PostgreSQL as the database for storing URL and click data.
Also have worker implemented like simple async python script that runs in the background to subscribe to raw info about click.
And then process that info and send it to the subscriber for further processing and storing in the database.
This allows for efficient handling of click data without blocking the main application.


##To run the application
you can follow these steps:

1. Clone the repository and navigate to the project directory.
   
2. Create a .env file in the project root directory or take a look at .env.example for reference and add the necessary environment variables such as database credentials and secret keys.

3. Run docker-compose up to start the application and the database. Migrations will be applied automatically when the application starts.

##Endpoints
all endpoints that require authentication are protected using JWT tokens, ensuring that only authorized users can access their URLs and related data.
example of endpoints:

POST /api/urls/ - Create a new short URL.
in the request body, you need to provide the original URL that you want to shorten. The response will include the generated short code and the original URL.
authentication is required to create a new short URL, and the created URL will be associated with the authenticated user.

GET /api/urls/ - Retrieve a list of all URLs created by the authenticated user with click count.
authentication is required to access this endpoint, and it will return a list of URLs along with the number of clicks each URL has received.

GET /api/urls/{id}/ - Retrieve details of a specific URL and recent 10 clicks by id.
authentication is required to access this endpoint, and it will return the details of the specified URL along with the recent 10 clicks associated with that URL.

DELETE /api/urls/{id}/ - Delete a specific URL by id.
authentication is required to access this endpoint, and it will delete the specified URL if it belongs to the authenticated user.

GET /{short_code}/ - Redirect to the original URL based on the short code.
authentication is not required to access this endpoint, and it will redirect the user to the original URL associated with the provided short code.


GET /api/urls/summary/ - Retrieve a summary of all URLs created by the authenticated user, including total clicks and click count for each URL.
GET /api/urls/{id}/stats/ - Retrieve detailed statistics for a specific URL, including total clicks, clicks by last 30 days and top 5 browsers and top 5 os.
authentication is required to access these endpoints, and they will return the requested statistics for the authenticated user's URLs.


##Query counts for endpoints:
get all urls endpoint - 1 query without authorization

get url by id endpoint - 2 queries without authorization

get url summary endpoint - 3 query without authorization

get url stats endpoint - 4 query without authorization


##DB indexes

In the URL shortener application, we have added indexes to the following fields in the `URL model`:

`short_code` - because it is used for lookups when redirecting to the original URL. 
This will speed up the retrieval of the original URL based on the short code.  

`owner` - ForeignKey in PostgreSQL indexing automatically. 
This will speed up queries that filter by owner, such as retrieving all URLs created by a specific user.

In the `Click model`, we have added an index to the:

`Url field` - ForeignKey to the URL model.
This will speed up queries that filter by URL, such as retrieving all clicks for a specific URL.

`created_at` - because it is used for filtering clicks by date.
This will speed up queries that filter clicks based on the date they were created, 
such as retrieving all clicks within a specific date range.

Created composite index for `owner` and `created_at` in the `URL model`.
This will speed up queries that filter URLs by owner and creation date,
such as retrieving all URLs created by a specific user within a specific date range.


##Architecture
redis have been used as a message broker for the click processing worker. 
When a click event occurs, the application publishes the click data to a Redis channel.

Worker subscribes to the Redis channel and listens for incoming click events. 
When a click event is received, the worker processes the data and sends it to the subscriber for further processing.

Api subscribes to the Redis channel and listens for processed click data from the worker. 
When the processed data is received, the API stores it in the PostgreSQL database for future retrieval and analysis.

##Choices:

short code generation works as follows:
1. When a user creates a new URL, the application generates a unique short code for that URL.
   
2. The short code is generated using a secrets.token_urlsafe to ensure uniqueness and randomness.
It is easy way to generate a short code that is easily generate and prevents collisions.


Keep Django sync with async worker:

It is simple to keep Django sync with async worker, because we are using Redis as a message broker for click processing. 
When a click event occurs, the application publishes the click data to a Redis channel.
This project is not big, so it is easy to keep Django sync with async worker.


Dockerfiles

Each service has its own Dockerfile, which defines the environment and dependencies required to run that service.
Each Dockerfile is optimized for its specific service, ensuring that the application runs efficiently and consistently across different environments.
Easy to maintain and update each service independently, as changes to one service do not affect the others.

##What I have learned from this project:

1. For this project, I have learned how to build a URL shortener application using Django REST Framework and PostgreSQL.
2. I have learned how to implement JWT authentication using the djangorestframework-simplejwt package.
3. ViewSets and Routers: I have learned how to use ViewSets and Routers in Django REST Framework to create API endpoints for managing URLs and clicks.
4. @action decorator: I have learned how to use the @action decorator in Django REST Framework to create custom actions for ViewSets, such as retrieving URL statistics and summaries.
5. using Redis as a message broker: I have learned how to use Redis as a message broker for asynchronous processing of click events, allowing for efficient handling of click data without blocking the main application.
6. using .env file for configuration: I have learned how to use a .env file for managing environment variables and configuration settings in a Django application.
7. async processing: I have learned how to implement asynchronous processing using a worker that subscribes to a Redis channel for click events, allowing for efficient handling of click data without blocking the main application.
8. it was the hardest thing to implement in this project, but I have learned how to use Redis as a message broker and how to process click data asynchronously using a worker.
9. Also creating test cases for the worker was a challenge, especially for worker service, but I have learned how to write test cases for asynchronous processing and how to mock Redis channels for testing purposes.



