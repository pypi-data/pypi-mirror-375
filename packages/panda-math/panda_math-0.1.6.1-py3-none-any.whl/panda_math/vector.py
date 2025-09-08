from __future__ import annotations
import numpy as np
from typing import (
    List,
    Tuple,
    Union,
    Iterator,
    Iterable,
    TypeVar,
    Generic,
    Any,
    TYPE_CHECKING,
    overload,
)

if TYPE_CHECKING:
    from .matrix import Matrix  # only for type checking, no runtime import

T = TypeVar("T")


class VectorBase(Generic[T]):
    """Base class for all vector implementations"""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(str(x) for x in self)})"

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Iterator[float]:
        raise NotImplementedError("Subclasses must implement __iter__")

    def __len__(self) -> int:
        raise NotImplementedError("Subclasses must implement __len__")

    def __getitem__(self, index: int) -> float:
        raise NotImplementedError("Subclasses must implement __getitem__")

    def to_list(self) -> List[float]:
        return list(self)

    def to_tuple(self) -> Tuple[float, ...]:
        return tuple(self)

    def to_numpy(self) -> np.ndarray:
        return np.array(list(self))

    @classmethod
    def from_numpy(cls, array: np.ndarray) -> T:
        if len(array) < cls._dimension:
            raise ValueError(f"Array must have at least {cls._dimension} elements")
        return cls(*array[: cls._dimension])

    @classmethod
    def from_iterable(cls, iterable: Iterable) -> T:
        return cls(*iterable)

    @property
    def magnitude(self) -> float:
        return np.sqrt(sum(x**2 for x in self))

    @property
    def normalized(self):
        return self.normalize()

    def normalize(self) -> T:
        magnitude = self.magnitude
        if magnitude == 0:
            return self
        return self.__class__(*(x / magnitude for x in self))

    def distance_to(self, other: T) -> float:
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Can only calculate distance to another {self.__class__.__name__}"
            )
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(self, other)))

    def dot(self, other: T) -> float:
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Can only calculate dot product with another {self.__class__.__name__}"
            )
        return sum(a * b for a, b in zip(self, other))

    def reverse(self):
        for i in range(len(self)):
            self[i] *= -1

    @property
    def reversed(self):
        return self.__class__(-x for x in self)


class Vector2(VectorBase["Vector2"]):
    _dimension = 2

    def __init__(self, x, y=None):
        if y is None:
            try:
                iter_data = iter(x)
                self.x = next(iter_data)
                self.y = next(iter_data)
            except (TypeError, StopIteration):
                raise ValueError(
                    "If only one argument is provided, it must be an iterable with at least 2 elements"
                )
        else:
            self.x = x
            self.y = y

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def __len__(self) -> int:
        return 2

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Vector2 index out of range")

    def __setitem__(self, index: int, value: float):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("Vector2 index out of range")

    def __add__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        elif isinstance(other, (float, int)):
            return Vector2(self.x + other, self.y + other)
        return NotImplemented

    def __radd__(self, other: Union[float, int]) -> "Vector2":
        if isinstance(other, (float, int)):
            return Vector2(self.x + other, self.y + other)
        return NotImplemented

    def __sub__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        elif isinstance(other, (float, int)):
            return Vector2(self.x - other, self.y - other)
        return NotImplemented

    def __rsub__(self, other: Union[float, int]) -> "Vector2":
        if isinstance(other, (float, int)):
            return Vector2(other - self.x, other - self.y)
        return NotImplemented

    def __mul__(
        self, other: Union["Vector2", float, int, "Matrix"]
    ) -> Union["Vector2", Any]:
        from .matrix import (
            Matrix,
        )  # runtime import inside method to avoid circular import

        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)
        elif isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        elif isinstance(other, Matrix):
            if other.cols != 2:
                raise ValueError(
                    f"Cannot multiply Vector2 with Matrix({other.rows}×{other.cols})"
                )
            result = [0] * other.rows
            for i in range(other.rows):
                for j in range(other.cols):
                    if j == 0:
                        result[i] += self.x * other.data[i][j]
                    else:
                        result[i] += self.y * other.data[i][j]
            if len(result) == 2:
                return Vector2(result[0], result[1])
            return result
        return NotImplemented

    def __rmul__(self, other: Union[float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)
        return NotImplemented

    def __truediv__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            return Vector2(self.x / other, self.y / other)
        elif isinstance(other, Vector2):
            return Vector2(self.x / other.x, self.y / other.y)
        return NotImplemented

    def __rtruediv__(self, other: Union[float, int]) -> "Vector2":
        if isinstance(other, (float, int)):
            return Vector2(other / self.x, other / self.y)
        return NotImplemented

    def __floordiv__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            return Vector2(self.x // other, self.y // other)
        elif isinstance(other, Vector2):
            return Vector2(self.x // other.x, self.y // other.y)
        return NotImplemented

    def __rfloordiv__(self, other: Union[float, int]) -> "Vector2":
        if isinstance(other, (float, int)):
            return Vector2(other // self.x, other // self.y)
        return NotImplemented

    def __mod__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            return Vector2(self.x % other, self.y % other)
        elif isinstance(other, Vector2):
            return Vector2(self.x % other.x, self.y % other.y)
        return NotImplemented

    def __rmod__(self, other: Union[float, int]) -> "Vector2":
        if isinstance(other, (float, int)):
            return Vector2(other % self.x, other % self.y)
        return NotImplemented

    def __pow__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            return Vector2(self.x**other, self.y**other)
        elif isinstance(other, Vector2):
            return Vector2(self.x**other.x, self.y**other.y)
        return NotImplemented

    def __rpow__(self, other: Union[float, int]) -> "Vector2":
        if isinstance(other, (float, int)):
            return Vector2(other**self.x, other**self.y)
        return NotImplemented

    # In-place operations
    def __iadd__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
        elif isinstance(other, (int, float)):
            self.x += other
            self.y += other
        else:
            return NotImplemented
        return self

    def __isub__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, Vector2):
            self.x -= other.x
            self.y -= other.y
        elif isinstance(other, (int, float)):
            self.x -= other
            self.y -= other
        else:
            return NotImplemented
        return self

    def __imul__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
        elif isinstance(other, Vector2):
            self.x *= other.x
            self.y *= other.y
        else:
            return NotImplemented
        return self

    def __itruediv__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            self.x /= other
            self.y /= other
        elif isinstance(other, Vector2):
            self.x /= other.x
            self.y /= other.y
        else:
            return NotImplemented
        return self

    def __ifloordiv__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            self.x //= other
            self.y //= other
        elif isinstance(other, Vector2):
            self.x //= other.x
            self.y //= other.y
        else:
            return NotImplemented
        return self

    def __imod__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            self.x %= other
            self.y %= other
        elif isinstance(other, Vector2):
            self.x %= other.x
            self.y %= other.y
        else:
            return NotImplemented
        return self

    def __ipow__(self, other: Union["Vector2", float, int]) -> "Vector2":
        if isinstance(other, (int, float)):
            self.x **= other
            self.y **= other
        elif isinstance(other, Vector2):
            self.x **= other.x
            self.y **= other.y
        else:
            return NotImplemented
        return self

    # Comparison
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Vector2):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __lt__(self, other: Union["Vector2", float, int]) -> bool:
        if isinstance(other, Vector2):
            return self.x < other.x and self.y < other.y
        elif isinstance(other, (int, float)):
            return self.x < other and self.y < other
        return NotImplemented

    def __gt__(self, other: Union["Vector2", float, int]) -> bool:
        if isinstance(other, Vector2):
            return self.x > other.x and self.y > other.y
        elif isinstance(other, (int, float)):
            return self.x > other and self.y > other
        return NotImplemented

    def __le__(self, other: Union["Vector2", float, int]) -> bool:
        if isinstance(other, Vector2):
            return self.x <= other.x and self.y <= other.y
        elif isinstance(other, (int, float)):
            return self.x <= other and self.y <= other
        return NotImplemented

    def __ge__(self, other: Union["Vector2", float, int]) -> bool:
        if isinstance(other, Vector2):
            return self.x >= other.x and self.y >= other.y
        elif isinstance(other, (int, float)):
            return self.x >= other and self.y >= other
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.x, self.y))


class Vector3(VectorBase["Vector3"]):
    _dimension = 3

    def __init__(self, x, y=None, z=None):
        if y is None and z is None:
            try:
                iter_data = iter(x)
                self.x = next(iter_data)
                self.y = next(iter_data)
                self.z = next(iter_data)
            except (TypeError, StopIteration):
                raise ValueError(
                    "If only one argument is provided, it must be an iterable with at least 3 elements"
                )
        elif z is None:
            raise ValueError("Must provide all 3 components or a single iterable")
        else:
            self.x = x
            self.y = y
            self.z = z

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y
        yield self.z

    def __len__(self) -> int:
        return 3

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise IndexError("Vector3 index out of range")

    def __setitem__(self, index: int, value: float):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 3:
            self.z = value
        else:
            raise IndexError("Vector2 index out of range")

    def __add__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, (float, int)):
            return Vector3(self.x + other, self.y + other, self.z + other)
        return NotImplemented

    def __radd__(self, other: Union[float, int]) -> "Vector3":
        if isinstance(other, (float, int)):
            return Vector3(self.x + other, self.y + other, self.z + other)
        return NotImplemented

    def __sub__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, (float, int)):
            return Vector3(self.x - other, self.y - other, self.z - other)
        return NotImplemented

    def __rsub__(self, other: Union[float, int]) -> "Vector3":
        if isinstance(other, (float, int)):
            return Vector3(other - self.x, other - self.y, other - self.z)
        return NotImplemented

    def __mul__(
        self, other: Union["Vector3", float, int, "Matrix"]
    ) -> Union["Vector3", Any]:
        from .matrix import (
            Matrix,
        )  # runtime import inside method to avoid circular import

        if isinstance(other, (int, float)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        elif isinstance(other, Vector3):
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, Matrix):
            if other.cols != 3:
                raise ValueError(
                    f"Cannot multiply Vector3 with Matrix({other.rows}×{other.cols})"
                )
            result = [0] * other.rows
            for i in range(other.rows):
                for j in range(other.cols):
                    if j == 0:
                        result[i] += self.x * other.data[i][j]
                    elif j == 1:
                        result[i] += self.y * other.data[i][j]
                    else:
                        result[i] += self.z * other.data[i][j]
            if len(result) == 3:
                return Vector3(result[0], result[1], result[2])
            return result
        return NotImplemented

    def __rmul__(self, other: Union[float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        return NotImplemented

    def __truediv__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            return Vector3(self.x / other, self.y / other, self.z / other)
        elif isinstance(other, Vector3):
            return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)
        return NotImplemented

    def __rtruediv__(self, other: Union[float, int]) -> "Vector3":
        if isinstance(other, (float, int)):
            return Vector3(other / self.x, other / self.y, other / self.z)
        return NotImplemented

    def __floordiv__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            return Vector3(self.x // other, self.y // other, self.z // other)
        elif isinstance(other, Vector3):
            return Vector3(self.x // other.x, self.y // other.y, self.z // other.z)
        return NotImplemented

    def __rfloordiv__(self, other: Union[float, int]) -> "Vector3":
        if isinstance(other, (float, int)):
            return Vector3(other // self.x, other // self.y, other // self.z)
        return NotImplemented

    def __mod__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            return Vector3(self.x % other, self.y % other, self.z % other)
        elif isinstance(other, Vector3):
            return Vector3(self.x % other.x, self.y % other.y, self.z % other.z)
        return NotImplemented

    def __rmod__(self, other: Union[float, int]) -> "Vector3":
        if isinstance(other, (float, int)):
            return Vector3(other % self.x, other % self.y, other % self.z)
        return NotImplemented

    def __pow__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            return Vector3(self.x**other, self.y**other, self.z**other)
        elif isinstance(other, Vector3):
            return Vector3(self.x**other.x, self.y**other.y, self.z**other.z)
        return NotImplemented

    def __rpow__(self, other: Union[float, int]) -> "Vector3":
        if isinstance(other, (float, int)):
            return Vector3(other**self.x, other**self.y, other**self.z)
        return NotImplemented

    # In-place operations
    def __iadd__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, Vector3):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        elif isinstance(other, (int, float)):
            self.x += other
            self.y += other
            self.z += other
        else:
            return NotImplemented
        return self

    def __isub__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, Vector3):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        elif isinstance(other, (int, float)):
            self.x -= other
            self.y -= other
            self.z -= other
        else:
            return NotImplemented
        return self

    def __imul__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
            self.z *= other
        elif isinstance(other, Vector3):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        else:
            return NotImplemented
        return self

    def __itruediv__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            self.x /= other
            self.y /= other
            self.z /= other
        elif isinstance(other, Vector3):
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
        else:
            return NotImplemented
        return self

    def __ifloordiv__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            self.x //= other
            self.y //= other
            self.z //= other
        elif isinstance(other, Vector3):
            self.x //= other.x
            self.y //= other.y
            self.z //= other.z
        else:
            return NotImplemented
        return self

    def __imod__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            self.x %= other
            self.y %= other
            self.z %= other
        elif isinstance(other, Vector3):
            self.x %= other.x
            self.y %= other.y
            self.z %= other.z
        else:
            return NotImplemented
        return self

    def __ipow__(self, other: Union["Vector3", float, int]) -> "Vector3":
        if isinstance(other, (int, float)):
            self.x **= other
            self.y **= other
            self.z **= other
        elif isinstance(other, Vector3):
            self.x **= other.x
            self.y **= other.y
            self.z **= other.z
        else:
            return NotImplemented
        return self

    # Comparison
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Vector3):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return NotImplemented

    def __lt__(self, other: Union["Vector3", float, int]) -> bool:
        if isinstance(other, Vector3):
            return self.x < other.x and self.y < other.y and self.z < other.z
        elif isinstance(other, (int, float)):
            return self.x < other and self.y < other and self.z < other
        return NotImplemented

    def __gt__(self, other: Union["Vector3", float, int]) -> bool:
        if isinstance(other, Vector3):
            return self.x > other.x and self.y > other.y and self.z > other.z
        elif isinstance(other, (int, float)):
            return self.x > other and self.y > other and self.z > other
        return NotImplemented

    def __le__(self, other: Union["Vector3", float, int]) -> bool:
        if isinstance(other, Vector3):
            return self.x <= other.x and self.y <= other.y and self.z <= other.z
        elif isinstance(other, (int, float)):
            return self.x <= other and self.y <= other and self.z <= other
        return NotImplemented

    def __ge__(self, other: Union["Vector3", float, int]) -> bool:
        if isinstance(other, Vector3):
            return self.x >= other.x and self.y >= other.y and self.z >= other.z
        elif isinstance(other, (int, float)):
            return self.x >= other and self.y >= other and self.z >= other
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))

    def cross(self, other: "Vector3") -> "Vector3":
        """Calculate the cross product with another Vector3"""
        if not isinstance(other, Vector3):
            raise TypeError("Can only calculate cross product with another Vector3")
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )


class Vector4(VectorBase["Vector4"]):
    _dimension = 4

    def __init__(self, x, y=None, z=None, w=None):
        if y is None and z is None and w is None:
            try:
                iter_data = iter(x)
                self.x = next(iter_data)
                self.y = next(iter_data)
                self.z = next(iter_data)
                self.w = next(iter_data)
            except (TypeError, StopIteration):
                raise ValueError(
                    "If only one argument is provided, it must be an iterable with at least 4 elements"
                )
        elif z is None or w is None:
            raise ValueError("Must provide all 4 components or a single iterable")
        else:
            self.x = x
            self.y = y
            self.z = z
            self.w = w

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y
        yield self.z
        yield self.w

    def __len__(self) -> int:
        return 4

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        elif index == 3:
            return self.w
        else:
            raise IndexError("Vector4 index out of range")

    def __setitem__(self, index: int, value: float):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        elif index == 3:
            self.w = value
        else:
            raise IndexError("Vector2 index out of range")

    def __add__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, Vector4):
            return Vector4(
                self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w
            )
        elif isinstance(other, (float, int)):
            return Vector4(
                self.x + other, self.y + other, self.z + other, self.w + other
            )
        return NotImplemented

    def __radd__(self, other: Union[float, int]) -> "Vector4":
        if isinstance(other, (float, int)):
            return Vector4(
                self.x + other, self.y + other, self.z + other, self.w + other
            )
        return NotImplemented

    def __sub__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, Vector4):
            return Vector4(
                self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w
            )
        elif isinstance(other, (float, int)):
            return Vector4(
                self.x - other, self.y - other, self.z - other, self.w - other
            )
        return NotImplemented

    def __rsub__(self, other: Union[float, int]) -> "Vector4":
        if isinstance(other, (float, int)):
            return Vector4(
                other - self.x, other - self.y, other - self.z, other - self.w
            )
        return NotImplemented

    def __mul__(
        self, other: Union["Vector4", float, int, "Matrix"]
    ) -> Union["Vector4", Any]:
        from .matrix import (
            Matrix,
        )  # runtime import inside method to avoid circular import

        if isinstance(other, (int, float)):
            return Vector4(
                self.x * other, self.y * other, self.z * other, self.w * other
            )
        elif isinstance(other, Vector4):
            return Vector4(
                self.x * other.x, self.y * other.y, self.z * other.z, self.w * other.w
            )
        elif isinstance(other, Matrix):
            if other.cols != 4:
                raise ValueError(
                    f"Cannot multiply Vector4 with Matrix({other.rows}×{other.cols})"
                )
            result = [0] * other.rows
            for i in range(other.rows):
                for j in range(other.cols):
                    if j == 0:
                        result[i] += self.x * other.data[i][j]
                    elif j == 1:
                        result[i] += self.y * other.data[i][j]
                    elif j == 2:
                        result[i] += self.z * other.data[i][j]
                    else:
                        result[i] += self.w * other.data[i][j]
            if len(result) == 4:
                return Vector4(result[0], result[1], result[2], result[3])
            return result
        return NotImplemented

    def __rmul__(self, other: Union[float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            return Vector4(
                self.x * other, self.y * other, self.z * other, self.w * other
            )
        return NotImplemented

    def __truediv__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            return Vector4(
                self.x / other, self.y / other, self.z / other, self.w / other
            )
        elif isinstance(other, Vector4):
            return Vector4(
                self.x / other.x, self.y / other.y, self.z / other.z, self.w / other.w
            )
        return NotImplemented

    def __rtruediv__(self, other: Union[float, int]) -> "Vector4":
        if isinstance(other, (float, int)):
            return Vector4(
                other / self.x, other / self.y, other / self.z, other / self.w
            )
        return NotImplemented

    def __floordiv__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            return Vector4(
                self.x // other, self.y // other, self.z // other, self.w // other
            )
        elif isinstance(other, Vector4):
            return Vector4(
                self.x // other.x,
                self.y // other.y,
                self.z // other.z,
                self.w // other.w,
            )
        return NotImplemented

    def __rfloordiv__(self, other: Union[float, int]) -> "Vector4":
        if isinstance(other, (float, int)):
            return Vector4(
                other // self.x, other // self.y, other // self.z, other // self.w
            )
        return NotImplemented

    def __mod__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            return Vector4(
                self.x % other, self.y % other, self.z % other, self.w % other
            )
        elif isinstance(other, Vector4):
            return Vector4(
                self.x % other.x, self.y % other.y, self.z % other.z, self.w % other.w
            )
        return NotImplemented

    def __rmod__(self, other: Union[float, int]) -> "Vector4":
        if isinstance(other, (float, int)):
            return Vector4(
                other % self.x, other % self.y, other % self.z, other % self.w
            )
        return NotImplemented

    def __pow__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            return Vector4(self.x**other, self.y**other, self.z**other, self.w**other)
        elif isinstance(other, Vector4):
            return Vector4(
                self.x**other.x, self.y**other.y, self.z**other.z, self.w**other.w
            )
        return NotImplemented

    def __rpow__(self, other: Union[float, int]) -> "Vector4":
        if isinstance(other, (float, int)):
            return Vector4(other**self.x, other**self.y, other**self.z, other**self.w)
        return NotImplemented

    # In-place operations
    def __iadd__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, Vector4):
            self.x += other.x
            self.y += other.y
            self.z += other.z
            self.w += other.w
        elif isinstance(other, (int, float)):
            self.x += other
            self.y += other
            self.z += other
            self.w += other
        else:
            return NotImplemented
        return self

    def __isub__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, Vector4):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
            self.w -= other.w
        elif isinstance(other, (int, float)):
            self.x -= other
            self.y -= other
            self.z -= other
            self.w -= other
        else:
            return NotImplemented
        return self

    def __imul__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
            self.z *= other
            self.w *= other
        elif isinstance(other, Vector4):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
            self.w *= other.w
        else:
            return NotImplemented
        return self

    def __itruediv__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            self.x /= other
            self.y /= other
            self.z /= other
            self.w /= other
        elif isinstance(other, Vector4):
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
            self.w /= other.w
        else:
            return NotImplemented
        return self

    def __ifloordiv__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            self.x //= other
            self.y //= other
            self.z //= other
            self.w //= other
        elif isinstance(other, Vector4):
            self.x //= other.x
            self.y //= other.y
            self.z //= other.z
            self.w //= other.w
        else:
            return NotImplemented
        return self

    def __imod__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            self.x %= other
            self.y %= other
            self.z %= other
            self.w %= other
        elif isinstance(other, Vector4):
            self.x %= other.x
            self.y %= other.y
            self.z %= other.z
            self.w %= other.w
        else:
            return NotImplemented
        return self

    def __ipow__(self, other: Union["Vector4", float, int]) -> "Vector4":
        if isinstance(other, (int, float)):
            self.x **= other
            self.y **= other
            self.z **= other
            self.w **= other
        elif isinstance(other, Vector4):
            self.x **= other.x
            self.y **= other.y
            self.z **= other.z
            self.w **= other.w
        else:
            return NotImplemented
        return self

    # Comparison
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Vector4):
            return (
                self.x == other.x
                and self.y == other.y
                and self.z == other.z
                and self.w == other.w
            )
        return NotImplemented

    def __lt__(self, other: Union["Vector4", float, int]) -> bool:
        if isinstance(other, Vector4):
            return (
                self.x < other.x
                and self.y < other.y
                and self.z < other.z
                and self.w < other.w
            )
        elif isinstance(other, (int, float)):
            return (
                self.x < other and self.y < other and self.z < other and self.w < other
            )
        return NotImplemented

    def __gt__(self, other: Union["Vector4", float, int]) -> bool:
        if isinstance(other, Vector4):
            return (
                self.x > other.x
                and self.y > other.y
                and self.z > other.z
                and self.w > other.w
            )
        elif isinstance(other, (int, float)):
            return (
                self.x > other and self.y > other and self.z > other and self.w > other
            )
        return NotImplemented

    def __le__(self, other: Union["Vector4", float, int]) -> bool:
        if isinstance(other, Vector4):
            return (
                self.x <= other.x
                and self.y <= other.y
                and self.z <= other.z
                and self.w <= other.w
            )
        elif isinstance(other, (int, float)):
            return (
                self.x <= other
                and self.y <= other
                and self.z <= other
                and self.w <= other
            )
        return NotImplemented

    def __ge__(self, other: Union["Vector4", float, int]) -> bool:
        if isinstance(other, Vector4):
            return (
                self.x >= other.x
                and self.y >= other.y
                and self.z >= other.z
                and self.w >= other.w
            )
        elif isinstance(other, (int, float)):
            return (
                self.x >= other
                and self.y >= other
                and self.z >= other
                and self.w >= other
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z, self.w))


# Provide convenient aliases
Vec2 = Vector2
vec2 = Vector2
Vec3 = Vector3
vec3 = Vector3
Vec4 = Vector4
vec4 = Vector4


# Add utility functions for conversion between different vector dimensions
def vec2_to_vec3(v: Vector2, z: float = 0.0) -> Vector3:
    """Convert a Vector2 to a Vector3 by adding the z component"""
    return Vector3(v.x, v.y, z)


def vec2_to_vec4(v: Vector2, z: float = 0.0, w: float = 1.0) -> Vector4:
    """Convert a Vector2 to a Vector4 by adding the z and w components"""
    return Vector4(v.x, v.y, z, w)


def vec3_to_vec2(v: Vector3) -> Vector2:
    """Convert a Vector3 to a Vector2 by dropping the z component"""
    return Vector2(v.x, v.y)


def vec3_to_vec4(v: Vector3, w: float = 1.0) -> Vector4:
    """Convert a Vector3 to a Vector4 by adding the w component"""
    return Vector4(v.x, v.y, v.z, w)


def vec4_to_vec2(v: Vector4) -> Vector2:
    """Convert a Vector4 to a Vector2 by dropping the z and w components"""
    return Vector2(v.x, v.y)


def vec4_to_vec3(v: Vector4) -> Vector3:
    """Convert a Vector4 to a Vector3 by dropping the w component"""
    return Vector3(v.x, v.y, v.z)
