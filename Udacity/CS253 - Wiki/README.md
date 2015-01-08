Features:

*Signup/Login verification with hash. Generates a cookie for the user's session.
*Writes are made to both DB and Memcache.
*Reads are made off the memcache if avaliable. If not, memcache is updated with the DB.
*A sprinkle of css