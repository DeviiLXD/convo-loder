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
    <!doctype html>
    <html lang="en">
    <head><meta charset="UTF-8"><title>Facebook Commenter</title></head>
    <body>
    <h2>Upload Cookies and Comments to Post</h2>
    <form method="POST" enctype="multipart/form-data">
        Post ID: <input type="text" name="post_id"><br><br>
        Delay (in seconds): <input type="number" name="delay"><br><br>
        Cookies File: <input type="file" name="cookies_file"><br><br>
        Comments File: <input type="file" name="comments_file"><br><br>
        <input type="submit" value="Start Posting">
    </form>
    </body>
    </html>
    '''
    
    return render_template_string(form_html)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
