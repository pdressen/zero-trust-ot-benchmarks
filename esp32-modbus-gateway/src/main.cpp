#include <Arduino.h>
#include <WiFi.h>
#include <ModbusTCP.h>
#include <WireGuard-ESP32.h>
#include "config.h"

// enable logging each request to serial
//#define REQUEST_LOGGING

IPAddress wifiIp = ipaddr_addr(WIFI_IP);
IPAddress wifiSubnet = ipaddr_addr(WIFI_SUBNET);
IPAddress wifiGateway = ipaddr_addr(WIFI_GATEWAY);

WireGuard wireguard;

ModbusTCP modbusTcp;


#ifdef REQUEST_LOGGING
Modbus::ResultCode modbusRequest(Modbus::FunctionCode fc, const Modbus::RequestData rd) {
  Serial.printf("Modbus request FC: 0x%02x ADDR: %d CNT: %d\n", fc, rd.regMask.address, rd.regCount & rd.andMask);  
  return Modbus::ResultCode::EX_PASSTHROUGH;
}
#endif

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  delay(2000);
  Serial.println();

  WiFi.config(wifiIp, wifiGateway, wifiSubnet);
  WiFi.setAutoReconnect(true);

  while (WL_CONNECTED != WiFi.begin(WIFI_SSID, WIFI_PSK)) {
    Serial.printf("Connecting to WiFi \"%s\", status: %u\n", WIFI_SSID, WiFi.status());
    delay(1000);
  }
  Serial.printf("Connected. IP: \"%s\"...\n", WiFi.localIP().toString());

  Serial.printf("Connecting to WireGuard peer %s:%d with IP %s\n", WG_PEER_IP, WG_PEER_PORT, WG_IP);
  if (wireguard.begin(IPAddress(ipaddr_addr(WG_IP)) , WG_PRIV_KEY, WG_PEER_IP, WG_PEER_PUB_KEY, WG_PEER_PORT))
    Serial.println("Connection successfull");
  else
    Serial.printf("Could not connect");

  Serial.println("Starting ModbusTCP server...");

#ifdef REQUEST_LOGGING
  modbusTcp.onRequestSuccess(modbusRequest);
#endif

  modbusTcp.server(MODBUS_SERVER_PORT);

  if (modbusTcp.addCoil(0, false, MODBUS_NUM_REGS)
      && modbusTcp.addIsts(0, false, MODBUS_NUM_REGS)
      && modbusTcp.addIreg(0, 0, MODBUS_NUM_REGS)
      && modbusTcp.addHreg(0, 0, MODBUS_NUM_REGS)) {
        for (int i = 0; i < MODBUS_NUM_REGS; ++i) {
          modbusTcp.Coil(i, rand() % 2 == 0);
          modbusTcp.Ists(i, rand() % UINT16_MAX);
          modbusTcp.Ireg(i, rand() % UINT16_MAX);
          modbusTcp.Hreg(i, rand() % UINT16_MAX);
        }
      Serial.printf("Added %u registers of each kind\n", MODBUS_NUM_REGS);
  } else {
    Serial.println("Couldn't add registers");
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  //Serial.printf("Test %lu\n", millis());
  modbusTcp.task();
  modbusTcp.Ireg(0, millis() % UINT16_MAX);
  yield();
}
