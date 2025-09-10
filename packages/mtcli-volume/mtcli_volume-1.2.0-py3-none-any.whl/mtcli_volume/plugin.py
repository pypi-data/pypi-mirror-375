"""Plugin para exibir o Volume Profile do ativo."""

import click
import MetaTrader5 as mt5
import csv
from datetime import datetime
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from .conf import DIGITOS, SYMBOL, STEP, PERIODS
from .volume_profile import calcular_volume_profile, calcular_estatisticas

log = setup_logger()


@click.command()
@click.version_option(package_name="mtcli-volume")
@click.option(
    "--symbol", "-s", default=SYMBOL, help="Símbolo do ativo (default WIN$N)."
)
@click.option(
    "--periods", "-p", default=PERIODS, help="Número de candles de 1 minuto (default 566)."
)
@click.option(
    "--step",
    "-e",
    type=float,
    default=STEP,
    help="Tamanho do agrupamento de preços (default 100).",
)
@click.option("-csv", "--exporta-csv", is_flag=True, help="Exportar para CSV.")
def volume(symbol, periods, step, exporta_csv):
    """Exibe o Volume Profile agrupando volumes por faixa de preço."""
    conectar()
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, periods)

    if rates is None or len(rates) == 0:
        click.echo("❌ Não foi possível obter os dados.")
        shutdown()
        return

    profile = calcular_volume_profile(rates, step)
    stats = calcular_estatisticas(profile)

    dados_ordenados = sorted(profile.items(), reverse = True)

    if exporta_csv:
        data_str = datetime.now().strftime("%Y%m%d_%H%M")
        nome_arquivo = f"volume_profile_{symbol}_{data_str}.csv"
        with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Faixa de Preço", "Volume"])
            writer.writerows(dados_ordenados)
        click.echo(f"Exportado para {nome_arquivo}")
        log.info(f"Exportado para {nome_arquivo}")
    else:
        click.echo(f"\nVolume Profile {symbol}\n")
        max_vol = max(profile.values())
        for preco, vol in dados_ordenados:
            barra = "█" * (vol // max(1, max_vol // 50))
            click.echo(f"{preco:>8.{DIGITOS}f} | {vol:>6} {barra}")

        # Estatísticas
        click.echo(f"\nPOC (Preço de Maior Volume): {stats['poc']:.{DIGITOS}f}")
        click.echo(
            f"Área de Valor: {stats['area_valor'][0]:.{DIGITOS}f} a {stats['area_valor'][1]:.{DIGITOS}f}"
        )
        click.echo(f"HVNs: {stats['hvns']}")
        click.echo(f"LVNs: {stats['lvns']}")

    shutdown()
