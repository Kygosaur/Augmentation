import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout, QWidget, QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QToolBar, QAction, QInputDialog, QSizePolicy, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPen, QKeySequence
from PyQt5.QtCore import Qt, QRectF, QSize, QPointF
import os

class ImageCropper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Cropper")
        self.images = []
        self.current_image_index = 0
        self.crop_size = QSize(640, 640)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setSceneRect(self.scene.itemsBoundingRect())
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_mouse_pressed = False
        self.mouse_press_pos = None

        self.view.mousePressEvent = self.mouse_press_event
        self.view.mouseReleaseEvent = self.mouse_release_event

        self.initialize_bounding_box()

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.image_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        load_folder_action = QAction("Load Folder", self)
        load_folder_action.setShortcut(QKeySequence.Open)
        load_folder_action.triggered.connect(self.load_folder)
        toolbar.addAction(load_folder_action)

        previous_image_action = QAction("Previous Image", self)
        previous_image_action.setShortcut(Qt.Key_Left)
        previous_image_action.triggered.connect(self.previous_image)
        toolbar.addAction(previous_image_action)

        next_image_action = QAction("Next Image", self)
        next_image_action.setShortcut(Qt.Key_Right)
        next_image_action.triggered.connect(self.next_image)
        toolbar.addAction(next_image_action)

        crop_image_action = QAction("Crop Image", self)
        crop_image_action.setShortcut(Qt.Key_C)
        crop_image_action.triggered.connect(self.crop_image)
        toolbar.addAction(crop_image_action)

        set_crop_size_action = QAction("Set Crop Size", self)
        set_crop_size_action.setShortcut(Qt.Key_S)
        set_crop_size_action.triggered.connect(self.set_crop_size)
        toolbar.addAction(set_crop_size_action)

    def load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
            if not self.images:
                QMessageBox.warning(self, "No Images Found", "No supported images were found in the selected folder.")
                return
            self.current_image_index = 0
            self.load_image(self.images[self.current_image_index])

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.scene.clear() # Clear the scene to remove all items

        # Add the image to the scene first
        self.scene.addPixmap(pixmap)

        # Dynamically create a new bounding box for the current image
        self.bounding_box = QGraphicsRectItem()
        self.bounding_box.setPen(QPen(Qt.red, 2)) # Ensure the pen is visible
        self.bounding_box.setRect(QRectF(0, 0, min(self.crop_size.width(), pixmap.width()), min(self.crop_size.height(), pixmap.height())))
        self.bounding_box.setFlag(QGraphicsRectItem.ItemIsMovable, True)

        # Add the bounding box to the scene after the image
        self.scene.addItem(self.bounding_box)

        # Center the bounding box within the image
        self.bounding_box.setPos(QPointF((pixmap.width() - self.bounding_box.rect().width()) / 2, (pixmap.height() - self.bounding_box.rect().height()) / 2))

        # Set up constraints to prevent the bounding box from being moved outside the image boundaries
        self.bounding_box.setAcceptHoverEvents(True)
        self.bounding_box.hoverMoveEvent = self.bounding_box_hover_move_event

        self.image_label.setText(f"{self.current_image_index + 1}/{len(self.images)}")
        self.scene.update() # Ensure the scene is updated
        self.view.update() # Ensure the view is updated

    def mouse_press_event(self, event):
        if event.button() == Qt.RightButton:
            self.right_mouse_pressed = True
            self.mouse_press_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.right_mouse_pressed:
            self.bounding_box_mouse_move_event(event)
        
    def mouse_release_event(self, event):
        if event.button() == Qt.RightButton:
            self.right_mouse_pressed = False
            self.mouse_press_pos = None

    def bounding_box_hover_move_event(self, event):
        # Get the current position of the bounding box
        current_pos = self.bounding_box.pos()
        # Calculate the new position based on the mouse movement
        new_pos = current_pos + event.pos() - event.lastPos()

        # Correctly retrieve the QGraphicsPixmapItem that contains the image
        # Assuming the first item is the image
        current_image_item = self.scene.items()[0]
        if isinstance(current_image_item, QGraphicsPixmapItem):
            current_image = current_image_item.pixmap()
            image_width = current_image.width()
            image_height = current_image.height()
        else:
            # Handle the case where the first item is not a QGraphicsPixmapItem
            # This might be due to the scene being cleared or the image not being loaded correctly
            return

        # Ensure the bounding box does not move outside the image boundaries
        new_pos.setX(max(min(new_pos.x(), image_width - self.bounding_box.rect().width()), 0))
        new_pos.setY(max(min(new_pos.y(), image_height - self.bounding_box.rect().height()), 0))
        # Update the position of the bounding box
        self.bounding_box.setPos(new_pos)
        
    def initialize_bounding_box(self):
        self.bounding_box = QGraphicsRectItem()
        self.bounding_box.setPen(QPen(Qt.red, 2))
        self.bounding_box.setRect(QRectF(0, 0, self.crop_size.width(), self.crop_size.height()))
        self.bounding_box.setFlag(QGraphicsRectItem.ItemIsMovable, True)

        # Custom mouse event handling
        self.bounding_box.mousePressEvent = self.bounding_box_mouse_press_event
        self.bounding_box.mouseMoveEvent = self.bounding_box_mouse_move_event
        self.bounding_box.mouseReleaseEvent = self.bounding_box_mouse_release_event

        self.scene.addItem(self.bounding_box)

    def bounding_box_mouse_press_event(self, event):
        if event.button() == Qt.RightButton:
            self.bounding_box.setFlag(QGraphicsRectItem.ItemIsMovable, True)
            self.mouse_press_pos = event.pos()
    
    def bounding_box_mouse_move_event(self, event):
        if self.bounding_box.flags() & QGraphicsRectItem.ItemIsMovable:
            # Calculate the new position based on the mouse movement
            new_pos = self.bounding_box.pos() + event.pos() - self.mouse_press_pos
            self.mouse_press_pos = event.pos()
    
            # Ensure the bounding box does not move outside the image boundaries
            current_image = self.scene.items()[0].pixmap() # Assuming the first item is the image
            image_width = current_image.width()
            image_height = current_image.height()
            new_pos.setX(max(min(new_pos.x(), image_width - self.bounding_box.rect().width()), 0))
            new_pos.setY(max(min(new_pos.y(), image_height - self.bounding_box.rect().height()), 0))
    
            # Update the position of the bounding box
            self.bounding_box.setPos(new_pos)
    
    def bounding_box_mouse_release_event(self, event):
        if event.button() == Qt.RightButton:
            self.bounding_box.setFlag(QGraphicsRectItem.ItemIsMovable, False)

    def previous_image(self):
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        self.load_image(self.images[self.current_image_index])

    def next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.load_image(self.images[self.current_image_index])

    def crop_image(self):
        if not self.images:
            QMessageBox.warning(self, "No Image Loaded", "Please load an image before cropping.")
            return

        image_path = self.images[self.current_image_index]
        pixmap = QPixmap(image_path)
        image = pixmap.toImage()

        # Get the position and size of the bounding box
        rect_pos = self.bounding_box.pos()
        rect_size = self.bounding_box.rect().size()

        # Adjust the crop rectangle to match the bounding box position and size
        crop_rect = QRectF(rect_pos, rect_size)

        cropped_image = image.copy(crop_rect.toRect())

        base_dir = os.path.dirname(image_path)
        crop_images_dir = os.path.join(base_dir, 'cropped_images')
        os.makedirs(crop_images_dir, exist_ok=True)

        base_name = os.path.basename(image_path)
        cropped_image_path = os.path.join(crop_images_dir, os.path.splitext(base_name)[0] + "_crop" + os.path.splitext(base_name)[1])
        cropped_image.save(cropped_image_path)

        QMessageBox.information(self, "Image Cropped", f"The image has been cropped and saved as {cropped_image_path}")

    def set_crop_size(self):
        width, ok = QInputDialog.getInt(self, "Set Crop Width", "Enter the width of the crop:", value=self.crop_size.width(), min=1, max=9999)
        if ok:
            height, ok = QInputDialog.getInt(self, "Set Crop Height", "Enter the height of the crop:", value=self.crop_size.height(), min=1, max=9999)
            if ok:
                self.crop_size = QSize(width, height)
                if self.images:
                    self.load_image(self.images[self.current_image_index])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageCropper()
    window.show()
    sys.exit(app.exec_())