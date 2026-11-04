# Limitaciones conocidas de steelfire

Lo que el paquete no hace o hace de forma simplificada.

- `iso834.FireEvaluator` (y el endpoint `/api/thermal/iso834`) es por defecto un estimador simplificado de la temperatura del acero, no el método de §4.2.5; con `use_en1993_exact_c_a=True` integra §4.2.5, pero el caso protegido usa una placa fija (15 mm, λ_p = 0,12, c_p = 1100, ρ_p = 400). Para veredictos usa `en_steel_temperature` o `/api/fire/check-profile`.
- La temperatura de referencia T_Ed y los perfiles de temperatura del Anexo A de EN 1992-1-2 no están implementados. La curva paramétrica del Anexo A de EN 1991-1-2 (aa269db) da Θ_g, pero no la API; en 1.2.1 se corrigió su enfriamiento en fuegos controlados por el combustible (Θ_max con Γ_lim y t*_max de la Ec. A.12: antes saltaba de 818 a 1052 °C en t_max).
- `protection_catalog` tiene seis productos genéricos sin tablas de ensayo cargadas; los intumescentes solo se verifican tras cargar filas del informe del fabricante.
- `check_fire_resistance_from_profile` usa k_sh = 0,90, A_p/V = Am/V y el espesor medio del rango del producto; afina con `ProtectedSteel` directamente.
- `thermal_fea` usa por defecto k = 45 W/mK constante (con `variable_k=True`, λ_a(θ) de §3.4.1.3 evaluada a la temperatura media de la sección, no celda a celda) y c_a a la temperatura media; la protección se modela como una resistencia térmica en el flujo, no como capa mallada. `fem_thermal_1d` usa h = 25 W/m²K en la cara expuesta (más radiación linealizada con ε = 0,7 si `include_radiation=True`) y propiedades constantes salvo con `variable_steel_properties=True`, que reconoce el acero por el nombre de la capa («steel» o «acero»).
- `concrete_fire` emplea un perfil de temperaturas semiempírico (difusividad dependiente de T y meseta a 100 °C); las tablas 5.2a/5.5/5.8 están resumidas.
- `fire_load_density`: valores característicos y factores δ por defecto; k_c = 0,07 min·m²/MJ es una simplificación de EN 1991-1-2 Anexo F.
- El código AU se enruta a la tabla EN sin los ajustes de AS 4100.
