# easy-loxone-influx


## What is it good for?

This tutorial shows you how to easily send Loxone statistics to InfluxDB 1.8 timescale database through UDP messages. Once you have your data stored InfluxDB, you can visualize them with Grafana.

## How to connect Loxone to InfluxDB?

In contrast to most other solutions and tutorials, this one does not use websockets for sending statistics from Loxone, but simple UDP (or HTTP) messages. It is very easy to setup and use. The configuration of individual measurements and statistics is done through Loxone Config. 

This tutorial is intended for InfluxDB 1.8. The new version (InfluxDB 2.0) does not have a built-in HTTP and UDP listener and requires Telegraph for parsing data (not tested, feel free to test and let me know....)

There are essentially two solutions. Both of them allow you to set measurement names and tags for your statistics within Loxone Config. Choose for yourself and go to more detailed tutorial below:

### 1. UDP logger

**Pros:**

* Easily attach UDP Logger to most objects in Loxone Config (no need to draw schema). 

**Cons:**

* Needs external Python script.
* Messages sent by Loxone utilize custom syntax.
* Loxone statistics can only be sent by UDP messages (not HTTP).

Here is a quick look at how it works:

<img src="/pics/02.png" alt="02" style="zoom:50%;" />

For detailed instructions, go to a UDP LOGGER -> INFLUXDB TUTORIAL .

### 2. Virtual output

**Pros:**

* Direct connection between Loxone and InfluxDB (no external script or third-party software).
* Messages sent by Loxone comply to standard InfluxDB line protocol (https://docs.influxdata.com/influxdb/v1.8/write_protocols/line_protocol_tutorial/).
* Loxone statistics can be sent either by UDP or HTTP (HTTPS) messages.

**Cons:**

* Requires you to draw a schema in Loxone Config.




