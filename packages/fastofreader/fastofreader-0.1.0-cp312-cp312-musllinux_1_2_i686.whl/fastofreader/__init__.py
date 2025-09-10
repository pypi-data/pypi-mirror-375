from .core import (
	read_faces,
	read_faces_from_text,
	read_int_groups_from_text,
	read_points,
	read_points_from_text,
)

__all__ = [
	"read_faces",
	"read_faces_from_text",
	"read_int_groups_from_text",
	"read_points",
	"read_points_from_text",
]

# Backwards compatibility aliases (old package/function names)
read_int_groups_from_file = read_faces  # deprecated

__version__ = "0.1.0"
