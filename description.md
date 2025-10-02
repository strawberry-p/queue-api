
This API allows users to create, delete, push to and pop from ordered tables (queues/stacks).
Reading from these tables is done using the `/api/pop` (pops the first added item, FIFO) and `/api/stack_pop` (pops the last added item, LIFO) endpoints, which remove the entry that was read.

### Queue management

Each table has 3 corresponding keys: the read key, the write key and the delete key.
The first two keys are supplied by the client when creating the queue with the PUT `/api/manage` endpoint. The delete key is a random string returned by the server as a response to that creation request. The delete key can also be used to change the read and write keys later on.

*Since the keys are currently stored in plaintext, it is recommended to supply a random string for the write and read keys.*
