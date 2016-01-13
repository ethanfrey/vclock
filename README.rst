VClock - Simple Vector Clocks for Python
========================================

Vector clocks are used to keep track of time in distributed systems, allowing us to 
maintain "partial orderings" of causually related events.  This is mainly used by
distributed databases, but applicable to any "offline-first" app.

One feature I had not seen, was the ability to generate serialized vector clocks, whose
lexographical order is also equivalent to a valid ordering of events (meaning, any event
that was visible to me before my action will be before me, and any that builds upon my action
will be after me).  The ordering of "concurrent" events will be arbitrary but deterministic.

The main use case here is to provide id strings for a key-value database, so we get back an ordered
list of events with a very efficient query that uses the b-tree index on the id field.

Usage
=====

TODO

More Background Info
===================

TODO


License
=======

This project is released under GPLv3.
