from django.core.paginator import Paginator

from aries.products.models import HubStock, Menu, Product
from aries.products.serializers import HubStockSerializer


class StockManager:

    def __init__(self, logger_info, logger_error):
        self.logger_info = logger_info
        self.logger_error = logger_error

    def get_stock_list(self, hub_id, page, limit):
        self.logger_info.info('[StockManager][get_stock_list]')
        hub_stocks = HubStock.objects.filter(
            hub=hub_id
        ).order_by('-id')
        hub_stock_count = hub_stocks.count()

        paginator = Paginator(hub_stocks, limit)
        hub_stock = paginator.page(page).object_list

        serializer = HubStockSerializer(hub_stock, many=True)
        hub_stock_data = serializer.data

        for hub_stock in hub_stock_data:
            menu_en = Menu.objects.get(id=hub_stock['menu'])
            hub_stock['menu_name_en'] = menu_en.name

            menu_cn = Menu.objects.using('aries_cn').get(id=hub_stock['menu'])
            hub_stock['menu_name_cn'] = menu_cn.name

        result = (hub_stock_count, hub_stock_data)
        return result

    def update_stock_list(self, hub_id, hub_stock_list):
        self.logger_info.info('[StockManager][update_stock_list]')

        for hub_stock in hub_stock_list:
            hub_stock['hub'] = hub_id

            if 'hub' in hub_stock:
                del hub_stock['hub']

            hub_stock_instance = HubStock.objects.get(id=hub_stock['id'])
            menu = hub_stock_instance.menu

            sales_status = 1

            if hub_stock['stock'] <= 0:
                # SOLD OUT
                product_qs = Product.objects.filter(hub=hub_id, menu=menu, status__lte=sales_status)
                product_qs.update(status=0)
            elif hub_stock['stock'] >= 1:
                # NOW SALES
                product_qs = Product.objects.filter(hub=hub_id, menu=menu, status__lte=sales_status)
                product_qs.update(status=1)

            serializer = HubStockSerializer(hub_stock_instance, data=hub_stock, partial=True)

            if serializer.is_valid():
                serializer.save()

        return True

    def check_sold_out(self, hub_id, menu_id_list):
        """
        Check stock of each menus
        :param hub_id: hub id
        :param menu_id_list: menu id list
        :return: If all menus are sold out, return True or False
        """
        self.logger_info.info('[StockManager][check_sold_out]')
        hub_stock_qs = HubStock.objects.filter(hub_id=hub_id, menu__in=menu_id_list)

        result = True
        for hub_stock in hub_stock_qs:
            if hub_stock.stock >= 1:
                result = False
                break

        return result

    def get_stock_map(self, hub_id, menu_id_list):
        """
        Get stock information to discount info
        :param hub_id: hub_id
        :param menu_id_list: menu id list
        :return: Stock dict
        """
        self.logger_info.info('[StockManager][get_stock_map]')
        hub_stock_qs = HubStock.objects.filter(hub_id=hub_id, menu__in=menu_id_list)
        hub_stock_data = HubStockSerializer(hub_stock_qs, many=True).data
        hub_stock_dict = {}

        for hub_stock in hub_stock_data:
            hub_stock_dict[hub_stock['menu']] = hub_stock['stock']

        return hub_stock_dict

    def get_all_stock_map(self, hub_id):
        """
        Get stock information to discount info
        :param hub_id: hub_id
        :return: Stock dict
        """
        self.logger_info.info('[StockManager][get_all_stock_map]')
        hub_stock_qs = HubStock.objects.filter(hub_id=hub_id)
        hub_stock_data = HubStockSerializer(hub_stock_qs, many=True).data
        hub_stock_dict = {}

        for hub_stock in hub_stock_data:
            hub_stock_dict[hub_stock['menu']] = hub_stock['stock']

        return hub_stock_dict
