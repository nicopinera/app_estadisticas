from infraestructura.ui.cli.formatters.table_formatter import formatear_tabla


def test_formatear_tabla_incluye_encabezados_y_valores():
    tabla = formatear_tabla([[1, "Atenas"], [2, "Instituto"]], ["ID", "Club"])

    for texto in ("ID", "Club", "Atenas", "Instituto"):
        assert texto in tabla


def test_formatear_tabla_dibuja_el_borde_de_una_tabla():
    tabla = formatear_tabla([[1, "Atenas"]], ["ID", "Club"])

    lineas = tabla.splitlines()
    assert lineas[0].startswith("+---")  # borde superior
    assert lineas[-1].startswith("+---")  # borde inferior
