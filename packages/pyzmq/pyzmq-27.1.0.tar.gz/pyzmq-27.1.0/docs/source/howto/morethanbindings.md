% PyZMQ Bindings doc, by Min Ragan-Kelley, 2011

(bindings)=

# More Than Just Bindings

PyZMQ is ostensibly the Python bindings for [ØMQ], but the project, following
Python's 'batteries included' philosophy, provides more than just Python methods and
objects for calling into the ØMQ C++ library.

## The Core as Bindings

PyZMQ is currently broken up into subpackages. First, is the Backend. `zmq.backend`
contains the actual bindings for ZeroMQ, and no extended functionality beyond the very
basics required.
This is the _compiled_ portion of pyzmq,
either with Cython (for CPython) or CFFI (for PyPy).

## Thread Safety

In ØMQ, Contexts are threadsafe objects, but Sockets are **not**. It is safe to use a
single Context (e.g. via {meth}`zmq.Context.instance`) in your entire multithreaded
application, but you should create sockets on a per-thread basis. If you share sockets
across threads, you are likely to encounter uncatchable c-level crashes of your
application unless you use judicious application of {py:class}`threading.Lock`, but this
approach is not recommended.

```{seealso}
ZeroMQ API note on threadsafety on [2.2](http://api.zeromq.org/2-2:zmq)
or [3.2](http://api.zeromq.org/3-2:zmq)
```

## Socket Options as Attributes

```{versionadded} 2.1.9
```

In 0MQ, socket options are set/retrieved with the `set/getsockopt()` methods. With the
class-based approach in pyzmq, it would be logical to perform these operations with
simple attribute access, and this has been added in pyzmq 2.1.9. Simply assign to or
request a Socket attribute with the (case-insensitive) name of a sockopt, and it should
behave just as you would expect:

```python
s = ctx.socket(zmq.DEALER)
s.identity = b"dealer"
s.hwm = 10
s.events
# 0
s.fd
# 16
```

### Default Options on the Context

```{versionadded} 2.1.11
```

Just like setting socket options as attributes on Sockets, you can do the same on Contexts.
This affects the default options of any *new* sockets created after the assignment.

```python
ctx = zmq.Context()
ctx.linger = 0
rep = ctx.socket(zmq.REP)
req = ctx.socket(zmq.REQ)
```

Socket options that do not apply to a socket (e.g. SUBSCRIBE on non-SUB sockets) will
simply be ignored.

## libzmq constants as Enums

```{versionadded} 23
```

libzmq constants are now available as Python enums,
making it easier to enumerate socket options, etc.

## Context managers

```{versionadded} 14
Context/Sockets as context managers
```

```{versionadded} 20
bind/connect context managers
```

For more Pythonic resource management,
contexts and sockets can be used as context managers.
Just like standard-library socket and file methods,
entering a context:

```python
import zmq

with zmq.Context() as ctx:
    with ctx.socket(zmq.PUSH) as s:
        s.connect(url)
        s.send_multipart([b"message"])
    # exiting Socket context closes socket
# exiting Context context terminates context
```

In addition, each bind/connect call may be used as a context:

```python
with socket.connect(url):
    s.send_multipart([b"message"])
# exiting connect context calls socket.disconnect(url)
```

## Core Extensions

We have extended the core functionality in some ways that appear inside the `zmq.sugar` layer, and are not general ØMQ features.

### Builtin Serialization

First, we added common serialization with the builtin {py:mod}`json` and {py:mod}`pickle`
as first-class methods to the {class}`~.zmq.Socket` class. A socket has the methods
{meth}`~.zmq.Socket.send_json` and {meth}`~.zmq.Socket.send_pyobj`, which correspond to sending an
object over the wire after serializing with {mod}`json` and {mod}`pickle` respectively,
and any object sent via those methods can be reconstructed with the
{meth}`~.zmq.Socket.recv_json` and {meth}`~.zmq.Socket.recv_pyobj` methods.

```{warning}
Deserializing with pickle grants the message sender access to arbitrary code execution on the receiver.
Never use `recv_pyobj` on a socket that might receive messages from untrusted sources
before authenticating the sender.

It's always a good idea to enable CURVE security if you can,
or authenticate messages with e.g. HMAC digests or other signing mechanisms.
```

Text strings are other objects that are not unambiguously sendable over the wire, so we include
{meth}`~.zmq.Socket.send_string` and {meth}`~.zmq.Socket.recv_string` that send bytes
after encoding the message ('utf-8' is the default).

These are all convenience methods, and users are encouraged to build their own serialization that best suits their applications needs,
especially concerning performance and security.

```{seealso}
- {ref}`Further information <serialization>` on serialization in pyzmq.
```

### MessageTracker

The second extension of basic ØMQ functionality is the {class}`.MessageTracker`. The
MessageTracker is an object used to track when the underlying ZeroMQ is done with a
message buffer. One of the main use cases for ØMQ in Python is the ability to perform
non-copying sends. Thanks to Python's buffer interface, many objects (including NumPy
arrays) provide the buffer interface, and are thus directly sendable. However, as with any
asynchronous non-copying messaging system like ØMQ or MPI, it can be important to know
when the message has actually been sent, so it is safe again to edit the buffer without
worry of corrupting the message. This is what the MessageTracker is for.

The MessageTracker is a simple object, but there is a penalty to its use. Since by its
very nature, the MessageTracker must involve threadsafe communication (specifically a
builtin {py:class}`~queue.Queue` object), instantiating a MessageTracker takes a modest
amount of time (10s of µs), so in situations instantiating many small messages, this can
actually dominate performance. As a result, tracking is optional, via the `track` flag,
which is optionally passed, always defaulting to `False`, in each of the three places
where a Frame object (the pyzmq object for wrapping a segment of a message) is
instantiated: The {class}`.Frame` constructor, and non-copying sends and receives.

A MessageTracker is very simple, and has just one method and one attribute. The property
{attr}`.MessageTracker.done` will be `True` when the Frame(s) being tracked are no
longer in use by ØMQ, and {meth}`.MessageTracker.wait` will block, waiting for the
Frame(s) to be released.

```{Note}
A Frame cannot be tracked after it has been instantiated without tracking. If a
Frame is to even have the *option* of tracking, it must be constructed with
`track=True`.
```

## Extensions

So far, PyZMQ includes four extensions to core ØMQ that we found basic enough to be
included in PyZMQ itself:

- {ref}`zmq.log <logging>` : Logging handlers for hooking Python logging up to the
  network
- {ref}`zmq.devices <devices>` : Custom devices and objects for running devices in the
  background
- {ref}`zmq.eventloop <eventloop>` : The [Tornado] event loop, adapted for use
  with ØMQ sockets.
- {ref}`zmq.ssh <ssh>` : Simple tools for tunneling zeromq connections via ssh.

[tornado]: https://www.tornadoweb.org
[ømq]: https://zeromq.org/
