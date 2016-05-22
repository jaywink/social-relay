# Relay design concept

## Status

This document is in working draft status and is subject to change.

## Description

This document describes the generic principles on how a relay should be built, and how the relay system should be interacted with.

For the original idea, see the [diaspora* project wiki](https://wiki.diasporafoundation.org/Relay_servers_for_public_posts).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC2119](https://www.w3.org/TR/activitystreams-core/#bib-RFC2119).

## Terms used in this document

* `node` - a server implementing the Diaspora protocol.
* `relay server` - a server acting as a relay for public visibility content.
* `relay system` - a group of independent relay servers.
* `protocol` - the Diaspora protocol which the relay system uses.
* `participation` - a comment, like or participation Diaspora protocol message.
* `retraction` - a removal of a commer, like or participation Diaspora protocol message.

## Integrating with the relay system

### Subscribing vs sending

There are two ways to integrate with the relay system - subscribing to content and sending content.

Nodes MAY subscribe to content from the relay system. Nodes MAY send out content to the relay system. These two are not depending on each other. A node does not have to subscribe to content to send content, or the other way around.

### Subscribing to content

#### Node subscription preferences

A node wishing to subscribe to content from the relay system MUST expose a `.well-known/x-social-relay` JSON document with the following schema.

    {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "id": "http://the-federation.info/social-relay/well-known-schema-v1.json",
      "type": "object",
      "properties": {
        "subscribe": {
          "type": "boolean"
        },
        "scope": {
          "type": "string",
          "pattern": "^all|tags$"
        },
        "tags": {
          "type": "array",
          "items": {"type": "string"},
          "uniqueItems": true
        }
      },
      "required": [
        "subscribe",
        "scope",
        "tags"
      ]
    }

`subscribe` indicates whether the node wants to receive content from the relay system.

`scope` is either `all` or `tags`. If `all`, the relay system will send all content to the subscriber. If `tags`, a list of `tags` (without the leading `#`) should be provided in the `tags` property.

If a previously subscribing node wants to stop subscribing, it MUST either remove the `.well-known/x-social-relay` file or set `subscribe` to `false`.

Example `.well-known/x-social-relay` document:

    {
      "subscribe": true,
      "scope": "tags",
      "tags": ["foo", "bar"]
    }

#### Node discovery

The relay system must somehow become aware of the node to fetch the `.well-known/x-social-relay` document. Currently nodes MUST register at the https://the-federation.info list. Once registered there, the relay system will automatically become aware of the node.

### Sending content to the relays

Only public visibility content is handled by the relay system. Nodes MUST NOT send out private messages to the relay system.

Nodes MUST NOT send a single status message, comment, like or other content to more than one relay server. Nodes MUST send each content payload only once and only to one relay server.

A node MAY send content to any relay server in the system. This server can be hard coded into settings to always be the same or the server can be randomized from a list on each send.

#### Relay servers

Relay servers are basically standard identities when it comes to discovering them. Each relay will have a handle in the form `relay@domain.tld`. Normal Diaspora protocol discovery methods SHOULD be used to interact with them.

When sending content to a relay, the payload MUST be composed as if the target identity was any other identity in the network. Nodes wishing to send out to relays need only carbon copy the relay server handle into any public content.

#### Choosing a relay server

A list of relay servers is not yet available since work on decentralizing the relay system is ongoing. The following relays are currently known to be operational:

* `relay@relay.iliketoast.net`
* `relay@podrelay.net`
* `relay@relay.diasp.org`

A node MAY send content to any of the relays.

#### Types of outgoing content

##### Status messages

A node MAY send out public visibility status messages to a relay.

A node MUST send out to a relay retractions for status messages that have been previously sent out to a relay.

##### Photos

Public visibility photos linked to status messages MAY be sent out to a relay. The relay system does not currently handle photos not linked to status messages.

A node MUST send out to a relay retractions for photos that have been previously sent out to a relay.

##### Participations (Comments, Likes and Participations)

A node MUST send out comments, likes and participations to a relay for any locally authored status messages, if the status message that is being commented, liked or participated upon was sent out to a relay. The relay SHOULD be the same, but this is not a hard requirement.

The key here is **locally authored status message**. As per the Diaspora protocol, any participations on local status messages from both local and remote users MUST be relayed to both local and remote subscribers. The same rules apply to sending participations to the relay. If the status message is local, any comments and likes MUST be sent out to the relay system, if the status message has also been sent out.

A node MUST send out to a relay retractions for participations on locally authored content, as per the rules above for sending out new participations.

## Building a relay server

TBD

## Author

Jason Robinson / @jaywink / https://jasonrobinson.me / https://iliketoast.net/u/jaywink

## License

[CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)

![](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)
