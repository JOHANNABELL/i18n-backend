from slowapi import Limiter
from slowapi.util import get_remote_address

# Here we are creating a rate limiter object
# The object is used to limit the number of requests to the API to prevent abuse and DoS attacks
# The key function is used to get the remote address of the client
# The key function is a function that returns a string that is used to identify the client
# The default limit is 100 requests per minute
limiter = Limiter(key_func=get_remote_address)