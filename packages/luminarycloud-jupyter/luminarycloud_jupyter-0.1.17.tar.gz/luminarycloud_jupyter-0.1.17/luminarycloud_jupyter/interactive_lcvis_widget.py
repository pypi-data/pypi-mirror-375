from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import struct

if TYPE_CHECKING:
    # We need to be careful w/ this import for typing otherwise
    # we'll introduce a circular import issue
    from luminarycloud_jupyter.lcvis_widget import LCVisWidget
    from luminarycloud.vis import Plane
    from luminarycloud.types import Vector3Like


class InteractiveLCVisWidget(ABC):
    """
    Base class for all Python side representations of the
    interactive LCVis widgets
    """

    owner: "LCVisWidget | None" = None
    id = -1

    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        self.owner = owner
        self.id = id

    def set_show_controls(self, show_controls: bool) -> None:
        if self.owner:
            self.owner.set_show_widget_controls(self, show_controls)

    def remove(self) -> None:
        if self.owner:
            self.owner.delete_widget(self)
            self.owner = None
            self.id = -1

    @abstractmethod
    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        pass

    @abstractmethod
    def _to_frontend_state(self) -> "tuple[dict, list[bytes] | None]":
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        pass


class LCVisPlaneWidget(InteractiveLCVisWidget):
    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        from luminarycloud.vis import Plane

        super().__init__(owner, id)
        self._plane = Plane()

    @property
    def plane(self) -> "Plane":
        return self._plane

    @plane.setter
    def plane(self, new_plane: "Plane") -> None:
        self._plane = new_plane
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def origin(self) -> "Vector3Like":
        return self._plane.origin

    @origin.setter
    def origin(self, origin: "Vector3Like") -> None:
        self._plane.origin = origin
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def normal(self) -> "Vector3Like":
        return self._plane.normal

    @normal.setter
    def normal(self, normal: "Vector3Like") -> None:
        self._plane.normal = normal
        if self.owner:
            self.owner.update_interactive_widget(self)

    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        from luminarycloud.types import Vector3

        x, y, z = struct.unpack("fff", buffers[0].tobytes())
        self._plane.origin = Vector3(x, y, z)

        x, y, z = struct.unpack("fff", buffers[1].tobytes())
        self._plane.normal = Vector3(x, y, z)

    def _to_frontend_state(self) -> tuple[dict, list[bytes] | None]:
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        origin_buf = struct.pack(
            "fff", self._plane.origin[0], self._plane.origin[1], self._plane.origin[2]
        )
        normal_buf = struct.pack(
            "fff", self._plane.normal[0], self._plane.normal[1], self._plane.normal[2]
        )
        return {"cmd": "update_widget", "type": "plane", "id": self.id}, [origin_buf, normal_buf]


class LCVisLineWidget(InteractiveLCVisWidget):
    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        from luminarycloud.types import Vector3

        super().__init__(owner, id)
        self._start = Vector3(0, 0, 0)
        self._end = Vector3(1, 1, 1)

    @property
    def start(self) -> "Vector3Like":
        return self._start

    @start.setter
    def start(self, start: "Vector3Like") -> None:
        self._start = start
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def end(self) -> "Vector3Like":
        return self._end

    @end.setter
    def end(self, end: "Vector3Like") -> None:
        self._end = end
        if self.owner:
            self.owner.update_interactive_widget(self)

    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        from luminarycloud.types import Vector3

        x, y, z = struct.unpack("fff", buffers[0].tobytes())
        self._start = Vector3(x, y, z)

        x, y, z = struct.unpack("fff", buffers[1].tobytes())
        self._end = Vector3(x, y, z)

    def _to_frontend_state(self) -> tuple[dict, list[bytes] | None]:
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        start_buf = struct.pack("fff", self._start[0], self._start[1], self._start[2])
        end_buf = struct.pack("fff", self._end[0], self._end[1], self._end[2])
        return {"cmd": "update_widget", "type": "line", "id": self.id}, [start_buf, end_buf]


class LCVisBoxWidget(InteractiveLCVisWidget):
    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        from luminarycloud.types import Vector3

        super().__init__(owner, id)
        self._center = Vector3(0, 0, 0)
        self._size = Vector3(1, 1, 1)
        self._rotation = Vector3(0, 0, 0)

    @property
    def center(self) -> "Vector3Like":
        return self._center

    @center.setter
    def center(self, center: "Vector3Like") -> None:
        self._center = center
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def size(self) -> "Vector3Like":
        return self._size

    @size.setter
    def size(self, size: "Vector3Like") -> None:
        self._size = size
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def rotation(self) -> "Vector3Like":
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: "Vector3Like") -> None:
        self._rotation = rotation
        if self.owner:
            self.owner.update_interactive_widget(self)

    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        from luminarycloud.types import Vector3

        x, y, z = struct.unpack("fff", buffers[0].tobytes())
        self._center = Vector3(x, y, z)

        x, y, z = struct.unpack("fff", buffers[1].tobytes())
        self._size = Vector3(x, y, z)

        x, y, z = struct.unpack("fff", buffers[2].tobytes())
        self._rotation = Vector3(x, y, z)

    def _to_frontend_state(self) -> tuple[dict, list[bytes] | None]:
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        center_buf = struct.pack("fff", self._center[0], self._center[1], self._center[2])
        size_buf = struct.pack("fff", self._size[0], self._size[1], self._size[2])
        rotation_buf = struct.pack("fff", self._rotation[0], self._rotation[1], self._rotation[2])
        return {"cmd": "update_widget", "type": "box", "id": self.id}, [
            center_buf,
            size_buf,
            rotation_buf,
        ]


class LCVisCylinderWidget(InteractiveLCVisWidget):
    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        from luminarycloud.types import Vector3

        super().__init__(owner, id)
        self._start = Vector3(0, 0, 0)
        self._end = Vector3(1, 1, 1)
        self._radius = 0.5

    @property
    def start(self) -> "Vector3Like":
        return self._start

    @start.setter
    def start(self, start: "Vector3Like") -> None:
        self._start = start
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def end(self) -> "Vector3Like":
        return self._end

    @end.setter
    def end(self, end: "Vector3Like") -> None:
        self._end = end
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, radius: float) -> None:
        self._radius = radius
        if self.owner:
            self.owner.update_interactive_widget(self)

    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        from luminarycloud.types import Vector3

        x, y, z = struct.unpack("fff", buffers[0].tobytes())
        self._start = Vector3(x, y, z)

        x, y, z = struct.unpack("fff", buffers[1].tobytes())
        self._end = Vector3(x, y, z)

        self._radius = struct.unpack("f", buffers[2].tobytes())[0]

    def _to_frontend_state(self) -> tuple[dict, list[bytes] | None]:
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        start_buf = struct.pack("fff", self._start[0], self._start[1], self._start[2])
        end_buf = struct.pack("fff", self._end[0], self._end[1], self._end[2])
        radius_buf = struct.pack("f", self._radius)
        return {"cmd": "update_widget", "type": "cylinder", "id": self.id}, [
            start_buf,
            end_buf,
            radius_buf,
        ]


class LCVisHalfSphereWidget(InteractiveLCVisWidget):
    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        from luminarycloud.types import Vector3

        super().__init__(owner, id)
        self._center = Vector3(0, 0, 0)
        self._normal = Vector3(0, 0, 1)
        self._radius = 0.5

    @property
    def center(self) -> "Vector3Like":
        return self._center

    @center.setter
    def center(self, center: "Vector3Like") -> None:
        self._center = center
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def normal(self) -> "Vector3Like":
        return self._normal

    @normal.setter
    def normal(self, normal: "Vector3Like") -> None:
        self._normal = normal
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, radius: float) -> None:
        self._radius = radius
        if self.owner:
            self.owner.update_interactive_widget(self)

    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        from luminarycloud.types import Vector3

        x, y, z = struct.unpack("fff", buffers[0].tobytes())
        self._center = Vector3(x, y, z)

        x, y, z = struct.unpack("fff", buffers[1].tobytes())
        self._normal = Vector3(x, y, z)

        self._radius = struct.unpack("f", buffers[2].tobytes())[0]

    def _to_frontend_state(self) -> tuple[dict, list[bytes] | None]:
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        center_buf = struct.pack("fff", self._center[0], self._center[1], self._center[2])
        normal_buf = struct.pack("fff", self._normal[0], self._normal[1], self._normal[2])
        radius_buf = struct.pack("f", self._radius)
        return {"cmd": "update_widget", "type": "half_sphere", "id": self.id}, [
            center_buf,
            normal_buf,
            radius_buf,
        ]


class LCVisSphereWidget(InteractiveLCVisWidget):
    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        from luminarycloud.types import Vector3

        super().__init__(owner, id)
        self._center = Vector3(0, 0, 0)
        self._radius = 1.0

    @property
    def center(self) -> "Vector3Like":
        return self._center

    @center.setter
    def center(self, center: "Vector3Like") -> None:
        self._center = center
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, radius: float) -> None:
        self._radius = radius
        if self.owner:
            self.owner.update_interactive_widget(self)

    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        from luminarycloud.types import Vector3

        x, y, z = struct.unpack("fff", buffers[0].tobytes())
        self._center = Vector3(x, y, z)

        self._radius = struct.unpack("f", buffers[1].tobytes())[0]

    def _to_frontend_state(self) -> tuple[dict, list[bytes] | None]:
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        center_buf = struct.pack("fff", self._center[0], self._center[1], self._center[2])
        radius_buf = struct.pack("f", self._radius)
        return {"cmd": "update_widget", "type": "sphere", "id": self.id}, [center_buf, radius_buf]


class LCVisFinitePlaneWidget(InteractiveLCVisWidget):
    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        from luminarycloud.types import Vector3

        super().__init__(owner, id)
        self._origin = Vector3(0, 0, 0)
        self._rotation = Vector3(0, 0, 0)
        self._width = 1.0
        self._height = 1.0
        self._display_seed_grid = 0
        self._n_seed_rows = 2
        self._n_seeds_per_row = 2
        # Read-only properties from frontend
        self._x_axis = Vector3(1, 0, 0)
        self._y_axis = Vector3(0, 1, 0)

    @property
    def origin(self) -> "Vector3Like":
        return self._origin

    @origin.setter
    def origin(self, origin: "Vector3Like") -> None:
        self._origin = origin
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def rotation(self) -> "Vector3Like":
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: "Vector3Like") -> None:
        self._rotation = rotation
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, width: float) -> None:
        self._width = width
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, height: float) -> None:
        self._height = height
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def display_seed_grid(self) -> int:
        return self._display_seed_grid

    @display_seed_grid.setter
    def display_seed_grid(self, display_seed_grid: int) -> None:
        self._display_seed_grid = display_seed_grid
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def n_seed_rows(self) -> int:
        return self._n_seed_rows

    @n_seed_rows.setter
    def n_seed_rows(self, n_seed_rows: int) -> None:
        self._n_seed_rows = n_seed_rows
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def n_seeds_per_row(self) -> int:
        return self._n_seeds_per_row

    @n_seeds_per_row.setter
    def n_seeds_per_row(self, n_seeds_per_row: int) -> None:
        self._n_seeds_per_row = n_seeds_per_row
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def x_axis(self) -> "Vector3Like":
        return self._x_axis

    @property
    def y_axis(self) -> "Vector3Like":
        return self._y_axis

    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        from luminarycloud.types import Vector3

        x, y, z = struct.unpack("fff", buffers[0].tobytes())
        self._origin = Vector3(x, y, z)

        x, y, z = struct.unpack("fff", buffers[1].tobytes())
        self._rotation = Vector3(x, y, z)

        self._width = struct.unpack("f", buffers[2].tobytes())[0]
        self._height = struct.unpack("f", buffers[3].tobytes())[0]
        self._display_seed_grid = struct.unpack("I", buffers[4].tobytes())[0]
        self._n_seed_rows = struct.unpack("I", buffers[5].tobytes())[0]
        self._n_seeds_per_row = struct.unpack("I", buffers[6].tobytes())[0]

        x, y, z = struct.unpack("fff", buffers[7].tobytes())
        self._x_axis = Vector3(x, y, z)

        x, y, z = struct.unpack("fff", buffers[8].tobytes())
        self._y_axis = Vector3(x, y, z)

    def _to_frontend_state(self) -> tuple[dict, list[bytes] | None]:
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        origin_buf = struct.pack("fff", self._origin[0], self._origin[1], self._origin[2])
        rotation_buf = struct.pack("fff", self._rotation[0], self._rotation[1], self._rotation[2])
        width_buf = struct.pack("f", self._width)
        height_buf = struct.pack("f", self._height)
        display_seed_grid_buf = struct.pack("I", self._display_seed_grid)
        n_seed_rows_buf = struct.pack("I", self._n_seed_rows)
        n_seeds_per_row_buf = struct.pack("I", self._n_seeds_per_row)
        return {"cmd": "update_widget", "type": "finite_plane", "id": self.id}, [
            origin_buf,
            rotation_buf,
            width_buf,
            height_buf,
            display_seed_grid_buf,
            n_seed_rows_buf,
            n_seeds_per_row_buf,
        ]
