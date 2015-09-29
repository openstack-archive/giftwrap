<div align="center"><img src="./giftwrap.png" alt="Giftwrap"></div><hr />

A tool for creating bespoke system-native OpenStack artifacts.

Anyone running OpenStack at scale typically crafts their own software distribution mechanism. There may be many reasons for this, but chief among them seem to be the desire to ship security patches, deliver custom code, lock their releases at a revision of their choosing, or just generally stay closer to trunk.

Unfortunately, until now, there has been no easy way to accomplish this. If one were to decide to utilize distribution packages they are now at the mercy of the distribution itself - who's release timeline may not be the same as yours.

On the other hand, if one were to install directly from source, they will encounter a slightly different problem. Because the Python community is quite active, and because OpenStack, in many regards, does not strictly call out it's dependencies, one may build OpenStack with incompatible (or at least unknown) dependencies. Even worse, one may even find that OpenStack components may be different on different nodes in the cluster.

Long story short, this sucks.

Inspired by some of the work I had done to create [omnibus-openstack](https://github.com/craigtracey/omnibus-openstack), I decided to do things slightly differently. While omnibus-openstack met most of my needs there were a few problems. First, the project was written in Ruby. While this, in my opinion, is not a problem, this makes it somewhat unapproachable to a vast segment of OpenStack users and operators. Second, the packages are HUGE. Again, while this may not be a real problem for many, the reason they are huge is that they manage all of the system level dependencies as well: things like openssl, libvirt, etc. These are not things that many folks typically want to be responsible for managing; whether for security or even complexity reasons.

With all of this in mind, it seemed to me that we already had all of the information that we already needed to create system-native (ie. rpm, deb, and even Docker) artifacts that had already been tested with the Gerrit CI infrastructure.  Hence, giftwrap.

Status
------
[![Build Status](https://api.travis-ci.org/blueboxgroup/giftwrap.png)](https://travis-ci.org/blueboxgroup/giftwrap)

Usage
=====

    $ pip install .
    $ python setup.py install
    $ giftwrap -h

Dependencies
------------

* `Vagrant`
* `fpm`
* `docker` (optional)

Development
-----------

    $ git clone https://github.com/blueboxgroup/giftwrap.git
    $ vagrant up

Testing
-------

    $ make test

Supports
--------
* Jinja2 templating - change your build by changing variables; not your manifest
* versioned paths - this allows you to run services side by side; easing the upgrade process.

How It Works
------------
giftwrap is pretty simple. The basic flow is something like this:
1. Create a YAML manifest with the packages you would like to build. See sample.yml
2. Run:
```
 giftwrap build -m <manifest> [-v <version>]
```
3. giftwrap will clone the git repo and git ref that you specify for each of the OpenStack projects
4. giftwrap will find the closest Gerrit Change-Id and retrieve it's build logs
5. From the build logs, giftwrap will find the pip dependencies used for that build and record them.
6. A new virtualenv will be built with the pip dependencies found
7. The OpenStack project code will be installed into the same virtualenv; but with locked pip dependencies
8. giftwrap will check [devstack](https://devstack.org) for the system dependencies necessary for that project (to be done)
9. An [fpm](https://github.com/jordansissel/fpm) package will be built from the intersection of the python install and system dependencies

DockerDockerDockerDockerDocker
------------------------------

This shows how to use docker-in-docker to build packages really fast.  the example shows doing it within the provided vagrant instance.  but this is for illustration purposes,  it should be runnable from any machine with docker installed.


Build a giftwrap docker container like this:

```
$ docker build -t bluebox/giftwrap .
```

Run the giftwrap docker image and map in your docker socket and your manifest file:

```
$ docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v /vagrant/sample.yml:/tmp/manifest.yml  bluebox/giftwrap
$ docker images openstack-9.0
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
openstack-9.0       bbc6                44c37c8d9672        10 minutes ago      499.5 MB

```

TODO
----
* Provide option for source removal; package only the executables
* Allow for additional pip dependencies, alternate pip dependency versions, and even user-defined pip dependencies
* Allow for additional/alternate system package dependencies

License
-------
|                      |                                                    |
|:---------------------|:---------------------------------------------------|
| **Authors**          |  John Dewey (<john@dewey.ws>)                      |
|                      |  Craig Tracey (<craigtracey@gmail.com>)            |
|                      |  Paul Czarkowski (<username.taken@gmail.com>)      |
|                      |                                                    |
| **Copyright**        |  Copyright (c) 2014, John Dewey                    |
|                      |  Copyright (c) 2014, Craig Tracey                  |
|                      |  Copyright (c) 2014, Paul Czarkowski               |

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
