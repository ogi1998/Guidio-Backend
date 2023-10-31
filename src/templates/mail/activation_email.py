def html(**kwargs):
    return f"""\
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
            </head>
            <body>
                <h1>Hi {kwargs["first_name"]}</h1>
                <p>To activate your account, click on the link below:</p><br>
                <a>{kwargs["url"]}</a>
            </body>
        </html>"""


if __name__ == "main":
    html()
