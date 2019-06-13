# My news order success
MY_NEWS_ORDER_SUCCESS_TITLE_EN = 'ORDER SUCCESS'
MY_NEWS_ORDER_SUCCESS_TITLE_CN = '成功下单'
MY_NEWS_ORDER_SUCCESS_CONTENT_EN = '["Your order was placed successfully"]'
MY_NEWS_ORDER_SUCCESS_CONTENT_CN = '["您已成功下单"]'

# My news order complete
MY_NEWS_DELIVERY_COMPLETE_TITLE_EN = 'DELIVERY COMPLETE'
MY_NEWS_DELIVERY_COMPLETE_TITLE_CN = '配送完成'
MY_NEWS_DELIVERY_COMPLETE_CONTENT_EN = '["Your delivery has been completed"]'
MY_NEWS_DELIVERY_COMPLETE_CONTENT_CN = '["您的订单已完成配送"]'

# My news order cancel
MY_NEWS_ORDER_CANCEL_TITLE_EN = 'ORDER CANCELED'
MY_NEWS_ORDER_CANCEL_TITLE_CN = '成功取消'
MY_NEWS_ORDER_CANCEL_CONTENT_EN = '["Your order cancellation has been submitted successfully"]'
MY_NEWS_ORDER_CANCEL_CONTENT_CN = '["您已成功提交取消订单申请"]'

# My news review request
MY_NEWS_REVIEW_REQUEST_TITLE_EN = 'How was the food?'
MY_NEWS_REVIEW_REQUEST_TITLE_CN = '菜品味道怎么样？'
MY_NEWS_REVIEW_REQUEST_CONTENT_EN = '["Let us know what you think by dropping us a line on REVIEWS & COMMENTS！"]'
MY_NEWS_REVIEW_REQUEST_CONTENT_CN = '["请通过评论或留言告诉我们您的感受和体验吧!"]'

# push - order success
PUSH_ORDER_SUCCESS_CONTENT_EN = 'We’ve got your order! Coming right up.'
PUSH_ORDER_SUCCESS_CONTENT_CN = '我们已收到您的订单！马上为您准备。'

# push - order preparing
PUSH_ORDER_PREPARING_CONTENT_EN = 'Kitchen just got busy! Your food will be ready soon.'
PUSH_ORDER_PREPARING_CONTENT_CN = '请稍等，厨房现在有点忙！您的食物会尽快准备好。'

# push - order delivery start
PUSH_DELIVERY_START_CONTENT_EN = 'Your food is on its way! Please wait for a short while.'
PUSH_DELIVERY_START_CONTENT_CN = '美味已经在路上啦！请稍等一会。'

# push - order delivery complete
PUSH_DELIVERY_COMPLETE_CONTENT_EN = 'Delivery has been completed. Bon appetite!'
PUSH_DELIVERY_COMPLETE_CONTENT_CN = '已完成配送，祝您用餐愉快！'

# push - order cancel
PUSH_ORDER_CANCEL_CONTENT_EN = 'Your order has been canceled. Hope to see you soon!'
PUSH_ORDER_CANCEL_CONTENT_CN = '您的订单已被取消， 期待下次再见到您！'

# menu - added data
MICROWAVE_EN = '* This menu needs to be heated up in the microwave\n'
MICROWAVE_CN = '* 此菜品需在微波炉中加热\n'
LUNCH_MENU_EN = '* This menu is available both for lunch and dinner ' \
                '(Lunch delivery : 11AM – 3PM / Dinner delivery : 3PM – 9PM)\n\n'
LUNCH_MENU_CN = '* 此菜品在午餐和晚餐时段都将供应 （午餐配送：11AM-3PM/晚餐配送：3PM-9PM）\n\n'
DINNER_MENU_EN = '* This menu is for dinner only (Dinner delivery : 3PM – 9PM)\n\n'
DINNER_MENU_CN = '* 此菜品仅晚餐供应 （晚餐配送：3PM-9PM）\n\n'


NEWS_ORDER_SUCCESS = 2
NEWS_ORDER_CANCEL = 3
NEWS_DELIVERY_COMPLETE = 5
NEWS_DELIVERY_REVIEW = 6


def get_mynews_message(news_type):
    if news_type == NEWS_ORDER_SUCCESS:
        result = (
            MY_NEWS_ORDER_SUCCESS_TITLE_CN, MY_NEWS_ORDER_SUCCESS_CONTENT_CN,
            MY_NEWS_ORDER_SUCCESS_TITLE_EN, MY_NEWS_ORDER_SUCCESS_CONTENT_EN,
        )
    elif news_type == NEWS_ORDER_CANCEL:
        result = (
            MY_NEWS_ORDER_CANCEL_TITLE_CN, MY_NEWS_ORDER_CANCEL_CONTENT_CN,
            MY_NEWS_ORDER_CANCEL_TITLE_EN, MY_NEWS_ORDER_CANCEL_CONTENT_EN,
        )
    elif news_type == NEWS_DELIVERY_COMPLETE:
        result = (
            MY_NEWS_DELIVERY_COMPLETE_TITLE_CN, MY_NEWS_DELIVERY_COMPLETE_CONTENT_CN,
            MY_NEWS_DELIVERY_COMPLETE_TITLE_EN, MY_NEWS_DELIVERY_COMPLETE_CONTENT_EN,
        )
    elif news_type == NEWS_DELIVERY_REVIEW:
        result = (
            MY_NEWS_REVIEW_REQUEST_TITLE_CN, MY_NEWS_REVIEW_REQUEST_CONTENT_CN,
            MY_NEWS_REVIEW_REQUEST_TITLE_EN, MY_NEWS_REVIEW_REQUEST_CONTENT_EN,
        )
    else:
        result = None
    return result


def get_order_success_push(cn_header):
    if cn_header:
        return PUSH_ORDER_SUCCESS_CONTENT_CN
    else:
        return PUSH_ORDER_SUCCESS_CONTENT_EN


def get_order_preparing_push(cn_header):
    if cn_header:
        return PUSH_ORDER_PREPARING_CONTENT_CN
    else:
        return PUSH_ORDER_PREPARING_CONTENT_EN


def get_delivery_start(cn_header):
    if cn_header:
        return PUSH_DELIVERY_START_CONTENT_CN
    else:
        return PUSH_DELIVERY_START_CONTENT_EN


def get_delivery_complete(cn_header):
    if cn_header:
        return PUSH_DELIVERY_COMPLETE_CONTENT_CN
    else:
        return PUSH_DELIVERY_COMPLETE_CONTENT_EN


def get_order_cancel_push(cn_header):
    if cn_header:
        return PUSH_ORDER_CANCEL_CONTENT_CN
    else:
        return PUSH_ORDER_CANCEL_CONTENT_EN


def get_about_the_menu_microwave(cn_header):
    if cn_header:
        return MICROWAVE_CN
    else:
        return MICROWAVE_EN


def get_about_the_menu_lunch(cn_header):
    if cn_header:
        return LUNCH_MENU_CN
    else:
        return LUNCH_MENU_EN


def get_about_the_menu_dinner(cn_header):
    if cn_header:
        return DINNER_MENU_CN
    else:
        return DINNER_MENU_EN


def get_about_desc(cn_header, sales_time):
    if sales_time == 0 and cn_header:
        result = LUNCH_MENU_CN
    elif sales_time == 0 and not cn_header:
        result = LUNCH_MENU_EN
    elif sales_time == 3 and cn_header:
        result = DINNER_MENU_CN
    else:
        result = DINNER_MENU_EN

    return result
