import smtplib
import passw

smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.starttls()

smtpObj.login(passw.login, passw.password)

