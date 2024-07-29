import cv2
import cv2_superres

def super_resolve_image(input_image_path, upscale_factor=2):
    try:
        # Load the input image
        image = cv2.imread(input_image_path)
        if image is None:
            raise ValueError("Could not read the input image.")

        # Create a super-resolution object
        sr = cv2_superres.Superres()
        sr.initModel("SRCNN", upscale=upscale_factor)

        # Apply super-resolution
        sr_image = sr.upscaleImage(image)

        # Display the original and super-resolved images
        cv2.imshow("Original Image", image)
        cv2.imshow("Super-Resolved Image", sr_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    input_image_path = r"path/to/your/input/image.jpg"
    super_resolve_image(input_image_path, upscale_factor=2)  # Upscale factor of 2