# url-shortener-task

url management

short code generation works as follows:
1. When a user creates a new URL, the application generates a unique short code for that URL.
2. The short code is generated using a secrets.token_urlsafe to ensure uniqueness and randomness.
It is easy way to generate a short code that is easily generate and prevents collisions.



db indexes

In the URL shortener application, we have added indexes to the following fields in the URL model:

short_code - because it is used for lookups when redirecting to the original URL. 
This will speed up the retrieval of the original URL based on the short code.  

owner - ForeignKey in PostgreSQL indexing automatically. 
This will speed up queries that filter by owner, such as retrieving all URLs created by a specific user.

In the Click model, we have added an index to the:

Url field - ForeignKey to the URL model.
This will speed up queries that filter by URL, such as retrieving all clicks for a specific URL.

created_at - because it is used for filtering clicks by date.
This will speed up queries that filter clicks based on the date they were created, 
such as retrieving all clicks within a specific date range.

Created composite index for owner and created_at in the URL model.
This will speed up queries that filter URLs by owner and creation date,
such as retrieving all URLs created by a specific user within a specific date range.
