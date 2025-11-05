import smtplib
import passw

smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)

smtpObj.login(passw.login, passw.password)
