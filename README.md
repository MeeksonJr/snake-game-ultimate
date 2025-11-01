# Snake Game ?? - Ultimate Edition

A beautiful, feature-rich Snake game built with Python and Pygame, complete with background music, power-ups, mini-games, high score tracking, modern UI, and Docker support!

## ? Features

### Core Gameplay
- ?? Classic Snake gameplay with smooth controls
- ?? **Background Music** - Looping background music during gameplay
- ?? **High Score System** - Persistent score tracking (saves top 10 scores)
- ?? **Latest Score Display** - Shows your most recent score
- ?? **New High Score Detection** - Highlights when you beat your record

### Visual Enhancements
- ?? **Modern UI Design** - Animated gradient backgrounds, rounded corners, smooth animations
- ? **Particle Effects** - Visual feedback when eating food and collecting items
- ?? **Enhanced Graphics** - Snake with eyes, glowing effects, animated backgrounds
- ?? **Sidebar** - Real-time score, speed, power-ups, and controls display

### Game Mechanics
- ?? **Progressive Speed** - Game speeds up as you score more points
- ? **Special Food** - Golden food gives bonus points (25 instead of 10)
- ?? **Coins** - Collect coins to trigger mini-games!

### Power-Up System
- ?? **Time Slow** (Press 1) - Slow down time for easier navigation
- ?? **Zoom** (Press 2) - Zoom in to see better
- ? **Speed Boost** (Press 3) - Temporarily increase speed
- ??? **Shield** (Press 4) - Protect against one collision

### Mini-Games
- ?? **Speed Challenge** - Collect coins to trigger mini-games with bonus scoring!

## ?? Controls

- **Arrow Keys**: Move the snake (Up, Down, Left, Right)
- **SPACE**: Start game (from menu) or return to menu (from game over)
- **R**: Reset the game (during gameplay)
- **1-4**: Activate collected power-ups (Time Slow, Zoom, Speed, Shield)
- **ESC**: Quit game or return to menu

## ?? Requirements

- Python 3.11+
- pygame 2.5.2

## ?? Installation & Running

### Option 1: Run Locally (Recommended)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the game:
```bash
python snake_game.py
```

**Note**: Make sure `Dreamin'.mp3` is in the same directory as `snake_game.py` for background music.

### Option 2: Run with Docker

1. Build the Docker image:
```bash
docker build -t snake-game .
```

**Note**: If you get an error about `Dreamin'.mp3` not found during build, you can comment out the COPY line for the music file in the Dockerfile. The game will work without music.

2. Run the container (requires X11 forwarding for GUI):
```bash
# For WSL/Linux with X11
xhost +local:docker
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  snake-game
```

**Note**: 
- Audio may not work in Docker containers. The game will run without music if audio is unavailable.
- For WSL2 with Windows, you may need to:
  - Install an X server (like VcXsrv or X410)
  - Set `DISPLAY=localhost:0.0` or configure X11 forwarding

### Option 3: Docker Compose (Easiest)

```bash
docker-compose up --build
```

## ?? How to Play

1. **Start Screen**: Press SPACE to begin
2. **Gameplay**: Use arrow keys to control the snake
3. **Eat Food**: 
   - Red food = 10 points
   - Golden food = 25 points (special bonus!)
4. **Collect Coins**: Purple coins ($) trigger mini-games!
5. **Collect Power-Ups**: Pick up glowing power-ups and press 1-4 to activate
6. **Avoid**: Walls and your own tail
7. **Speed**: Game gets faster as your score increases
8. **High Scores**: Your scores are automatically saved

## ?? Scoring System

- **Regular Food**: 10 points each
- **Special Food** (Golden): 25 points each
- **Mini-Game Bonus**: Double points during mini-games!
- **Mini-Game Completion**: +50 bonus points
- **Speed Bonus**: Game speed increases every 50 points
- **High Scores**: Top 10 scores are saved to `high_scores.json`
- **Latest Score**: Your most recent score is displayed on the menu
- **New Record**: When you beat your high score, it's highlighted!

## ?? Power-Up System

### Collecting Power-Ups
- Power-ups spawn randomly on the field
- Collect them by moving your snake over them
- Collected power-ups appear in the sidebar

### Activating Power-Ups
- **1**: Time Slow - Slows down game speed (5 seconds)
- **2**: Zoom - Zooms in for better visibility (5 seconds)
- **3**: Speed Boost - Increases movement speed (5 seconds)
- **4**: Shield - Protects against one collision (5 seconds)

### Power-Up Colors
- ?? Orange: Time Slow
- ?? Purple: Zoom
- ?? Green: Speed Boost
- ?? Blue: Shield

## ?? Mini-Games

- **Trigger**: Collect purple coins ($) scattered around the field
- **Duration**: ~3 seconds
- **Reward**: Double points for all food collected during mini-game + 50 bonus points
- **Goal**: Collect as much food as possible during the mini-game!

## ?? UI Features

- **Animated Backgrounds**: Dynamic gradient backgrounds that shift over time
- **Rounded Corners**: Smooth, polished visuals on all elements
- **Sidebar**: Real-time game stats, power-up status, and controls
- **Particle Effects**: Visual feedback when eating food and collecting items
- **Animations**: Smooth transitions, pulsing effects, and glowing elements
- **Color Coding**: Different colors for different game elements
- **Snake Eyes**: Snake head shows eyes facing movement direction
- **Shield Effect**: Visual shield circle when shield power-up is active

## ?? Files

- `snake_game.py` - Main game file
- `Dreamin'.mp3` - Background music file
- `high_scores.json` - Saved high scores (auto-generated)
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Docker Compose setup
- `.gitignore` - Git ignore file

## ?? Troubleshooting

### Music Not Playing
- Ensure `Dreamin'.mp3` is in the same directory as `snake_game.py`
- Check that pygame.mixer is properly initialized
- Game will run without music if file is missing

### Docker Audio Issues
- Audio devices are not available in Docker containers by default
- The game will automatically detect this and run without music
- You'll see a warning message: "Warning: Audio not available. Game will run without music."
- This is normal and the game will function perfectly without audio
- **The error you saw is now fixed** - the game handles missing audio gracefully

### Docker GUI Issues
If pygame doesn't display in Docker, run locally:
```bash
pip install -r requirements.txt
python snake_game.py
```

### WSL2 Display Issues
Set DISPLAY variable:
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```

### High Scores Not Saving
Make sure the game has write permissions in the directory. Scores are saved to `high_scores.json` in the same directory as the game.

## ?? Game Tips

- **Special Food**: Look for golden food - it's worth more points!
- **Coins**: Collect purple coins to trigger mini-games for bonus points
- **Power-Ups**: Save power-ups for difficult situations
- **Shield**: Use shield when you're about to hit a wall or yourself
- **Time Slow**: Perfect for navigating tight spaces
- **Mini-Games**: Try to collect as much food as possible during mini-games
- **Speed Management**: As the game speeds up, plan your moves ahead
- **Pattern Recognition**: Learn to predict where food will spawn
- **Corner Strategy**: Be careful in corners - they're collision hotspots

## ?? Music

The game includes background music (`Dreamin'.mp3`) that loops during gameplay. The music adds atmosphere and enhances the gaming experience!

Enjoy the game! ?????
