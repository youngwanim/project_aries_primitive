message_map_eng = dict()
message_map_chn = dict()

# RECEIPT ERROR CODE
message_map_eng[1201] = 'Receipt can be saved within 5 items'
message_map_chn[1201] = 'Receipt can be saved within 5 items (chn)'

# LOGIN ERROR CODE
message_map_eng[1016] = 'An authentication information is not enough'
message_map_chn[1016] = 'An authentication information is not enough (chn)'

message_map_eng[3007] = ' Selected delivery time slot is closed now. Please check and place your order again.'
message_map_chn[3007] = '您选择的配送时间段已结束。请再确认后再次下单'
message_map_eng[3015] = 'Lunch time is over now. Please check and place your order again.'
message_map_chn[3015] = '午餐时间已结束，请确认后再次下单。'

message_map_eng[4004] = 'Payment request failed. Please try again later.'
message_map_chn[4004] = '付款请求失败，请稍后再试。'

# PURCHASE ORDER ERROR CODE
message_map_eng[3001] = 'There has been a change in the stock numbers. ' \
                        'Please check the stock status from the shopping bag and place your order again.'
message_map_chn[3001] = '由于库存数有变化，下单前请再次查看购物袋的库存状态。'
message_map_eng[3002] = 'ERROR_3002_PURCHASE_ORDER_NOT_FOUND'
message_map_chn[3002] = 'ERROR_3002_PURCHASE_ORDER_NOT_FOUND'
message_map_eng[3003] = 'ERROR_3003_USER_ADDRESS_INVALID'
message_map_chn[3003] = 'ERROR_3003_USER_ADDRESS_INVALID'
message_map_eng[3004] = 'ERROR_3004_COUPON_OWNER_NOT_FOUND'
message_map_chn[3004] = 'ERROR_3004_COUPON_OWNER_NOT_FOUND'
message_map_eng[3005] = 'ERROR_3005_COUPON_APPLY_ERROR'
message_map_chn[3005] = 'ERROR_3005_COUPON_APPLY_ERROR'
message_map_eng[3006] = 'ERROR_3006_PAYMENT_PRICE_INVALID'
message_map_chn[3006] = 'ERROR_3006_PAYMENT_PRICE_INVALID'
message_map_eng[3007] = 'ERROR_3007_DELIVERY_SCHEDULE_INVALID'
message_map_chn[3007] = 'ERROR_3007_DELIVERY_SCHEDULE_INVALID'
message_map_eng[3008] = 'ERROR_3008_ORDER_ID_INVALID'
message_map_chn[3008] = 'ERROR_3008_ORDER_ID_INVALID'
message_map_eng[3009] = 'ERROR_3009_ORDER_EDIT_NOT_AVAILABLE'
message_map_chn[3009] = 'ERROR_3009_ORDER_EDIT_NOT_AVAILABLE'
message_map_eng[3010] = 'ERROR_3010_DELIVERY_CHANGE_NOT_ALLOWED'
message_map_chn[3010] = 'ERROR_3010_DELIVERY_CHANGE_NOT_ALLOWED'
message_map_eng[3011] = 'ERROR_3011_NO_AVAILABLE_DELIVERY_SCHEDULE'
message_map_chn[3011] = 'ERROR_3011_NO_AVAILABLE_DELIVERY_SCHEDULE'
message_map_eng[3012] = 'ERROR_3012_NOT_SUPPORT_DELIVERY_METHOD'
message_map_chn[3012] = 'ERROR_3012_NOT_SUPPORT_DELIVERY_METHOD'
message_map_eng[3013] = 'ERROR_3013_COUPON_CREATION_FAILED'
message_map_chn[3013] = 'ERROR_3013_COUPON_CREATION_FAILED'
message_map_eng[3015] = 'There is a menu in your shopping bag that cannot be delivered in the time slot you selected'
message_map_chn[3015] = '您的购物袋中有一件商品无法在您选择的时间区间进行配送'
message_map_eng[3101] = 'ERROR_3101_SERIAL_NUMBER_INVALID'
message_map_chn[3101] = 'ERROR_3101_SERIAL_NUMBER_INVALID'
message_map_eng[3102] = 'ERROR_3102_SERIAL_ALREADY_ISSUED'
message_map_chn[3102] = 'ERROR_3102_SERIAL_ALREADY_ISSUED'
message_map_eng[3103] = 'ERROR_3103_COUPON_ISSUE_CONDITION_INVALID'
message_map_chn[3103] = 'ERROR_3103_COUPON_ISSUE_CONDITION_INVALID (chn)'
message_map_eng[3104] = 'COUPON_EXPIRED'
message_map_chn[3104] = '优惠券已过期'
message_map_eng[3105] = 'COUPON_ALREADY_ISSUED'
message_map_chn[3105] = '优惠券已发布'
message_map_eng[3106] = 'This events is only available on native platform.'
message_map_chn[3106] = 'This events is only available on native platform. (chn)'
message_map_eng[3201] = 'Reward point not enough. Please check your point.'
message_map_chn[3201] = 'Reward point not enough. Please check your point. (chn)'
message_map_eng[3202] = 'This reward coupon is already issued. Please check your coupon.'
message_map_chn[3202] = 'This reward coupon is already issued. Please check your coupon. (chn)'

# Payment error message
# ERROR_4005_PAYMENT_SYNC_ERROR
message_map_eng[4001] = 'ERROR_4001_PAYMENT_VALIDATION_FAILED'
message_map_chn[4001] = 'ERROR_4001_PAYMENT_VALIDATION_FAILED (chn)'
message_map_eng[4002] = 'ERROR_4002_PAYMENT_IS_NOT_FOUND'
message_map_chn[4002] = 'ERROR_4002_PAYMENT_IS_NOT_FOUND (chn)'
message_map_eng[4003] = 'ERROR_4003_PAYMENT_REFUND_FAIL'
message_map_chn[4003] = 'ERROR_4003_PAYMENT_REFUND_FAIL (chn)'
message_map_eng[4004] = 'ERROR_4004_PAYMENT_INTERFACE_FAILED'
message_map_chn[4004] = 'ERROR_4004_PAYMENT_INTERFACE_FAILED (chn)'
message_map_eng[4005] = 'ERROR_4005_PAYMENT_SYNC_ERROR'
message_map_chn[4005] = 'ERROR_4005_PAYMENT_SYNC_ERROR (chn)'

# Temporary roulette error message
message_map_eng[5001] = 'Event period finished'
message_map_chn[5001] = '活动时间已过期'
message_map_eng[5002] = 'You are already played. Please try again next time.'
message_map_chn[5002] = '您已经转过一次，下次再试哦'
message_map_eng[5003] = 'Event information error'
message_map_chn[5003] = '活动信息有误'
message_map_eng[5004] = 'Event history create error'
message_map_chn[5004] = '活动历史有误'


def get(code, cn_header):
    mapper = message_map_chn if cn_header else message_map_eng
    return mapper.get(code, 'Do not find key. Please call CS center')


def get_with_target_db(code, target_db):
    mapper = message_map_chn if target_db == 'aries_cn' else message_map_eng
    return mapper.get(code, 'Do not find key. Please call CS center')
