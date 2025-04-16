## basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import time
import subprocess
import Quartz
from AppKit import NSWorkspace, NSScreen
from ScriptingBridge import SBApplication
import pyautogui
from pynput.mouse import Button, Controller

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


# Global variables for Preview app automation
preview_app = None

# @mcp.tool()
# async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
#     """Draw a rectangle in Preview from (x1,y1) to (x2,y2)"""
#     global preview_app
#     try:
#         if not preview_app:
#             return {
#                 "content": [
#                     TextContent(
#                         type="text",
#                         text="Preview is not open. Please call open_preview first."
#                     )
#                 ]
#             }
        
#         # Get screen dimensions
#         main_screen = NSScreen.mainScreen()
#         screen_frame = main_screen.frame()
#         screen_height = screen_frame.size.height
        
#         # AppleScript to draw rectangle in Preview
#         # Note: macOS coordinates have origin at bottom-left, so we need to transform y-coordinates
#         y1_transformed = screen_height - y1
#         y2_transformed = screen_height - y2
        
#         script = f'''
#         tell application "Preview"
#             activate
#             delay 0.5
#             tell application "System Events"
#                 tell process "Preview"
#                     # Select rectangle tool
#                     click menu item "Rectangle" of menu "Tools" of menu bar 1
#                     delay 0.2
                    
#                     # Get window position
#                     set frontWindow to front window
#                     set winPos to position of frontWindow
#                     set winSize to size of frontWindow
                    
#                     # Draw rectangle
#                     set startX to {x1}
#                     set startY to {y1_transformed}
#                     set endX to {x2}
#                     set endY to {y2_transformed}
                    
#                     # Adjust for window position
#                     click at {{startX, startY}}
#                     drag from {{startX, startY}} to {{endX, endY}}
#                 end tell
#             end tell
#         end tell
#         '''
        
#         subprocess.run(["osascript", "-e", script])
        
#         return {
#             "content": [
#                 TextContent(
#                     type="text",
#                     text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"
#                 )
#             ]
#         }
#     except Exception as e:
#         return {
#             "content": [
#                 TextContent(
#                     type="text",
#                     text=f"Error drawing rectangle: {str(e)}"
#                 )
#             ]
#         }

@mcp.tool()
async def add_text_in_preview(text: str) -> dict:
    """Add text in Preview"""
    global preview_app
    try:
        if not preview_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Preview is not open. Please call open_preview first."
                    )
                ]
            }
        
        # AppleScript to add text in Preview
        script = f'''
        tell application "Preview"
            activate
            delay 0.5
            tell application "System Events"
                tell process "Preview"
                    # Select text tool
                    click menu item "Text" of menu "Tools" of menu bar 1
                    delay 0.2
                    
                    # Click in the middle of the document
                    set frontWindow to front window
                    set winSize to size of frontWindow
                    set clickX to (item 1 of winSize) / 2
                    set clickY to (item 2 of winSize) / 2
                    
                    click at {{clickX, clickY}}
                    delay 0.2
                    
                    # Type the text
                    keystroke "{text}"
                    
                    # Click elsewhere to finish text entry
                    click at {{clickX + 100, clickY + 100}}
                end tell
            end tell
        end tell
        '''
        
        subprocess.run(["osascript", "-e", script])
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added successfully"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }
    

# Initialize the mouse controller

@mcp.tool()
async def open_powerpoint():
    """
    Open Microsoft PowerPoint application 
    Args:
        None
    Returns:
        dict: A dictionary containing the success message
    """
    subprocess.run(['open', '-a', 'Microsoft PowerPoint'])
    time.sleep(3)  # Wait for PowerPoint to open
    return {
        "content": [
            types.TextContent(
                type="text",
                text="PowerPoint opened successfully"
            )
        ]
    }


@mcp.tool()
async def create_new_presentation():
    """
    Create a new PowerPoint presentation
    Args:
        None
    Returns:
        dict: A dictionary containing the success message
    """
    # Click on "Blank Presentation" if it appears
    mouse = Controller()
    try:
        x0,y0 = 200,180
        pyautogui.moveTo(x0, y0)
        pyautogui.click()
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(0.2)
        pyautogui.click()
        mouse.press(Button.left)
        pyautogui.press("enter")
      
        # blank_presentation = pyautogui.locateOnScreen('blank_presentation.png', confidence=0.8)
        # if blank_presentation:
        #     pyautogui.click(blank_presentation)
        #     time.sleep(1)
        return {
        "content": [
            types.TextContent(
                type="text",
                text="PowerPoint new presentation created successfully"
            )
        ]
    }
    except:
        # If we can't find the blank presentation button, try keyboard shortcut
        pyautogui.hotkey('command', 'n')
        time.sleep(1)


@mcp.tool()
async def draw_rectangle() -> dict:
    """
    Draw a rectangle in powerpoint blank slide, and click on it to write text
    Args:
        None
    Returns:
        dict: A dictionary containing the success message
    """
    try:
        mouse = Controller()
        # Coordinates for the rectangle
        x1, y1 = 90, 72
        x2, y2 = 366, 113
        x3, y3 = 575, 180

        time.sleep(0.5)  # Adjust if you want to ensure Paint is in focus

        # Click on the rectangle tool (adjust based on where the tool is located on the screen)
        # pyautogui.click(x=535, y=90)
        # time.sleep(0.5)

        # Move to the first point (x1, y1) and click to start the rectangle
        pyautogui.moveTo(x1, y1)
        pyautogui.click()
        mouse.press(Button.left)
        time.sleep(0.5)

        # Move to the second point (x2, y2) and release the mouse to draw the rectangle
        pyautogui.moveTo(x2, y2)
        pyautogui.click()
        mouse.press(Button.left)
        time.sleep(0.5)

        # # Optionally, move to the third point (x3, y3) to complete the shape or just adjust size
        pyautogui.moveTo(x3, y3)
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.click()


        pyautogui.moveTo(1000, 300)
        pyautogui.click()
        mouse.press(Button.left)
        time.sleep(0.5)
        pyautogui.moveTo(1000, 500)
        
        # pyautogui.moveTo(1000, 300)
        # pyautogui.moveTo(1000, 500)
        pyautogui.moveTo(650, 300)
        mouse.release(Button.left)

        text_x, text_y = 640 + 200, 300 + 40  # Example: adjust to be inside the rectangle
        pyautogui.moveTo(text_x, text_y)
        time.sleep(0.5)

        # Click to focus on the area and start typing
        pyautogui.click()
        time.sleep(0.5)

        # # Type 'Hello World' inside the rectangle
        # pyautogui.write('Hello World', interval=0.1)


        # Return the success message with the rectangle's coordinates
        time.sleep(2)  # Give time for the drawing action
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"
                )
            ]
        }

    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }



@mcp.tool()
async def write_text(text, x=640, y=300):
    """
    Write text in PowerPoint at the specified position
    Args:
        text: str, the text to write, provide the text from the LLM response
        x: int, the x coordinate of the position to write the text , use the default value
        y: int, the y coordinate of the position to write the text, use the default value
    Returns:
        dict: A dictionary containing the success message
    """
    try:
        x = 850
        y = 340
        # Move to the position and click
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(0.5)
        
        # Type the text
        pyautogui.write(text, interval=0.1)
        time.sleep(1)
        
        return {
            "content": [
                types.TextContent(
                    type="text",
                    text=f"Text '{text}' written at position ({x}, {y})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                types.TextContent(
                    type="text",
                    text=f"Error writing text: {str(e)}"
                )
            ]
        }


@mcp.tool()
async def open_preview() -> dict:
    """Open Preview app and create a new document"""
    global preview_app
    try:
        # Create a new blank image file to open with Preview
        temp_image_path = "/tmp/blank_canvas.png"
        
        # Create a small blank image
        from PIL import Image as PILImage
        blank_image = PILImage.new('RGB', (1000, 800), (255, 255, 255))
        blank_image.save(temp_image_path)
        
        # Open the image with Preview
        script = f'''
        tell application "Preview"
            activate
            open "{temp_image_path}"
            # Position window on secondary display if available
            tell application "System Events"
                tell process "Preview"
                    set frontWindow to front window
                    
                    # Check if there's a second screen
                    set screenCount to count of screens
                    if screenCount > 1 then
                        # Get second screen bounds
                        set screen2 to item 2 of screens
                        set screen2Bounds to bounds of screen2
                        
                        # Move window to second screen
                        set position of frontWindow to {{item 1 of screen2Bounds + 50, item 2 of screen2Bounds + 50}}
                        
                        # Maximize window
                        set size of frontWindow to {{800, 600}}
                    end if
                end tell
            end tell
        end tell
        '''
        
        subprocess.run(["osascript", "-e", script])
        
        # Set global variable
        preview_app = True
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Preview opened successfully with a blank canvas"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Preview: {str(e)}"
                )
            ]
        }

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution