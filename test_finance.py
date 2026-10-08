from decimal import Decimal
from services.financial import calculate_service_settlement, calculate_prolabore_status

print("=== TESTANDO CALCULO DE REPASSE DO SALAO (NAILBOSS) ===\n")

gross = Decimal("180.00")
cmv = Decimal("20.00")
rate = Decimal("30.00")

res_gross = calculate_service_settlement(gross, cmv, rate, commission_base_type="GROSS")
print("1. Comissao do Salao sobre Valor BRUTO:")
print(f"   Valor do Servico: R$ {res_gross['gross_amount']}")
print(f"   Insumos (CMV):    R$ {res_gross['cmv_cost']}")
print(f"   Comissao Salao:   R$ {res_gross['salon_fee']} (30% de 180)")
print(f"   Lucro Manicure:   R$ {res_gross['net_amount']}\n")

res_net = calculate_service_settlement(gross, cmv, rate, commission_base_type="NET")
print("2. Comissao do Salao sobre Valor LIQUIDO (Abatendo CMV):")
print(f"   Valor do Servico: R$ {res_net['gross_amount']}")
print(f"   Insumos (CMV):    R$ {res_net['cmv_cost']}")
print(f"   Comissao Salao:   R$ {res_net['salon_fee']} (30% de [180 - 20])")
print(f"   Lucro Manicure:   R$ {res_net['net_amount']}\n")

pro_status = calculate_prolabore_status(
    total_net_profit=Decimal("3500.00"),
    prolabore_target=Decimal("4000.00"),
    total_withdrawals=Decimal("1500.00")
)
print("3. Gestao de Pro-Labore (PJ x PF):")
print(f"   Meta Salarial:    R$ {pro_status['prolabore_target']}")
print(f"   Retirado (PF):    R$ {pro_status['total_withdrawals']} ({pro_status['percentage_withdrawn']}%)")
print(f"   Falta Retirar:    R$ {pro_status['remaining_prolabore']}")
print(f"   Caixa do Studio:  R$ {pro_status['business_cash_available']}")
