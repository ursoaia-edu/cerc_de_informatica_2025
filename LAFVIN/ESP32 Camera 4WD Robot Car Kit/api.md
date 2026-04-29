# ESP32 Camera 4WD Robot Car - HTTP API

## Connection

The robot creates a WiFi Access Point:
- **SSID:** `ESP32-CAM Robot`
- **Password:** *(open network, no password)*
- **Base URL:** `http://192.168.4.1` (default AP IP)

Two HTTP servers run simultaneously:
| Server | Port | Purpose |
|--------|------|---------|
| Main   | 80   | Web UI, control commands, camera settings |
| Stream | 81   | MJPEG video stream |

---

## Movement Commands

All movement endpoints accept `GET` requests and return `OK` (text/html).

| Endpoint | Action | Description |
|----------|--------|-------------|
| `GET /go` | Forward | Both motors forward (speed=150) |
| `GET /back` | Backward | Both motors backward |
| `GET /left` | Turn left | Left motors backward, right motors forward |
| `GET /right` | Turn right | Left motors forward, right motors backward |
| `GET /stop` | Stop | All motors stop (duty=0) |

### Motor Logic

| Direction | LEFT_M0 (GPIO 13) | LEFT_M1 (GPIO 12) | RIGHT_M0 (GPIO 14) | RIGHT_M1 (GPIO 15) |
|-----------|--------------------|--------------------|---------------------|---------------------|
| Forward   | 0 | speed | 0 | speed |
| Backward  | speed | 0 | speed | 0 |
| Right     | 0 | speed | speed | 0 |
| Left      | speed | 0 | 0 | speed |
| Stop      | 0 | 0 | 0 | 0 |

Default `speed` = **150** (out of 255, 8-bit PWM at 2000 Hz).

---

## LED (Flashlight) Control

| Endpoint | Action |
|----------|--------|
| `GET /ledon` | Turn on flash LED (GPIO 4 HIGH) |
| `GET /ledoff` | Turn off flash LED (GPIO 4 LOW) |

---

## Camera Endpoints

### Capture a Single Frame

```
GET /capture
```
Returns a JPEG image (`image/jpeg`).

### MJPEG Video Stream

```
GET :81/stream
```
Returns a continuous MJPEG stream (`multipart/x-mixed-replace`). Runs on port **81**.

---

## Camera Settings

### Get Current Status

```
GET /status
```
Returns JSON with all current camera sensor settings:

```json
{
  "framesize": 4,
  "quality": 10,
  "brightness": 0,
  "contrast": 0,
  "saturation": 0,
  "special_effect": 0,
  "wb_mode": 0,
  "awb": 1,
  "awb_gain": 1,
  "aec": 1,
  "aec2": 1,
  "ae_level": 0,
  "aec_value": 168,
  "agc": 1,
  "agc_gain": 0,
  "gainceiling": 0,
  "bpc": 0,
  "wpc": 1,
  "raw_gma": 1,
  "lenc": 1,
  "hmirror": 0,
  "dcw": 1,
  "colorbar": 0
}
```

### Change a Camera Setting

```
GET /control?var={variable}&val={value}
```

| Variable | Description | Values |
|----------|-------------|--------|
| `framesize` | Resolution | 0=96x96, 3=QVGA(240x176), 4=CIF(400x296), 5=HVGA(480x320), 6=VGA(640x480), 8=SVGA(800x600), 9=XGA(1024x768), 10=SXGA(1280x1024), 13=UXGA(1600x1200) |
| `quality` | JPEG quality | 10-63 (lower = better quality) |
| `brightness` | Brightness | -2 to 2 |
| `contrast` | Contrast | -2 to 2 |
| `saturation` | Saturation | -2 to 2 |
| `special_effect` | Effect | 0=None, 1=Negative, 2=Grayscale, 3=Red tint, 4=Green tint, 5=Blue tint, 6=Sepia |
| `wb_mode` | White balance mode | 0=Auto, 1=Sunny, 2=Cloudy, 3=Office, 4=Home |
| `awb` | Auto white balance | 0=Off, 1=On |
| `awb_gain` | AWB gain | 0=Off, 1=On |
| `aec` | Auto exposure | 0=Off, 1=On |
| `aec2` | Auto exposure (DSP) | 0=Off, 1=On |
| `ae_level` | Auto exposure level | -2 to 2 |
| `aec_value` | Manual exposure value | 0-1200 |
| `agc` | Auto gain control | 0=Off, 1=On |
| `agc_gain` | Manual gain | 0-30 |
| `gainceiling` | Gain ceiling | 0-6 |
| `bpc` | Black pixel correction | 0=Off, 1=On |
| `wpc` | White pixel correction | 0=Off, 1=On |
| `raw_gma` | Raw gamma | 0=Off, 1=On |
| `lenc` | Lens correction | 0=Off, 1=On |
| `hmirror` | Horizontal mirror | 0=Off, 1=On |
| `vflip` | Vertical flip | 0=Off, 1=On |
| `dcw` | Downsize enable | 0=Off, 1=On |
| `colorbar` | Color bar test | 0=Off, 1=On |

---

## Web UI

```
GET /
```
Serves an HTML control page with:
- Live video stream (from port 81)
- Forward / Left / Stop / Right / Backward buttons (hold to move, release to stop)
- Light ON / Light OFF buttons

---

## Usage Examples

```bash
# Move forward for 2 seconds
curl http://192.168.4.1/go
sleep 2
curl http://192.168.4.1/stop

# Turn on flashlight
curl http://192.168.4.1/ledon

# Take a photo
curl -o photo.jpg http://192.168.4.1/capture

# Set resolution to VGA
curl "http://192.168.4.1/control?var=framesize&val=6"

# Set brightness to max
curl "http://192.168.4.1/control?var=brightness&val=2"

# Get current camera settings
curl http://192.168.4.1/status
```
