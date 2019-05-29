box.cfg{}
box.schema.user.grant('guest', 'read, write, execute', 'universe', nil, {if_not_exists=true})
require('console').listen('127.0.0.1:3312')
