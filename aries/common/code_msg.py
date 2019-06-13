from __future__ import unicode_literals


msg_mapper = dict()

# COMMON
DEFAULT_MSG = 'UNKNOWN CODE'
msg_mapper[401] = ['Unauthorized requests', '认证错误']

# USER SIGN UP ERROR CODE
msg_mapper[1001] = ['Sms request data invalid.', '短信请求数据无效。']
msg_mapper[1002] = ['Sms sending failure.', '短信发送失败。']
msg_mapper[1003] = ['sms verification failure.', '短信验证失败。']
msg_mapper[1004] = ['User already registered.', '用户已注册。']
msg_mapper[1005] = ['User already registered.', '用户已注册。']
msg_mapper[1006] = ['Id or password error.', '账号或密码错误。']
msg_mapper[1007] = ['Member invalid.', '会员无效。']
msg_mapper[1008] = ['Sms validation info not found.', '找不到短信验证信息。']
msg_mapper[1009] = ['Sns token api error.', 'Sns token api 错误。']
msg_mapper[1010] = ['User already connected.', '用户已连接。']
msg_mapper[1011] = ['Get access token failure.', '获取access token失败。']
msg_mapper[1012] = ['Login info not found.', '找不到登录信息。']
msg_mapper[1013] = ['Only one login info', '只有一个登录信息']
msg_mapper[1014] = ['Incorrect current password', '当前密码不正确']
msg_mapper[1015] = ['Address slot not enough', '地址槽不足']
msg_mapper[1100] = ['File upload failure', '文件上传失败']
msg_mapper[1101] = ['Not supported file format', '不支持的文件格式']
msg_mapper[1102] = ['File over size', '超过文件大小']

# USER RECEIPT ERROR
msg_mapper[1201] = ['Receipt limit error', '收据限制错误']


# PRODUCT SIGN UP ERROR CODE
msg_mapper[2001] = ['Review already registered', '已注册的评论']

# PURCHASE ORDER ERROR CODE
msg_mapper[3001] = ['Product already sold', '您的购物袋中有一件已售尽的商品']
msg_mapper[3002] = ['Purchase order not found ', '未找到购买订单']
msg_mapper[3003] = ['User address invalid', '用户地址无效']
msg_mapper[3004] = ['Coupon owner not found', '未找到优惠券拥有者']
msg_mapper[3005] = ['Coupon apply error', '优惠券适用错误']
msg_mapper[3006] = ['Payment price invalid', '付款价格无效']
msg_mapper[3007] = ['Delivery schedule invalid', '配送时间段无效']
msg_mapper[3008] = ['Order id invalid', '订单ID无效']
msg_mapper[3009] = ['Order edit not available', '订单编辑不可用']
msg_mapper[3010] = ['Delivery change not changed', '配送更改未变更']
msg_mapper[3011] = ['No available delivery schedule', '没有可用的配送行程']
msg_mapper[3012] = ['Not support delivery method', '不支持配送方式']
msg_mapper[3015] = ['Product delivery time invalid', '您的购物袋中有一件商品无法在您选择的时间段进行配送']
msg_mapper[3016] = ['There are items that can not be purchased', '一些商品无法购买。']
msg_mapper[3017] = ['The time slot you selected has already passed.', '您选的时间段已过，请重新选择时间段。']
msg_mapper[3101] = ['Serial number invalid', '序列号无效']
msg_mapper[3102] = ['Serial number already issued', '序列号已经发行']
msg_mapper[3103] = ['Coupon issue condition invalid', '优惠券发行条件无效']
msg_mapper[3104] = ['Coupon expired', '优惠券已过期']
msg_mapper[3105] = ['Coupon already issued', '优惠券已经发行']
msg_mapper[3106] = ['Coupon issue platform error', '优惠券发行平台错误']

# 3200 - Referral coupon error
msg_mapper[3201] = ['Reward point not found', '奖励积分未找到']
msg_mapper[3202] = ['Reward already issue', '奖励已经发放']

# PAYMENT ERROR CODE
msg_mapper[4001] = ['Payment validation failed', '支付验证失败']
msg_mapper[4002] = ['Payment history is not found', '找不到支付历史记录']
msg_mapper[4003] = ['Payment refund failed', '支付退款失败']
msg_mapper[4004] = ['Payment interface connect failed', '支付接口链接失败']
msg_mapper[4005] = ['Payment sync error', '支付同步错误']

# ADMIN ERROR CODE
msg_mapper[8001] = ['Product already published', '产品已经发布']
msg_mapper[8002] = ['Plan schedule error', '计划时间表错误']

# MISC ERROR CODE
msg_mapper[9000] = ['Internal interface error', '请求数据无效。']
msg_mapper[9001] = ['Parameter error', '请求数据无效。']

# PASSWORD TEMP CODE
msg_mapper[1301] = ['You have created an account with us using your SNS account.' +
                    'Please use the SNS account to log in. *Only WeChat account ' +
                    'can be used for our WeChat APP in APP, Androids and iPhone.',
                    '您已是社交账号绑定顾客，请通过社交账号登录。 微信账户，仅支持公众号平台以及APP端的登录。']
msg_mapper[1302] = ['We can\'t find member information.', '我们找不到会员信息']


# True is chinese
def get_msg(code, cn_header=True):
    if code not in msg_mapper:
        msg = DEFAULT_MSG
    else:
        index = 1 if cn_header else 0
        msg = msg_mapper[code][index]

    return msg
