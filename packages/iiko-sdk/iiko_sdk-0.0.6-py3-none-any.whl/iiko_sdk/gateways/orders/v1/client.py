import uuid
from dataclasses import dataclass
from datetime import datetime

from iiko_sdk.gateways.iiko_utils import BaseIIKOGateway


@dataclass
class Payment:
    payment_type_id: uuid.UUID
    payment_type_kind: str
    amount: int


@dataclass
class OrderItem:
    product_id: uuid.UUID
    amount: int
    item_type: str | None = 'Product'


ORDER_STATUSES = {'New', 'Bill', 'Closed', 'Deleted'}
ORDER_CREATION_STATUSES = {'Success', 'InProgress', 'Error'}


class OrdersGateway(BaseIIKOGateway):
    """ General API """
    version = 'api/1'

    async def get_orders_by_tables(self, restaurant_ids: list[uuid.UUID], table_ids: list[uuid.UUID],
                                   statuses: list[str] | None = None, date_from: datetime | None = None,
                                   date_to: datetime | None = None):
        """ Получение заказов по id столов
        POST /api/1/order/by_table """
        json_request = {
            'organizationIds': restaurant_ids,
            'tableIds': table_ids
        }
        if statuses:
            statuses = set(statuses)
            diff = statuses - ORDER_STATUSES
            if diff:
                raise ValueError(f'Invalid statuses {','.join(diff)}')
            json_request['statuses'] = list(statuses)

        if date_from:
            # yyyy-MM-dd HH:mm:ss.fff
            json_request['dateFrom'] = date_from.strftime('%Y-%m-%d %H:%M:%S.%f')

        if date_to:
            json_request['dateTo'] = date_to.strftime('%Y-%m-%d %H:%M:%S.%f')

        return await self.send_and_validate('/order/by_table', json_request=json_request)

    async def get_orders_by_ids(self, restaurant_ids: list[uuid.UUID],
                                order_ids: list[uuid.UUID] | None = None, pos_order_ids: list[uuid.UUID] | None = None):
        """ Получение заказов по id
        POST /api/1/order/by_id """
        if not order_ids and not pos_order_ids:
            raise ValueError('order_ids and pos_order_ids are none or empty')

        json_request = {
            'organizationIds': restaurant_ids,
        }
        if order_ids:
            json_request['orderIds'] = order_ids

        if pos_order_ids:
            json_request['posOrderIds'] = pos_order_ids

        return await self.send_and_validate('/order/by_id', json_request=json_request)

    async def create_order(self, restaurant_id: uuid.UUID, terminal_group_id: uuid.UUID, order_items: list[OrderItem],
                           table_ids: list[uuid.UUID] | None = None, payments: list[Payment] | None = None):
        """ Создание заказа
        POST /api/1/order/create """
        if not order_items:
            raise ValueError('Order items is none or empty')

        json_request = {
            'organizationId': restaurant_id,
            'terminalGroupId': terminal_group_id,
            'order': {
                'items': [
                    {
                        'productId': i.product_id,
                        'amount': i.amount,
                        'type': i.item_type
                    } for i in order_items
                ]
            }
        }
        if table_ids:
            json_request['order']['tableIds'] = table_ids

        if payments:
            json_request['order']['payments'] = [{
                'sum': p.amount,
                'paymentTypeKind': p.payment_type_kind,
                'paymentTypeId': p.payment_type_id
            } for p in payments]

        return await self.send_and_validate('/order/create', json_request=json_request)
