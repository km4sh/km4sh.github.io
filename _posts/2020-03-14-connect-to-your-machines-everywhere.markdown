---
layout: post
title:  "Connect to your Machines Everywhere."
date:   2020-03-14 20:57:12 +0800
categories: Networks


# Table of Contents

1.  [Reverse SSH Forwarding.](#org62afd15)
    1.  [Some reference:](#org130fb40)
        1.  [Reverse SSH command options](#org0f718b0)
    2.  [Solution](#org6286da6)
        1.  [Step 1: RSA-key publication](#org7ccf9e8)
        2.  [Step 2 Reverse SSH Tunnel by port forwarding](#orgb0ca664)
        3.  [Stpe 3 (optional) Open a direct door](#orgdef335f)
        4.  [Stpe 4 (really?) Connect to the GPU Cluster](#orge451427)


<a id="org62afd15"></a>

I have these hosts:

    - GPU Cluster: elijah@10.0.0.10 (in LAB LAN)
    - Personal Ubuntu: elijah@10.0.0.104 (in LAB LAN)
    - UCloud Server: root@120.132.2.138 (in WAN)
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

Use `ssh-keygen` on `10.0.0.4`, then copy the RSA public key to `120.132.2.138` using
`ssh-copy-id`. This is to avoid typing password while reconnection.
    {% highlight shell %}

    elijah@10.0.0.104 > $
    ssh-keygen
    ssh-copy-id root@120.132.2.138

    {% endhighlight %}
In our case you **should NOT type any passphase** in `ssh-keygen`, because you may
need to type the RSA key passphase while using the key.


<a id="orgb0ca664"></a>

### Step 2 Reverse SSH Tunnel by port forwarding

Then pull a *Port forwarding* from `120.132.2.138` to `10.0.0.4`, for example run this
command on `10.0.0.104`:

    elijah@10.0.0.104 > $
    autossh -M 33255 -fCNR 33254:localhost:22 root@120.132.2.138

where `autossh` is a very useful tool to keep connection from TIMEOUT exception.
and `33254:localhost:22 root@120.132.2.138` means let the **remote port(33254)** point
to the **localhost port(22 default SSH port)**. The option `-M 33255` is used for
autossh monitoring if the "SSH connection"(actually a port forwarding) is good,
and if not, autossh will reconnect automatically as its name.


<a id="orgdef335f"></a>

### Stpe 3 (optional) Open a direct door

Actually now it is possible to connenct the `10.0.0.104` by using command

    root@120.132.2.138 > $
    ssh -p 33254 elijah@localhost

on `120.132.2.138`. and the `elijah` above should be the username you wanna log as
on `10.0.0.104`. Amazing!

But you still need to SSH to `120.132.2.138` at the beginning on your machine. Why
not open another port to directly connect to `10.0.0.104` on the jump-server?

Good to know that SSH also allow us to do local port forwarding operation.

    root@120.132.2.138 > $
    ssh -fCNL *:9209:localhost:33254 localhost

This command point `localhost:9209` to `localhost:33254`, that is exactally the same
as `120.132.2.138:9209` to `localhost:33254`. So we are able to connect to
`10.0.0.104` directly from our own machine by typing

    me@macbook_pro > $
    ssh -p 9209 elijah@120.132.2.138

Amazing, again!


<a id="orge451427"></a>

### TODO Stpe 4 (really?) Connect to the GPU Cluster

Because there are so many users still logged in on `10.0.0.10` (GPU Cluster if you
forgot) right now, the best way to do it is write this down in your `~/.bashrc`

    alias wcid="ssh elijah@10.0.0.10"

booyah! A perfect SSH connection established!
Enjoy!
