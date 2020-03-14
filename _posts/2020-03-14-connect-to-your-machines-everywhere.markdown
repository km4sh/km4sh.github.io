---
layout: post
title:  "Connect to your Machines Everywhere."
date:   2020-03-14 20:57:12 +0800
categories: Networks
---
# Table of Contents

- [Reverse SSH Forwarding.](#org62afd15)
    - [Some reference:](#org130fb40)
      - [Reverse SSH command options](#org0f718b0)
    - [Solution](#org6286da6)
      - [Step 1: RSA-key publication](#org7ccf9e8)
      - [Step 2 Reverse SSH Tunnel by port forwarding](#orgb0ca664)
      - [Stpe 3 (optional) Open a direct door](#orgdef335f)
      - [Stpe 4 (really?) Connect to the GPU Cluster](#orge451427)


<a id="org62afd15"></a>

I have these hosts:

    - GPU Cluster: elijah@10.8.92.10 (in LAB LAN)
    - Personal Ubuntu: elijah@10.8.92.104 (in LAB LAN)
    - UCloud Server: root@128.128.128.128 (in WAN)
    - Macbook Pro: me@I.DON.T.KNOW (in Happy)

and I wanna use my **Macbook Pro** to connect to the **GPU Cluster** directly.


<a id="org130fb40"></a>

## Some reference:


<a id="org0f718b0"></a>

### Reverse SSH command options

1.  `-R`

    Specifies that connections to the given TCP port or Unix socket on the remote
    (server) host are **to be forwarded to** the local side.

2.  `-L`

    Specifies that connections to the given TCP port or Unix socket on the local
    (client) host are to be forwarded to the given host and port, or Unix socket, on
    the remote side.

3.  TODO `-f`

    Run SSH as daemon progress


<a id="org6286da6"></a>

## Solution


<a id="org7ccf9e8"></a>

### Step 1: RSA-key publication

Use `ssh-keygen` on `10.8.92.4`, then copy the RSA public key to `128.128.128.128` using
`ssh-copy-id`. This is to avoid typing password while reconnection.

    elijah@10.8.92.104 > $
    ssh-keygen
    ssh-copy-id root@128.128.128.128

In our case you **should NOT type any passphase** in `ssh-keygen`, because you may
need to type the RSA key passphase while using the key.


<a id="orgb0ca664"></a>

### Step 2 Reverse SSH Tunnel by port forwarding

Then pull a *Port forwarding* from `128.128.128.128` to `10.8.92.4`, for example run this
command on `10.8.92.104`:

    elijah@10.8.92.104 > $
    autossh -M 33255 -fCNR 3838:localhost:22 root@128.128.128.128

where `autossh` is a very useful tool to keep connection from TIMEOUT exception.
and `3838:localhost:22 root@128.128.128.128` means let the **remote port(3838)** point
to the **localhost port(22 default SSH port)**. The option `-M 33255` is used for
autossh monitoring if the "SSH connection"(actually a port forwarding) is good,
and if not, autossh will reconnect automatically as its name.


<a id="orgdef335f"></a>

### Stpe 3 (optional) Open a direct door

Actually now it is possible to connenct the `10.8.92.104` by using command

    root@128.128.128.128 > $
    ssh -p 3838 elijah@localhost

on `128.128.128.128`. and the `elijah` above should be the username you wanna log as
on `10.8.92.104`. Amazing!

But you still need to SSH to `128.128.128.128` at the beginning on your machine. Why
not open another port to directly connect to `10.8.92.104` on the jump-server?

Good to know that SSH also allow us to do local port forwarding operation.

    root@128.128.128.128 > $
    ssh -fCNL *:4040:localhost:3838 localhost

This command point `localhost:4040` to `localhost:3838`, that is exactally the same
as `128.128.128.128:4040` to `localhost:3838`. So we are able to connect to
`10.8.92.104` directly from our own machine by typing

    me@macbook_pro > $
    ssh -p 4040 elijah@128.128.128.128

Amazing, again!


<a id="orge451427"></a>

### TODO Stpe 4 (really?) Connect to the GPU Cluster

Because there are so many users still logged in on `10.8.92.10` (GPU Cluster if you
forgot) right now, the best way to do it is write this down in your `~/.bashrc`

    alias wcid="ssh elijah@10.8.92.10"

booyah! A perfect SSH connection established!
Enjoy!
