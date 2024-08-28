`titanclient` is a Python3 library/abstraction layer to access and
control TitanSIm using the DsREST API and manipulate configuration
files.

The current (alpha) version is `1.2.0`.

It's work-in-progress, and the API is subject to unannounced changes
(it will be stable once the library reaches beta). This means it's
still very malleable, and we'd love to hear your suggestions for
future improvements and your feedback about the sorts of things you
think a library like `titanclient` should support if it doesn't
already.

The stuff that's already working is based on daily work in NWST, but
we appreciate feedback from any viewpoint.

Why?
----

The TitanSim DsREST API is a very general API with access to most
nooks and crannies of TitanSim, but the author found its hierarchical
JSON format and similarly involved responses a bit complex. The
purpose of this library is to hide this complexity and simplify
scripting.

Who for?
--------

Anyone looking to programatically control or monitor TitanSim
executions using Python. If you want to write tools to check execution
state or poll statistics in TitanSim, you might find `titanclient`
useful.

Where?
------

The latest version can be found [on Gerrit](https://gerrit.ericsson.se/#/admin/projects/IMS_NWST_ETH/py-titanclient).

Installation
------------

Make sure you are registered in Gerrit Central and that you can read
the repository. All registered users should have read access by
default, but contact the authors if you run into any problems.

Install `pip3`:

```
$ sudo apt-get install python3-pip
```

Install `titanclient` using `pip3` and the Gerrit Central repository
link (replace your SIGNUM with the placeholder in the URL):


```bash
$ pip3 install "git+https:// _USER_SIGNUM_ @gerrit.ericsson.se/a/IMS_NWST_ETH/py-titanclient@0.1.9a1"
```

or use the same `pip3` + `git` command with a local repo:

```bash
$ pip3 install git+file:///path/to/cloned/repo
```

Usage at a Glance
-----------------

Instantiate `titanclient` and list all scenarios found on TitanSim
running on `10.10.10.10` and listening on port `8080`.

```
>>> from titanclient.client import Client
>>> client = Client("10.10.10.10")
>>> client
<titanclient.Client object at 0x7f2258f8a780>
>>> client.scenarios()
[<scenario 0010PsPs_A>, <scenario 0010PsPs_B>, ... ]
```

Load a configuration file and list the same information:

```
>>> from titanclient.config import Config
>>> config = Config("/tmp/TrafficMix.cfg")
>>> config
<titanclient.Config object at 0x7f8d93f572e8>
>>> config.scenarios()
[<scenario 0010PsPs_A>, <scenario 0010PsPs_B>, ... ]
```

See the API documentation below for details of use.

Notes
-----------------

Both `titanclient.client` and `titanclient.config` provide a
simplified view of what's really going on. The DsREST API itself
exposes a hierarchy of entity groups, scenario groups, scenarios and
traffic cases. The configuration, on the other hand, keeps tabs on
scenarios and traffic cases, which - roughly - correspond to scenario
groups and scenarios in the DsREST API.

It wouldn't help the goal of simplification if this mismatch were to
be propagated at a higher level by using both models. Instead, we do
the next worst thing: we add a new one. Currently (that is, until a
better idea comes along), the `Scenario` abstraction, a severe,
possibly broken oversimplification is used in this library.

To Do
-----------

There is lots of stuff that's still missing of course.

A more general (though still not entirely automatic) response handling
scheme is getting there, but DsRequest responses nevertheless require
the user to write their own walker for it.

`titanclient.config` setting of values is work-in-progress.

`DsRequest.callback` is too brittle.

Timeline queries are undesigned at the API level. Either `Client`,
`Scenario` or both should have an API to access Timeline information.

Support `Python 2.7` if there is a need.

Authors
-------

- Levi (peter.soos@ericsson.com)
