.. _ntp.time_server_mc:

################
ntp.time_server
################

This Model Component provides NTP services for all nodes in the experiment graph.

.. warning::

    This Model Component currently **ONLY** works with Ubuntu-Trusty VMs. Prior to using it with newer/different
    operating systems, modifications will be necessary.


**Model Component Dependencies:**
    * :ref:`linux.base_objects_mc`
    * :ref:`linux.ubuntu_mc`

************
VM Resources
************

This MC provides the following VM Resources:
    * ``ntp-trusty-server.tar`` - A tar-compressed directory containing the NTP debian package and its dependency (``libopts25``).

*****************
Available Objects
*****************

.. automodule:: ntp.time_server
    :members:
    :undoc-members:
    :special-members:
    :private-members:
    :show-inheritance:
    :exclude-members: __dict__,__weakref__,__module__
