import argparse
import os
import time
import json
import paho.mqtt.client as mqtt
from mcp.server.fastmcp import FastMCP
import threading
from typing import List, Dict, Any

# --- Configuration ---

parser = argparse.ArgumentParser(description="MCP Server for MQTT Operations")
# MQTT Configuration
parser.add_argument('--broker', default=os.getenv('MQTT_BROKER_ADDRESS', 'localhost'), help='MQTT broker address')
parser.add_argument('--port', type=int, default=int(os.getenv('MQTT_PORT', 1883)), help='MQTT broker port')
parser.add_argument('--client-id', default=os.getenv('MQTT_CLIENT_ID', 'mcp-mqtt-client'), help='MQTT client ID')
parser.add_argument('--username', default=os.getenv('MQTT_USERNAME'), help='MQTT username')
parser.add_argument('--password', default=os.getenv('MQTT_PASSWORD'), help='MQTT password')

# Transport Configuration
parser.add_argument('--transport', choices=['stdio', 'streamable-http', 'sse'], default='stdio', 
                   help='Transport type (default: stdio)')
args = parser.parse_args()

# --- MCP Server Setup ---

mcp = FastMCP("MQTT Bridge")

# --- MQTT Client Helper ---

def get_mqtt_client(client_id_suffix: str = "") -> mqtt.Client:
    """Creates and configures an MQTT client based on parsed args."""
    client_id = f"{args.client_id}{client_id_suffix}"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    if args.username:
        client.username_pw_set(args.username, args.password)
    return client

# --- MCP Tools ---

@mcp.tool()
def mqtt_publish(topic: str, message: str, qos: int = 0, retain: bool = False) -> str:
    """
    Publishes a message to a specific MQTT topic.

    Args:
        topic: The MQTT topic to publish to.
        message: The message payload to send.
        qos: The Quality of Service level (0, 1, or 2). Defaults to 0.
        retain: Whether the message should be retained by the broker. Defaults to False.

    Returns:
        A confirmation message string.
    """
    if qos not in [0, 1, 2]:
        return "Error: QoS must be 0, 1, or 2."

    client = get_mqtt_client("-publisher")
    result = None
    error_message = None

    def on_connect(client, userdata, flags, reason_code, properties):
        nonlocal result
        nonlocal error_message
        if reason_code == 0:
            print(f"Publisher connected to {args.broker}:{args.port}")
            publish_info = client.publish(topic, message, qos=qos, retain=retain)
            # For QoS 1 and 2, wait for PUBACK/PUBCOMP. For QoS 0, it returns immediately.
            if qos > 0:
                 # Wait a reasonable amount of time for ACK. In a real app, might use on_publish callback.
                publish_info.wait_for_publish(timeout=5)
                if publish_info.is_published():
                     result = f"Message published to topic \'{topic}\' (QoS {qos}, Retain: {retain})"
                else:
                    error_message = f"Failed to publish message to topic \'{topic}\' (Timeout or Error)"

            else: # QoS 0
                 result = f"Message published to topic \'{topic}\' (QoS 0, Retain: {retain})"

            client.loop_stop() # Stop loop after publishing
            client.disconnect()
        else:
            error_message = f"Failed to connect to broker: {reason_code}"
            client.loop_stop() # Stop loop on connection failure

    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        print(f"Publisher disconnected: {reason_code}")


    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(args.broker, args.port, 60)
        client.loop_start() # Start network loop in background thread

        # Wait for connection and publish attempt
        # The loop will be stopped in on_connect or on_disconnect
        # Give it a bit more time than the publish timeout
        loop_timeout = 10 # seconds
        start_time = time.monotonic()
        while client.is_connected() or (time.monotonic() - start_time < loop_timeout):
             if result is not None or error_message is not None:
                 break
             time.sleep(0.1) # Prevent busy-waiting

        # Ensure loop is stopped if timeout occurred before callback finished
        if client._thread and client._thread.is_alive():
            client.loop_stop()
            client.disconnect() # Attempt disconnect if loop stopped prematurely


    except Exception as e:
        error_message = f"MQTT connection or publish error: {e}"
        if client._thread and client._thread.is_alive():
            client.loop_stop()


    return result if result is not None else error_message or "Publish operation finished with unknown state."

@mcp.tool()
def mqtt_subscribe(topic: str, num_messages: int = 1, timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Subscribes to an MQTT topic and receives a specified number of messages or waits for a timeout.

    Args:
        topic: The MQTT topic to subscribe to (can include wildcards like + or #).
        num_messages: The maximum number of messages to receive. Defaults to 1.
        timeout: The maximum time (in seconds) to wait for messages. Defaults to 10.

    Returns:
        A list of dictionaries, where each dictionary represents a received message
        with 'topic' and 'payload' keys.
    """
    client = get_mqtt_client("-subscriber")
    received_messages: List[Dict[str, Any]] = []
    received_count = 0
    connection_error = None
    stop_event = threading.Event() # Used to signal when to stop the loop

    def on_connect(client, userdata, flags, reason_code, properties):
        nonlocal connection_error
        if reason_code == 0:
            print(f"Subscriber connected to {args.broker}:{args.port}")
            # Subscribe upon successful connection
            client.subscribe(topic)
            print(f"Subscribed to topic: {topic}")
        else:
            connection_error = f"Failed to connect: {reason_code}"
            stop_event.set() # Signal to stop if connection fails

    def on_message(client, userdata, msg):
        nonlocal received_count
        message_data = {
            "topic": msg.topic,
            "payload": msg.payload.decode('utf-8', errors='ignore'), # Decode payload safely
            "qos": msg.qos,
            "retain": msg.retain
        }
        received_messages.append(message_data)
        received_count += 1
        print(f"Received message {received_count}/{num_messages} on topic '{msg.topic}'")
        if received_count >= num_messages:
            stop_event.set() # Signal to stop once desired messages are received

    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        print(f"Subscriber disconnected: {reason_code}")
        # If disconnected unexpectedly, signal stop
        if not stop_event.is_set():
             print("Unexpected disconnection, stopping subscribe operation.")
             stop_event.set()

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(args.broker, args.port, 60)
        client.loop_start()

        # Wait for the stop event to be set (by timeout, message count, or error)
        stop_event.wait(timeout=timeout)

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        connection_error = f"MQTT connection or subscribe error: {e}"
        if client._thread and client._thread.is_alive():
            client.loop_stop()

    if connection_error:
         # We might have received some messages before the error, but indicate failure
         # Alternatively, raise an exception or return an error structure
         print(f"Error during subscription: {connection_error}")
         # Returning what we got, but the caller should check status/logs
         # Or return a specific error object: return {"error": connection_error, "received": received_messages}
         # For simplicity here, just returning the messages collected so far.

    print(f"Subscribe operation finished. Received {len(received_messages)} messages.")
    return received_messages

def main():
    print(f"🚀 Starting MQTT MCP Server...")
    print(f"📡 MQTT Broker: {args.broker}:{args.port}")
    print(f"🚚 Transport: {args.transport}")
    
    if args.transport == 'stdio':
        print("📺 Running in STDIO mode (for local development/Claude Desktop)")
        mcp.run()
        
    elif args.transport == 'streamable-http':
        print("💡 Recommended for web deployments")
        mcp.run(
            transport="streamable-http"
        )
        
    elif args.transport == 'sse':
        print("⚠️  WARNING: SSE transport is deprecated. Consider using streamable-http.")
        mcp.run(
            transport="sse",
        )

# --- Main Execution ---
if __name__ == "__main__":
    main()