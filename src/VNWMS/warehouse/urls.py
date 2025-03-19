from django.urls import re_path as url

from warehouse.views import index, packing_material_stock_in, packing_material_stock_out, stockin_detail, \
    get_product_order_info, \
    packing_material_stock_in_post, packing_material_stock_out_post, dashboard, get_purchase_no_info, \
    product_order_search, \
    transfer_and_adjust, bin_transfer, \
    bin_transfer_page, get_product_order_stout, product_order_bin_search, product_order_hist_data, \
    get_purchase_no_stout, \
    bin_adjust_page, bin_adjust, upload_excel, open_data_import, inventory_sheet, warehouse_map, get_all_areas, \
    check_bin_exists, download_excel_template, result_search, warehouse_list, get_bin_data, get_bins, get_areas, \
    bin_search, bin_list, edit_bin, check_po_exists, bin_action, create_bin, area_list, area_delete, create_area, \
    edit_area, warehouse_delete, create_warehouse, edit_warehouse, show_warehouse, test, bin_by_area, bin_delete, \
    area_by_warehouse, open_data_import_api, open_data_import_confirm_api

urlpatterns = [
    url(r'^test/$', test, name='test'),
    url(r'^show_warehouse/(?P<pk>\w+)/$', show_warehouse, name='show_warehouse'),
    url(r'^edit/(?P<warehouse_code>\w+)/$', edit_warehouse, name='edit_warehouse'),
    url(r'^create/$', create_warehouse, name='warehouse_create'),
    url(r'^delete/(?P<pk>\w+)/$', warehouse_delete, name='warehouse-delete'),

    url(r'^area/edit/(?P<area_code>[^/]+)/$', edit_area, name='edit_area'),
    url(r'^area/create/(?P<wh_code>[^/]+)/$', create_area, name='area_create'),
    url(r'^area/area_by_warehouse/(?P<wh_code>\w+)/$', area_by_warehouse, name='area_by_warehouse'),
    url(r'^area/delete/(?P<pk>[^/]+)/$', area_delete, name='area-delete'),
    url(r'^area/list/$', area_list, name='area_list'),
    url(r'^area/get-all-areas/$', get_all_areas, name='get_all_areas'),

    url(r'^bin/bin_action/$', bin_action, name='bin_action'),
    url(r'^bin/check_po_exists/$', check_po_exists, name='check_po_exists'),
    url(r'^bin/create/(?P<area_code>[^/]+)$', create_bin, name='bin_create'),
    url(r'^bin/edit/(?P<bin_code>[^/]+)/$', edit_bin, name='edit_bin'),
    url(r'^bin/list/$', bin_list, name='bin_list'),
    url(r'^bin/bin_by_area/(?P<area_code>[^/]+)$', bin_by_area, name='bin_by_area'),
    url(r'^bin/delete/(?P<pk>[^/]+)/$', bin_delete, name='bin-delete'),
    url(r'^bin/open_data_import/$', open_data_import, name="open_data_import"),
    url(r'^bin/open_data_import_api/$', open_data_import_api, name="open_data_import_api"),
    url(r'^bin/open_data_import_confirm_api/$', open_data_import_confirm_api, name="open_data_import_confirm_api"),

    url(r'^bin/search/$', bin_search, name='bin_search'),
    url(r'^get-areas/$', get_areas, name='get_areas'),
    url(r'^get-bins/$', get_bins, name='get_bins'),
    url(r'^get-bin-data/$', get_bin_data, name='get_bin_data'),
    url(r'^check-bin-exists/$', check_bin_exists, name='check_bin_exists'),
    url(r'^inventory_sheet/$', inventory_sheet, name="inventory_sheet"),
    url(r'^$', warehouse_list, name='warehouse_list'),

    url(r'^packing_material_stock_in/', packing_material_stock_in, name='packing_material_stock_in'),
    url(r'^packing_material_stock_out/', packing_material_stock_out, name='packing_material_stock_out'),
    url(r'^stockin_detail/(?P<pk>\w+)/$', stockin_detail, name='stockin_detail'),
    url(r'^get_product_order_info/', get_product_order_info, name='get_product_order_info'),
    url(r'^get_product_order_stout/', get_product_order_stout, name='get_product_order_stout'),
    url(r'^get_purchase_no_stout/', get_purchase_no_stout, name='get_purchase_no_stout'),
    url(r'^get_purchase_no_info/', get_purchase_no_info, name='get_purchase_no_info'),
    url(r'^packing_material_stock_in_post/', packing_material_stock_in_post, name='packing_material_stock_in_post'),
    url(r'^packing_material_stock_out_post/', packing_material_stock_out_post, name='packing_material_stock_out_post'),
    url(r'^dashboard/', dashboard, name='warehouse_dashboard'),
    url(r'^upload/$', upload_excel, name="upload_excel"),

    url(r'^product_order_search/$', product_order_search, name='product_order_search'),
    url(r'^product_order_hist_data/$', product_order_hist_data, name='product_order_hist_data'),
    url(r'^product_order_bin_search/$', product_order_bin_search, name='product_order_bin_search'),
    url(r'^transfer_and_adjust/$', transfer_and_adjust, name='transfer_and_adjust'),
    url(r'^bin_transfer_page/$', bin_transfer_page, name='bin_transfer_page'),
    url(r'^bin/transfer/$', bin_transfer, name='bin_transfer'),
    url(r'^bin_adjust_page/$', bin_adjust_page, name='bin_adjust_page'),
    url(r'^bin/adjust/$', bin_adjust, name='bin_adjust'),
    url(r'^result_search/$', result_search, name='result_search'),
    # url(r'^export_excel/$', export_excel, name='export_excel'),
    url(r'^map/(?P<pk>\w+)/$', warehouse_map, name='warehouse_map'),
    url(r'^download-template/(?P<filename>[\w\-.]+)/$', download_excel_template, name='download_excel_template'),
    url(r'^$', index, name='warehouse_index'),
]




