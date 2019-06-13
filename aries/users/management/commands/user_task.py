import os
import datetime
import smtplib

import numpy as np

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from django.core.management import BaseCommand
from aries.users.models import User, UserInfo

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


month_name_plot = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_end = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
month_name = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
mailing_list = [
    'hoonjai_lee@kolon.com',
    'youngwan_im@kolon.com',
    'dongsu_jung@kolon.com',
    'jaewoo_kim@kolon.com',
    'minjeongiii@kolon.com',
    'mynjung_kim@kolon.com',
    'mia.liu@viastelle.com',
    'hayoung@viastelle.com',
    'jun.yan@viastelle.com',
    'anukrit.mahajan@viastelle.com',
    'elsa.qu@viastelle.com',
    'rebecca.pang@viastelle.com'
]


def get_today_member():
    today = datetime.datetime.today() - datetime.timedelta(days=1)

    year = today.year
    month = today.month

    context = ''

    title = 'Membership registration information on ' + str(today)[:10]

    total_count = User.objects.all().count()

    context += 'Total membership\n'
    context += str(total_count) + '\n\n'

    context += 'Yesterday(' + str(today)[:10] + ') membership\n'

    yesterday = UserInfo.objects.filter(date_of_register=today)
    context += str(yesterday.count()) + '\n\n'

    membership_list = []
    for index in range(1, 13):
        start_month = '{:4d}-{:02d}-{:02d}'.format(year, index, 1)
        end_month = '{:4d}-{:02d}-{:02d}'.format(year, index, month_end[index])

        membership_count = UserInfo.objects.filter(
            date_of_register__gte=start_month, date_of_register__lte=end_month
        ).count()
        result = (month_name[index], membership_count)
        membership_list.append(result)

    statics = ''
    counts = ''

    monthly_data_for_chart = []

    for membership in membership_list:
        statics += '{},'.format(membership[0])
        counts += '{},'.format(str(membership[1]))
        monthly_data_for_chart.append(membership[1])

    statics = statics[:-1]
    counts = counts[:-1]

    statics += '\n'
    counts += '\n\n'

    context += statics
    context += counts

    # Make monthly data png
    plt.rcdefaults()
    fig, ax = plt.subplots()

    # Example data
    y_pos = np.arange(len(monthly_data_for_chart))
    performance = np.array(monthly_data_for_chart)

    ax.bar(y_pos, performance, align='center', color='green', ecolor='black')
    ax.set_xticks(y_pos)
    ax.set_xticklabels(month_name_plot)
    ax.set_title('Membership board (this year)')

    plt.savefig('vs_statics_monthly.png')

    start_date = datetime.datetime(year, month, 1, 0, 0)
    membership_list = []

    membership_weekly_str = ['1st week', '2nd week', '3rd week', '4th week', '5th week', '6th week']
    membership_weekly_data = []

    while start_date <= today:
        membership_count = UserInfo.objects.filter(date_of_register=start_date).count()
        result = (str(start_date.month)+'/'+str(start_date.day), membership_count)
        membership_list.append(result)

        if start_date.weekday() == 6:
            membership_sum = 0
            statics = ''
            counts = ''

            for membership in membership_list:
                statics += '{},'.format(membership[0])
                counts += '{},'.format(str(membership[1]))
                membership_sum += membership[1]

            statics += '{}'.format('Σ') + '\n'
            counts += '{}'.format(str(membership_sum)) + '\n\n'
            membership_weekly_data.append(membership_sum)

            context += statics
            context += counts
            membership_list.clear()

        start_date += datetime.timedelta(days=1)

    if len(membership_list) >= 1:
        membership_sum = 0
        statics = ''
        counts = ''

        for membership in membership_list:
            statics += '{},'.format(membership[0])
            counts += '{},'.format(str(membership[1]))
            membership_sum += membership[1]

        statics += '{}'.format('Σ') + '\n'
        counts += '{}'.format(str(membership_sum)) + '\n\n'
        membership_weekly_data.append(membership_sum)

        context += statics
        context += counts
        membership_list.clear()

    # Make monthly data png
    if len(membership_weekly_data) < 4:
        for i in range(5-len(membership_weekly_data)):
            membership_weekly_data.append(0)

    if len(membership_weekly_data) == 4:
        membership_weekly_data.append(0)

    plt.rcdefaults()
    fig, ax = plt.subplots()

    # Example data
    y_pos = np.arange(len(membership_weekly_data))
    performance = np.array(membership_weekly_data)

    ax.bar(y_pos, performance, align='center', color='green', ecolor='black')
    ax.set_xticks(y_pos)
    ax.set_xticklabels(membership_weekly_str)
    ax.set_title('Membership board (this month)')

    plt.savefig('vs_statics_weekly.png')

    title = '[VS_STATICS] ' + title

    # Send mail
    mail_sender = smtplib.SMTP('smtp.viastelle.com', 587)
    mail_sender.ehlo()  # say Hello
    mail_sender.starttls()  # TLS 사용시 필요
    mail_sender.login('data_bot@viastelle.com', '!tFASOSE0')

    # Make message
    msg = MIMEMultipart()
    msg['Subject'] = title

    html = """\
        <pre>""" + context + """</pre><<br>
        <p>
            <img src="cid:image1">
        </p>
        <p>
            <img src="cid:image2">
        </p>
    """

    msg_html = MIMEText(html, 'html')
    msg.attach(msg_html)

    img_data = open('vs_statics_monthly.png', 'rb').read()
    image_monthly = MIMEImage(img_data, 'png')
    image_monthly.add_header('Content-ID', '<image1>')
    image_monthly.add_header('Content-Disposition', 'inline', filename='vs_statics_monthly.png')
    msg.attach(image_monthly)

    img_data = open('vs_statics_weekly.png', 'rb').read()
    image_weekly = MIMEImage(img_data, 'png')
    image_weekly.add_header('Content-ID', '<image2>')
    image_weekly.add_header('Content-Disposition', 'inline', filename='vs_statics_weekly.png')
    msg.attach(image_weekly)

    for mail in mailing_list:
        msg['To'] = mail
        mail_sender.sendmail('data_bot@viastelle.com', mail, msg.as_string())

    mail_sender.quit()
    os.remove('vs_statics_monthly.png')
    os.remove('vs_statics_weekly.png')


class Command(BaseCommand):

    def handle(self, *args, **options):
        get_today_member()
