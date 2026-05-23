"""
Modelo elemento finito 1D para transferencia térmica a través de la
protección + sección de acero.

Espacio: línea 1D normal a la cara expuesta.
Tiempo: Crank-Nicolson implícito.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class Material1D:
    name: str
    thickness_m: float
    k_W_per_mK: float
    rho_kg_m3: float
    c_J_per_kgK: float


@dataclass(frozen=True)
class Thermal1DResult:
    times_s: list[float]
    temperatures_K: list[list[float]]    # snapshots por tiempo


def solve_1d_thermal(layers: list[Material1D],
                      fire_curve: Callable[[float], float],
                      duration_s: float,
                      dt_s: float = 30.0,
                      n_elements_per_layer: int = 5,
                      T_initial_K: float = 293.15,
                      h_far_W_m2K: float = 9.0,
                      T_far_K: float = 293.15) -> Thermal1DResult:
    """Resuelve la transferencia 1D.

    BC izquierda: convección + radiación con el fuego.
    BC derecha: convección a ambiente frío.
    """
    # Discretización
    nodes: list[float] = []
    rho_c: list[float] = []
    k: list[float] = []
    pos = 0.0
    for layer in layers:
        h = layer.thickness_m / n_elements_per_layer
        for i in range(n_elements_per_layer + 1):
            nodes.append(pos + i * h)
            if i < n_elements_per_layer:
                rho_c.append(layer.rho_kg_m3 * layer.c_J_per_kgK)
                k.append(layer.k_W_per_mK)
        pos += layer.thickness_m

    nodes = np.array(nodes)
    n = len(nodes)
    # Coalescing — quitar duplicados de interfaces
    unique_nodes, idx_uniq = np.unique(nodes, return_index=True)
    nodes = unique_nodes
    n = len(nodes)

    # Propiedades por elemento
    n_el = n - 1
    rho_c_arr = np.zeros(n_el)
    k_arr = np.zeros(n_el)
    pos = 0.0
    el_idx = 0
    for layer in layers:
        for _ in range(n_elements_per_layer):
            if el_idx < n_el:
                rho_c_arr[el_idx] = layer.rho_kg_m3 * layer.c_J_per_kgK
                k_arr[el_idx] = layer.k_W_per_mK
                el_idx += 1

    # Matrices C, K
    C = np.zeros((n, n))
    K = np.zeros((n, n))
    for e in range(n_el):
        L_e = nodes[e + 1] - nodes[e]
        if L_e <= 0:
            continue
        Ce = (rho_c_arr[e] * L_e / 6.0) * np.array([[2, 1], [1, 2]])
        Ke = (k_arr[e] / L_e) * np.array([[1, -1], [-1, 1]])
        C[e:e + 2, e:e + 2] += Ce
        K[e:e + 2, e:e + 2] += Ke

    # Convection BC right (último nodo): K[-1,-1] += h_far
    K[-1, -1] += h_far_W_m2K

    T = np.full(n, T_initial_K)
    times = []
    history: list[list[float]] = []
    t = 0.0
    while t <= duration_s:
        T_fire = fire_curve(t / 60.0) + 273.15
        # Convection BC left: hot
        h_fire = 25.0   # combinado conv+rad simplificado
        K_bc = K.copy()
        K_bc[0, 0] += h_fire
        rhs = (C / dt_s) @ T
        rhs[0] += h_fire * T_fire
        rhs[-1] += h_far_W_m2K * T_far_K
        A = C / dt_s + K_bc
        T = np.linalg.solve(A, rhs)
        if int(t) % 60 == 0 or t == 0:
            times.append(t)
            history.append(T.tolist())
        t += dt_s

    return Thermal1DResult(times_s=times, temperatures_K=history)


__all__ = ["Material1D", "Thermal1DResult", "solve_1d_thermal"]
