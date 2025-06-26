import cv2
import numpy as np
from PIL import Image, ImageDraw
import math

class CompassImage:
    """A wrapper class to make PIL Image work with the compass setup function"""
    def __init__(self, width=16, height=16):
        self.image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        self.pixels = list(self.image.getdata())
        self.width = width
        self.height = height
    
    def __iter__(self):
        return iter(self.pixels)
    
    def set_pixeli(self, index, color):
        """Set pixel by index"""
        if isinstance(color, tuple) and len(color) >= 3:
            self.pixels[index] = color
        else:
            # Convert hex color to RGBA
            if isinstance(color, str) and color.startswith('#'):
                hex_color = color[1:]
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                self.pixels[index] = (r, g, b, 255)
    
    def set_pixel(self, x, y, color):
        """Set pixel by x, y coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            index = y * self.width + x
            self.set_pixeli(index, color)
    
    def get_pil_image(self):
        """Convert back to PIL Image"""
        new_image = Image.new('RGBA', (self.width, self.height))
        new_image.putdata(self.pixels)
        return new_image

def setup_compass_sprite(item: CompassImage, angle: float, output: CompassImage):
    NX = 8.5
    NY = 7.5
    SCALE_X = 0.3
    SCALE_Y = SCALE_X * 0.5
    
    # copy the item's texture into the output
    for i, pix in enumerate(item):
        output.set_pixeli(i, pix)
    
    rx = math.sin(-angle-135)
    ry = math.cos(-angle-135)
    
    # draw the smaller horizontal spurs of the needle
    # 1 is added to the endpoint, as `range` here is
    # end-exclusive. The original loops did `i <= 4`
    for i in range(-4, 4 + 1):
        x = int(NX + ry * i * SCALE_X)
        y = int(NY - rx * i * SCALE_Y)
        output.set_pixel(x, y, '#646464')
    
    # draw the main part needle
    for i in range(-8, 16 + 1):
        x = int(NX + rx * i * SCALE_X)
        y = int(NY + ry * i * SCALE_Y)
        if i >= 0:
            # Main red pointer
            output.set_pixel(x, y, '#FF1414')
        else:
            # Grey back half
            output.set_pixel(x, y, '#646464')

class CompassApp:
    def __init__(self):
        self.compass_angle = 0.0
        self.window_size = 600
        self.compass_center = (self.window_size // 2, self.window_size // 2)
        self.compass_radius = 250
        
        # Load or create base compass texture
        try:
            self.base_compass = Image.open('compass.png').convert('RGBA')
            self.base_compass = self.base_compass.resize((16, 16), Image.NEAREST)
        except FileNotFoundError:
            # Create a simple base compass texture if file doesn't exist
            self.base_compass = self.create_base_compass()
        
        # Convert to CompassImage format
        self.base_compass_data = CompassImage(16, 16)
        pixels = list(self.base_compass.getdata())
        for i, pixel in enumerate(pixels):
            self.base_compass_data.set_pixeli(i, pixel)
    
    def create_base_compass(self):
        """Create a simple base compass texture"""
        img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))  # Brown background
        # draw = ImageDraw.Draw(img)
        # # Draw a simple border
        # draw.rectangle([0, 0, 15, 15], outline=(101, 67, 33, 255), width=1)
        return img
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks to set compass heading"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Calculate angle from center to mouse position
            dx = x - self.compass_center[0]
            dy = y - self.compass_center[1]
            
            # Calculate angle (atan2 returns angle in radians)
            # Adjust to match compass orientation (0 = North, clockwise positive)
            self.compass_angle = math.atan2(dx, -dy)
            
            print(f"Compass heading set to: {math.degrees(self.compass_angle):.1f}°")
    
    def draw_compass_display(self):
        """Draw the compass display with current heading"""
        # Create output image
        display = np.zeros((self.window_size, self.window_size, 3), dtype=np.uint8)
        display.fill(50)  # Dark gray background
        
        # Draw compass circle
        cv2.circle(display, self.compass_center, self.compass_radius, (100, 100, 100), 2)
        
        # Draw cardinal directions
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 2
        
        # North
        cv2.putText(display, 'N', 
                   (self.compass_center[0] - 15, self.compass_center[1] - self.compass_radius - 20),
                   font, font_scale, (255, 255, 255), thickness)
        # East
        cv2.putText(display, 'E', 
                   (self.compass_center[0] + self.compass_radius + 10, self.compass_center[1] + 10),
                   font, font_scale, (255, 255, 255), thickness)
        # South
        cv2.putText(display, 'S', 
                   (self.compass_center[0] - 15, self.compass_center[1] + self.compass_radius + 40),
                   font, font_scale, (255, 255, 255), thickness)
        # West
        cv2.putText(display, 'W', 
                   (self.compass_center[0] - self.compass_radius - 30, self.compass_center[1] + 10),
                   font, font_scale, (255, 255, 255), thickness)
        
        # Generate compass sprite with current angle
        output_compass = CompassImage(16, 16)
        setup_compass_sprite(self.base_compass_data, self.compass_angle, output_compass)
        
        # Convert to PIL and then to OpenCV for display
        pil_compass = output_compass.get_pil_image()
        # Scale up the compass for better visibility
        pil_compass = pil_compass.resize((128, 128), Image.NEAREST)
        
        # Convert PIL to OpenCV format
        compass_array = np.array(pil_compass)
        if compass_array.shape[2] == 4:  # RGBA
            # Convert RGBA to BGR for OpenCV
            compass_bgr = cv2.cvtColor(compass_array, cv2.COLOR_RGBA2BGR)
        else:
            compass_bgr = cv2.cvtColor(compass_array, cv2.COLOR_RGB2BGR)
        
        # Place compass in center of display
        compass_size = 128
        start_x = self.compass_center[0] - compass_size // 2
        start_y = self.compass_center[1] - compass_size // 2
        
        # Ensure we don't go out of bounds
        end_x = min(start_x + compass_size, self.window_size)
        end_y = min(start_y + compass_size, self.window_size)
        
        display[start_y:end_y, start_x:end_x] = compass_bgr[:end_y-start_y, :end_x-start_x]
        
        # Draw angle text
        angle_degrees = math.degrees(self.compass_angle)
        if angle_degrees < 0:
            angle_degrees += 360
        
        angle_text = f"Heading: {angle_degrees:.1f}°"
        cv2.putText(display, angle_text, (20, 40), font, 0.8, (255, 255, 255), 2)
        
        # Instructions
        cv2.putText(display, "Click anywhere to set compass heading", 
                   (20, self.window_size - 20), font, 0.6, (200, 200, 200), 1)
        
        return display
    
    def run(self):
        """Main application loop"""
        cv2.namedWindow('Compass Generator')
        cv2.setMouseCallback('Compass Generator', self.mouse_callback)
        
        print("Compass Generator Started!")
        print("Click anywhere in the window to set the compass heading.")
        print("Press 'q' to quit, 's' to save current compass sprite.")
        
        while True:
            display = self.draw_compass_display()
            cv2.imshow('Compass Generator', display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current compass sprite
                output_compass = CompassImage(16, 16)
                for i in [x / 100.0 for x in range(-314, 315)]:
                    setup_compass_sprite(output_compass, i, output_compass)
                pil_compass = output_compass.get_pil_image()
                
                # Save both original size and upscaled version
                pil_compass.save('generated_compass.png')
                pil_compass.resize((128, 128), Image.NEAREST).save('generated_compass_large.png')
                print(f"Saved compass sprite with heading {math.degrees(self.compass_angle):.1f}°")
        
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = CompassApp()
    app.run()