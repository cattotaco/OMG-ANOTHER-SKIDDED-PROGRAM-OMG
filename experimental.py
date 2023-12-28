import asyncio
import aiohttp
from bs4 import BeautifulSoup
from PIL import Image
import os
import io
import numpy as np
from colorama import Fore, Style, init

init(autoreset=True)

image_counter = 1
counter_lock = asyncio.Lock()  # Create a lock to synchronize access to image_counter

# Function to create a directory if it doesn't exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

image_counter = 1  # Global variable to keep track of image count

async def download_single_image(session, image_url, filename, white_images_directory):
    try:
        async with session.get(image_url) as response:
            if response.status == 200:
                image_data = await response.read()

                with open(filename, 'wb') as f:
                    f.write(image_data)

                async with counter_lock:
                    global image_counter
                    current_counter = image_counter
                    image_counter += 1

                if is_mostly_white(image_data):
                    new_filename = f"{white_images_directory}/image_{current_counter}.png"
                    os.rename(filename, new_filename)
                    print(f"grabbed: {Fore.GREEN}{filename} {Fore.YELLOW}(moved to white_images)")
                else:
                    print(f"grabbed: {Fore.GREEN}{filename}")

    except Exception as e:
        print(f"failed to grab {filename}: {Fore.RED}{e}")

def is_mostly_white(image_data, threshold=0.7):
    # Load the image using Pillow
    img = Image.open(io.BytesIO(image_data))
    
    # Convert the image to grayscale
    img = img.convert('L')

    # Convert the image to a NumPy array
    img_array = np.array(img)

    # Calculate the average pixel value (0 for black, 255 for white)
    average_pixel_value = np.mean(img_array) / 255.0

    # Check if the average pixel value is above the threshold
    return average_pixel_value > threshold

async def download_images(url, directory, white_images_directory):
    global image_counter  # Access the global image_counter variable

    async with aiohttp.ClientSession() as session:
        page = await session.get(url)
        soup = BeautifulSoup(await page.text(), 'html.parser')
        image_tags = soup.find_all('img')

        create_directory(directory)
        create_directory(white_images_directory)

        tasks = []
        for image in image_tags:
            image_url = image['src']
            filename = f"{directory}/image_{image_counter}.png"  # Incremental file naming

            task = download_single_image(session, image_url, filename, white_images_directory)
            tasks.append(task)

            image_counter += 1  # Increment the counter for the next image

        await asyncio.gather(*tasks)

def main_menu():
    print(
        f"{Fore.CYAN}"
        """   
                                                              $$$$$$\           
                                                            $$  __$$\          
$$$$$$$$\  $$$$$$\  $$$$$$$\   $$$$$$\   $$$$$$$\  $$$$$$\  $$ /  \__|$$$$$$\  
\____$$  |$$  __$$\ $$  __$$\ $$  __$$\ $$  _____| \____$$\ $$$$\    $$  __$$\ 
  $$$$ _/ $$ /  $$ |$$ |  $$ |$$$$$$$$ |\$$$$$$\   $$$$$$$ |$$  _|   $$$$$$$$ |
 $$  _/   $$ |  $$ |$$ |  $$ |$$   ____| \____$$\ $$  __$$ |$$ |     $$   ____|
$$$$$$$$\ \$$$$$$  |$$ |  $$ |\$$$$$$$\ $$$$$$$  |\$$$$$$$ |$$ |     \$$$$$$$\ 
\________| \______/ \__|  \__| \_______|\_______/  \_______|\__|      \_______|
                                                                               
                                                                               
                                                                               
          $$\       $$\       $$\       $$\                 $$\                
          $$ |      \__|      $$ |      $$ |                $$ |               
 $$$$$$$\ $$ |  $$\ $$\  $$$$$$$ | $$$$$$$ | $$$$$$\   $$$$$$$ |               
$$  _____|$$ | $$  |$$ |$$  __$$ |$$  __$$ |$$  __$$\ $$  __$$ |               
\$$$$$$\  $$$$$$  / $$ |$$ /  $$ |$$ /  $$ |$$$$$$$$ |$$ /  $$ |               
 \____$$\ $$  _$$<  $$ |$$ |  $$ |$$ |  $$ |$$   ____|$$ |  $$ |               
$$$$$$$  |$$ | \$$\ $$ |\$$$$$$$ |\$$$$$$$ |\$$$$$$$\ \$$$$$$$ |               
\_______/ \__|  \__|\__| \_______| \_______| \_______| \_______|               
                                                                               
                                                                               
                                                                               
                                                                     $$\       
                                                                     $$ |      
 $$$$$$$\  $$$$$$$\  $$$$$$\  $$$$$$\   $$$$$$\   $$$$$$\   $$$$$$\  $$ |      
$$  _____|$$  _____|$$  __$$\ \____$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$ |      
\$$$$$$\  $$ /      $$ |  \__|$$$$$$$ |$$ /  $$ |$$$$$$$$ |$$ |  \__|\__|      
 \____$$\ $$ |      $$ |     $$  __$$ |$$ |  $$ |$$   ____|$$ |                
$$$$$$$  |\$$$$$$$\ $$ |     \$$$$$$$ |$$$$$$$  |\$$$$$$$\ $$ |      $$\       
\_______/  \_______|\__|      \_______|$$  ____/  \_______|\__|      \__|      
                                       $$ |                                    
                                       $$ |                                    
                                       \__|                                    
        """
    )

    start = input(f"{Fore.YELLOW}Start? (Y/N): ").lower()
    if start == 'y':
        return True
    elif start == 'n':
        return False
    else:
        print(f"{Fore.RED}Invalid input. Please type 'Y' for Yes or 'N' for No.")
        return False

if __name__ == "__main__":
    website_url = "https://randomavatar.com"
    output_directory = "Avatars"

    iterations = 30000000000000000000  # Number of iterations to scrape

    white_images_directory = "white_images"
    
    if main_menu():
        for _ in range(iterations):
            asyncio.run(download_images(website_url, output_directory, white_images_directory))
            print(f"Iteration Complete. {Fore.MAGENTA}Waiting for the next wave of images...")
        print(f"{Fore.LIGHTBLUE_EX}All iterations completed.")
    else:
        print(f"{Fore.RED}Exiting the script.")