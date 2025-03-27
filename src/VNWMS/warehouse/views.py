import json
import os
import pandas as pd
from datetime import datetime
from django.utils.translation import get_language
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import transaction
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from VNWMS.database import sap_database, vnedc_database
from VNWMS.settings.base import MEDIA_URL
from users.models import CustomUser
from warehouse.utils import Do_Transaction, get_item_type_name, inventory_search, inventory_history
from .forms import WarehouseForm, AreaForm, BinForm, BinValueForm, BinSearchForm, StockInPForm, StockOutPForm, \
    BinTransferForm, QuantityAdjustForm, ExcelUploadForm, BinValueSearchForm, BinValueDeleteForm
from .models import Warehouse, Area, Bin, Bin_Value, Bin_Value_History, StockInForm, Series, \
    MovementType, ItemType, StockOutForm
from django.db.models import Case, When, Value, BooleanField, Q


# Warehouse
def create_warehouse(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST, request.FILES)  # Xử lý dữ liệu POST và FILES
        if form.is_valid():
            # Lưu đối tượng với user hiện tại
            warehouse = form.save(commit=False)  # Không lưu ngay lập tức

            # Gán người dùng vào các trường create_by và update_by
            warehouse.create_by = request.user
            warehouse.update_by = request.user

            # Lưu đối tượng với các trường đã được gán
            warehouse.save()  # Lưu đối tượng vào cơ sở dữ liệu
            return redirect('warehouse_list')  # Điều hướng đến trang thành công
    else:
        form = WarehouseForm()  # Tạo form trống

    return render(request, 'warehouse/create_warehouse.html', locals())


def warehouse_list(request):
    # Lấy toàn bộ danh sách warehouse từ cơ sở dữ liệu
    warehouses = Warehouse.objects.all()

    return render(request, 'warehouse/list_warehouse.html', locals())


def edit_warehouse(request, warehouse_code):
    warehouse = get_object_or_404(Warehouse, wh_code=warehouse_code)

    if request.method == 'POST':
        form = WarehouseForm(request.POST, request.FILES, instance=warehouse)

        if form.is_valid():
            form.save()  # Lưu các thay đổi vào cơ sở dữ liệu
            return redirect('warehouse_list')  # Điều hướng về danh sách kho
    else:
        form = WarehouseForm(instance=warehouse)

    return render(request, 'warehouse/edit_warehouse.html', locals())


def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == 'POST':
        warehouse.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({'message': 'Warehouse deleted successfully.', 'success': True}, status=200)

        return redirect('warehouse_list')

    return JsonResponse({'message': 'Invalid request method.'}, status=400)


def test(request):

    return render(request, 'warehouse/test.html', locals())


def show_warehouse(request, pk):
    if request.method == 'POST':
        form = BinValueForm(request.POST)
        if form.is_valid():
            form.save()
            list_value = list(Bin_Value.objects.values())
            return JsonResponse(list_value, safe=False)

    warehouse = Warehouse.objects.get(wh_code=pk)
    bins = Bin.objects.filter(area__warehouse=warehouse)
    form = BinValueForm()

    bins_status = []

    for bin in bins:
        bin_value_exists = Bin_Value.objects.filter(bin=bin).exists()

        status = 'red' if bin_value_exists else 'green'

        bins_status.append({
            'bin_id': bin.bin_id,
            'status': status,  # Sử dụng biến status đã gán
        })
    return render(request, 'warehouse/test.html', locals())


# Area
def create_area(request, wh_code):
    if request.method == 'POST':
        form = AreaForm(request.POST)  # Xử lý dữ liệu POST và FILES
        if form.is_valid():

            area = form.save(commit=False)  # Không lưu ngay lập tức
            # Gán người dùng vào các trường create_by và update_by
            area.create_by = request.user
            area.update_by = request.user

            # Lưu đối tượng với các trường đã được gán
            area.save()  # Lưu đối tượng vào cơ sở dữ liệu
            return redirect('area_by_warehouse', wh_code=wh_code)  # Điều hướng đến trang thành công
    else:
        form = AreaForm(initial={'warehouse': wh_code})  # Tạo form trống

    return render(request, 'warehouse/area/create_area.html', locals())


def area_list(request):
    areas = Area.objects.all()
    return render(request, 'warehouse/area/list_area.html', locals())


def area_by_warehouse(request, wh_code):
    # Lấy đối tượng Warehouse tương ứng với wh_code
    warehouse = Warehouse.objects.get(wh_code=wh_code)

    if warehouse:
        # Lấy tất cả các Area có wh_code là mã kho của warehouse
        areas = Area.objects.filter(warehouse=warehouse)
    else:
        areas = []

    return render(request, 'warehouse/area/area_by_warehouse.html', locals())


def edit_area(request, area_code):
    area = get_object_or_404(Area, area_id=area_code)
    wh_code = area.warehouse_id

    if request.method == 'POST':
        # Khởi tạo form với dữ liệu từ request
        form = AreaForm(request.POST, request.FILES, instance=area)

        if form.is_valid():
            form.save()  # Lưu các thay đổi vào cơ sở dữ liệu
            return redirect('area_by_warehouse', wh_code=wh_code)
    else:
        form = AreaForm(instance=area)

    return render(request, 'warehouse/area/edit_area.html', locals())


def area_delete(request, pk):
    area = get_object_or_404(Area, pk=pk)
    wh = Area.objects.get(area_id=area).warehouse_id
    if request.method == 'POST':
        # Xóa đối tượng
        area.delete()

        # Trả về phản hồi AJAX nếu yêu cầu là AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({'message': 'Area deleted successfully.', 'redirect': 'warehouse/list/', 'success': True}, status=200)
        else:
            # Điều hướng thông thường nếu không phải là AJAX
            return redirect(area_by_warehouse, wh_code=wh)

    # Không cần render trang riêng cho việc xóa
    return JsonResponse({'message': 'Invalid request method.'}, status=400)


#Bin
def create_bin(request, area_code):
    # Lấy đối tượng Area từ area_code
    area = get_object_or_404(Area, area_id=area_code)

    if request.method == 'POST':
        form = BinForm(request.POST, request.FILES)
        if form.is_valid():
            # Gắn đối tượng area vào form trước khi lưu
            bin = form.save(commit=False)

            # Gán người dùng vào các trường create_by và update_by
            bin.create_by = request.user if request.user.is_authenticated else 'Unknown'
            bin.update_by = request.user if request.user.is_authenticated else 'Unknown'

            bin.area = area
            bin.save()
            return redirect('bin_by_area', area_code=area_code)  # Điều hướng đến trang bin_by_area
    else:
        # Truyền đối tượng area vào form, không phải chỉ area_code
        form = BinForm(initial={'area': area})

    return render(request, 'warehouse/bin/create_bin.html', locals())


def bin_list(request):
    bins = Bin.objects.all()
    return render(request, 'warehouse/bin/list_bin.html', {'bins': bins})


def edit_bin(request, bin_code):
    bin = get_object_or_404(Bin, bin_id=bin_code)
    area_code = bin.area_id

    if request.method == 'POST':
        # Khởi tạo form với dữ liệu từ request
        form = BinForm(request.POST, request.FILES, instance=bin)

        if form.is_valid():
            form.save()  # Lưu các thay đổi vào cơ sở dữ liệu
            return redirect('bin_by_area', area_code=area_code)
    else:
        form = BinForm(instance=bin)

    return render(request, 'warehouse/bin/edit_bin.html', locals())


def bin_delete(request, pk):

    bin = get_object_or_404(Bin, pk=pk)

    if request.method == 'POST':
        # Xóa đối tượng
        bin.delete()

        # Trả về phản hồi AJAX nếu yêu cầu là AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX
            return JsonResponse({'message': 'Bin deleted successfully.', 'success': True}, status=200)

        # Điều hướng thông thường nếu không phải là AJAX
        return redirect('bin_by_area', area_code=bin.area.area_id)

    # Không cần render trang riêng cho việc xóa
    return JsonResponse({'message': 'Invalid request method.'}, status=400)


def bin_by_area(request, area_code):
    # Lấy đối tượng Warehouse tương ứng với wh_code
    area = Area.objects.get(area_id=area_code)
    wh_code = area.warehouse_id

    if area:
        # Lấy tất cả các Area có wh_code là mã kho của warehouse
        bins = Bin.objects.filter(area=area)
    else:
        bins = []

    # Truyền dữ liệu vào context
    return render(request, 'warehouse/bin/bin_by_area.html', locals())


def bin_search(request):
    db = vnedc_database()
    form = BinSearchForm(request.GET or None)

    if request.GET and form.is_valid():
        query_bin = form.cleaned_data.get('bin')
        query_po_no = form.cleaned_data.get('po_no')
        query_size = form.cleaned_data.get('size')
        query_from = form.cleaned_data.get('from_date')
        query_to = form.cleaned_data.get('to_date')

        if query_bin or query_po_no or query_size:

            bin_hists = inventory_history(location=query_bin, product_order=query_po_no, size=query_size, from_date=query_from, to_date=query_to)
            if not bin_hists.exists():
                message = "No matching records found."

            bin_values = inventory_search(location=query_bin, product_order=query_po_no, size=query_size)

            # Lọc kết quả cuối cùng
            result_history = bin_hists
            result_value = bin_values

        else:
            result_history = None
            result_value = None

    return render(request, 'warehouse/search_bin_history.html', locals())


def check_po_exists(request):
    po_no = request.POST.get('po_no')
    bin_id = request.POST.get('bin_id')

    # Kiểm tra xem PO có tồn tại trong cơ sở dữ liệu không
    if Bin_Value.objects.filter(bin=bin_id, po_no=po_no).exists():
        return JsonResponse({'exists': True})
    else:
        return JsonResponse({'exists': False})


def bin_action(request):

    if request.method == 'POST':
        bin_id = request.POST.get('bin')  # Lấy giá trị `bin` từ yêu cầu AJAX
        status = request.POST.get('status')  # Lấy giá trị `status` (nếu có)
        action = request.POST.get('action')

        form = BinSearchForm(request.POST or None, bin_value=bin_id)

        act_type = 'STOCKOUT'

        if status == 'edit':
            # Lấy các giá trị cần thiết từ request
            po = request.POST.get('po')
            size = request.POST.get('size')
            qty = int(request.POST.get('qty'))
            old = int(request.POST.get('qty'))
            old_qty = 0

            try:
                # Lấy bin_object từ bin_id
                bin_object = Bin.objects.get(bin_id=bin_id)
                bin_value = Bin_Value.objects.filter(bin=bin_object, po_no=po).first()

                if bin_value:
                    # So sánh giá trị `po` từ form với `po_no` trong DB
                    if po != bin_value.po_no:
                        act_type = 'STOCKIN'  # Nếu không khớp, gán giá trị act_type = 'STOCK IN'
                    else:
                        old_qty = bin_value.qty
                        qty = old_qty - qty  # Trừ số lượng cũ với số lượng mới được nhập từ form
                else:
                    act_type = 'STOCKIN'  # Nếu không tìm thấy bin_value, coi như nhập mới

                if qty == 0:
                    bin_value.delete()
                elif qty > 0:
                    Bin_Value.objects.update_or_create(
                        bin=bin_object,
                        po_no=po,
                        defaults={
                            'size': size,
                            'qty': qty,
                            'status': 'edit',
                            'update_by': request.user
                        }
                    )
                # new = old - qty
                # Lưu lịch sử
                Bin_Value_History.objects.create(
                    bin=bin_object,
                    po_no=po,
                    size=size,
                    act_type=act_type,
                    old_qty=int(old_qty),
                    act_qty=-int(old),
                    new_qty=int(qty),
                    create_by=request.user
                )

            except Bin.DoesNotExist:
                return JsonResponse({'error': f'Bin {bin_id} does not exist.'}, status=404)

        elif status == 'STOCK':
            po = request.POST.get('po')
            size = request.POST.get('size')
            qty = int(request.POST.get('qty'))

            try:
                # Lấy bin_object từ bin_id
                bin_object = Bin.objects.get(bin_id=bin_id)

                # Cập nhật hoặc tạo mới Bin_Value với số lượng mới
                Bin_Value.objects.update_or_create(
                    bin=bin_object,
                    po_no=po,
                    defaults={
                        'size': size,
                        'qty': qty,
                        'status': 'STOCK',
                        'update_by': request.user
                    }
                )

                # Lưu lịch sử
                Bin_Value_History.objects.create(
                    bin=bin_object,
                    po_no=po,
                    size=size,
                    act_type='STOCKIN',
                    old_qty=0,
                    act_qty=int(qty),
                    new_qty=int(qty),
                    create_by=request.user
                )

            except Bin.DoesNotExist:
                return JsonResponse({'error': f'Bin {bin_id} does not exist.'}, status=404)

        # Lọc dữ liệu theo bin_id và trả về danh sách
        list_bin_value = Bin_Value.objects.filter(bin__bin_id=bin_id).values('bin', 'po_no', 'size', 'qty')
        form = BinSearchForm()
        data = {
            'list_bin_value': list(list_bin_value),
            'message': 'Data successfully updated!',
            'bin_code': bin_id,
            'from': form.fields['from_date'].initial,
            'to': form.fields['to_date'].initial,
        }

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def index(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse/index.html', locals())


def dashboard(request):

    return render(request, 'warehouse/dashboard.html', locals())


def warehouse_map(request, pk):
    warehouse = Warehouse.objects.get(wh_code__contains='PKG', wh_plant=request.user.plant)
    # bg = warehouse.wh_bg.url

    bg = warehouse.wh_bg.url if warehouse.wh_bg else None
    print(pk)

    return render(request, 'warehouse/warehouse_map.html', locals())


# 入庫作業
@transaction.atomic
@login_required
def packing_material_stock_in(request):

    warehouse_code = 'PKG'

    bins = Bin.objects.filter(area__warehouse__wh_code='PKG').annotate(
        has_stock=Case(
            When(value_bin__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    )

    warehouses = Warehouse.objects.all()

    if request.method == 'POST':
        hidItem_list = request.POST.get('hidItem_list')
        if hidItem_list:
            items = json.loads(hidItem_list)

        apply_date = request.POST.get('apply_date')
        pr_no = request.POST.get('pr_no')
        desc = request.POST.get('desc')

        save_tag = transaction.savepoint()
        try:
            stock_in = StockInForm()
            YYYYMM = datetime.now().strftime("%Y%m")
            key = "SI"+YYYYMM
            stock_in.form_no = key + str(get_series_number(key, "入庫單")).zfill(3)
            stock_in.pr_no = pr_no
            stock_in.requester = request.user
            stock_in.apply_date = apply_date
            stock_in.reason = desc
            stock_in.create_by = request.user
            stock_in.save()

            for item in items:
                Do_Transaction(request, stock_in.form_no, 'STIN', item['item_code'], item['bin_code'], int(item['qty']),
                               item['purchase_unit'], item['comment'])

        except Exception as e:
            transaction.savepoint_rollback(save_tag)
            print(e)

        return redirect(stock_in.get_absolute_url())
    form = StockInPForm()
    return render(request, 'warehouse/packing_material_stock_in.html', locals())


@login_required
def stockin_form(request, pk):
    return render(request, 'warehouse/stockin_form.html', locals())


def get_product_order_stout(request):
    data_list_stout = []

    if request.method == 'GET':
        product_order = request.GET.get('product_order')
        purchase_no = request.GET.get('purchase_no')

        if product_order == '':
            return JsonResponse({"status": "no_change"}, status=200)
        else:
            raws_stout = inventory_search(product_order=product_order, purchase_order=purchase_no)
            for raw in raws_stout:
                data_list_stout.append({'product_order': raw['product_order'],
                                        'size': raw['size'],
                                        'qty': int(raw['qty']),
                                        'bin_id': raw['bin_id'],
                                        'purchase_no': raw['purchase_no'],
                                        'version_no': raw['version_no'],
                                        'version_seq': raw['version_seq'],
                                        'purchase_unit': raw['purchase_unit'],
                                        'customer_no': raw['customer_no'],
                                        'supplier': raw['supplier'],
                                        'lot_no': raw['lot_no'],
                                        'purchase_qty': raw['purchase_qty'],
                                        'item_type': raw['item_type'],
                                        'post_date': raw['post_date'],
                                        'sap_mtr_no': raw['sap_mtr_no'],
                                        'desc': raw['desc'],
                                        })

    return JsonResponse({
        "data_list_stout": data_list_stout
    }, safe=False)


def get_purchase_no_stout(request):
    data_list_stout = []
    if request.method == 'GET':
        product_order = request.GET.get('product_order')
        purchase_no = request.GET.get('purchase_no')

        if purchase_no == '':
            return JsonResponse({"status": "no_change"}, status=200)
        else:
            raws_stout = inventory_search(purchase_order=purchase_no, product_order=product_order)
            for raw in raws_stout:
                data_list_stout.append({'product_order': raw['product_order'],
                                        'size': raw['size'],
                                        'qty': int(raw['qty']),
                                        'bin_id': raw['bin_id'],
                                        'purchase_no': raw['purchase_no'],
                                        'version_no': raw['version_no'],
                                        'version_seq': raw['version_seq'],
                                        'purchase_unit': raw['purchase_unit'],
                                        'customer_no': raw['customer_no'],
                                        'supplier': raw['supplier'],
                                        'lot_no': raw['lot_no'],
                                        'purchase_qty': raw['purchase_qty'],
                                        'item_type': raw['item_type'],
                                        'post_date': raw['post_date'],
                                        'sap_mtr_no': raw['sap_mtr_no'],
                                        'desc': raw['desc'],
                                        })

    return JsonResponse({
        "data_list_stout": data_list_stout
    }, safe=False)


def stockin_filter(raws):
    vnedc_db = vnedc_database()
    data_list = []
    for raw in raws:
        product_order = raw['VBELN']
        purchase_no = raw['EBELN']
        version_no = raw['ZZVERSION']
        version_seq = raw['ZZVERSION_SEQ']
        size = raw['ZSIZE']
        order_qty = raw['MENGE']

        sql2 = f"""
        SELECT sum(order_qty) order_qty FROM [VNWMS].[dbo].[warehouse_stockinform]
        WHERE product_order='{product_order}' and purchase_no='{purchase_no}'
        and version_no='{version_no}' and version_seq='{version_seq}' and size='{size}'
        """
        stocks = vnedc_db.select_sql_dict(sql2)

        if stocks[0]["order_qty"]:
            qty = int(order_qty) - stocks[0]["order_qty"]
        else:
            qty = int(order_qty)

        if qty > 0:
            data_list.append({'product_order': product_order, 'customer_no': '', 'version_no': version_no,
                              'version_seq': version_seq, 'lot_no': raw['LOTNO'], 'item_type': raw['WGBEZ'],
                              'purchase_no': purchase_no, 'purchase_qty': raw['MENGE_PO'],
                              'size': size, 'purchase_unit': raw['MEINS'], 'post_date': raw['BUDAT'],
                              'order_qty': qty, 'supplier': raw['LIFNR'], 'sap_mtr_no': raw['MBLNR']
                              })
    return data_list


def get_product_order_info(request):
    data_list = []
    if request.method == 'GET':
        product_order = request.GET.get('product_order')
        sap_db = sap_database()

        if product_order == '':
            return JsonResponse({"status": "no_change"}, status=200)
        else:
            sql = f"""
            SELECT VBELN, ZZVERSION, ZZVERSION_SEQ, LOTNO, WGBEZ, EBELN, MENGE_PO, ZSIZE, MEINS, BUDAT, MENGE, LIFNR,
            NAME1, MBLNR
            FROM [PMG_SAP].[dbo].[ZMMT4001] WHERE VBELN = '{product_order}'
            """

        raws = sap_db.select_sql_dict(sql)

        data_list = stockin_filter(raws)

    return JsonResponse(data_list, safe=False)


def get_purchase_no_info(request):
    data_list = []
    if request.method == 'GET':
        purchase_no = request.GET.get('purchase_no')
        db = sap_database()

        if purchase_no == '':
            return JsonResponse({"status": "no_change"}, status=200)
        else:
            sql = f"""
                    SELECT VBELN, ZZVERSION, ZZVERSION_SEQ, LOTNO, WGBEZ, EBELN, MENGE_PO, ZSIZE, MEINS, BUDAT, MENGE,
                    LIFNR, NAME1, MBLNR
                    FROM [PMG_SAP].[dbo].[ZMMT4001] WHERE EBELN = '{purchase_no}'
                    """

        raws = db.select_sql_dict(sql)

        data_list = stockin_filter(raws)

    return JsonResponse(data_list, safe=False)


def get_series_number(_key, _key_name):
    obj = Series.objects.filter(key=_key)
    if obj:
        _series = obj[0].series + 1
        obj.update(series=_series, desc=_key_name)
    else:
        _series = 1
        Series.objects.create(key=_key, series=1, desc=_key_name)
    return _series


@csrf_exempt
def packing_material_stock_in_post(request):

    if request.method == "POST":
        try:
            # 解析 JSON 資料
            data = json.loads(request.body)

            # STIN-202412310001
            YYYYMM = datetime.now().strftime("%Y%m")
            key = "STIN" + YYYYMM
            form_no = key + str(get_series_number(key, "STOCKIN")).zfill(3)

            mvt = MovementType.objects.get(mvt_code="STIN")

            for item in data:
                bin = Bin.objects.get(bin_id=item['order_bin'])

                if 'order_qty' in item and int(item['order_qty']) <= 0:
                    return JsonResponse(
                        {
                            "status": "fail",
                            "error": {
                                "field": "order_qty",
                                "message": _("The quantity must be a positive number!")
                            }

                        },
                        status=400
                    )

                if 'item_type' in item and item['item_type']:
                    try:
                        item_type = ItemType.objects.get(
                            Q(type_code=item['item_type']) |
                            Q(type_name=item['item_type']) |
                            Q(type_vn_name=item['item_type'])
                        )
                        item['item_type'] = item_type.type_code

                        stockin_form = StockInForm(
                            form_no=form_no,
                            product_order=item['product_order'],
                            customer_no=item['customer_no'],
                            version_no=item['version_no'],
                            version_seq=item['version_seq'],
                            lot_no=item['lot_no'],
                            item_type=item_type,
                            purchase_no=item['purchase_no'],
                            purchase_qty=int(float(item['purchase_qty'])),
                            size=item['size'],
                            purchase_unit=item['purchase_unit'],
                            post_date=item['post_date'],
                            order_qty=int(float(item['order_qty'])),
                            order_bin=bin,
                            supplier=item['supplier'],
                            sap_mtr_no=item['sap_mtr_no'],
                            desc=item['desc'],
                            create_at=timezone.now(),
                            create_by_id=request.user.id
                        )
                        stockin_form.save()

                        Do_Transaction(request,
                                       form_no,
                                       item['product_order'], item['purchase_no'], item['version_no'],
                                       item['version_seq'], item['size'], mvt, item['order_bin'], item['order_qty'],
                                       item['purchase_unit'], item['desc'], stockin_form=form_no)

                    except Exception as e:
                        raise ValueError(f"{e}")
                        print(e)

            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': _('Invalid request method')}, status=405)


# @transaction.atomic
# @login_required
def packing_material_stock_out(request):
    if request.method == 'POST':
        form = StockOutPForm(request.POST)
    else:
        form = StockOutPForm()
    return render(request, 'warehouse/packing_material_stock_out.html', {'form': form})


@csrf_exempt
def packing_material_stock_out_post(request):
    if request.method == "POST":
        try:
            # 解析 JSON 資料
            data = json.loads(request.body)

            # STIN-202412310001
            YYYYMM = datetime.now().strftime("%Y%m")
            key = "STOU" + YYYYMM
            form_no = key + str(get_series_number(key, "STOCKOUT")).zfill(3)

            mvt = MovementType.objects.get(mvt_code="STOU")

            for item in data:
                bin = Bin.objects.get(bin_id=item['bin_id'])
                comment = item['desc'] if 'desc' in item else ""

                try:
                    stockout_form = StockOutForm(
                        form_no=form_no,
                        product_order=item['product_order'],
                        version_no=item['version_no'],
                        version_seq=item['version_seq'],
                        purchase_no=item['purchase_no'],
                        size=item['size'],
                        purchase_unit=item['purchase_unit'],
                        order_bin=bin,
                        desc=comment,
                        create_at=timezone.now(),
                        create_by_id=request.user.id
                    )
                    stockout_form.save()

                    qty = int(item['qty']) * -1

                    result = Do_Transaction(request, form_no, item['product_order'],
                                            item['purchase_no'], item['version_no'], item['version_seq'],
                                            item['size'], mvt,
                                            item['bin_id'], qty, item['purchase_unit'], comment,
                                            stockout_form=form_no)

                except Exception as e:
                    raise ValueError(f"{e}")
                    print(e)

            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def product_order_search(request):
    product_order = request.GET.get('product_order')
    size = request.GET.get('size')

    if not product_order and not size:
        return JsonResponse({"status": "blank"}, status=200)

    request.session['search_results_url'] = request.get_full_path()

    if product_order or size:
        bin_values = Bin_Value.objects.select_related(
            'bin__area__warehouse'  # bin->area->warehouse
        ).filter(
            product_order__icontains=product_order,
            size__icontains=size,
        ).values(
            'bin__area__warehouse__wh_code',
            'product_order',
            'purchase_no',
            'version_no',
            'version_seq',
            'size',
            'bin',
            'qty'
        )

        data = list(bin_values)

        if not data:
            return JsonResponse({"status": "blank"}, status=200)

    return JsonResponse(data, safe=False)


def transfer_and_adjust(request):
    return render(request, 'warehouse/transfer_and_adjust.html')


def result_search(request):
    search_results_url = request.session.get('search_results_url', '/default-search-url/')
    return render(request, 'warehouse/bin_adjust_page.html', {'back_url': search_results_url})


# no use this
def bin_transfer(request):
    if request.GET:
        request.session['warehouse'] = request.GET.get('warehouse', '')
        request.session['product_order'] = request.GET.get('product_order', '')
        request.session['purchase_no'] = request.GET.get('purchase_no', '')
        request.session['version_no'] = request.GET.get('version_no', '')
        request.session['version_seq'] = request.GET.get('version_seq', '')
        request.session['size'] = request.GET.get('size', '')
        request.session['bin'] = request.GET.get('bin', '')
        request.session['qty'] = request.GET.get('qty', '')

        # Lấy dữ liệu từ session nếu không có GET request
    warehouse = request.session.get('warehouse', '')
    product_order = request.session.get('product_order', '')
    purchase_no = request.session.get('purchase_no', '')
    version_no = request.session.get('version_no', '')
    version_seq = request.session.get('version_seq', '')
    size = request.session.get('size', '')
    bin = request.session.get('bin', '')
    qty = request.session.get('qty', '')

    item_data = {
        'bin__area__warehouse__wh_code': warehouse,
        'product_order': product_order,
        'purchase_no': purchase_no,
        'version_no': version_no,
        'version_seq': version_seq,
        'size': size,
        'bin': bin,
        'qty': qty
    }

    return JsonResponse(item_data, safe=False)


# When click 'Transfer' button, execute this one
def bin_transfer_page(request):

    if request.GET:
        request.session['warehouse'] = request.GET.get('warehouse', '')
        request.session['product_order'] = request.GET.get('product_order', '')
        request.session['purchase_no'] = request.GET.get('purchase_no', '')
        request.session['version_no'] = request.GET.get('version_no', '')
        request.session['version_seq'] = request.GET.get('version_seq', '')
        request.session['size'] = request.GET.get('size', '')
        request.session['bin'] = request.GET.get('bin', '')
        request.session['qty'] = request.GET.get('qty', '')
        request.session['purchase_unit'] = request.GET.get('purchase_unit', '')

        # Lấy dữ liệu từ session nếu không có GET request
    warehouse = request.session.get('warehouse', '')
    product_order = request.session.get('product_order', '')
    purchase_no = request.session.get('purchase_no', '')
    version_no = request.session.get('version_no', '')
    version_seq = request.session.get('version_seq', '')
    size = request.session.get('size', '')
    bin = request.session.get('bin', '')
    qty = request.session.get('qty', '')
    purchase_unit = request.session.get('purchase_unit', '')

    mvt = MovementType.objects.get(mvt_code="TRNS")

    YYYYMM = datetime.now().strftime("%Y%m")
    key = "TRNS" + YYYYMM
    form_no = key + str(get_series_number(key, "TRANSFER")).zfill(3)

    if request.method == 'POST':
        form = BinTransferForm(request.POST)
        if form.is_valid():
            bin_selected = form.cleaned_data['bin']
            qty = form.cleaned_data['qty']

            Do_Transaction(request, form_no, product_order, purchase_no, version_no, version_seq, size, mvt,
                           bin_selected, qty, purchase_unit, desc=None)
            Do_Transaction(request, form_no, product_order, purchase_no, version_no, version_seq, size, mvt,
                           bin, -qty, purchase_unit, desc=None)

            item_data = {
                'bin__area__warehouse__wh_code': warehouse,
                'product_order': product_order,
                'purchase_no': purchase_no,
                'version_no': version_no,
                'version_seq': version_seq,
                'size': size,
                'bin': bin,
                'qty': qty
            }
            return render(request, 'warehouse/transfer_and_adjust.html', locals())
    form = BinTransferForm()

    return render(request, 'warehouse/bin/bin_transfer.html', locals())
    # return JsonResponse(item_data, safe=False)


def bin_adjust(request):
    if request.GET:
        request.session['warehouse'] = request.GET.get('warehouse', '')
        request.session['product_order'] = request.GET.get('product_order', '')
        request.session['purchase_no'] = request.GET.get('purchase_no', '')
        request.session['version_no'] = request.GET.get('version_no', '')
        request.session['version_seq'] = request.GET.get('version_seq', '')
        request.session['size'] = request.GET.get('size', '')
        request.session['bin'] = request.GET.get('bin', '')
        request.session['qty'] = request.GET.get('qty', '')

        # Lấy dữ liệu từ session nếu không có GET request
    warehouse = request.session.get('warehouse', '')
    product_order = request.session.get('product_order', '')
    purchase_no = request.session.get('purchase_no', '')
    version_no = request.session.get('version_no', '')
    version_seq = request.session.get('version_seq', '')
    size = request.session.get('size', '')
    bin = request.session.get('bin', '')
    qty = request.session.get('qty', '')

    item_data = {
        'bin__area__warehouse__wh_code': warehouse,
        'product_order': product_order,
        'purchase_no': purchase_no,
        'version_no': version_no,
        'version_seq': version_seq,
        'size': size,
        'bin': bin,
        'qty': qty
    }

    return JsonResponse(item_data, safe=False)


# When click 'Transfer' button, execute this one
def bin_adjust_page(request):

    if request.GET:
        request.session['warehouse'] = request.GET.get('warehouse', '')
        request.session['product_order'] = request.GET.get('product_order', '')
        request.session['purchase_no'] = request.GET.get('purchase_no', '')
        request.session['version_no'] = request.GET.get('version_no', '')
        request.session['version_seq'] = request.GET.get('version_seq', '')
        request.session['size'] = request.GET.get('size', '')
        request.session['bin'] = request.GET.get('bin', '')
        request.session['qty'] = request.GET.get('qty', '')
        request.session['purchase_unit'] = request.GET.get('purchase_unit', '')

        # Lấy dữ liệu từ session nếu không có GET request
    warehouse = request.session.get('warehouse', '')
    product_order = request.session.get('product_order', '')
    purchase_no = request.session.get('purchase_no', '')
    version_no = request.session.get('version_no', '')
    version_seq = request.session.get('version_seq', '')
    size = request.session.get('size', '')
    bin = request.session.get('bin', '')
    qty = request.session.get('qty', '')
    purchase_unit = request.session.get('purchase_unit', '')

    mvt = MovementType.objects.get(mvt_code="ADJS")

    YYYYMM = datetime.now().strftime("%Y%m")
    key = "ADJS" + YYYYMM
    form_no = key + str(get_series_number(key, "ADJUST")).zfill(3)

    if request.method == 'POST':
        form = QuantityAdjustForm(request.POST)
        if form.is_valid():
            qty = int(form.cleaned_data['qty']) - int(qty)

            Do_Transaction(request, form_no, product_order, purchase_no, version_no, version_seq, size, mvt,
                           bin, qty, purchase_unit, desc=None)

            item_data = {
                'bin__area__warehouse__wh_code': warehouse,
                'product_order': product_order,
                'purchase_no': purchase_no,
                'version_no': version_no,
                'version_seq': version_seq,
                'size': size,
                'bin': bin,
                'qty': qty
            }
            return render(request, 'warehouse/transfer_and_adjust.html', locals())
    form = QuantityAdjustForm()

    return render(request, 'warehouse/bin/bin_adjust.html', locals())


def product_order_hist_data(request):
    product_order = request.GET.get('product_order')
    bin_id = request.GET.get('bin_id')
    size = request.GET.get('size')
    comment = request.GET.get('comment')

    if not (product_order or bin_id or size or comment):
        return JsonResponse({"status": "blank"}, status=200)

    current_language = get_language()
    if current_language == "zh-hant":
        _mvt = 'mvt__desc'
    elif current_language == "vi":
        _mvt = 'mvt__mvt_vn_name'
    else:
        _mvt = 'mvt_id'

    bin_values = Bin_Value_History.objects.filter(
        (Q(product_order__icontains=product_order) if product_order else Q()) &
        (Q(bin__bin_id__icontains=bin_id) if bin_id else Q()) &
        (Q(size__icontains=size) if size else Q()) &
        (Q(comment__icontains=comment) if comment else Q())
    ).values(
        'product_order',
        'purchase_no',
        'version_no',
        'version_seq',
        'size',
        'comment',
        _mvt,
        'bin_id',
        'plus_qty',
        'minus_qty',
        'remain_qty',
        'create_at',
        'create_by__username'
    )

    data = [
        {
            "product_order": item["product_order"],
            "purchase_no": item["purchase_no"],
            "version_no": item["version_no"],
            "version_seq": item["version_seq"],
            "size": item["size"],
            "comment": item["comment"],
            "mvt_id": item[_mvt],
            "bin_id": item["bin_id"],
            "plus_qty": intcomma(item["plus_qty"]),
            "minus_qty": intcomma(item["minus_qty"]),
            "remain_qty": intcomma(item["remain_qty"]),
            "create_at": item["create_at"].strftime("%d/%m/%Y %H:%M") if isinstance(item["create_at"], datetime) else
            item["create_at"],
            "create_by__username": item["create_by__username"]
        }
        for item in bin_values
    ]

    if not data:
        return JsonResponse({"status": "blank"}, status=200)

    return JsonResponse(data, safe=False)


def product_order_bin_search(request):
    return render(request, 'warehouse/product_order_bin_search.html')


def upload_excel(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["file"]
            df_dict = pd.read_excel(excel_file, sheet_name=None)  # Đọc tất cả các sheet

            for sheet_name, df in df_dict.items():
                # Warehouse (Sheet Warehouse)
                if sheet_name == "Warehouse":
                    warehouse_codes = df["Warehouse Code"].unique()
                    warehouse_dict = {w.wh_code: w for w in Warehouse.objects.filter(wh_code__in=warehouse_codes)}

                    warehouses_to_update = []
                    warehouses_to_create = []

                    for _, row in df.iterrows():
                        wh_code = row["Warehouse Code"]
                        wh_name = to_string_or_none(row["Warehouse"])
                        wh_plant = to_string_or_none(row["Plant"])
                        wh_comment = to_string_or_none(row["Warehouse comment"])

                        if wh_code in warehouse_dict:
                            obj = warehouse_dict[wh_code]
                            if obj.wh_name != wh_name or obj.wh_comment != wh_comment or obj.wh_plant != wh_plant:
                                obj.wh_name = wh_name
                                obj.wh_plant = wh_plant
                                obj.wh_comment = wh_comment
                                obj.update_at = timezone.now()
                                obj.update_by = request.user
                                warehouses_to_update.append(obj)
                        else:
                            warehouses_to_create.append(Warehouse(
                                wh_code=wh_code,
                                wh_name=wh_name,
                                wh_plant=wh_plant,
                                wh_comment=wh_comment,
                                create_at=timezone.now(),
                                create_by=request.user,
                                update_at=timezone.now(),
                                update_by=request.user
                            ))

                    # Dùng transaction để đảm bảo tính toàn vẹn
                    with transaction.atomic():
                        if warehouses_to_update:
                            Warehouse.objects.bulk_update(warehouses_to_update,
                                                          ["wh_name", "wh_comment", "wh_plant", "update_at", "update_by"])
                        if warehouses_to_create:
                            Warehouse.objects.bulk_create(warehouses_to_create)

                # Area (Sheet Area)
                if sheet_name == "Area":
                    warehouse_codes = df["Warehouse Code"].unique()
                    warehouses = {w.wh_code: w for w in Warehouse.objects.filter(wh_code__in=warehouse_codes)}

                    area_ids = df["Area Id"].unique()
                    existing_areas = {a.area_id: a for a in Area.objects.filter(area_id__in=area_ids)}

                    areas_to_update = []
                    areas_to_create = []

                    for _, row in df.iterrows():
                        area_id = row["Area Id"]
                        area_name = to_string_or_none(row["Area Name"])
                        warehouse_instance = warehouses.get(row["Warehouse Code"])  # Lấy warehouse từ cache
                        pos_x = row["Position X"]
                        pos_y = row["Position Y"]
                        area_l = row["Area Length"]
                        area_w = row["Area Width"]
                        if area_id in existing_areas:
                            obj = existing_areas[area_id]
                            if obj.warehouse != warehouse_instance or obj.area_name != area_name or obj.area_l != area_l or \
                                        obj.area_w != area_w or obj.pos_x != pos_x or obj.pos_y != pos_y:
                                obj.warehouse = warehouse_instance
                                obj.area_name = area_name
                                obj.update_at = timezone.now()
                                obj.update_by = request.user
                                areas_to_update.append(obj)
                        else:
                            areas_to_create.append(Area(
                                area_id=area_id,
                                warehouse=warehouse_instance,
                                area_name=area_name,
                                area_w=area_w,
                                area_l=area_w,
                                pos_x=pos_x,
                                pos_y=pos_y,
                                create_at=timezone.now(),
                                create_by=request.user,
                                update_at=timezone.now(),
                                update_by=request.user
                            ))

                    with transaction.atomic():
                        if areas_to_update:
                            Area.objects.bulk_update(areas_to_update,
                                                     ["warehouse", "area_name", "area_w", "area_l", "pos_x",
                                                      "pos_y", "update_at", "update_by"])
                        if areas_to_create:
                            Area.objects.bulk_create(areas_to_create)

                # Bin (Sheet Location)
                if sheet_name == "Location":
                    with transaction.atomic():  # 🔹 Đảm bảo tính toàn vẹn dữ liệu

                        # 🔹 Tạo mapping warehouse và area để giảm số lượng truy vấn
                        warehouse_map = {
                            w.wh_code: w for w in Warehouse.objects.filter(wh_code__in=df["Warehouse"])
                        }

                        area_map = {
                            a.area_id: a for a in Area.objects.filter(area_id__in=df["Area"])
                        }

                        existing_bins = {
                            b.bin_id: b for b in Bin.objects.filter(bin_id__in=df["Bin Id"])
                        }

                        bin_instances = []  # Lưu danh sách để bulk_create

                        for _, row in df.iterrows():
                            warehouse_instance = warehouse_map.get(row["Warehouse"])
                            if not warehouse_instance:
                                continue  # 🔹 Bỏ qua nếu Warehouse không tồn tại

                            area_instance = area_map.get(row["Area"])
                            if not area_instance:
                                continue  # 🔹 Bỏ qua nếu Area không tồn tại

                            bin_id = row["Bin Id"]
                            bin_name = to_string_or_none(row["Bin Name"])
                            bin_w = to_int_or_none(row["bin_w"])
                            bin_l = to_int_or_none(row["bin_l"])
                            pos_x = to_int_or_none(row["pos_x"])
                            pos_y = to_int_or_none(row["pos_y"])

                            if bin_id in existing_bins:
                                obj = existing_bins[bin_id]
                                if obj.bin_name != bin_name or obj.area != area_instance or obj.bin_l != bin_l or \
                                        obj.bin_w != bin_w or obj.pos_x != pos_x or obj.pos_y != pos_y:
                                    obj.bin_name = bin_name
                                    obj.area = area_instance
                                    obj.bin_l = bin_l
                                    obj.bin_w = bin_w
                                    obj.pos_x = pos_x
                                    obj.pos_y = pos_y
                                    obj.update_at = timezone.now()
                                    obj.update_by = request.user
                                    obj.save(update_fields=["bin_name", "area", "bin_l", "bin_w", "pos_x", "pos_y",
                                                            "update_at", "update_by"])
                            else:
                                bin_instances.append(Bin(
                                    bin_id=bin_id,
                                    bin_name=bin_name,
                                    area=area_instance,
                                    bin_w=bin_w,
                                    bin_l=bin_l,
                                    pos_x=pos_x,
                                    pos_y=pos_y,
                                    create_at=timezone.now(),
                                    create_by=request.user,
                                    update_at=timezone.now(),
                                    update_by=request.user,
                                ))

                        if bin_instances:
                            Bin.objects.bulk_create(bin_instances)  # 🔹 Chèn nhiều dòng một lần

            return render(request, "warehouse/upload.html", {"form": form, "message": "Upload successfully!"})

    else:
        form = ExcelUploadForm()

    return render(request, "warehouse/upload.html", locals())


def to_int_or_none(value):
    """Chuyển đổi giá trị thành int nếu không phải NaN, ngược lại trả về None"""
    return int(value) if pd.notna(value) else None


def to_string_or_none(value):
    return "" if pd.isna(value) else value


def open_data_import(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():

            excel_file = request.FILES["file"]
            df = pd.read_excel(excel_file, dtype=str)  # Đọc tất cả các sheet, ép kiểu về str
            df.fillna("", inplace=True) # 避免 NaN 值

            valid_bins = set(Bin.objects.values_list("bin_name", flat=True))

            valid_data = df[df["Location"].isin(valid_bins)]
            invalid_data = df[~df["Location"].isin(valid_bins)]

            valid_records = valid_data.to_dict(orient="records")
            invalid_records = invalid_data.to_dict(orient="records")

            for row in valid_records:
                print(row['Location'])

            request.session["valid_data"] = valid_records
            request.session["invalid_data"] = invalid_records

            return render(request, "warehouse/bin/open_data_import.html", locals())
    else:
        form = ExcelUploadForm()

    return render(request, "warehouse/bin/open_data_import.html", {"form": form})


def open_data_import_api(request):
    if request.method == "POST" and request.FILES.get("file"):
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():

            excel_file = request.FILES["file"]
            df = pd.read_excel(excel_file, dtype=str)  # Đọc tất cả các sheet, ép kiểu về str
            df.fillna("", inplace=True) # 避免 NaN 值
            df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce")
            df = df.groupby(["CustomerName", "ProductOrder", "PackingVersion",
                                     "Lot", "ItemType", "Size", "StockInDate", "Location",
                                     "Supplier", "PurchaseOrder", "TransactionNo"], as_index=False)["Qty"].sum()

            valid_bins = set(Bin.objects.values_list("bin_name", flat=True))
            valid_types = set(ItemType.objects.values_list("type_name", flat=True))

            valid_data = df[df["Location"].isin(valid_bins) & df["ItemType"].isin(valid_types)]

            # 找出 Location 和 Type 同時錯誤的資料
            invalid_data = df[~df.index.isin(valid_data.index)]  # 這裡包含所有不符合條件的資料

            valid_records = valid_data.to_dict(orient="records")
            invalid_records = invalid_data.to_dict(orient="records")

            request.session["valid_data"] = valid_data.to_dict(orient="records")
            request.session["excel_file"] = excel_file

            return JsonResponse({
                "valid_data": valid_records,
                "invalid_data": invalid_records
            })

    return JsonResponse({"error": "Invalid request"}, status=400)

def open_data_import_confirm_api(request):
    if request.method == "POST":
        try:
            valid_data = request.session.get("valid_data", [])
            excel_file = request.session.get("excel_file", "")

            if not valid_data:
                return JsonResponse({"error": "沒有可匯入的數據"}, status=400)

            with transaction.atomic():

                Bin_Value_History.objects.all().delete()
                Bin_Value.objects.all().delete()
                StockInForm.objects.all().delete()
                StockOutForm.objects.all().delete()

                YYYYMM = datetime.now().strftime("%Y%m")
                key = "OPEN" + YYYYMM
                form_no = key + str(get_series_number(key, "OPEN")).zfill(3)

                mvt = MovementType.objects.get(mvt_code="OPEN")

                for row in valid_data:
                    productOrder = row['ProductOrder']
                    purchaseOrder = row['PurchaseOrder']
                    packingVersion = row['PackingVersion']
                    packingSeq = ""
                    size = row['Size']
                    location = row['Location']
                    supplier = row['Supplier']
                    customer = row['CustomerName']
                    stockInDate = row['StockInDate']
                    qty = row['Qty']
                    transactionNo = row['TransactionNo']
                    lot_no = row['Lot']
                    unit = ""
                    item_type = ItemType.objects.get(type_name=row['ItemType'])
                    location = Bin.objects.get(bin_id=location)

                    stockin_form = StockInForm(
                        form_no=form_no,
                        product_order=productOrder,
                        customer_no=customer,
                        version_no=packingVersion,
                        version_seq=packingSeq,
                        lot_no=lot_no,
                        item_type=item_type,
                        purchase_no=purchaseOrder,
                        size=size,
                        post_date=stockInDate,
                        order_qty=qty,
                        order_bin=location,
                        supplier=supplier,
                        sap_mtr_no=transactionNo,
                        create_at=timezone.now(),
                        create_by_id=request.user.id
                    )
                    stockin_form.save()

                    Do_Transaction(request, form_no, productOrder, purchaseOrder,
                                   packingVersion, packingSeq, size, mvt, location.bin_id,
                                   qty, unit, desc="", stockin_form=form_no)

                # if hasattr(excel_file, 'temporary_file_path'):
                #     os.remove(excel_file.temporary_file_path())

                del request.session["valid_data"]
                del request.session["excel_file"]

                return JsonResponse({"message": "成功匯入 {} 筆資料".format(len(valid_data))})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "請使用 POST 方法"}, status=400)

def open_data_import1(request):
    form = ExcelUploadForm()

    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():

            excel_file = request.FILES["file"]
            df_dict = pd.read_excel(excel_file, sheet_name=None, dtype=str)  # Đọc tất cả các sheet, ép kiểu về str

            sheet_name, df = next(iter(df_dict.items()))
            # Chuẩn hóa dữ liệu về chuỗi, loại bỏ khoảng trắng
            df["Product Order"] = df["Product Order"].astype(str).str.strip()
            df["Purchase Order"] = df["Purchase Order"].astype(str).str.strip()
            df["Version No"] = df["Version No"].astype(str).str.strip()
            df["Version Seq"] = df["Version Seq"].astype(str).str.strip()
            df["Location"] = df["Location"].astype(str).str.strip()
            df["Unit"] = df["Unit"].astype(str).str.strip()
            df["Size"] = df["Size"].astype(str).str.strip()

            # Chuyển Qty về số nguyên, giữ 0 nếu không hợp lệ
            df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce").fillna(0).astype(int)

            locations = list(df["Location"].dropna().unique())

            # Lấy danh sách bin_id hợp lệ từ database
            bin_map = {b.bin_id: b for b in Bin.objects.filter(bin_id__in=locations)}

            error = ""
            try:
                for _, row in df.iterrows():
                    bin_id = bin_map[row["Location"]]
            except Exception as e:
                error = f"<tr><td>{bin_id}</td><td>Not Exist</td></tr>"

            if len(error) > 0:
                error_msg = "<table>{error}</table>".format(error=error)
                return render(request, "warehouse/bin/open_data_import.html", locals())
            else:
                Bin_Value.objects.all().delete()

                YYYYMM = datetime.now().strftime("%Y%m")
                key = "OPEN" + YYYYMM
                form_no = key + str(get_series_number(key, "OPEN")).zfill(3)

                mvt = MovementType.objects.get(mvt_code="OPEN")

                for _, row in df.iterrows():
                    bin_id = row["Location"]

                    Do_Transaction(request, form_no, row["Product Order"], row['Purchase Order'],
                                   row["Version No"], row["Version Seq"], row["Size"], mvt, bin_map[bin_id],
                                   row["Qty"], row["Unit"], desc="")

                if hasattr(excel_file, 'temporary_file_path'):
                    os.remove(excel_file.temporary_file_path())

                return render(request, "warehouse/bin/open_data_import.html",
                              {"form": form, "message": "Upload successfully!"})

    return render(request, "warehouse/bin/open_data_import.html", {"form": form})


def inventory_sheet(request):
    form = BinValueSearchForm(request.GET)
    results = []
    warehouses = Warehouse.objects.filter(wh_plant=request.user.plant)
    return render(request, 'warehouse/bin/search_bin_value.html',
                  {'form': form, 'results': results, 'warehouses': warehouses})


def inventory_deletion(request):
    form = BinValueDeleteForm(request.GET)
    results = []
    warehouses = Warehouse.objects.filter(wh_plant=request.user.plant)

    if form.is_valid():
        bin_id = form.cleaned_data.get('bin')
        if bin_id:
            results = Bin_Value.objects.filter(bin__bin_id=bin_id)

    return render(request, 'warehouse/bin/delete_bin_value.html',
                  {'form': form, 'results': results, 'warehouses': warehouses})


@csrf_exempt
def delete_inventory(request):
    if request.method == "POST":
        try:

            data = json.loads(request.body)  # Đọc dữ liệu từ AJAX
            ids_to_delete = data.get("ids", [])

            YYYYMM = datetime.now().strftime("%Y%m")

            key = "DELT" + YYYYMM

            form_no = key + str(get_series_number(key, "DELT")).zfill(3)

            mvt = MovementType.objects.get(mvt_code="DELT")

            for row in data["list_data"]:
                test = row['qty']
                qty = int(row['qty']) * -1

                Do_Transaction(request, form_no, row['productOrder'], row['purchaseNo'],
                               row['versionNo'], row['versionSeq'], row['size'],
                               mvt, row['binId'], qty, row['purchaseUnit'], desc="")

            if not ids_to_delete:
                return JsonResponse({"success": False, "error": "Không có dữ liệu để xóa!"})

            # Xóa các bản ghi có ID trong danh sách
            deleted_count, _ = Bin_Value.objects.filter(id__in=ids_to_delete).delete()

            return JsonResponse({"success": True, "deleted_count": deleted_count})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Phương thức không hợp lệ!"})


# GET DATA
def get_areas(request):
    warehouse_id = request.GET.get('warehouse')
    areas = Area.objects.filter(warehouse_id=warehouse_id).values('area_id', 'area_name')
    return JsonResponse(list(areas), safe=False)


def get_all_areas(request):
    areas = Area.objects.all().values('area_id', 'area_name', 'pos_y', 'pos_x', 'area_l', 'area_w', 'layer')
    return JsonResponse(list(areas), safe=False)


def get_bins(request):
    area_id = request.GET.get('area')
    bins = Bin.objects.filter(area_id=area_id).values('bin_id', 'bin_name')
    return JsonResponse(list(bins), safe=False)


def check_bin_exists(request):
    area_id = request.GET.get('area')
    bins = Bin.objects.filter(area_id=area_id).values('bin_id', 'bin_name').order_by('create_at')

    bin_data = []

    data_list = list(Bin_Value.objects.values_list("bin__bin_id", flat=True))

    for bin in bins:

        status = "red" if bin['bin_id'] in data_list else "green"  # Nếu tồn tại giá trị thì đỏ, ngược lại xanh

        bin_data.append({
            "bin_id": bin["bin_id"],
            "bin_name": bin["bin_name"],
            "status": status
        })

    return JsonResponse(bin_data, safe=False)


def get_bin_data(request):
    warehouse_id = request.GET.get("warehouse")
    area_id = request.GET.get("area")
    bin_id = request.GET.get("bin")
    po_id = request.GET.get("po")

    if warehouse_id or area_id or bin_id or po_id:

        products = inventory_search(warehouse=warehouse_id, area=area_id, location=bin_id, product_order=po_id)

        return JsonResponse(list(products), safe=False)

    return JsonResponse([], safe=False)

# -- END DATA --


def download_excel_template(request, filename):
    file_path = os.path.join(settings.BASE_DIR, 'static/excel', filename)

    if not os.path.exists(file_path):
        raise Http404("File not exist")

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)


# def export_excel(request):
#     # Xác định ngôn ngữ hiện tại
#     language = request.LANGUAGE_CODE  # Lấy ngôn ngữ hiện tại từ Django
#
#     # Định nghĩa tiêu đề cột theo ngôn ngữ
#     columns = {
#         "product_order": _("Product Order"),
#         "purchase_no": _("Purchase Order"),
#         "version_no": _("Version No"),
#         "version_seq": _("Version Seq"),
#         "size": _("Size"),
#         "location": _("Location"),
#         "qty": _("Qty"),
#         "unit": _("Unit"),
#
#     }
#
#     # Chuyển đổi sang DataFrame
#     df = pd.DataFrame(columns=columns.values())
#
#     # Đổi tiêu đề cột theo ngôn ngữ
#     df.rename(columns=columns, inplace=True)
#
#     # Tạo response với file Excel
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = f'attachment; filename="data_{language}.xlsx"'
#
#     with pd.ExcelWriter(response, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name="Sheet1")
#
#
#         # Lấy workbook và sheet hiện tại
#         workbook = writer.book
#         sheet = workbook.active
#
#         # Thiết lập độ rộng cột
#         column_widths = {
#             "A": 20,  # Product Order
#             "B": 25,  # Purchase Order
#             "C": 15,  # Version No
#             "D": 15,  # Version Seq
#             "E": 10,  # Size
#             "F": 20,  # Location
#             "G": 10,  # Qty
#             "H": 20,  # Unit
#         }
#
#         for col, width in column_widths.items():
#             sheet.column_dimensions[col].width = width
#
#     return response