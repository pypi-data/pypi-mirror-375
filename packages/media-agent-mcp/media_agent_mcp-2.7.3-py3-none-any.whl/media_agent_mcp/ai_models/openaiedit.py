import os
from typing import Dict, Any, List
import openai
import requests
import tempfile
import os
import base64
from urllib.parse import urlparse
from media_agent_mcp.storage.tos_client import upload_to_tos
from google import genai
from PIL import Image
from io import BytesIO


def openaiedit(image_urls: List[str], prompt: str, size: str = "1024x1024") -> Dict[str, Any]:
    """
    Perform image editing using the OpenAI Images API.

    :param image_urls: List of URLs of the input images (1 to 4 images).
    :param prompt: The editing prompt.
    :param size: The size of the generated images. Must be one of "256x256", "512x512", or "1024x1024".
    :return: JSON response with status, data (image URL), and message.
    """
    try:
        client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )

        # Validate and limit number of images
        if not image_urls or not isinstance(image_urls, list):
            return {
                "status": "error",
                "data": None,
                "message": "image_urls must be a non-empty list of URLs"
            }
        if len(image_urls) > 4:
            return {
                "status": "error",
                "data": None,
                "message": "A maximum of 4 images are supported"
            }

        # Download images and save to temporary files
        temp_files: List[str] = []
        for image_url in image_urls:
            response = requests.get(image_url)
            response.raise_for_status()

            parsed_url = urlparse(image_url)
            file_ext = os.path.splitext(parsed_url.path)[1]
            if not file_ext:
                content_type = response.headers.get('content-type')
                if content_type and 'image' in content_type:
                    file_ext = '.' + content_type.split('/')[1]
                else:
                    file_ext = '.png'  # default

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            tmp.write(response.content)
            tmp.close()
            temp_files.append(tmp.name)

        # Call OpenAI API with the local files
        files = []
        try:
            for p in temp_files:
                files.append(open(p, "rb"))

            response = client.images.edit(
                model="gpt-image-1",
                image=files,
                prompt=prompt,
                n=1,
                size=size
            )
        finally:
            for f in files:
                try:
                    f.close()
                except Exception:
                    pass
            # Clean up the temporary input files
            for p in temp_files:
                try:
                    os.unlink(p)
                except Exception:
                    pass

        # Prefer URL if provided, otherwise use b64_json
        result_data = response.data[0]
        generated_tos_url: str
        if getattr(result_data, "url", None):
            image_url = result_data.url

            # Download the edited image
            edited_image_response = requests.get(image_url)
            edited_image_response.raise_for_status()

            # Save the edited image to a temporary file
            parsed_url = urlparse(image_url)
            file_ext = os.path.splitext(parsed_url.path)[1] or '.png'

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_edited_file:
                temp_edited_file.write(edited_image_response.content)
                temp_edited_file_path = temp_edited_file.name

            try:
                # Upload the edited image to TOS
                generated_tos_url = upload_to_tos(temp_edited_file_path)
            finally:
                os.unlink(temp_edited_file_path)  # Clean up the temporary file
        else:
            # Fallback to b64_json
            b64 = getattr(result_data, "b64_json", None)
            if not b64:
                return {
                    "status": "error",
                    "data": None,
                    "message": "OpenAI response does not contain url or b64_json"
                }
            image_bytes = base64.b64decode(b64)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_edited_file:
                temp_edited_file.write(image_bytes)
                temp_edited_file_path = temp_edited_file.name
            try:
                generated_tos_url = upload_to_tos(temp_edited_file_path)
            finally:
                os.unlink(temp_edited_file_path)

        return {
            "status": "success",
            "data": {"image_url": generated_tos_url},
            "message": "Image edited and uploaded to TOS successfully."
        }
    except openai.APIError as e:
        return {
            "status": "error",
            "data": None,
            "message": f"OpenAI API Error: {e}"
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error downloading image: {e}"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"An unexpected error occurred: {e}"
        }

def google_edit(image_urls: List[str], prompt: str) -> Dict[str, Any]:
    """
    Perform image editing using the Google Gemini API.

    :param image_urls: List of URLs of the input images.
    :param prompt: The editing prompt.
    :return: JSON response with status, data (image URL), and message.
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "data": None,
                "message": "GOOGLE_API_KEY environment variable is not set."
            }

        if not image_urls or not isinstance(image_urls, list):
            return {
                "status": "error",
                "data": None,
                "message": "image_urls must be a non-empty list of URLs"
            }

        pil_images = []
        for image_url in image_urls:
            response = requests.get(image_url)
            response.raise_for_status()
            pil_images.append(Image.open(BytesIO(response.content)))

        contents = pil_images + [prompt]
        
        client = genai.Client(
            api_key=api_key,
        )

        # 最多尝试3次
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image-preview",
                    contents=contents
                )

                image_data = None
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    image_parts = [
                        part.inline_data.data
                        for part in response.candidates[0].content.parts
                        if part.inline_data
                    ]
                    if image_parts:
                        image_data = image_parts[0]

                # 如果获取到了图片数据，跳出重试循环
                if image_data:
                    break
                    
                # 如果是最后一次尝试且仍然没有图片数据，返回错误
                if attempt == max_retries - 1:
                    return {
                        "status": "error",
                        "data": None,
                        "message": f"Google API response did not contain image data after {max_retries} attempts."
                    }
                    
            except Exception as api_error:
                # 如果是最后一次尝试，抛出异常
                if attempt == max_retries - 1:
                    raise api_error
                # 否则继续下一次尝试
                continue

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_edited_file:
            temp_edited_file.write(image_data)
            temp_edited_file_path = temp_edited_file.name
        
        try:
            generated_tos_url = upload_to_tos(temp_edited_file_path)
        finally:
            os.unlink(temp_edited_file_path)

        return {
            "status": "success",
            "data": {"image_url": generated_tos_url},
            "message": "Image edited with Google and uploaded to TOS successfully."
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error downloading image: {e}"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"An unexpected error occurred: {e}"
        }

if __name__ == '__main__':
    # Make sure to set your OPENAI_API_KEY environment variable
    # For example: export OPENAI_API_KEY='your-api-key'
    image_url = 'https://carey.tos-ap-southeast-1.bytepluses.com/Art%20Portrait/Art%20Portrait/Art%20Portrait/Art%20Portrait%20(1).jpg'
    prompt = 'A cute baby sea otter cooking a meal'
    # result = openaiedit([image_url, image_url], prompt)
    # print(result)
    
    # Test for google_edit
    # Make sure to set your GOOGLE_API_KEY environment variable
    # For example: export GOOGLE_API_KEY='your-api-key'
    print("\nTesting Google Edit...")
    if os.getenv("GOOGLE_API_KEY"):
        google_prompt = "make the person smile"
        google_result = google_edit([image_url, image_url], google_prompt)
        print(f"Google Edit result: {google_result}")
    else:
        print("GOOGLE_API_KEY not set, skipping google_edit test.")