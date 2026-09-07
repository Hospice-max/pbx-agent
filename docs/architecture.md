# Architecture

PBX Agent is deliberately small. The agent has three responsibilities:

1. maintain an AMI connection;
2. normalize selected Asterisk events into an in-memory state store;
3. expose that state through HTTP.

The AMI client reconnects after a failure. Event handling is intentionally isolated from HTTP serving so a dashboard request cannot block AMI processing.

## State lifecycle

At connection time the agent requests endpoint, extension and channel lists. Afterwards it consumes asynchronous AMI events.

The state store keeps:

- extension state;
- PJSIP endpoint/contact information;
- active channels;
- AMI health and timestamps.

A JSON snapshot is persisted atomically to the configured state path.
