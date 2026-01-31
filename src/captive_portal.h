#ifndef CAPTIVE_PORTAL_H
#define CAPTIVE_PORTAL_H

/* Start captive portal (HTTP server + DNS redirect).
   Call this after wifi_manager_init() returns false (AP mode). */
void captive_portal_start(void);

/* Stop captive portal (call after successful WiFi connection) */
void captive_portal_stop(void);

#endif
