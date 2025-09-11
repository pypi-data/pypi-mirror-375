import numpy as np
from vtkmodules.vtkCommonCore import vtkUnsignedCharArray
from .arcball_camera_style import ArcballCameraInteractorStyle
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk



class BoxSelectionInteractorStyle(ArcballCameraInteractorStyle):
    def __init__(self) -> None:
        ArcballCameraInteractorStyle.__init__(self)

        self.is_selecting = False
        self._click_position = (0, 0)
        self._mouse_position = (0, 0)
        self._saved_pixels = vtkUnsignedCharArray()
        self.selection_color = (255, 0, 0, 255)

    def _left_button_press_event(self, obj, event):
        super()._left_button_press_event(obj, event)
        self._click_position = self.GetInteractor().GetEventPosition()
        self.start_selection()

    def _left_button_release_event(self, obj, event):
        super()._left_button_release_event(obj, event)
        self.stop_selection()

    def _mouse_move_event(self, obj, event):
        super()._mouse_move_event(obj, event)
        self._mouse_position = self.GetInteractor().GetEventPosition()
        self.update_selection()

    def start_selection(self):
        self.is_selecting = True

        size = self.GetInteractor().GetSize()
        render_window = self.GetInteractor().GetRenderWindow()
        render_window.Render()
        # Save the current screen state
        render_window.GetRGBACharPixelData(
            0, 0, size[0] - 1, size[1] - 1, 0, self._saved_pixels
        )

    def update_selection(self):
        if not self.is_selecting:
            return
        
        size = self.GetInteractor().GetSize()
        min_x, max_x = sorted([self._click_position[0], self._mouse_position[0]])
        min_y, max_y = sorted([self._click_position[1], self._mouse_position[1]])
        min_x, max_x = np.clip([min_x, max_x], 0, size[0])
        min_y, max_y = np.clip([min_y, max_y], 0, size[1])

        # Copy the saved screen state, transform to numpy and draw over it
        selected_pixels = (
            vtk_to_numpy(self._saved_pixels)
            .reshape(size[1], size[0], 4)
            .copy()
        )

        # Draw the borders
        line_width = 2
        selected_pixels[min_y : min_y + line_width, min_x:max_x] = self.selection_color  # bottom
        selected_pixels[max_y : max_y + line_width, min_x:max_x] = self.selection_color  # top 
        selected_pixels[min_y:max_y, min_x : min_x + line_width] = self.selection_color  # left 
        selected_pixels[min_y:max_y, max_x : max_x + line_width] = self.selection_color  # right

        # Fill the box with a transparent color
        transparency = 0.3
        def lerp(a, b, t):
            return t*a + (1-t) * b

        selected_pixels[min_y:max_y, min_x:max_x] = lerp(
            np.array(self.selection_color),
            selected_pixels[min_y:max_y, min_x:max_x],
            transparency
        )

        renderWindow = self.GetInteractor().GetRenderWindow()
        renderWindow.SetRGBACharPixelData(
            0, 0, size[0] - 1, size[1] - 1, numpy_to_vtk(selected_pixels.reshape(-1, 4)), 0
        )
        renderWindow.Frame()

    def stop_selection(self):
        self.is_selecting = False
        render_window = self.GetInteractor().GetRenderWindow()
        render_window.Render()
