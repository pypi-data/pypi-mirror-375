import numpy as np
from numba import njit
import math


@njit
def compute_error_map_jit(terrain: np.ndarray) -> np.ndarray:
    """
    Compute RTIN error map using the Martini algorithm.
    """
    size = terrain.shape[0]
    tile_size = size - 1

    # Check that size is 2^n + 1
    if (tile_size & (tile_size - 1)) != 0:
        raise ValueError(f"Expected grid size to be 2^n+1, got {size}")

    num_triangles = tile_size * tile_size * 2 - 2
    num_parent_triangles = num_triangles - tile_size * tile_size

    # Flatten terrain for 1D indexing (matching Martini's approach)
    terrain_flat = terrain.flatten()
    errors = np.zeros(terrain_flat.shape[0], dtype=np.float32)

    # Generate triangle coordinates (matching Martini's coordinate generation)
    coords = np.zeros((num_triangles, 4), dtype=np.int32)

    for i in range(num_triangles):
        triangle_id = i + 2
        ax, ay, bx, by, cx, cy = 0, 0, 0, 0, 0, 0

        if triangle_id & 1:
            # bottom-left triangle
            bx = by = cx = tile_size
        else:
            # top-right triangle
            ax = ay = cy = tile_size

        while triangle_id >> 1 > 1:
            triangle_id >>= 1
            mx = (ax + bx) >> 1
            my = (ay + by) >> 1

            if triangle_id & 1:  # left half
                bx, by = ax, ay
                ax, ay = cx, cy
            else:  # right half
                ax, ay = bx, by
                bx, by = cx, cy
            cx, cy = mx, my

        coords[i, 0] = ax
        coords[i, 1] = ay
        coords[i, 2] = bx
        coords[i, 3] = by

    # Iterate over all triangles from smallest to largest (reverse order)
    for i in range(num_triangles - 1, -1, -1):
        ax = coords[i, 0]
        ay = coords[i, 1]
        bx = coords[i, 2]
        by = coords[i, 3]
        mx = (ax + bx) >> 1
        my = (ay + by) >> 1
        cx = mx + my - ay
        cy = my + ax - mx

        # Calculate error in the middle of the long edge of the triangle
        interpolated_height = (
            terrain_flat[ay * size + ax] + terrain_flat[by * size + bx]
        ) / 2.0
        middle_index = my * size + mx
        middle_error = abs(interpolated_height - terrain_flat[middle_index])

        errors[middle_index] = max(errors[middle_index], middle_error)

        if i < num_parent_triangles:
            # Bigger triangles; accumulate error with children
            left_child_index = ((ay + cy) >> 1) * size + ((ax + cx) >> 1)
            right_child_index = ((by + cy) >> 1) * size + ((bx + cx) >> 1)
            errors[middle_index] = max(
                errors[middle_index],
                errors[left_child_index],
                errors[right_child_index],
            )

    # Reshape back to 2D
    return errors.reshape((size, size))


def compute_error_map(dem: np.ndarray) -> np.ndarray:
    """
    Compute the error map for mesh decimation using the RTIN method.



    Args:
        dem (np.ndarray): A square 2D numpy array of height values.
                         Must be (2^n + 1) x (2^n + 1) size (e.g., 257x257).

    Returns:
        np.ndarray: A 2D numpy array of error values, same shape as dem.

    Raises:
        ValueError: If the input is not square or not 2^n + 1 size.
        ImportError: If Numba is not installed (required for efficiency).

    Example:
        import numpy as np
        dem = np.random.rand(257, 257)  # 257 = 2^8 + 1
        error_map = compute_error_map(dem)
    """
    if dem.shape[0] != dem.shape[1]:
        raise ValueError("DEM must be a square array.")

    dem = np.ascontiguousarray(dem.astype(np.float32))
    return compute_error_map_jit(dem)


def generate_random_dem(
    size: int = 256, roughness: float = 0.5, seed: int = 42
) -> np.ndarray:
    """

    Generate a random DEM using the diamond-square algorithm



    This is for testing and validation. It produces a (size+1) x (size+1)

    array (e.g., 257x257 for size=256).



    Args:

        size (int): Grid size parameter (should be power of 2 for full

            hierarchy).

        roughness (float): Controls the amplitude of random variations

            (default 0.5).

        seed (int): Random seed for reproducibility (default 42).



    Returns:

        np.ndarray: A (size+1) x (size+1) array of height values.



    Example:

        dem = generate_random_dem(64)

        error_map = compute_error_map(dem)

    """

    np.random.seed(seed)
    dim = size + 1
    heights = np.zeros((dim, dim), dtype=np.float32)
    # Initialize corners to 0
    heights[0, 0] = 0
    heights[0, size] = 0
    heights[size, 0] = 0
    heights[size, size] = 0
    step = size
    while step > 1:
        half = step // 2
        # Diamond step
        for y in range(half, dim - 1, step):
            for x in range(half, dim - 1, step):
                avg = (
                    heights[y - half, x - half]
                    + heights[y - half, x + half]
                    + heights[y + half, x - half]
                    + heights[y + half, x + half]
                ) / 4
                heights[y, x] = avg + (np.random.random() - 0.5) * 2 * half * roughness
        # Square step
        for y in range(0, dim, half):
            offset = 0 if y % step == 0 else half
            for x in range(offset, dim, step):
                sum_v = 0.0
                count = 0
                if x - half >= 0:
                    sum_v += heights[y, x - half]
                    count += 1
                if x + half < dim:
                    sum_v += heights[y, x + half]
                    count += 1
                if y - half >= 0:
                    sum_v += heights[y - half, x]
                    count += 1
                if y + half < dim:
                    sum_v += heights[y + half, x]
                    count += 1
                avg = sum_v / count
                heights[y, x] = avg + (np.random.random() - 0.5) * 2 * half * roughness
        step = half
    return heights
