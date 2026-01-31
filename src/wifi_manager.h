#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <stdbool.h>

/* Call once at startup. Returns true if connected to saved WiFi, false if AP mode started. */
bool wifi_manager_init(void);

/* Save credentials to NVS and attempt connection. Returns true on success. */
bool wifi_manager_connect(const char *ssid, const char *password);

/* Erase saved credentials and restart into AP mode */
void wifi_manager_reset(void);

/* Check if currently connected to WiFi (STA mode) */
bool wifi_manager_is_connected(void);

#endif
