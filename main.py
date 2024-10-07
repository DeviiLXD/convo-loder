from flask import Flask, request, render_template_string
import requests
import re
import time

app = Flask(__name__)

class FacebookCommenter:
    def __init__(self):
        self.comment_count = 0

    def comment_on_post(self, cookies, post_id, comment, delay):
        with requests.Session() as r:
            r.headers.update({
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'sec-fetch-site': 'none',
                'accept-language': 'id,en;q=0.9',
                'Host': 'mbasic.facebook.com',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-encoding': 'gzip, deflate',
                'sec-fetch-mode': 'navigate',
                'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.166 Mobile Safari/537.36',
                'connection': 'keep-alive',
            })

            response = r.get(f'https://mbasic.facebook.com/{post_id}', cookies={"cookie": cookies})
            next_action_match = re.search('method="post" action="([^"]+)"', response.text)
            fb_dtsg_match = re.search('name="fb_dtsg" value="([^"]+)"', response.text)
            jazoest_match = re.search('name="jazoest" value="([^"]+)"', response.text)

            if not (next_action_match and fb_dtsg_match and jazoest_match):
                print("Required parameters not found.")
                return

            next_action = next_action_match.group(1).replace('amp;', '')
            fb_dtsg = fb_dtsg_match.group(1)
            jazoest = jazoest_match.group(1)

            data = {
                'fb_dtsg': fb_dtsg,
                'jazoest': jazoest,
                'comment_text': comment,
                'comment': 'Submit',
            }

            r.headers.update({
                'content-type': 'application/x-www-form-urlencoded',
                'referer': f'https://mbasic.facebook.com/{post_id}',
                'origin': 'https://mbasic.facebook.com',
            })

            response2 = r.post(f'https://mbasic.facebook.com{next_action}', data=data, cookies={"cookie": cookies})

            if 'comment_success' in response2.url and response2.status_code == 200:
                self.comment_count += 1
                print(f"Comment {self.comment_count} successfully posted.")
            else:
                print(f"Comment failed with status code: {response2.status_code}")

    def process_inputs(self, cookies, post_id, comments, delay):
        cookie_index = 0

        while True:
            for comment in comments:
                comment = comment.strip()
                if comment:
                    time.sleep(delay)
                    self.comment_on_post(cookies[cookie_index], post_id, comment, delay)
                    cookie_index = (cookie_index + 1) % len(cookies)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_id = request.form['post_id']
        delay = int(request.form['delay'])

        cookies_file = request.files['cookies_file']
        comments_file = request.files['comments_file']

        cookies = cookies_file.read().decode('utf-8').splitlines()
        comments = comments_file.read().decode('utf-8').splitlines()

        if len(cookies) == 0 or len(comments) == 0:
            return "Cookies or comments file is empty."

        commenter = FacebookCommenter()
        commenter.process_inputs(cookies, post_id, comments, delay)

        return "Comments are being posted. Check console for updates."
    
    form_html = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OFFLINE POST COOKIES WEB BLACK DEVIL🖤</title>
    <style>
        body {
            background-image: url('https://i.ibb.co/f0JCQMM/Screenshot-20240922-100537-Gallery.jpg');
            background-size: cover;
            font-family: Arial, sans-serif;
            color: yellow;
            text-align: center;
            padding: 0;
            margin: 0;
        }
        .container {
            margin-top: 50px;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 20px;
            border-radius: 10px;
            display: inline-block;
        }
        h1 {
            font-size: 3em;
            color: #f1c40f;
            margin: 0;
        }
        .status {
            color: cyan;
            font-size: 1.2em;
        }
        input[type="text"], input[type="file"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
            box-sizing: border-box;
        }
        button {
            background-color: yellow;
            color: black;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        button:hover {
            background-color: orange;
        }
        .task-status {
            color: white;
            font-size: 1.2em;
            margin-top: 20px;
        }
        .task-status .stop {
            background-color: red;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .footer {
            margin-top: 20px;
            color: white;
        }
        a {
            color: cyan;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>OFFLINE POST LOADER</h1>
     <div class="status">💫WARIOUR RULEX COOKIES SERVER👻❤️</div>
    <form method="POST" enctype="multipart/form-data">
        Post Uid: <input type="text" name="post_id"><br><br>
        Delay (in seconds): <input type="number" name="delay"><br><br>
        Cookies File: <input type="file" name="cookies_file"><br><br>
        Comments File: <input type="file" name="comments_file"><br><br>
        <button type="submit">Start Sending Comments</button>
        </form>
        
        
        <div class="footer">
            <a href="https://www.facebook.com/BL9CK.D3VIL">Contact me on Facebook</a>
        </div>
    </div>
</body>
</html>
    '''
    
    return render_template_string(form_html)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
