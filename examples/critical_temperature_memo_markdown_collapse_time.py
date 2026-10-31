"""Memoria de temperatura crítica y tiempo de colapso bajo ISO 834, en Markdown y LaTeX (extra `memos`).

Viga IPE 300 con Am/V = 200 m⁻¹, k_sh = 0,9, grado de utilización 0,55 y exigencia R30:
θ_cr por la ec. 4.22, instante en que el acero sin proteger la alcanza (ec. 4.25) y
veredicto. Después, la misma viga con 20 mm de placa (λ_p = 0,20) y exigencia R60.
Requiere `pip install "steelfire[memos]"`.

Ejecutar:  python examples/critical_temperature_memo_markdown_collapse_time.py
"""
from steelfire.memos.critical_temperature import CriticalTempMemoInput, render_critical_temp_memo_full


def main() -> None:
    bare = render_critical_temp_memo_full(
        CriticalTempMemoInput(member_type="beam", load_ratio=0.55, section_label="IPE 300", Am_V=200.0, ksh=0.9),
        fire_resistance_min=30.0,
    )
    print(f"Sin proteger: μ₀ = {bare.mu_0}, θ_cr = {bare.theta_cr_C:.1f} °C, t_cr = {bare.t_cr_min:.1f} min "
          f"→ R30 {'CUMPLE' if bare.pass_check else 'NO CUMPLE'}")

    prot = render_critical_temp_memo_full(
        CriticalTempMemoInput(member_type="beam", load_ratio=0.55, section_label="IPE 300", Am_V=200.0, ksh=0.9,
                              protected=True, dp_m=0.020, lambda_p=0.20, cp=1000.0, rho_p=900.0),
        fire_resistance_min=60.0,
    )
    t_cr = f"{prot.t_cr_min:.1f} min" if prot.t_cr_min is not None else "> 240 min"
    print(f"Con placa 20 mm: θ_cr = {prot.theta_cr_C:.1f} °C, t_cr = {t_cr} → R60 {'CUMPLE' if prot.pass_check else 'NO CUMPLE'}")

    print("\n--- Markdown (primeras líneas, caso sin proteger) ---")
    print("\n".join(bare.markdown.splitlines()[:22]))
    print(f"\nLaTeX: {len(bare.latex)} caracteres")


if __name__ == "__main__":
    main()
