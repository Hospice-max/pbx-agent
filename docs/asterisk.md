# Asterisk integration

PBX Agent uses Asterisk AMI. AMI is an asynchronous client/server management interface: clients send actions and receive events. The official documentation describes port 5038 as the default TCP AMI port when enabled.

The initial implementation uses these actions/events:

- `Login`
- `PJSIPShowEndpoints`
- `ExtensionStateList`
- `CoreShowChannels`
- `EndpointList`
- `ContactStatus`
- `ExtensionStatus`
- `ExtensionState`
- `Newchannel`
- `Newstate`
- `Hangup`

Event fields can vary by Asterisk version and channel technology. The implementation therefore treats unknown fields conservatively.
