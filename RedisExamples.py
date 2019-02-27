import redis

#######################################################
# Inserting a Document

r = redis.Redis(host='localhost', port=6379, db=0)

deger = r.get('foo')
print(deger)
#######################################################

