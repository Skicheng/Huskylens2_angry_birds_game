# 🐦 Gesture-Controlled Angry Birds using HUSKYLENS 2 + Arduino UNO + Python

## 🎮 Overview
This project demonstrates an **interactive Angry Birds-style game** that is fully **controlled through hand gestures** using the **HUSKYLENS 2 AI Vision Sensor**.  
By tracking hand movement in real time, the system converts gestures into control parameters — allowing you to **aim, pull, and launch the bird** with natural hand motion.  


---

## 🧩 Project Structure

| File | Description |
|------|--------------|
| **`angry_birds_game.py`** | Main Python game logic using Pygame. Handles graphics, physics, trajectory prediction, and gesture input visualization. |
| **`main_uno.py`** | Python serial bridge. Receives gesture data from Arduino UNO and transmits it to the main game. |
| **`Huskylens2_angry_birds_game.ino`** | Arduino sketch for HUSKYLENS 2. Detects hand position, computes power & angle, and sends results to the PC over UART. |

---

## ⚙️ Hardware Requirements

- **HUSKYLENS 2 AI Vision Sensor**  
- **DFRduino UNO R3** (Arduino UNO-compatible board)  
- **USB Type-A to Type-B cable**  
- (Optional) **HUSKYLENS 2 Universal Mount** – for attaching the camera to a monitor or fixed structure (supports 5–24 mm thickness)

---

## 💻 Software Requirements

- **Python 3.8+**
- **Arduino IDE** (latest version)

Install Python dependencies:
```bash
pip install pygame pyserial

### Arduino Libraries
- DFRobot_HuskylensV2 (install via Arduino IDE Library Manager)

## 🚀 Quick Start

### 1. Hardware Setup

1. Connect HuskyLens to Arduino Uno-compatible board:

2. Upload the Arduino sketch:
   ```bash
   # Open Huskylens2_angry_birds_game.ino in Arduino IDE
   # Install DFRobot_HuskylensV2 library
   # Upload to Arduino Uno
   ```

### 2. HuskyLens Training

1. Power on HuskyLens
2. Navigate to **Hand Recognition** algorithm
3. Train two gestures:
   - **Fist** (ID: 1) - for aiming/drawing
   - **Open Palm** (ID: 2) - for releasing/firing

### 3. Run the Game

```bash
# Clone the repository
git clone <your-repo-url>
cd Huskylens2_angry_birds_game

# Install dependencies
pip install pygame pyserial

# Run the game
python main_uno.py
```

## 🎯 How to Play

1. **Aiming**: Make a fist gesture and move your hand to aim
2. **Power Control**: Move your fist further right for more power
3. **Launching**: Open your palm to release the bird
4. **Objective**: Destroy all pigs to advance to the next level

## 📁 Project Structure

```
Huskylens2_angry_birds_game/
├── angry_birds_game.py      # Main game engine
├── main_uno.py             # Serial communication & gesture processing
├── Huskylens2_angry_birds_game.ino  # Arduino sketch
├── background.png          # Game background image
├── bird.png               # Bird sprite
├── pig.png                # Pig sprite
├── Scoring_Zone.png             # Score panel background
└── README.md              # This file
```

## 🔧 Configuration

### Game Parameters (main_uno.py)
```python
FRAME_W = 320              # HuskyLens frame width
FRAME_H = 240              # HuskyLens frame height
MAX_ANGLE_H_DEG = 45       # Max horizontal aiming angle
MAX_ANGLE_V_DEG = 45       # Max vertical aiming angle
MIN_LAUNCH_POWER = 0       # Minimum launch power
SMOOTH_ALPHA = 0.35        # Gesture smoothing factor
```

### Arduino Settings
```cpp
#define ID_FIST     1       // Fist gesture ID
#define ID_PALM     2       // Open palm gesture ID
```

## 🎨 Game Features

### Physics Engine
- Realistic projectile motion with gravity
- Collision detection between birds, blocks, and pigs
- Destructible blocks with different materials (wood, stone, ice)
- Particle effects for explosions and impacts

### Visual Effects
- Dynamic background with animated clouds
- Trail effects for flying birds
- Particle systems for explosions
- Health bars for damaged objects
- Trajectory prediction while aiming

### Level Design
- Progressive difficulty across levels
- Multiple block types with different properties
- Strategic pig placement
- Random level generation for higher levels

## 🔍 Troubleshooting

### Common Issues

**Game doesn't start:**
- Check if Arduino is connected and HuskyLens is powered
- Verify COM port in main_uno.py
- Ensure all Python dependencies are installed

**Gestures not recognized:**
- Retrain gestures on HuskyLens
- Ensure good lighting conditions
- Check gesture IDs match Arduino sketch


### Serial Communication Issues
```python
# Check available COM ports
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.