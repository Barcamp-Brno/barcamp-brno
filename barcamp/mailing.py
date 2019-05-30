# coding: utf-8
import markdown

from flask import request
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .barcamp import app

def Message(to, subject, body_html, body_txt, from_email="petr@barcampbrno.cz", from_name="Petr z Barcamp Brno"):
    return {
            'from': { 'email': from_email, 'name': from_name},
            'personalizations': [{'to': [{'email': to}],'subject': subject}],
            'content': [
                {'type': 'text/plain', 'value': body_txt},
                {'type': 'text/html', 'value': body_html}
            ]
        }

def send_message(message):
    try:
        sg = SendGridAPIClient(app.config.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return True
    except Exception as e:
        print(e.message)
        return False


def send_message_from_template(subject, to, template, data, from_email="petr@barcampbrno.cz", from_name="Petr z Barcamp Brno"):
    data.update({
        'ip': request.remote_addr,
        'user_agent': request.user_agent,
        'mail': to,
    })

    body = read_file(template) or ""
    body = body % data

    message = Message(
        subject,
        to,
        markdown.markdown(body),
        body
    )
    return send_message(message)

def send_test_message():
    message = Message("petr@joachim.cz", 'test', '<h1>aaaa</h1>', 'aaaa')
    return send_message(message)

def read_file(filename):
    return open(filename).read()



# def send_feedback_mail(subject, template, data, user, url):
#     mail = Mail(app)
#     body = read_file(template) or ""
#
#     data = copy(data)
#     data['ip'] = request.remote_addr
#     data['user_agent'] = request.user_agent
#     data['url'] = url
#     data.update(user)
#     body = body % data
#
#     msg = Message(
#         subject,
#         recipients=["petr@joachim.cz"],
#         sender=(user['name'], user['email'])
#     )
#     msg.body = body
#     msg.html = markdown.markdown(body)
#     mail.send(msg)
#
#
# def mail_bulk_connection():
#     mail = Mail(app)
#     return mail.connect()
#
# def send_bulk_mail(conn, subject, to, message_file, url=""):
#     body = read_file(message_file) or ""
#     body = body % {
#         'url': url,
#         'ip': request.remote_addr,
#         'user_agent': request.user_agent,
#         'mail': to,
#     }
#
#     msg = Message(
#         subject,
#         recipients=[to],
#         sender=(u"Petr Joachim", "petr@joachim.cz")
#     )
#     msg.body = body
#     msg.html = markdown.markdown(body)
#     conn.send(msg)
#
#
# def mail(subject, sender, recipient, file, data, sender_name=None):
#     body = read_file(file) or ""
#
#     body = body % data
#     if sender_name:
#         sender = (sender_name, sender)
#
#     msg = Message(
#         subject,
#         sender=sender,
#         recipients=[recipient]
#     )
#
#     msg.body = body
#     msg.html = markdown.markdown(body)
#
#     mail = Mail(app)
#     return mail.send(msg)
