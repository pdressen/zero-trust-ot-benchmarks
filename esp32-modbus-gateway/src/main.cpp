#include <Arduino.h>
#include <WiFi.h>
#include <ModbusTCP.h>
#include "config.h"

IPAddress wifiIp = ipaddr_addr(WIFI_IP);
IPAddress wifiSubnet = ipaddr_addr(WIFI_SUBNET);
IPAddress wifiGateway = ipaddr_addr(WIFI_GATEWAY);

ModbusTCP modbusTcp;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  delay(2000);
  Serial.println();

  WiFi.config(wifiIp, wifiGateway, wifiSubnet);

  while (WL_CONNECTED != WiFi.begin(WIFI_SSID, WIFI_PSK)) {
    Serial.printf("Connecting to WiFi \"%s\", status: %u\n", WIFI_SSID, WiFi.status());
    delay(1000);
  }
  Serial.printf("Connected. IP: \"%s\"...\n", WiFi.localIP().toString());

  Serial.printf("Starting ModbusTCP server...");
  modbusTcp.server(MODBUS_SERVER_PORT);
  if (modbusTcp.addHreg(0, 0, MODBUS_NUM_HREGS))
    Serial.println("Added Hregs");
  else
    Serial.println("Couldn't add Hregs");
}

void loop() {
  // put your main code here, to run repeatedly:
  //Serial.printf("Test %lu\n", millis());
  modbusTcp.task();
  yield();
}
