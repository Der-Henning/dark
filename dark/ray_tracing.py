import pygame
import torch


class RayTracing:
    """Implementation based on https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection"""
    def __init__(self, walls: list[tuple[pygame.Vector2, pygame.Vector2]], rays: int, tol=1e-10, device="cpu"):
        self.tol = tol
        self.device = torch.device(device)

        # Prepare wall vectors
        self.wall_start = torch.tensor([wall[0] for wall in walls], dtype=torch.float32, device=self.device)
        self.wall_end   = torch.tensor([wall[1] for wall in walls], dtype=torch.float32, device=self.device)
        self.wall_vec   = self.wall_end - self.wall_start 

        # Prepare ray vectors
        angles_deg = torch.arange(0, 360, step=360 / rays, dtype=torch.float32, device=self.device)     # 0 to 360
        angles_rad = torch.deg2rad(angles_deg)                                                          # 0 to 2pi
        # Each row is a 2D unit vector [cos(θ), sin(θ)]
        self.rays = torch.stack([torch.cos(angles_rad), torch.sin(angles_rad)], axis=1)                 # (n, 2)

        # Calculate matrix dimensions
        self.n, self.m = self.rays.shape[0], self.wall_vec.shape[0]

        # Prepare Matix
        self.d1_b = torch.broadcast_to(self.rays.reshape(-1, 1, 2),       (self.n, self.m, 2))          # (n, m, 2)
        self.d2_b = torch.broadcast_to(self.wall_vec.reshape(1, -1, 2),   (self.n, self.m, 2))          # (n, m, 2)
        self.q1_b = torch.broadcast_to(self.wall_start.reshape(1, -1, 2), (self.n, self.m, 2))          # (n, m, 2)

    def calculate_intersections(self, n, m, p1, d1, q1_b, d1_b, d2_b, unlimit=False):
        """
        Calculates the closest intersections of n times m lines where all n lines
        share the same starting point.
        
        """
        b = q1_b - p1                                                                                   # (n, m, 2)

        A = torch.stack([d1_b, d2_b], axis=-1)                                                          # (n, m, 2, 2)
        det = A[..., 0, 0] * A[..., 1, 1] - A[..., 0, 1] * A[..., 1, 0]                                 # (n, m)
        parallel_mask = torch.abs(det) < self.tol                                                       # (n, m)
        valid = ~parallel_mask                                                                          # (n, m)

        intersections = torch.full((n, m, 2), torch.nan, dtype=torch.float32, device=self.device)       # (n, m, 2)
        t_all = torch.full((n, m), torch.nan, dtype=torch.float32, device=self.device)                  # (n, m)
        if torch.any(valid):
            A_valid = A[valid]
            b_valid = b[valid]
            det_valid = det[valid]

            t = (b_valid[:, 0] * A_valid[:, 1, 1] - b_valid[:, 1] * A_valid[:, 0, 1]) / det_valid
            u = (b_valid[:, 0] * A_valid[:, 1, 0] - b_valid[:, 1] * A_valid[:, 0, 0]) / det_valid

            # Apply parametric constraints: t ≥ 0 (fan ray), 0 ≤ u ≤ 1 (segment)
            mask_tu = (t >= 0) & (unlimit | (t <= 1)) & (u >= 0) & (u <= 1)

            # Map back into full (n, m) shape
            full_indices = torch.nonzero(valid.flatten(), as_tuple=False).flatten()
            accepted_indices = full_indices[mask_tu]

            d1_valid = d1_b.reshape(-1, 2)[accepted_indices]
            intersections.reshape(-1, 2)[accepted_indices] = p1 + t[mask_tu, None] * d1_valid
            t_all.reshape(-1)[accepted_indices] = t[mask_tu]

        # Compute distances (along the ray, so t * |d1|)
        d1_norm = torch.linalg.matrix_norm(d1)                                                          # (n, )
        distances = t_all * d1_norm                                                                     # (n, m)
        distances[~torch.isfinite(distances)] = torch.inf

        min_indices = torch.argmin(distances, axis=1)                                                   # (n,)
        closest_points = intersections[torch.arange(n, device=self.device), min_indices]                # (n, 2)

        return closest_points

    def get_ray_intersections(self, position: pygame.Vector2) -> list[pygame.Vector2]:
        """
        For each of n rays (from common point position with direction ray),
        find the closest intersection with walls.

        Args:
            position (pygame.Vector2): Current Position

        Returns:
            list[pygame.Vector2]: List of ray intersections with walls
        """
        p1 = torch.tensor(position, dtype=torch.float32, device=self.device).reshape(1, 1, 2)               # (1, 1, 2)

        closest_points = self.calculate_intersections(self.n, self.m, p1, self.rays, self.q1_b, self.d1_b, self.d2_b, True)
        return [pygame.Vector2(point[0], point[1]) for point in closest_points]

    def get_wall_collision(self, position: pygame.Vector2, direction: pygame.Vector2) -> pygame.Vector2 | None:
        """
        Calculates the next intersection with a wall on the way from the current direction 
        to the target location.

        Args:
            position (pygame.Vector2): Current Position
            target (pygame.Vector2): Target Position

        Returns:
            pygame.Vector2 | None: Intersection with wall if any.
        """
        p1 = torch.tensor(position, dtype=torch.float32, device=self.device).reshape(1, 1, 2)               # (1, 1, 2)
        d1 = torch.tensor(direction, dtype=torch.float32, device=self.device).reshape(1, 1, 2)              # (1, 1, 2)
        d1_b = torch.broadcast_to(d1, (1, self.m, 2))                                                       # (1, m, 2)
        q1_b = self.wall_start.reshape(1, -1, 2)                                                            # (1, m, 2)
        d2_b = self.wall_vec.reshape(1, -1, 2)                                                              # (1, m, 2)

        closest_point = self.calculate_intersections(1, self.m, p1, d1, q1_b, d1_b, d2_b).reshape((2,))     # (2, )
        return None if torch.isnan(closest_point).any() else pygame.Vector2(closest_point[0], closest_point[1])
