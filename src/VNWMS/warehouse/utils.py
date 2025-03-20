from datetime import datetime
import uuid
from django.utils.translation import get_language

from VNWMS.database import vnedc_database
from warehouse.models import MovementType, Bin, Bin_Value, Bin_Value_History


def get_item_type_name():
    language = get_language()
    if language == 'zh-hant':
        item_type_column = "type_name"
    elif language == 'zh-hans':
        item_type_column = "type_name"
    elif language == 'vi':
        item_type_column = "type_vn_name"
    else:
        item_type_column = "type_code"
    return item_type_column

def Do_Transaction(request, form_no, product_order, purchase_no, version_no, version_seq, size, mvt, bin_code, qty,
                   purchase_unit, desc, stockin_form=None, stockout_form=None):
    try:
        qty = float(qty)
        bin = Bin.objects.get(bin_id=bin_code)
        mvt = MovementType.objects.get(mvt_code=mvt)
        if bin and product_order and purchase_no:
            # 更新庫存資料
            invs = Bin_Value.objects.filter(product_order=product_order, purchase_no=purchase_no, version_no=version_no,
                                            version_seq=version_seq, size=size, bin=bin)
            if invs:
                remain_qty = int(invs.first().qty) + qty
            else:
                remain_qty = qty

            if remain_qty >= 0:
                if remain_qty == 0:
                    Bin_Value.objects.filter(product_order=product_order, purchase_no=purchase_no,
                                                       version_no=version_no,
                                                       version_seq=version_seq, size=size, bin=bin).delete()
                else:
                    tmp1 = {}
                    if stockin_form:
                        tmp1 = {'stockin_form': stockin_form}
                    if stockout_form:
                        tmp1 = {'stockout_form': stockout_form}

                    tmp = {'qty': remain_qty, 'purchase_unit': purchase_unit,
                             'update_by': request.user,
                             }
                    tmp.update(tmp1)
                    Bin_Value.objects.update_or_create(product_order=product_order, purchase_no=purchase_no,
                                                       version_no=version_no,
                                                       version_seq=version_seq, size=size, bin=bin,
                                                       defaults=tmp)

                if qty > 0:
                    Bin_Value_History.objects.create(batch_no=form_no, product_order=product_order,
                                                     purchase_no=purchase_no, version_no=version_no,
                                                     version_seq=version_seq, size=size, bin=bin, mvt=mvt, plus_qty=qty,
                                                     minus_qty=0, remain_qty=remain_qty, comment=desc,
                                                     purchase_unit=purchase_unit,
                                                     create_by=request.user)
                else:
                    Bin_Value_History.objects.create(batch_no=form_no, product_order=product_order,
                                                     purchase_no=purchase_no, version_no=version_no,
                                                     version_seq=version_seq, size=size, bin=bin, mvt=mvt, plus_qty=0,
                                                     minus_qty=-qty, remain_qty=remain_qty,
                                                     purchase_unit=purchase_unit,
                                                     comment=desc, create_by=request.user)
                result = "DONE"
            else:
                msg = '無庫存可以扣帳'
                print(msg)
                raise ValueError(msg)
    except Exception as e:
        print(e)
        result = "ERROR"
    return result

def transfer_stock(product_order, purchase_no, version_no, version_seq, size, bin_code_from, bin_code_to, warehouse, qty):
    try:
        # Bước 1: Kiểm tra số lượng trong kho xuất
        bin_from = Bin_Value.objects.get(product_order=product_order, purchase_no=purchase_no, version_no=version_no,
                                         version_seq=version_seq, size=size, bin_id=bin_code_from,
                                         bin__area__warehouse__wh_code=warehouse)
        bin_to = Bin_Value.objects.get(bin_id=bin_code_to, bin__area__warehouse__wh_code=warehouse,
                                       product_order=product_order, purchase_no=purchase_no, version_no=version_no,
                                       version_seq=version_seq, size=size,)

        # Lấy thông tin sản phẩm trong kho xuất
        inv_from = Bin_Value.objects.filter(
            product_order=product_order,
            purchase_no=purchase_no,
            version_no=version_no,
            version_seq=version_seq,
            size=size,
            bin_id=bin_from.bin_id
        ).first()
        print(inv_from)

        if not inv_from or inv_from.qty < qty:
            raise ValueError("Không đủ số lượng trong kho xuất.")

        # Bước 2: Cập nhật số lượng trong kho xuất (giảm số lượng)
        inv_from.qty -= qty
        inv_from.save()

        # Bước 3: Kiểm tra và cập nhật số lượng trong kho đích
        inv_to = Bin_Value.objects.filter(
            product_order=product_order,
            purchase_no=purchase_no,
            version_no=version_no,
            version_seq=version_seq,
            size=size,
            bin=bin_to.bin_id
        ).first()

        if inv_to:
            # Nếu kho đích đã có sản phẩm, cập nhật số lượng
            inv_to.qty += qty
        else:
            # Nếu kho đích chưa có sản phẩm, tạo mới
            inv_to = Bin_Value(
                product_order=product_order,
                purchase_no=purchase_no,
                version_no=version_no,
                version_seq=version_seq,
                size=size,
                bin=bin_to,
                qty=qty,
                status="IN_TRANSIT"  # Ví dụ trạng thái trong quá trình chuyển
            )
        inv_to.save()

        return {"success": True, "message": "Chuyển hàng thành công."}

    except Exception as e:
        return {"success": False, "message": str(e)}

def inventory_search(warehouse=None, area=None, location=None, product_order=None, purchase_order=None, size=None):
    db = vnedc_database()

    item_type_name = get_item_type_name()

    sql = f"""
                SELECT b.product_order
                      ,b.size
                      ,b.qty
                      ,b.bin_id
                      ,b.purchase_no
                      ,b.version_no
                      ,b.version_seq
                      ,b.purchase_unit
                      ,customer_no
                      ,supplier
                      ,lot_no
                      ,purchase_qty
                      ,b.purchase_unit
                      ,{item_type_name} item_type
                      ,post_date
                      ,sap_mtr_no
    				  ,d.[desc]
                FROM [VNWMS].[dbo].[warehouse_bin_value] b
                JOIN [VNWMS].[dbo].[warehouse_bin] bin on b.bin_id = bin.bin_id
				JOIN [VNWMS].[dbo].[warehouse_area] area on bin.area_id = area.area_id
                LEFT JOIN [VNWMS].[dbo].[warehouse_stockinform] d on b.stockin_form = d.form_no
				and b.product_order = d.product_order and b.purchase_no = d.purchase_no and b.version_no = d.version_no
    						and b.size = d.size
				JOIN [VNWMS].[dbo].[warehouse_itemtype] item on d.item_type_id = item.type_code
                WHERE qty > 0
                """

    if product_order:
        sql += f" AND b.product_order = '{product_order}'"

    if purchase_order:
        sql += f" AND b.purchase_no = '{purchase_order}'"

    if warehouse:
        sql += f" AND area.warehouse_id = '{warehouse}'"

    if area:
        sql += f" AND area.area_id = '{area}'"

    if location:
        sql += f" AND bin.bin_id = '{location}'"

    if size:
        sql += f" AND b.size = '{size}'"

    results = db.select_sql_dict(sql)

    return results

def inventory_history(location=None, product_order=None, purchase_order=None, size=None, from_date=None, to_date=None):
    bin_hists = Bin_Value_History.objects.filter()

    if location:
        bin_hists = bin_hists.filter(bin__bin_id=location)  # Lọc chính xác mã `bin`
    if product_order:
        bin_hists = bin_hists.filter(product_order=product_order)
    if purchase_order:
        bin_hists = bin_hists.filter(purchase_no=purchase_order)
    if size:
        bin_hists = bin_hists.filter(size=size)
    if from_date:
        start_datetime = datetime.combine(from_date, datetime.min.time())  # Đầu ngày (00:00:00)
        bin_hists = bin_hists.filter(create_at__gte=start_datetime)
    if to_date:
        end_datetime = datetime.combine(to_date, datetime.max.time())
        bin_hists = bin_hists.filter(create_at__lte=end_datetime)

    return bin_hists












