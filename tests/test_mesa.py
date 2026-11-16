
from waremind.mesa_model import WarehouseMesaModel


def test_mesa_agents_created():
    model = WarehouseMesaModel()

    assert len(model.robot_agents) == 3
    assert len(model.agents) == 3


def test_mesa_order_delivery():
    model = WarehouseMesaModel()
    model.add_order((3, 2))

    for _ in range(100):
        model.step()

        if model.warehouse.completed_count == 1:
            break

    assert model.warehouse.completed_count == 1


def test_mesa_data_collection():
    model = WarehouseMesaModel()
    model.add_order((3, 2))

    model.step()

    data = model.datacollector.get_model_vars_dataframe()

    assert len(data) == 1
    assert "Completed Orders" in data.columns
    assert "Average Battery" in data.columns
