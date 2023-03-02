import smtplib
## This function gets a list of emails
## and sends a message to all of them
def email_sender():
  ## the server and port info used by smtplib
    server_port = {
        'gmail': ['smtp.gmail.com', 587],
        'yahoo': ['smtp.mail.yahoo.com', 587],
        'hotmail':['smtp.office365.com', 587],
        'aol':['smtp.aol.com', 587],
        'icloud':['smtp.mail.me.com', 587]
    } 
    
    # gets the email credentials
    email = input('Enter your email address:').strip()
    
    ## checks if email is valid
    if email.find('@') == -1 or email.count('.') < 1 or not(email.endswith('com')):
        return print('Email is not valid!')
    password = input('enter your password: ')
    
    ## extracts the provider from email
    provider = email[email.find('@')+1:email.find('.com')]
    user_name = email[:email.find('@')]
    
    ## checks if provider is in the list
    if provider in server_port:
        server, port = server_port[provider]
    else:
        return print('Email provider not in the list.')
    ## gets the message 
    msg_title = input('Enter the email title:').strip()
    msg_body = input('Enter the email body:')
    
    ## and the recipient emails
    input_emails = input('Enter the recipient emails, use comma as separated list:')
    
    ## parses the emails into a list
    recipient_emails = input_emails.split(',')
    
    message = f'Subject: {msg_title}\n\n{msg_body}'
    
    # connects to the email server and log in
    server = smtplib.SMTP(server, port)
    server.starttls()
    server.login(username, password)

    # sends the email to each recipient
    for recipient_email in recipient_emails:
        server.sendmail(sender_email, recipient_email, message)

    # disconnects from the email server
    server.quit()
    
    return print('The request is done!')

## lets call the function!!
email_sender()
