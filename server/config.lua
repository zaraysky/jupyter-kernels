box.cfg{}
box.schema.user.revoke('guest', 'read, write, execute', 'universe')
box.schema.user.grant('guest', 'read, write, execute', 'universe')
require('console').listen('127.0.0.1:3312')
