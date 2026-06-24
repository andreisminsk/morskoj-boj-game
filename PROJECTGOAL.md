Act as an expert Python game developer specializing in retro arcade emulations. Write a complete, single-file, production-ready Python script using the Pygame library to build a 2D retro arcade game inspired by the classic Soviet "Morskoj Boj" (Sea Battle) periscope slot machine. 

### 1. Visual & Audio Style (Retro Aesthetics)
- Resolution: Fixed 800x600 pixels.
- Theme: Submarine periscope view.
- Color Palette: Mostly black background inside the periscope view. Ships should be glowing pixel-art style silhouettes (neon green, cyan, or red). Torpedoes are bright white/cyan dots or short lines.
- Periscope Overlay: Draw a persistent vector-graphic periscope HUD overlay: a large circular viewing window in the center, a horizontal waterline grid crosshair, and a degrees/bearing scale at the top.
- Sound & Graphics Fallback: Do not rely on external asset files (.png, .wav). Generate all graphics programmatically using pygame.draw (rectangles, polygons, circles). For sound effects, use Python's built-in `math` module to generate raw square/sine wave audio buffers and convert them to pygame.mixer.Sound objects for firing, explosions, and misses.

### 2. Core Game Mechanics
- Player Viewport: The player stays stationary at the bottom center. Turning the periscope rotates the camera view left and right. Implement this by keeping the player central and shifting the background horizontal coordinate (world offset) based on Mouse Movement or Left/Right Arrow keys.
- Target Ships: Automatically spawn ships at the top horizon line (just below the waterline). They move horizontally from one side of the screen to the other at varying speeds and depths (scaling sizes slightly for perspective).
- Ammo & Score System: 
  * The player starts with exactly 10 torpedoes.
  * Display a retro counter for "Torpedos Left" and "Score/Hits".
  * If the player scores 10 out of 10 hits, trigger a "Bonus Round" with 10 more torpedoes.
- Torpedo Physics (The Lead/Uprezhdenie Factor):
  * Firing is triggered by Spacebar or Mouse Click.
  * Torpedoes travel vertically from the bottom of the periscope view up toward the horizon.
  * Because ships move horizontally, the player must calculate the "lead time" (aim ahead of the ship) to score a hit.
- Collisions: Simple bounding box or distance-based collision check at the horizon level. A hit triggers an explosion animation (expanding pixelated circles) and removes the ship.

### 3. Code Architecture Requirements
- Single-File Solution: Provide all code within one cleanly formatted script.
- Code Structure: Use clear Object-Oriented Programming (OOP) with separate classes for `Game`, `Periscope`, `Ship`, `Torpedo`, and `Explosion`.
- Clean Execution: Include a standard `if __name__ == '__main__':` block. Ensure the game loop handles 60 FPS capped frame rates, window closing events, and safe pygame.quit() cleanups.
- Documentation: Add brief, meaningful comments explaining the mathematical logic behind the horizontal scrolling world offset and procedural sound generation.

Act as an expert Python game developer specializing in retro arcade emulations. Write a complete, single-file, production-ready Python script using the Pygame library to build a 2D retro arcade game inspired by the classic Soviet "Morskoj Boj" (Sea Battle) periscope slot machine. 

### 1. Visual & Audio Style (Retro Aesthetics)
- Resolution: Fixed 800x600 pixels.
- Theme: Submarine periscope view.
- Color Palette: Mostly black background inside the periscope view. Ships should be glowing pixel-art style silhouettes (neon green, cyan, or red). Torpedoes are bright white/cyan dots or short lines.
- Periscope Overlay: Draw a persistent vector-graphic periscope HUD overlay: a large circular viewing window in the center, a horizontal waterline grid crosshair, and a degrees/bearing scale at the top.
- Sound & Graphics Fallback: Do not rely on external asset files (.png, .wav). Generate all graphics programmatically using pygame.draw (rectangles, polygons, circles). For sound effects, use Python's built-in `math` module to generate raw square/sine wave audio buffers and convert them to pygame.mixer.Sound objects for firing, explosions, and misses.

### 2. Core Game Mechanics
- Player Viewport: The player stays stationary at the bottom center. Turning the periscope rotates the camera view left and right. Implement this by keeping the player central and shifting the background horizontal coordinate (world offset) based on Mouse Movement or Left/Right Arrow keys.
- Target Ships: Automatically spawn ships at the top horizon line (just below the waterline). They move horizontally from one side of the screen to the other at varying speeds and depths (scaling sizes slightly for perspective).
- Ammo & Score System: 
  * The player starts with exactly 10 torpedoes.
  * Display a retro counter for "Torpedos Left" and "Score/Hits".
  * If the player scores 10 out of 10 hits, trigger a "Bonus Round" with 10 more torpedoes.
- Torpedo Physics (The Lead/Uprezhdenie Factor):
  * Firing is triggered by Spacebar or Mouse Click.
  * Torpedoes travel vertically from the bottom of the periscope view up toward the horizon.
  * Because ships move horizontally, the player must calculate the "lead time" (aim ahead of the ship) to score a hit.
- Collisions: Simple bounding box or distance-based collision check at the horizon level. A hit triggers an explosion animation (expanding pixelated circles) and removes the ship.

### 3. Code Architecture Requirements
- Single-File Solution: Provide all code within one cleanly formatted script.
- Code Structure: Use clear Object-Oriented Programming (OOP) with separate classes for `Game`, `Periscope`, `Ship`, `Torpedo`, and `Explosion`.
- Clean Execution: Include a standard `if __name__ == '__main__':` block. Ensure the game loop handles 60 FPS capped frame rates, window closing events, and safe pygame.quit() cleanups.
- Documentation: Add brief, meaningful comments explaining the mathematical logic behind the horizontal scrolling world offset and procedural sound generation.
